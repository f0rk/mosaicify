# Copyright 2017, Ryan P. Kelly. All Rights Reserved.

from __future__ import absolute_import

from PIL import Image


def output_from_matrix(reference_image, tile_size, output_matrix):
    """Generate the output mosaic image by laying out the output matrix into a
    single image canvas.

    :param reference_image: The image that is the source of pixels for the
        output.
    :param tile_size: How large each source image will be rendered in the final
        output.
    :param output_matrix: An list of python lists consisting of source images.
    :returns: An image object.

    """

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
