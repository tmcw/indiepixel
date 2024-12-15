from __future__ import annotations
from indiepixel import Rect, Text, Box, Root


def test_rect():
    r = Rect(width = 10, height = 10, background = '#f00')
    assert r.measure((0, 0, 100, 100)) == (10, 10)

def test_text():
    t = Text(text = 'Hello world')
    assert t.measure((0, 0, 100, 100)) == (51, 8)

def test_box():
    t = Text(text = 'Hello world')
    b = Box(t)
    # TODO: this is probably wrong, this should
    # be the same as the text that is contained!
    assert b.measure((0, 0, 100, 100)) == (52, 9)

def test_root():
    r = Root(child = Rect(width = 10, height = 10, background = '#000'))
    assert r.measure((0, 0, 64, 32)) == (64, 32)
