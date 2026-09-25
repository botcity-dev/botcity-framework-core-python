import numpy
from PIL import Image

from botcity.core import DesktopBot, cv2find


def _bot_with_screen(tmp_path, monkeypatch, needle, screen):
    needle_path = tmp_path / "needle.png"
    Image.fromarray(needle).save(needle_path)

    bot = DesktopBot()
    bot.add_image("needle", str(needle_path))
    monkeypatch.setattr(bot, "_fix_display_size", lambda: (200, 100))
    monkeypatch.setattr(bot, "get_screenshot", lambda *a, **k: Image.fromarray(screen))
    monkeypatch.setattr("botcity.core.bot.is_retina", lambda: False)
    return bot


def test_find_all_drops_overlapping_matches_above_or_left_of_the_best(
    tmp_path, monkeypatch
):
    rng = numpy.random.default_rng(0)
    screen = rng.integers(0, 256, (100, 200, 3), dtype=numpy.uint8)
    # A smooth element also scores well one or more pixels away from where
    # it really is, in every direction.
    needle = numpy.zeros((20, 20, 3), numpy.uint8)
    needle[:] = numpy.linspace(0, 255, 20, dtype=numpy.uint8)[None, :, None]
    screen[40:60, 50:70] = needle

    bot = _bot_with_screen(tmp_path, monkeypatch, needle, screen)

    found = list(bot.find_all("needle", matching=0.8, waiting_time=1000))

    assert found == [cv2find.Box(50, 40, 20, 20)]


def test_find_all_keeps_elements_that_touch_but_do_not_overlap(
    tmp_path, monkeypatch
):
    rng = numpy.random.default_rng(1)
    screen = rng.integers(0, 256, (100, 200, 3), dtype=numpy.uint8)
    needle = rng.integers(0, 256, (10, 10, 3), dtype=numpy.uint8)
    screen[20:30, 40:50] = needle
    screen[20:30, 50:60] = needle

    bot = _bot_with_screen(tmp_path, monkeypatch, needle, screen)

    found = sorted(bot.find_all("needle", matching=0.9, waiting_time=1000))

    assert found == [cv2find.Box(40, 20, 10, 10), cv2find.Box(50, 20, 10, 10)]
