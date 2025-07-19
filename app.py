import asyncio
import json
import os
import re
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import pytubefix
import tzlocal
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, ORJSONResponse, PlainTextResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pytubefix.exceptions import AgeRestrictedError
from starlette.middleware.sessions import SessionMiddleware
from ytsearch import Search

from conf import TEMP_DIR, download_process_database
from constants import DownloadStep
from downloads import DownloadSession, get_stream_by_itag
from stream_filter import get_valid_formats

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.urandom(12))
app.mount('/static', StaticFiles(directory='static'), name='static')


@asynccontextmanager
async def lifespan(app: FastAPI):
    from apscheduler.schedulers.background import BackgroundScheduler

    from file_clean import FileCleaner
    from minify import minify

    TEMP_DIR.mkdir(exist_ok=True)
    minify()
    file_cleaner = FileCleaner(TEMP_DIR, 60 * 7, 60 * 3)
    scheduler = BackgroundScheduler(timezone=str(tzlocal.get_localzone()))
    scheduler.add_job(func=file_cleaner.check, trigger='interval', seconds=20)
    scheduler.start()
    [tempfile.unlink() for tempfile in TEMP_DIR.iterdir()]
    yield

app.router.lifespan_context = lifespan


def get_channel_name(youtube: pytubefix.YouTube):
    name = youtube.vid_info.get('videoDetails', {}).get('author', None)
    if not name:
        try:
            name = youtube.vid_info['endscreen']['endscreenRenderer']['elements'][0]['endscreenElementRenderer']['title']['simpleText']
        except KeyError:
            pass
    return name


@app.get('/')
def index():
    return FileResponse('templates/index.html')


class SearchPayload(BaseModel):
    query: str


@app.post('/search')
def search_videos(payload: SearchPayload):
    videos = list(Search().search_videos(payload.query))
    return ORJSONResponse([
        {
            'id': video.id,
            'title': video.title,
            'channel': video.channel_name
        }
        for video in videos
    ])


def secs_to_str(secs):
    hours = secs // 3600
    minutes = (secs % 3600) // 60
    seconds = secs % 60
    return '{:0>2}:{:0>2}:{:0>2}'.format(hours, minutes, seconds)


@app.get('/download/init')
async def download_metadata(request: Request, url: str | None = None):
    if not url:
        return ORJSONResponse({'error': 'Missing parameter: url'}, 400)

    if 'sid' in request.session and download_process_database.exists(request.session['sid']):
        download_process_database.delete_process(request.session['sid'])

    sid = str(uuid4())
    request.session['sid'] = sid

    youtube = pytubefix.YouTube(url, use_oauth=False, token_file='./token.json')
    try:
        streams = youtube.streams
    except AgeRestrictedError:
        youtube = pytubefix.YouTube(url, use_oauth=True, token_file='./token.json')
        streams = youtube.streams
    except Exception as e:
        print(e)
        return ORJSONResponse({'error': 'Failed to retrieve video information.'}, 500)
    formats = get_valid_formats(streams)

    available_itags = set()
    for formats_ in (formats['video'], formats['audio']):
        for format in formats_:
            available_itags |= set(format[2])

    download_process_database.create_process(
        sid,
        streams=streams,
        title=youtube.title,
        channel=get_channel_name(youtube) or 'UNKNOWN',
        vid=youtube.video_id,
        available_itags=available_itags
    )
    return ORJSONResponse({
        'id': youtube.video_id,
        'title': youtube.title,
        'channel': get_channel_name(youtube),
        'thumbnail': youtube.thumbnail_url,
        'formats': formats,
        'range': secs_to_str(youtube.length)
    })

TIME_PATTERN = re.compile(r'^(\d*):(\d{1,2}):(\d{1,2})$|^(\d{1,2}):(\d{1,2})$')

class DownloadStartPayload(BaseModel):
    format: str | None = None
    start: str | None = None
    end: str | None = None


@app.post('/download/s')
async def download_start(request: Request, payload: DownloadStartPayload):
    sid = request.session.get('sid')
    session = download_process_database.get_process(sid, ['available_itags', 'step', 'streams'])

    if not session:
        return ORJSONResponse({'error': 'No active download session'}, 403)

    if session['step'] != DownloadStep.STANDBY:
        return {'error': 'session has already started'}, 400

    itags_raw = payload.format
    if not itags_raw:
        return {'error': 'Missing parameter "format"'}, 400

    itags = itags_raw.split('|')

    if not (1 <= len(itags) <= 2):
        return {'error': 'Invalid parameter "format"'}

    for itag in itags:
        if itag not in session['available_itags']:
            return {'error': 'Invalid parameter "format"'}, 400

    start = payload.start
    end = payload.end
    if start:
        if not TIME_PATTERN.fullmatch(start):
            return {'error': 'Invalid parameter "start"'}, 400
    if end:
        if not TIME_PATTERN.fullmatch(end):
            return {'error': 'Invalid parameter "end"'}, 400

    itags_ = [t.split('/')[0] for t in itags]
    streams = [get_stream_by_itag(session['streams'], t) for t in itags_]
    DownloadSession(sid).start_downloading(streams, itags, start, end)

    return ORJSONResponse({})

async def status_sse(sid):
    INCLUDE_PROGRESS_STEPS = (
        DownloadStep.DOWNLOADING_AUDIO,
        DownloadStep.DOWNLOADING_VIDEO,
        DownloadStep.CONVERTING_TO_MP3,
        DownloadStep.MERGING_FILES
    )

    while True:
        process = download_process_database.get_process(sid, ['step', 'progress', 'error', 'filename'])
        STEP = process['step'] or DownloadStep.STANDBY

        data = {
            'step': STEP.value,
        }
        if STEP in INCLUDE_PROGRESS_STEPS:
            data['progress'] = process['progress']

        if STEP == DownloadStep.ERROR:
            data['error'] = process['error']
            break

        if STEP == DownloadStep.FINISHED:
            data['fileId'] = process['filename']
            break

        yield 'data: %s\n\n' % json.dumps(data)
        await asyncio.sleep(1)
    yield 'data: %s\n\n' % json.dumps(data)


@app.get('/download/status')
def download_status(request: Request):
    sid = request.session.get('sid')
    if not sid:
        return ORJSONResponse({'error': 'No active download session'}, 403)
    return StreamingResponse(status_sse(sid), media_type='text/event-stream')


def is_uuid4(string):
    try:
        UUID(string, version=4)
        is_uuid4 = True
    except ValueError:
        is_uuid4 = False
    return is_uuid4


@app.get('/download')
async def download(request: Request, file: str | None, dnf: str = '[title]'):
    file_id = file
    if not file_id:
        return ORJSONResponse({'error': 'Missing parameter "file"'}, 400)
    if not is_uuid4(file_id):
        return ORJSONResponse({'error': 'Invalid parameter "file"'}, 400)

    sid = request.session.get('sid')

    session = download_process_database.get_process(sid, ['filename', 'mime_type', 'vid', 'title', 'channel'])

    if not session:
        return ORJSONResponse({'error': 'No active download session'}, 403)

    if session['filename'] != file_id:
        return ORJSONResponse({'error': 'You do not have permission to access this file'}, 403)

    file_path = TEMP_DIR / file_id
    if not file_path.exists():
        return ORJSONResponse({'error': 'File not found'}, 404)

    mime_type = session['mime_type']

    file_type, file_format = mime_type.split('/')

    if file_type == 'video':
        ext = 'mp4'
    if file_type == 'audio':
        if file_format == 'mp4':
            ext = 'm4a'
        else:
            ext = file_format

    download_name_format = dnf
    download_name_format = download_name_format.replace('[id]', session['vid'])
    download_name_format = download_name_format.replace('[title]', session['title'])
    download_name_format = download_name_format.replace('[channel]', session['channel'] or 'UNKNOWN')
    download_process_database.delete_process(sid)
    response = FileResponse(file_path, media_type=mime_type, filename=f'{download_name_format}.{ext}')
    return response


@app.get('/robots.txt', response_class=PlainTextResponse)
def robots_txt():
    return 'User-agent: *\nDisallow:\n\nSitemap: https://ytdler.com/sitemap.xml'


pages = [
    {'loc': 'https://ytdler.com/', 'lastmod': '2025-07-19'},
]

@app.get('/sitemap.xml', response_class=Response)
async def sitemap():
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_xml += f"""  <url>
    <loc>{page["loc"]}</loc>
    <lastmod>{page["lastmod"]}</lastmod>
  </url>\n"""

    sitemap_xml += '</urlset>'

    return Response(content=sitemap_xml, media_type='application/xml')


@app.middleware('http')
async def add_cache_control_header(request, call_next):
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    return ORJSONResponse({'error': 'Internal server error'}, 500)

# HTTP 429 Too Many Requests
@app.exception_handler(429)
async def too_many_requests_handler(request: Request, exc: Exception):
    return ORJSONResponse({'error': 'Too many requests, please try again later.'}, 429)
