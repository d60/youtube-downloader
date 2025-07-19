from math import ceil
from threading import Thread
from uuid import uuid4

import pytubefix.request as pytube_request
import requests

import ffmpeg_progress
from conf import TEMP_DIR, download_process_database
from constants import DownloadStep, FileType
from database import SerializedStream

SEGMENT_SIZE = 1024 * 1024 * 9
pytube_request.default_range_size = SEGMENT_SIZE


def fetch_segment(url, file_size, segment, session: requests.Session):
    start = (segment - 1) * SEGMENT_SIZE
    end = min(start + SEGMENT_SIZE, file_size) - 1
    return session.get(
        f'{url}&range={start}-{end}'
    ).content


def get_stream_by_itag(streams, itag) -> SerializedStream | None:
    return next(
        filter(
            lambda x: str(x['itag']) == str(itag),
            streams
        ), None
    )


TYPE_STEP_MAP = {
    FileType.VIDEO: DownloadStep.DOWNLOADING_VIDEO,
    FileType.AUDIO: DownloadStep.DOWNLOADING_AUDIO
}


class FFmpeg:
    @staticmethod
    def run_with_range(cmd, start, end, output):
        if start:
            cmd += ['-ss', start]
        if end:
            cmd += ['-to', end]
        cmd.append(output)
        return ffmpeg_progress.run(cmd)

    @staticmethod
    def merge_video_and_audio(input_1, input_2, output, start, end):
        cmd = [
            'ffmpeg',
            '-i', input_1,
            '-i', input_2,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'mp4',
        ]
        return FFmpeg.run_with_range(cmd, start, end, output)

    @staticmethod
    def to_mp3(input, output, start, end):
        cmd = [
            'ffmpeg',
            '-i', input,
            '-vn',
            '-c:a', 'libmp3lame',
            '-f', 'mp3',
            '-threads', '1',
        ]
        return FFmpeg.run_with_range(cmd, start, end, output)

    @staticmethod
    def cut_file(input, output, start, end, format):
        cmd = [
            'ffmpeg',
            '-i', input,
            '-c', 'copy',
            '-f', format
        ]
        return FFmpeg.run_with_range(cmd, start, end, output)

CONVERT_MAP = {
    0: ('audio/mp3', DownloadStep.CONVERTING_TO_MP3, FFmpeg.to_mp3)
}


class DownloadError(Exception):
    ...



class DownloadSession:
    def __init__(self, sid):
        self.sid = sid
        self.output_dir = TEMP_DIR

    def set_progress(self, step: DownloadStep | None = None, progress: float | None = None):
        mapping = {}
        if step is not None:
            mapping['step'] = step
        if progress is not None:
            mapping['progress'] = progress
        download_process_database.update_data(self.sid, **mapping)

    def download_file(self, segment_count, stream, fp, session):
        for segment_number in range(1, segment_count + 1):
            seg = fetch_segment(stream['url'], stream['filesize'], segment_number, session)
            fp.write(seg)
            self.set_progress(progress=segment_number / segment_count)

    def download(self, streams: list[SerializedStream], itags, start, end):
        downloads: list[tuple[SerializedStream, FileType]]
        need_cutting = bool(start or end)

        downloads, mime_type, cvt_fn = self.prepare_downloads(streams, itags)
        download_process_database.delete_keys(self.sid, ['streams', 'available_itags'])

        try:
            filenames = self.download_files(downloads)
        except Exception as e:
            raise DownloadError('An error occurs while downloading file')

        if len(filenames) == 1:
            filename = filenames[0]
        if len(filenames) == 2:
            try:
                filename = self.merge_files(filenames, start, end)
            except Exception as e:
                raise DownloadError('An error occurs while merging files')
            need_cutting = False

        if cvt_fn is not None:
            try:
                filename = self.convert_file(filename, cvt_fn, start, end)
            except Exception as e:
                raise DownloadError('An error occurs while converting the file')
            need_cutting = False

        if need_cutting:
            try:
                filename = self.cut_file(filename, mime_type.split('/')[1], start, end)
            except Exception as e:
                raise DownloadError('An error occurs whille cutting the file')

        download_process_database.update_data(self.sid, mime_type=mime_type, filename=filename, step=DownloadStep.FINISHED)

    def prepare_downloads(self, streams: list[SerializedStream], itags):
        downloads: list[tuple[SerializedStream, FileType]] = []
        convert_flag = None
        cvt_fn = None

        if len(itags) == 1:
            itag = itags[0]
            parts = itag.split('/')
            itag = parts[0]
            stream = streams[0]
            mime_type = stream['mime_type']

            if itags[0].endswith('cvt'):
                convert_flag = int(parts[-2])
                if convert_flag not in CONVERT_MAP:
                    raise DownloadError(f'Invalid convert flag.')
                mime_type, self.step, cvt_fn = CONVERT_MAP[convert_flag]

            if stream['is_progressive']:
                file_type = FileType.VIDEO
            elif stream['includes_audio_track'] and not stream['includes_video_track']:
                file_type = FileType.AUDIO
            else:
                raise DownloadError(f'Format {itags[0]} is neither progressive nor audio-only.')

            downloads.append((stream, file_type))

        if len(itags) == 2:
            video_stream = get_stream_by_itag(streams, itags[0])
            audio_stream = get_stream_by_itag(streams, itags[1])
            if not (
                video_stream['includes_video_track'] and
                not video_stream['includes_audio_track'] and
                not audio_stream['includes_video_track'] and
                audio_stream['includes_audio_track']
            ):
                raise DownloadError(f'Format is incorrect')

            mime_type = 'video/mp4'
            downloads.append((video_stream, FileType.VIDEO))
            downloads.append((audio_stream, FileType.AUDIO))

        return downloads, mime_type, cvt_fn

    def download_files(self, downloads: list[tuple[SerializedStream, FileType]]):
        filenames = []
        for download in downloads:
            stream, file_type = download
            self.set_progress(step=TYPE_STEP_MAP[file_type], progress=0)
            filename = str(uuid4())
            filenames.append(filename)
            segment_count = ceil(stream['filesize'] / SEGMENT_SIZE)
            session = requests.Session()
            with open(self.output_dir / filename, 'wb') as fp:
                self.download_file(segment_count, stream, fp, session)
        return filenames

    def merge_files(self, filenames, start, end):
        self.set_progress(DownloadStep.MERGING_FILES, 0)
        filename = str(uuid4())
        input1 = self.output_dir / filenames[0]
        input2 = self.output_dir / filenames[1]
        output = self.output_dir / filename
        ffmpeg_gen = FFmpeg.merge_video_and_audio(input1, input2, output, start, end)
        for progress in ffmpeg_gen:
            self.set_progress(progress=progress)
        input1.unlink()
        input2.unlink()
        return filename

    def convert_file(self, filename, cvt_fn, start, end):
        self.set_progress(DownloadStep.CONVERTING_TO_MP3)
        filename_ = filename
        filename = str(uuid4())
        input = self.output_dir / filename_
        output = self.output_dir / filename
        gen = cvt_fn(input, output, start, end)
        for progress in gen:
            ###############
            ###############
            self.set_progress(progress=progress)
        input.unlink()
        return filename

    def cut_file(self, filename, format, start, end):
        self.set_progress(DownloadStep.CUTTING)
        filename_ = filename
        filename = str(uuid4())
        input = self.output_dir / filename_
        output = self.output_dir / filename
        gen = FFmpeg.cut_file(input, output, start, end, format)
        for progress in gen:
            ###############
            ###############
            self.set_progress(progress=progress)
        return filename

    def download_(self, *args, **kwargs):
        try:
            self.download(*args, **kwargs)
            return
        except DownloadError as e:
            error = e
        except Exception as e:
            error = DownloadError('Unknown error occurs')
        download_process_database.update_data(self.sid, error=str(error))

    def start_downloading(self, *args, **kwargs):
        thread = Thread(target=self.download_, args=args, kwargs=kwargs, daemon=True)
        thread.start()
