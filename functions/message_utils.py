"""Shared helpers for message send-time resolution."""
import re

TIME_RE = re.compile(r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")


def _hm_to_minutes(hm: str) -> int:
    """Convert HH:MM to minutes since midnight."""
    if not hm or not TIME_RE.match(hm):
        return -1
    h, m = map(int, hm.split(":"))
    return h * 60 + m


def get_send_times_from_range(time_range_start: str, time_range_end: str, interval_minutes: int) -> list[str]:
    """
    Generate list of HH:MM times in [start, end) at interval_minutes.
    interval_minutes must be in 1..60; start must be < end (within same day).
    """
    start_min = _hm_to_minutes(time_range_start)
    end_min = _hm_to_minutes(time_range_end)
    if start_min < 0 or end_min < 0 or interval_minutes < 1 or interval_minutes > 60:
        return []
    if start_min >= end_min:
        return []
    out = []
    t = start_min
    while t < end_min:
        h, m = divmod(t, 60)
        out.append(f"{h:02d}:{m:02d}")
        t += interval_minutes
    return out
