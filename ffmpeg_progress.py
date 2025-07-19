import re
import subprocess

DURATION_PATTERN = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{2})')
TIME_PATTERN = re.compile(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})')


def duration_str_to_secs(duration_str):
    return sum([
        60**i * float(x)
        for i, x in enumerate(reversed(duration_str.split(':')))
    ])


def run(cmd, *args, **kwargs):
    kwargs.update(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        universal_newlines=True
    )
    process = subprocess.Popen(cmd, *args, **kwargs)
    duration = None
    yield 0.0

    while True:
        output = process.stderr.readline()
        if not output and process.poll() is not None:
            break
        if output:
            line = output.strip()

            if not duration and line.startswith('Duration'):
                duration = duration_str_to_secs(DURATION_PATTERN.search(line).group(1))
                continue

            m = TIME_PATTERN.search(line)
            if m:
                if duration is None:
                    continue
                current_time = duration_str_to_secs(m.group(1))
                yield current_time / duration

    yield 1.0
