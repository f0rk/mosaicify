# Copyright 2017, Ryan P. Kelly. All Rights Reserved.

from __future__ import absolute_import

import random

import numpy
import numpy.linalg
from PIL import Image

from mosaicify.output import output_from_matrix


def _random_pixel(reference_image):
    """Return a random pixel coordinate from the reference image.

    :param reference_image: The image to return a random coordinate from.
    :returns: A 2-tuple of the ranodm x, y coordinate.

    """

    x = random.randint(0, reference_image.width - 1)
    y = random.randint(0, reference_image.height - 1)

    return (x, y)


def _norm_for_source(reference_image, source, location):
    """Return the norm for a source.

    :param reference_image: The image that is the source of the comparison
        pixel.
    :param source: A 2-tuple of source image and representative color.
    :param location: A 2-tuple representing a position in the reference image.
    :returns: The norm for the pixel given by location in the reference image
        and source.

    """

    pixel = reference_image.getpixel(location)
    r = pixel[0]
    g = pixel[1]
    b = pixel[2]
    reference_vec = numpy.array([[r, g, b]])

    _, rep_color = source

    source_vec = numpy.array([rep_color])
    norm = numpy.linalg.norm(reference_vec - source_vec)

    return norm


def _simplify_matrix(output_matrix):

    """Simplify the matrix format used by this module's ``create_mosaic``
    method into the matrix expected by the output image generation function.

    :param output_matrix: This module's matrix representation (each location is
        an image, color tuple).
    :returns: A new, simplified matrix.

    """

    new_matrix = []
    for row in output_matrix:

        new_row = []
        for image, _ in row:
            new_row.append(image)

        new_matrix.append(new_row)

    return new_matrix


def create_mosaic(reference_image, source_images, tile_size, generations=1000000):
    """Generate the output mosaic image by randomly distributing tile images and
    then randomly swapping them if the swap improves the image.

    :param reference_image: The image that is the source of pixels for the
        output.
    :param source_images: The list of images as returned by `load_sources` for
        use as "pixels" of the output image.
    :param tile_size: How large each source image will be rendered in the final
        output.
    :param generations: How many pixel-swapping attempts to perform (default:
        100,000).
    :returns: An image object.

    """

    pool = source_images[:]

    output_matrix = []
    for _ in range(reference_image.height):

        row = []
        for _ in range(reference_image.width):

            if not pool:
                pool = source_images[:]

            source = random.choice(pool)

            pool.remove(source)

            row.append(source)

        output_matrix.append(row)

    for _ in xrange(generations):

        # select two random pixels
        loc_1 = _random_pixel(reference_image)

        while True:
            loc_2 = _random_pixel(reference_image)
            if loc_1 != loc_2:
                break

        # the output matrix is accessed by selecting a row (y) and then a
        # position in that row (x)
        source_1 = output_matrix[loc_1[1]][loc_1[0]]
        source_2 = output_matrix[loc_2[1]][loc_2[0]]

        current_norm_1 = _norm_for_source(
            reference_image,
            source_1,
            loc_1,
        )
        current_norm_2 = _norm_for_source(
            reference_image,
            source_2,
            loc_2,
        )

        swapped_norm_1 = _norm_for_source(
            reference_image,
            source_2,
            loc_1,
        )
        swapped_norm_2 = _norm_for_source(
            reference_image,
            source_1,
            loc_2,
        )

        # swapping is an improvement, perform the swap
        if swapped_norm_1 + swapped_norm_2 < current_norm_1 + current_norm_2:

            output_matrix[loc_1[1]][loc_1[0]] = source_2
            output_matrix[loc_2[1]][loc_2[0]] = source_1

    # simplify our output matrix a little so we can generate the output
    new_matrix = _simplify_matrix(output_matrix)

    # create and return output
    return output_from_matrix(reference_image, tile_size, new_matrix)
