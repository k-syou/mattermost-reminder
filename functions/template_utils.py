import re
from datetime import datetime, timezone
from typing import Callable, Union

# Support Firestore Timestamp or datetime as "now"
def _normalize_dt(now: Union[datetime, None]) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if isinstance(now, datetime):
        return now
    if hasattr(now, "timestamp"):
        return datetime.fromtimestamp(now.timestamp(), tz=timezone.utc)
    return datetime.now(timezone.utc)


_TOKEN_RENDERERS: list[tuple[str, Callable[[datetime], str]]] = [
    ("yyyy", lambda dt: f"{dt.year:04d}"),
    ("MM", lambda dt: f"{dt.month:02d}"),
    ("dd", lambda dt: f"{dt.day:02d}"),
    ("HH", lambda dt: f"{dt.hour:02d}"),
    ("mm", lambda dt: f"{dt.minute:02d}"),
    ("M", lambda dt: f"{dt.month}"),
    ("d", lambda dt: f"{dt.day}"),
    ("H", lambda dt: f"{dt.hour}"),
    ("m", lambda dt: f"{dt.minute}"),
]


def format_dt_pattern(now: datetime, pattern: str) -> str:
    """
    Format datetime using a lightweight token format:
    - yyyy, MM, dd, HH, mm
    - M, d, H, m (no zero-padding)
    Example: "yyyy-MM-dd HH:mm" -> "2026-03-09 16:05", "M/d" -> "3/9".
    """
    p = (pattern or "").strip()
    if not p:
        raise ValueError("empty pattern")

    # Fallback for common pattern so it always works
    if p == "yyyy-MM-dd HH:mm" or p.replace(" ", "") == "yyyy-MM-ddHH:mm":
        return f"{now.year:04d}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}"

    out: list[str] = []
    i = 0
    used_token = False
    while i < len(p):
        matched = False
        for token, fn in _TOKEN_RENDERERS:
            if p.startswith(token, i):
                out.append(fn(now))
                i += len(token)
                matched = True
                used_token = True
                break
        if not matched:
            out.append(p[i])
            i += 1
    if not used_token:
        raise ValueError("no supported tokens")
    return "".join(out)


_BRACE_PATTERN = re.compile(r"\{([^{}]+)\}")


def render_message_template(content: str, now: Union[datetime, None]) -> str:
    """
    Replace {pattern} placeholders in message content with formatted datetime.
    Unrecognized/invalid patterns are left as-is.
    """
    if content is None:
        content = ""
    content = str(content)
    if not content or "{" not in content:
        return content

    dt = _normalize_dt(now)

    def _repl(match: re.Match) -> str:
        raw = match.group(0)
        pat = (match.group(1) or "").strip()
        if not pat:
            return raw
        try:
            return format_dt_pattern(dt, pat)
        except Exception:
            return raw

    return _BRACE_PATTERN.sub(_repl, content)

