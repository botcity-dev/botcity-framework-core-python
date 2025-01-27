"""
This module was extracted from https://github.com/asweigart/pyscreeze and modified to fit with our search when
using the web bot and also for PEP8 compliance.

Copyright (c) 2014, Al Sweigart
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of PyScreeze nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import collections
import cv2
import numpy
from PIL.Image import Image
from typing import Union, Tuple, Optional, Generator, Any

RUNNING_CV_2 = cv2.__version__[0] < "3"

Box = collections.namedtuple("Box", "left top width height")

if RUNNING_CV_2:
    LOAD_COLOR = cv2.CV_LOAD_IMAGE_COLOR
    LOAD_GRAYSCALE = cv2.CV_LOAD_IMAGE_GRAYSCALE
else:
    LOAD_COLOR = cv2.IMREAD_COLOR
    LOAD_GRAYSCALE = cv2.IMREAD_GRAYSCALE


def _load_cv2(
    img: Union[Image, numpy.ndarray, str], grayscale: bool = False
) -> numpy.ndarray:
    """
    TODO
    """
    # load images if given filename, or convert as needed to opencv
    # Alpha layer just causes failures at this point, so flatten to RGB.
    # RGBA: load with -1 * cv2.CV_LOAD_IMAGE_COLOR to preserve alpha
    # to matchTemplate, need template and image to be the same wrt having alpha

    if isinstance(img, str):
        # The function imread loads an image from the specified file and
        # returns it. If the image cannot be read (because of missing
        # file, improper permissions, unsupported or invalid format),
        # the function returns an empty matrix
        # http://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html
        if grayscale:
            img_cv = cv2.imread(img, LOAD_GRAYSCALE)
        else:
            img_cv = cv2.imread(img, LOAD_COLOR)
        if img_cv is None:
            raise IOError(
                "Failed to read %s because file is missing, "
                "has improper permissions, or is an "
                "unsupported or invalid format" % img
            )
    elif isinstance(img, numpy.ndarray):
        # don't try to convert an already-gray image to gray
        if grayscale and len(img.shape) == 3:  # and img.shape[2] == 3:
            img_cv = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img_cv = img
    elif hasattr(img, "convert"):
        # assume its a PIL.Image, convert to cv format
        img_array = numpy.array(img.convert("RGB"))
        img_cv = img_array[:, :, ::-1].copy()  # -1 does RGB -> BGR
        if grayscale:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        raise TypeError("expected an image filename, OpenCV numpy array, or PIL image")
    return img_cv


def locate_all_opencv(
    needle_image: Union[Image, numpy.ndarray, str],
    haystack_image: Union[Image, numpy.ndarray, str],
    grayscale: bool = False,
    limit: int = 10000,
    region: Optional[Tuple[int, int, int, int]] = None,
    step: int = 1,
    confidence: float = 0.999,
) -> Generator[Box, Any, None]:
    """
    TODO - rewrite this
        faster but more memory-intensive than pure python
        step 2 skips every other row and column = ~3x faster but prone to miss;
            to compensate, the algorithm automatically reduces the confidence
            threshold by 5% (which helps but will not avoid all misses).
        limitations:
          - OpenCV 3.x & python 3.x not tested
          - RGBA images are treated as RBG (ignores alpha channel)
    """

    confidence = float(confidence)

    needle_image = _load_cv2(needle_image, grayscale)
    needle_height, needle_width = needle_image.shape[:2]
    haystack_image = _load_cv2(haystack_image, grayscale)

    if region:
        haystack_image = haystack_image[
            region[1]: region[1] + region[3], region[0]: region[0] + region[2]
        ]
    else:
        region = (0, 0, 0, 0)  # full image; these values used in the yield statement

    if (
        haystack_image.shape[0] < needle_image.shape[0]
        or haystack_image.shape[1] < needle_image.shape[1]
    ):
        # avoid semi-cryptic OpenCV error below if bad size
        raise ValueError(
            "needle dimension(s) exceed the haystack image or region dimensions"
        )

    if step == 2:
        confidence *= 0.95
        needle_image = needle_image[::step, ::step]
        haystack_image = haystack_image[::step, ::step]
    else:
        step = 1

    # get all matches at once, credit:
    # https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
    result = cv2.matchTemplate(haystack_image, needle_image, cv2.TM_CCOEFF_NORMED)
    match_indices = numpy.arange(result.size)[(result > confidence).flatten()]
    matches = numpy.unravel_index(match_indices[:limit], result.shape)

    if len(matches[0]) == 0:
        return

    # use a generator for API consistency:
    matchx = matches[1] * step + region[0]  # vectorized
    matchy = matches[0] * step + region[1]

    # Order results before sending back
    ordered = sorted(
        zip(matchx, matchy), key=lambda p: result[p[1]][p[0]], reverse=True
    )
    for x, y in ordered:
        yield Box(x, y, needle_width, needle_height)
