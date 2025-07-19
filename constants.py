from enum import Enum


class DownloadStep(Enum):
    STANDBY = 0
    DOWNLOADING_VIDEO = 1
    DOWNLOADING_AUDIO = 2
    MERGING_FILES = 3
    CONVERTING_TO_MP3 = 4
    CUTTING = 5
    STOPPED = 7
    ERROR = 8
    FINISHED = 9

class FileType(Enum):
    VIDEO = 0
    AUDIO = 1
