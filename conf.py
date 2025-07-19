from pathlib import Path

from redis import Redis

from database import DownloadProcessDatabase

download_process_database = DownloadProcessDatabase(
    client = Redis(host='localhost', port=6379, decode_responses=True, max_connections=100)
)
TEMP_DIR = Path('_temp')
