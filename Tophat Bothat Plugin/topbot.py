#!/usr/bin/env python

from gimpfu import *
from array import array
import math
# import numpy as np


def python_topbot(img, layer):
    #pdb.gim_image_undo_group_start(img)
    target_layer = gimp.Layer(img, 'target-layer', layer.width, layer.height, layer.type, layer.opacity, layer.mode)
    img.add_layer(target_layer, 0)
    pdb.gimp_image_resize(img, img.width * 2, img.height * 2, 0, 0)
    pdb.gimp_layer_resize_to_image_size(layer)
    pdb.gimp_layer_resize_to_image_size(target_layer)

    source_width = layer.width
    source_height = layer.height
    source_region = layer.get_pixel_rgn(0, 0, source_width, source_height, False, False)
    bytes_pp = source_region.bpp
    target_region = target_layer.get_pixel_rgn(0, 0, source_width, source_height, True, True)
    source_pixels = array("B", source_region[0:source_width, 0:source_height])
    target_pixels = array("B", "\x00" * (source_width * source_height * bytes_pp))

    for x in range(0, source_width / 2):
        for y in range(0, source_height / 2):
            src_pos = (source_width * y + x) * bytes_pp
            pixel = source_pixels[src_pos: src_pos + bytes_pp]


            # temp = pixel[0]
            # pixel[0] = pixel[2]
            # pixel[2] = temp
            #			pixel[3] sets transparency if image has alpha channel

            dest_pos_1 = (source_width * y * 2 + x) * bytes_pp + x * bytes_pp
            dest_pos_2 = (source_width * y * 2 + x) * bytes_pp + x * bytes_pp + bytes_pp
            dest_pos_3 = (source_width * y * 2 + x) * bytes_pp + x * bytes_pp + source_width * bytes_pp
            dest_pos_4 = (source_width * y * 2 + x) * bytes_pp + x * bytes_pp + source_width * bytes_pp + bytes_pp

            target_pixels[dest_pos_1: dest_pos_1 + bytes_pp] = array('B', pixel)
            target_pixels[dest_pos_2: dest_pos_2 + bytes_pp] = array('B', pixel)
            target_pixels[dest_pos_3: dest_pos_3 + bytes_pp] = array('B', pixel)
            target_pixels[dest_pos_4: dest_pos_4 + bytes_pp] = array('B', pixel)

    target_region[0:source_width, 0:source_height] = target_pixels.tostring()

    target_layer.flush()
    target_layer.merge_shadow(True)
    target_layer.update(0, 0, source_width, source_height)

    return


# def channelData(layer):
#     w = layer.width
#     h = layer.height
#     #w, h = layer.width, layer.height
#     region = layer.get_pixel_rgn(0, 0, w, h)
#     pixChars = region[:, :]
#     bpp = region.bpp
#     return np.frombuffer(pixChars, dtype = np.uint8).reshape(w,h,bpp)


# register(
# name of the plugin,
# brief description,
# longer description,
# plugin author,
# copyright owner,
# year,
# menu entry,
# color space * - apply to all types of images,
# [ input arguments ],
# [return values (may be empty)],
# name of oru function)


register(
    "python_fu_topbot",
    "Top-hat and bot-hat operations",
    "Uses morphological operations such as top-hat and bot-hat to manipulate picture converted to monochromatic type "
    "- grey scale",
    "Jakub Czachor",
    "Jakub Czachor",
    "2019",
    "<Image>/Filters/Generic/Top-hat, bot-hat..."
    "RGB*",
    [],
    [],
    python_topbot)

main()
