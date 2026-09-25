import numpy

from botcity.core import cv2find


def _images():
    rng = numpy.random.default_rng(0)
    needle = rng.integers(0, 256, (10, 10, 3), dtype=numpy.uint8)
    haystack = rng.integers(0, 256, (100, 200, 3), dtype=numpy.uint8)
    return needle, haystack


def test_locate_all_opencv_with_region_offset_returns_match():
    needle, haystack = _images()
    haystack[60:70, 150:160] = needle

    # Search only the right half of the screen, as find(x=100, ...) does.
    found = list(
        cv2find.locate_all_opencv(
            needle, haystack, region=(100, 0, 100, 100), confidence=0.9
        )
    )

    assert found == [cv2find.Box(150, 60, 10, 10)]


def test_locate_all_opencv_with_region_offset_orders_by_score():
    needle, haystack = _images()
    # A slightly damaged copy scores lower than the exact copy.
    damaged = needle.copy()
    damaged[0:3, 0:3] = 255 - damaged[0:3, 0:3]
    haystack[10:20, 110:120] = damaged
    haystack[60:70, 150:160] = needle

    found = list(
        cv2find.locate_all_opencv(
            needle, haystack, region=(100, 0, 100, 100), confidence=0.5
        )
    )

    assert found[0] == cv2find.Box(150, 60, 10, 10)
    assert cv2find.Box(110, 10, 10, 10) in found


def test_find_with_x_offset_returns_element(tmp_path, monkeypatch):
    from PIL import Image

    from botcity.core import DesktopBot

    needle, haystack = _images()
    haystack[60:70, 150:160] = needle
    needle_path = tmp_path / "needle.png"
    Image.fromarray(needle[:, :, ::-1]).save(needle_path)

    bot = DesktopBot()
    bot.add_image("needle", str(needle_path))
    monkeypatch.setattr(bot, "_fix_display_size", lambda: (200, 100))
    monkeypatch.setattr(
        bot, "get_screenshot", lambda *a, **k: Image.fromarray(haystack[:, :, ::-1])
    )
    monkeypatch.setattr("botcity.core.bot.is_retina", lambda: False)

    ele = bot.find("needle", x=100, matching=0.9, waiting_time=1000)

    assert ele == cv2find.Box(150, 60, 10, 10)
