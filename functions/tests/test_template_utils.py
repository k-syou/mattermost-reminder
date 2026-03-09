from datetime import datetime

import pytest

from template_utils import format_dt_pattern, render_message_template


def test_format_dt_pattern_basic():
    now = datetime(2026, 3, 9, 16, 5, 0)
    assert format_dt_pattern(now, "yyyy-MM-dd HH:mm") == "2026-03-09 16:05"
    assert format_dt_pattern(now, "M/d") == "3/9"
    assert format_dt_pattern(now, "MM/dd") == "03/09"


def test_render_message_template_multiple_placeholders():
    now = datetime(2026, 3, 9, 16, 5, 0)
    content = "A {yyyy-MM-dd} B {HH:mm} C {M/d} D {MM/dd}"
    rendered = render_message_template(content, now)
    assert rendered == "A 2026-03-09 B 16:05 C 3/9 D 03/09"


def test_render_message_template_invalid_kept():
    now = datetime(2026, 3, 9, 16, 5, 0)
    content = "X {unknown-token} Y"
    assert render_message_template(content, now) == content


def test_format_dt_pattern_empty_raises():
    now = datetime(2026, 3, 9, 16, 5, 0)
    with pytest.raises(ValueError):
        format_dt_pattern(now, "")

