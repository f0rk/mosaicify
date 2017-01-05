# Copyright 2017, Ryan P. Kelly. All Rights Reserved.

"""
Pixel-related functions.
"""

from __future__ import absolute_import

import random

from mosaicify.colors import perceived_luminance



def ordered_pixels(reference_image):
    """Returns an ordered list of (x, y) tuples representing pixel coordinates
    in the image.

    The pixels are order by column. The first column, where all pixels are y =
    0, appears first, followed by y = 1, and so on.

    :param reference_image: The image that is the source of pixels for the
        output.
    :returns: A list of pixel coordinate tuples.

    """

    pixels = []
    for x in range(reference_image.width):
        for y in range(reference_image.height):
            pixels.append((x, y))

    return pixels


def random_pixels(reference_image):
    """Returns a randomized list of (x, y) tuples representing pixel
    coordinates in the image.

    :param reference_image: The image that is the source of pixels for the
        output.
    :returns: A list of pixel coordinate tuples.

    """

    pixels = ordered_pixels(reference_image)

    random.shuffle(pixels)

    return pixels


def _pixels_with_brightness(reference_image):
    """Returns a list of (brightness, (x, y coordinate)) tuples.

    :param reference_image: The image that is the source of pixels for the
        output.
    :returns: A list of brightness and pixel coordinate tuples.

    """

    pixels = ordered_pixels(reference_image)

    with_brightness = []

    for x, y in pixels:
        r, g, b = reference_image.getpixel((x, y))

        brightness = perceived_luminance(r, g, b)

        with_brightness.append((brightness, (x, y)))

    return with_brightness


def midtone_pixels(reference_image):
    """Returns a list of (x, y) tuples representing pixel coordinates in the
    image, ordered by how far they are from the average luminance.

    :param reference_image: The image that is the source of pixels for the
        output.
    :returns: A list of pixel coordinate tuples.

    """

    with_brightness = _pixels_with_brightness(reference_image)

    total_brightness = sum([b for b, _ in with_brightness])
    average_brightness = total_brightness / len(with_brightness)

    def midtone_sort(v):
        """Return the distance between the brightness value of the given tuple
        and the average brightness.

        :param v: A (brightness, pixel location) tuple.
        :returns: A positive number representing the difference between the
            brightness given by `v` and the average brightness.

        """

        b, _ = v
        return abs(average_brightness - b)

    with_brightness.sort(key=midtone_sort)

    return [(x, y) for _, (x, y) in with_brightness]


def darkest_pixels(reference_image):
    """Returns a list of (x, y) tuples representing pixel coordinates in the
    image, ordered by how far they are from 0 luminance.

    :param reference_image: The image that is the source of pixels for the
        output.
    :returns: A list of pixel coordinate tuples.

    """

    with_brightness = _pixels_with_brightness(reference_image)

    with_brightness.sort()

    return [(x, y) for _, (x, y) in with_brightness]


def brightest_pixels(reference_image):
    """Returns a list of (x, y) tuples representing pixel coordinates in the
    image, ordered by how far they are from the maximum luminance.

    :param reference_image: The image that is the source of pixels for the
        output.
    :returns: A list of pixel coordinate tuples.

    """

    pixels = darkest_pixels(reference_image)
    pixels.reverse()

    return pixels

