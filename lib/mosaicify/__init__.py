# Copyright 2017, Ryan P. Kelly. All Rights Reserved.

import fnmatch
import math
import os
import random

import numpy
import numpy.linalg
from PIL import Image


__version__ = "1.0"


def average_color(img):
    """Return the average color of the given image.

    :param img: An image object.
    :returns: A three-tuple representing the average color.

    """

    h = img.histogram()

    # split into red, green, blue
    r = h[0:256]
    g = h[256:512]
    b = h[512:768]

    def wavg(s):
        """Find the weighted average of the sequence, which is a color channel.

        :param s: A color channel sequence.
        :returns: The weighted average.

        """

        # i is the index which is the channel value. w is the weight which is
        # the frequency of occurence.
        weighted = sum(i*w for i, w in enumerate(s))

        # sum of all values, which is how many times they occur
        total = sum(s)

        return int(weighted / float(total))

    return (wavg(r), wavg(g), wavg(b))


def crop_image(img):

    if img.width > img.height:
        new_width = img.height
        new_height = img.height

        start_x = (img.width - img.height) / 2
        start_y = 0

        img = img.crop((
            start_x,
            start_y,
            start_x + new_width,
            start_y + new_height,
        ))
    elif img.height > img.width:
        new_width = img.width
        new_height = img.width

        start_x = 0
        start_y = (img.height - img.width) / 2

        img = img.crop((
            start_x,
            start_y,
            start_x + new_width,
            start_y + new_height,
        ))

    return img


def load_sources(path, tile_size, filter, is_color=False, crop=crop_image):

    source_images = []

    for root, _, files in os.walk(path):
        for file in files:

            if filter is not None and not fnmatch.fnmatch(file, filter):
                continue

            image_path = os.path.join(root, file)

            loaded = load_source(
                image_path,
                tile_size,
                is_color=is_color,
                crop=crop,
            )

            source_images.append(loaded)

    return source_images


def load_source(path, tile_size, is_color=True, crop=crop_image):

    source_image = Image.open(path)

    source_image = crop(source_image)

    source_image.thumbnail((tile_size, tile_size))

    if not is_color:
        source_image = source_image.convert("L")

    # always need to force into RGB only
    source_image = source_image.convert("RGB")

    (
        average_r,
        average_g,
        average_b,
    ) = average_color(source_image)

    return (source_image, (average_r, average_g, average_b))


def ordered_pixels(reference_image):

    pixels = []
    for x in range(reference_image.width):
        for y in range(reference_image.height):
            pixels.append((x, y))

    return pixels


def random_pixels(reference_image):

    pixels = ordered_pixels(reference_image)

    random.shuffle(pixels)

    return pixels


def perceived_luminance(r, g, b):
    """Calculate the perceived luminance of a color.

    See http://alienryderflex.com/hsp.html for more information.

    :param r: Red value.
    :param g: Green value.
    :param b: Blue value.
    :returns: Perceived luminance.

    """

    return math.sqrt(0.299 * r**2 + 0.587 * g**2 + 0.114 * b**2)


def _pixels_with_brightness(reference_image):

    pixels = ordered_pixels(reference_image)

    with_brightness = []

    for x, y in pixels:
        r, g, b = reference_image.getpixel((x, y))

        brightness = perceived_luminance(r, g, b)

        with_brightness.append((brightness, (x, y)))

    return with_brightness


def midtone_pixels(reference_image):

    with_brightness = _pixels_with_brightness(reference_image)

    total_brightness = sum([b for b, _ in with_brightness])
    average_brightness = total_brightness / len(with_brightness)

    def midtone_sort(v):
        b, _ = v
        return abs(average_brightness - b)

    with_brightness.sort(key=midtone_sort)

    return [(x, y) for _, (x, y) in with_brightness]


def darkest_pixels(reference_image):

    with_brightness = _pixels_with_brightness(reference_image)

    with_brightness.sort()

    return [(x, y) for _, (x, y) in with_brightness]


def brightest_pixels(reference_image):

    pixels = darkest_pixels(reference_image)
    pixels.reverse()

    return pixels


def create_mosaic(reference_image, source_images, pixels, tile_size):

    pool = source_images[:]

    output_matrix = []
    for _ in range(reference_image.height):
        output_matrix.append([None for _ in range(reference_image.width)])

    for x, y in pixels:

        if not pool:
            pool = source_images[:]

        pixel = reference_image.getpixel((x, y))
        r = pixel[0]
        g = pixel[1]
        b = pixel[2]
        reference_vec = numpy.array([[r, g, b]])

        normed_images = []
        for image, avg_color in pool:
            source_vec = numpy.array([avg_color])

            norm = numpy.linalg.norm(reference_vec - source_vec)
            normed_images.append((norm, image, avg_color))

        normed_images.sort()
        top20 = normed_images[:20]
        random.shuffle(top20)

        _, selected_image, avg_color = top20[0]

        pool.remove((selected_image, avg_color))

        output_matrix[y][x] = selected_image

    output_width = tile_size * reference_image.width
    output_height = tile_size * reference_image.height
    output_image = Image.new("RGB", (output_width, output_height))

    y_offset = 0
    for row in output_matrix:

        x_offset = 0

        for image in row:

            paste_box = (
                x_offset,
                y_offset,
                x_offset + tile_size,
                y_offset + tile_size,
            )

            output_image.paste(image, paste_box)

            x_offset += tile_size

        y_offset += tile_size

    return output_image
