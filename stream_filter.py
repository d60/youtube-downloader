from pytubefix import Stream, StreamQuery


def get_valid_audio_formats(streams: StreamQuery) -> list[Stream]:
    def filter_(x: Stream):
        return all([
            x.mime_type in ('audio/mp4', 'audio/webm'),
            x.includes_audio_track and not x.includes_video_track
        ])

    streams = list(filter(filter_, streams))

    done = set()
    result = []
    for s in streams:
        if s.itag not in done:
            done.add(s.itag)
            result.append(s)
    return result


def get_valid_video_formats(streams: StreamQuery) -> list[Stream]:
    def filter_(x: Stream):
        return all([
            x.mime_type in 'video/mp4',
            x.video_codec and x.video_codec.startswith('avc1')
        ])
    return list(filter(filter_, streams))


def get_valid_formats(streams):
    valid_audio_formats = get_valid_audio_formats(streams)
    valid_video_formats = get_valid_video_formats(streams)
    audio_formats = []
    video_formats = []

    for f in valid_audio_formats:
        audio_formats.append([f.mime_type, f.abr, [str(f.itag)]])


    mp4_audio = next(
        (x for x in valid_audio_formats if x.mime_type == 'audio/mp4')
    )
    audio_formats.append(
        ['audio/mp3', mp4_audio.abr, [str(mp4_audio.itag) + '/0/cvt']]
    )

    for f in valid_video_formats:
        if f.is_progressive:
            video_formats.append([f.mime_type, f.resolution, [str(f.itag)]])
        else:
            if next(
                filter(
                    lambda x:
                        x[0] == f.mime_type and
                        x[1] == f.resolution and
                        len(x[2]) == 1,
                    video_formats
                ),
                None
            ):
                continue
            video_formats.append([f.mime_type, f.resolution, [str(f.itag), str(mp4_audio.itag)]])
    video_formats.sort(key=lambda x: int(x[1].removesuffix('p')))

    return {
        'audio': audio_formats,
        'video': video_formats
    }
