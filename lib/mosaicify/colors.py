# Copyright 2017, Ryan P. Kelly. All Rights Reserved.

"""
Color-related functions.
"""

from __future__ import absolute_import

import math


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


def commonest_color(img):
    """Return the most common color of the given image.

    :param img: An image object.
    :returns: A three-tuple representing the commonest color.

    """

    counts = {}
    for color in img.getdata(): # flat list of color tuples
        if color not in counts:
            counts[color] = 0
        counts[color] += 1

    # go from the mapping of color -> count to tuples of count, color
    counted = [(count, color) for color, count in counts.items()]

    # sort will sort on the first item, which is count
    counted.sort()

    # take the last item, which has the highest count
    _, color = counted[-1]
    return color


def perceived_luminance(r, g, b):
    """Calculate the perceived luminance of a color.

    See http://alienryderflex.com/hsp.html for more information.

    :param r: Red value.
    :param g: Green value.
    :param b: Blue value.
    :returns: Perceived luminance.

    """

    return math.sqrt(0.299 * r**2 + 0.587 * g**2 + 0.114 * b**2)

