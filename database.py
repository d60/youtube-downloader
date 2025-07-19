from typing import Literal, TypedDict

import orjson
from pytubefix import Stream, StreamQuery
from redis import Redis

from constants import DownloadStep

TRUE = 1
FALSE = 0
BOOL_TYPE = Literal[0, 1]


class SerializedStream(TypedDict):
    url: str
    is_progressive: BOOL_TYPE
    is_adaptive: BOOL_TYPE
    mime_type: str
    itag: int
    includes_audio_track: BOOL_TYPE
    includes_video_track: BOOL_TYPE
    filesize: int


def serialize_stream(stream: Stream):
    return SerializedStream(
        url=stream.url,
        is_progressive=int(stream.is_progressive),
        is_adaptive=int(stream.is_adaptive),
        mime_type=stream.mime_type,
        itag=stream.itag,
        includes_audio_track=int(stream.includes_audio_track),
        includes_video_track=int(stream.includes_video_track),
        filesize=stream.filesize
    )


class SerializedProcessData(TypedDict, total=False):
    streams: str
    error: str
    filename: str
    step: int
    title: str
    channel: str
    vid: str
    available_itags: str
    progress: str


def selialize_process_data(**kwargs) -> SerializedProcessData:
    if 'streams' in kwargs:
        kwargs['streams'] = orjson.dumps(kwargs['streams'])
    if 'step' in kwargs:
        kwargs['step'] = kwargs['step'].value
    if 'available_itags' in kwargs:
        kwargs['available_itags'] = '|'.join(kwargs['available_itags'])
    if 'progress' in kwargs:
        kwargs['progress'] = str(kwargs['progress'])
    return kwargs


class ProcessData(TypedDict, total=False):
    streams: list[SerializedStream]
    error: str
    filename: str
    step: DownloadStep
    title: str
    channel: str
    vid: str
    available_itags: list[str]
    progress: float
    mime_type: str


def deselialize_process_data(data: dict):
    if 'streams' in data:
        data['streams'] = orjson.loads(data['streams'])
    if 'step' in data and data['step'] is not None:
        data['step'] = DownloadStep(int(data['step']))
    if 'available_itags' in data:
        data['available_itags'] = data['available_itags'].split('|')
    if 'progress' in data and data['progress'] is not None:
        data['progress'] = float(data['progress'])
    return data


class DownloadProcessDatabase:
    def __init__(self, client: Redis) -> None:
        self.client = client

    def create_process(self, sid, streams: StreamQuery, title, channel, vid, available_itags):
        serialize_streams = [serialize_stream(stream) for stream in streams]
        value = selialize_process_data(
            streams=serialize_streams,
            step=DownloadStep.STANDBY,
            title=title,
            channel=channel,
            vid=vid,
            available_itags=available_itags
        )
        self.client.hset(sid, mapping=value)
        self.client.expire(sid, 1000)

    def get_process(self, sid, keys) -> ProcessData | None:
        try:
            pr = self.client.hmget(sid, keys)
            return deselialize_process_data(
                dict(zip(keys, pr))
            )
        except orjson.JSONDecodeError:
            return None

    def exists(self, sid):
        return bool(self.client.exists(sid))

    def update_data(self, sid, **mapping):
        self.client.hset(sid, mapping=selialize_process_data(**mapping))

    def delete_process(self, sid):
        self.client.delete(sid)

    def delete_keys(self, sid, keys):
        self.client.hdel(sid, *keys)

    def expire(self, sid, time):
        self.client.expire(sid, time)
