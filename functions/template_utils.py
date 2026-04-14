import logging
import re
import unicodedata
from datetime import datetime, timezone
from typing import Callable, Union

_logger = logging.getLogger(__name__)

# Support Firestore Timestamp or datetime as "now"
def _normalize_dt(now: Union[datetime, None]) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if isinstance(now, datetime):
        return now
    if hasattr(now, "timestamp"):
        return datetime.fromtimestamp(now.timestamp(), tz=timezone.utc)
    return datetime.now(timezone.utc)


def _year4(dt: datetime) -> str:
    return f"{dt.year:04d}"


def _day2(dt: datetime) -> str:
    return f"{dt.day:02d}"


# weekday(): Monday=0 … Sunday=6
_KOREAN_WEEKDAY_SHORT = ("월", "화", "수", "목", "금", "토", "일")
_KOREAN_WEEKDAY_LONG = (
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일",
)


def _korean_weekday_short(dt: datetime) -> str:
    return _KOREAN_WEEKDAY_SHORT[dt.weekday()]


def _korean_weekday_long(dt: datetime) -> str:
    return _KOREAN_WEEKDAY_LONG[dt.weekday()]


_TOKEN_RENDERERS: list[tuple[str, Callable[[datetime], str]]] = [
    # YYYY / DD: Java/SimpleDateFormat-style; must be before lowercase yyyy/dd
    ("YYYY", _year4),
    ("yyyy", _year4),
    ("MM", lambda dt: f"{dt.month:02d}"),
    ("DD", _day2),
    ("dd", _day2),
    ("HH", lambda dt: f"{dt.hour:02d}"),
    ("mm", lambda dt: f"{dt.minute:02d}"),
    ("ss", lambda dt: f"{dt.second:02d}"),
    # EE must be before E
    ("EE", _korean_weekday_long),
    ("E", _korean_weekday_short),
    ("M", lambda dt: f"{dt.month}"),
    ("d", lambda dt: f"{dt.day}"),
    ("H", lambda dt: f"{dt.hour}"),
    ("m", lambda dt: f"{dt.minute}"),
]


_DASH_CHARS = (
    "\u2010",
    "\u2011",
    "\u2012",
    "\u2013",
    "\u2014",
    "\u2212",
    "\uff0d",
)


def _normalize_placeholder_pattern(pat: str) -> str:
    """NFKC, ASCII hyphen, collapse spaces — copy/paste from Word/PDF often breaks tokens."""
    p = unicodedata.normalize("NFKC", pat or "")
    for ch in _DASH_CHARS:
        p = p.replace(ch, "-")
    p = " ".join(p.split())
    return p.strip()


def format_dt_pattern(now: datetime, pattern: str) -> str:
    """
    Format datetime using a lightweight token format:
    - yyyy, MM, dd, HH, mm
    - M, d, H, m (no zero-padding)
    - E (한글 요일 짧게: 월, 화, …), EE (한글 요일 길게: 월요일, 화요일, …)
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
    # Fullwidth braces (common from IME / copy-paste) do not match \{...\}
    content = content.replace("\uff5b", "{").replace("\uff5d", "}")
    if not content or "{" not in content:
        return content

    dt = _normalize_dt(now)

    def _repl(match: re.Match) -> str:
        raw = match.group(0)
        pat = (match.group(1) or "").strip()
        # Strip zero-width / format chars that break token matching or equality checks
        for ch in ("\u200b", "\u200c", "\u200d", "\ufeff"):
            pat = pat.replace(ch, "")
        pat = pat.strip()
        if not pat:
            return raw
        pat = _normalize_placeholder_pattern(pat)
        if not pat:
            return raw
        try:
            return format_dt_pattern(dt, pat)
        except Exception as e:
            # Likely date intent if pattern has format letters; else e.g. {foo} — only warn former
            if any(c in pat for c in "yYmMdHhsE"):
                _logger.warning("template placeholder kept as-is: %r (%s)", raw, e)
            return raw

    return _BRACE_PATTERN.sub(_repl, content)


