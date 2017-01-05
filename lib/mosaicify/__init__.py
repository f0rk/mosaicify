# Copyright 2017, Ryan P. Kelly. All Rights Reserved.

from __future__ import absolute_import

import fnmatch
import os
import random

import numpy
import numpy.linalg
from PIL import Image

from mosaicify.colors import average_color


__version__ = "1.0"


def crop_image(img):
    """Crop the given image square.

    :param img: An image object.
    :returns: An sqaure image.

    """

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


def load_sources(path, tile_size, filter, is_color=False, crop=crop_image,
                 color_method=average_color):
    """Load the all the source images.

    :param path: The path to the directory containing the source images.
    :param tile_size: How large each image will appear in the output.
    :param filter: A shell-like glob expression to filter files in the given
        `path` directory. Use `None` to disable filtering.
    :param is_color: Whether or not to produce a color output (default: False).
    :param crop: The function that crops the source images square (default:
        `crop_image`).
    :param color_method: The function that determines the representative color
        for a source image (default: `average_color`).
    :returns: A list of appropriately prepared source images.

    """

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
                color_method=color_method,
            )

            source_images.append(loaded)

    return source_images


def load_source(path, tile_size, is_color=True, crop=crop_image,
                color_method=average_color):
    """Load a single source image.

    :param path: The path to the image.
    :param tile_size: How large each image will appear in the output.
    :param is_color: Whether or not to produce a color output (default: False).
    :param crop: The function that crops the source images square (default:
        `crop_image`).
    :param color_method: The function that determines the representative color
        for a source image (default: `average_color`).
    :returns: A list of appropriately prepared source images.

    """

    source_image = Image.open(path)

    source_image = crop(source_image)

    source_image.thumbnail((tile_size, tile_size))

    if not is_color:
        source_image = source_image.convert("L")

    # always need to force into RGB only
    source_image = source_image.convert("RGB")

    (
        representative_r,
        representative_g,
        representative_b,
    ) = color_method(source_image)

    return (source_image, (representative_r, representative_g, representative_b))


def create_mosaic(reference_image, source_images, pixels, tile_size):
    """Generate the output mosaic image.

    :param reference_image: The image that is the source of pixels for the
        output.
    :param source_images: The list of images as returned by `load_sources` for
        use as "pixels" of the output image.
    :param pixels: The list of pixel coordinates representing the order in
        which pixels will be processed when assembling the output mosaic.
    :param tile_size: How large each source image will be rendered in the final
        output.
    :returns: An image object.

    """

    pool = source_images[:]

    output_matrix = []
    for _ in range(reference_image.height):
        output_matrix.append([None for _ in range(reference_image.width)])

    for x, y in pixels:

        # pool may become depleted if the number of pixels in the reference
        # image exceeds the number of source images
        if not pool:
            pool = source_images[:]

        pixel = reference_image.getpixel((x, y))
        r = pixel[0]
        g = pixel[1]
        b = pixel[2]
        reference_vec = numpy.array([[r, g, b]])

        normed_images = []
        for image, rep_color in pool:
            source_vec = numpy.array([rep_color])

            # norm gives us the "distance" or "length" of the vector that is
            # the difference between the actual pixel color in the image and
            # the representative color of the source or tile image
            norm = numpy.linalg.norm(reference_vec - source_vec)
            normed_images.append((norm, image, rep_color))

        # sort to find the closest matching values
        normed_images.sort()

        # but only chose randomly among the top 20, to avoid too aggressively
        # matching some source images
        top20 = normed_images[:20]
        random.shuffle(top20)

        _, selected_image, rep_color = top20[0]

        # remove the image from the pool, to minimize repetition
        pool.remove((selected_image, rep_color))

        output_matrix[y][x] = selected_image

    # generate the output image, starting with a blank canvas
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
