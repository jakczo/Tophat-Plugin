#!/usr/bin/env python

from gimpfu import *
from array import array

def python_topbot(image, layer):
    greyscale_layer = gimp.Layer(image, '1Greyscale', layer.width, layer.height, layer.type, layer.opacity, layer.mode)
    dilatation_layer = gimp.Layer(image, '2Dilatation', layer.width, layer.height, layer.type, layer.opacity, layer.mode)
    erosion_layer = gimp.Layer(image, '3Erosion', layer.width, layer.height, layer.type, layer.opacity, layer.mode)
    tophat_layer = gimp.Layer(image, '4Tophat', layer.width, layer.height, layer.type, layer.opacity, layer.mode)
    image.add_layer(greyscale_layer, 0)
    image.add_layer(dilatation_layer, 0)
    image.add_layer(erosion_layer, 0)
    image.add_layer(tophat_layer, 0)

    source_width = layer.width
    source_height = layer.height
    source_region = layer.get_pixel_rgn(0, 0, source_width, source_height, False, False)
    bytes_pp = source_region.bpp
    source_pixels = array('B', source_region[0:source_width, 0:source_height])
    pdb.gimp_message("bytes_pp = " + str(bytes_pp))

    greyscale_region = greyscale_layer.get_pixel_rgn(0, 0, source_width, source_height, True, True)
    dilatation_region = dilatation_layer.get_pixel_rgn(0, 0, source_width, source_height, True, True)
    erosion_region = erosion_layer.get_pixel_rgn(0, 0, source_width, source_height, True, True)
    tophat_region = tophat_layer.get_pixel_rgn(0, 0, source_width, source_height, True, True)

    greyscale_pixels = array('B', "\x00" * (source_width * source_height * bytes_pp))
    dilatation_pixels = array('B', "\x00" * (source_width * source_height * bytes_pp))
    erosion_pixels = array('B', "\x00" * (source_width * source_height * bytes_pp))
    tophat_pixels = array('B', "\x00" * (source_width * source_height * bytes_pp))

#   calculating greyscale_pixels
    for x in range(0, source_width):
        for y in range(0, source_height):
            src_pos = (x + source_width * y) * bytes_pp
            pixel = source_pixels[src_pos: src_pos + bytes_pp]
            pixel_copy = pixel[:]

            pixel[0] = int(pixel_copy[0] * 0.3 + pixel_copy[1] * 0.59 + pixel_copy[2] * 0.11)
            pixel[1] = int(pixel_copy[0] * 0.3 + pixel_copy[1] * 0.59 + pixel_copy[2] * 0.11)
            pixel[2] = int(pixel_copy[0] * 0.3 + pixel_copy[1] * 0.59 + pixel_copy[2] * 0.11)

            pdb.gimp_message("( " + str(x) + ", " + str(y) + "): (R, G, B) = ("
                             + str(pixel_copy[0]) + ", " + str(pixel_copy[1]) + ", " + str(pixel_copy[2]) + ")\nGrey = ("
                             + str(pixel[0]) + ", " + str(pixel[1]) + ", " + str(pixel[2])
                             + ")\nstr_pos = " + str(src_pos) + "\n")

            greyscale_pixels[src_pos: src_pos + bytes_pp] = array('B', pixel)

# calculating dilatation_pixels with element: 1 |1| 1
    i = 0
    for y in range(0, source_height):
        for x in range(0, source_width):
            grey_pos = i * bytes_pp

            # not checking the x-1 pixel
            if x == 0:
                pixel = greyscale_pixels[grey_pos: grey_pos + bytes_pp * 2]
                pixel_copy = pixel[:]
                pixel[0] = max(pixel_copy)
                pixel[1] = max(pixel_copy)
                pixel[2] = max(pixel_copy)
                dilatation_pixels[grey_pos: grey_pos + bytes_pp] = array('B', pixel[0: 3])

            # not checking the x+1 pixel
            elif x == source_width - 1:
                pixel = greyscale_pixels[grey_pos - bytes_pp: grey_pos + bytes_pp]
                pixel_copy = pixel[:]
                pixel[3] = max(pixel_copy)
                pixel[4] = max(pixel_copy)
                pixel[5] = max(pixel_copy)
                dilatation_pixels[grey_pos: grey_pos + bytes_pp] = array('B', pixel[3: 6])

            # check the x-1, x and x+1 position
            else:
                pixel = greyscale_pixels[grey_pos - bytes_pp: grey_pos + bytes_pp * 2]
                pixel_copy = pixel[:]
                pixel[3] = max(pixel_copy)
                pixel[4] = max(pixel_copy)
                pixel[5] = max(pixel_copy)
                dilatation_pixels[grey_pos: grey_pos + bytes_pp] = array('B', pixel[3: 6])

            i = i + 1

# calculating erosion_pixels with element: 1 |1| 1
    i = 0
    for y in range(0, source_height):
        for x in range(0, source_width):
            dilate_pos = i * bytes_pp

            # not checking the x-1 pixel
            if x == 0:
                pixel = dilatation_pixels[dilate_pos: dilate_pos + bytes_pp * 2]
                pixel_copy = pixel[:]
                pixel[0] = min(pixel_copy)
                pixel[1] = min(pixel_copy)
                pixel[2] = min(pixel_copy)
                erosion_pixels[dilate_pos: dilate_pos + bytes_pp] = array('B', pixel[0: 3])

            # not checking the x+1 pixel
            elif x == source_width - 1:
                pixel = dilatation_pixels[dilate_pos - bytes_pp: dilate_pos + bytes_pp]
                pixel_copy = pixel[:]
                pixel[3] = min(pixel_copy)
                pixel[4] = min(pixel_copy)
                pixel[5] = min(pixel_copy)
                erosion_pixels[dilate_pos: dilate_pos + bytes_pp] = array('B', pixel[3: 6])

            # check the x-1, x and x+1 position
            else:
                pixel = dilatation_pixels[dilate_pos - bytes_pp: dilate_pos + bytes_pp * 2]
                pixel_copy = pixel[:]
                pixel[3] = min(pixel_copy)
                pixel[4] = min(pixel_copy)
                pixel[5] = min(pixel_copy)
                erosion_pixels[dilate_pos: dilate_pos + bytes_pp] = array('B', pixel[3: 6])

            i = i + 1


    greyscale_region[0:source_width, 0:source_height] = greyscale_pixels.tostring()
    greyscale_layer.flush()
    greyscale_layer.merge_shadow(True)
    greyscale_layer.update(0, 0, source_width, source_height)

    dilatation_region[0:source_width, 0:source_height] = dilatation_pixels.tostring()
    dilatation_layer.flush()
    dilatation_layer.merge_shadow(True)
    dilatation_layer.update(0, 0, source_width, source_height)

    erosion_region[0:source_width, 0:source_height] = erosion_pixels.tostring()
    erosion_layer.flush()
    erosion_layer.merge_shadow(True)
    erosion_layer.update(0, 0, source_width, source_height)

    return

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
    "Uses morphological operations to manipulate picture converted to grey scale",
    "Jakub Czachor",
    "Jakub Czachor",
    "2019",
    "<Image>/Test/top bot...",
    "RGB*",
    [],
    [],
    python_topbot)

main()
