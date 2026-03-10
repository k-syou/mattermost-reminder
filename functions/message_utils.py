"""Shared helpers for message send-time resolution."""
import re

TIME_RE = re.compile(r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")


def _hm_to_seconds(hm: str) -> int:
    """Convert HH:MM to seconds since midnight."""
    if not hm or not TIME_RE.match(hm):
        return -1
    h, m = map(int, hm.split(":"))
    return (h * 60 + m) * 60


def get_send_times_from_range(
    time_range_start: str, time_range_end: str, interval_seconds: int
) -> list[str]:
    """
    Generate list of times in [start, end) at interval_seconds.
    Returns "HH:MM:SS" when interval has seconds, else "HH:MM".
    interval_seconds 1..86400; start must be < end (same day).
    """
    start_sec = _hm_to_seconds(time_range_start)
    end_sec = _hm_to_seconds(time_range_end)
    if start_sec < 0 or end_sec < 0 or interval_seconds < 1 or interval_seconds > 86400:
        return []
    if start_sec >= end_sec:
        return []
    use_seconds = interval_seconds % 60 != 0
    out = []
    t = start_sec
    while t < end_sec:
        h, r = divmod(t, 3600)
        m, s = divmod(r, 60)
        if use_seconds:
            out.append(f"{h:02d}:{m:02d}:{s:02d}")
        else:
            out.append(f"{h:02d}:{m:02d}")
        t += interval_seconds
    return out
