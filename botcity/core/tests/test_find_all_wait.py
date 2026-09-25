import numpy
from PIL import Image

from botcity.core import DesktopBot, cv2find


def test_find_all_keeps_looking_until_the_element_appears(tmp_path, monkeypatch):
    rng = numpy.random.default_rng(0)
    needle = rng.integers(0, 256, (10, 10, 3), dtype=numpy.uint8)
    empty_screen = rng.integers(0, 256, (100, 200, 3), dtype=numpy.uint8)
    loaded_screen = empty_screen.copy()
    loaded_screen[20:30, 40:50] = needle
    # The element shows up on the third screenshot, well within waiting_time.
    screens = [empty_screen, empty_screen, loaded_screen]

    needle_path = tmp_path / "needle.png"
    Image.fromarray(needle).save(needle_path)
    bot = DesktopBot()
    bot.add_image("needle", str(needle_path))
    monkeypatch.setattr(bot, "_fix_display_size", lambda: (200, 100))
    monkeypatch.setattr(
        bot,
        "get_screenshot",
        lambda *a, **k: Image.fromarray(
            screens.pop(0) if len(screens) > 1 else screens[0]
        ),
    )
    monkeypatch.setattr("botcity.core.bot.is_retina", lambda: False)

    found = list(bot.find_all("needle", matching=0.9, waiting_time=5000))

    assert found == [cv2find.Box(40, 20, 10, 10)]
