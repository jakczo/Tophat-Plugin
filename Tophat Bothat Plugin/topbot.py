#!/usr/bin/env python

from gimpfu import *
from array import array

def python_topbot(image, layer):
    width = layer.width
    height = layer.height
    source_region = layer.get_pixel_rgn(0, 0, width, height, False, False)
    bytes_pp = source_region.bpp
    source_pixels = array('B', source_region[0:width, 0:height])
    pdb.gimp_message("bytes_pp = " + str(bytes_pp))

#   Black Top-Hat transform (using close morphological operator)
    black_tophat(image, layer, bytes_pp, source_pixels)

    return


#   calculating greyscale_pixels
def convert_to_greyscale(img, lay, bytes_per_pixel, input_pixel_list):
    greyscale_layer = gimp.Layer(img, '1. Black Tophat - greyscale', lay.width, lay.height, lay.type, lay.opacity, lay.mode)
    img.add_layer(greyscale_layer, 0)
    width = greyscale_layer.width
    height = greyscale_layer.height
    greyscale_region = greyscale_layer.get_pixel_rgn(0, 0, width, height, True, True)
    greyscale_pixels_list = array('B', "\x00" * (width * height * bytes_per_pixel))

    for x in range(0, width):
        for y in range(0, height):
            src_pos = (x + width * y) * bytes_per_pixel
            pixel = input_pixel_list[src_pos: src_pos + bytes_per_pixel]
            pixel_copy = pixel[:]

            pixel[0] = int(pixel_copy[0] * 0.3 + pixel_copy[1] * 0.59 + pixel_copy[2] * 0.11)
            pixel[1] = int(pixel_copy[0] * 0.3 + pixel_copy[1] * 0.59 + pixel_copy[2] * 0.11)
            pixel[2] = int(pixel_copy[0] * 0.3 + pixel_copy[1] * 0.59 + pixel_copy[2] * 0.11)

            pdb.gimp_message("( " + str(x) + ", " + str(y) + "): (R, G, B) = ("
                             + str(pixel_copy[0]) + ", " + str(pixel_copy[1]) + ", " + str(
                pixel_copy[2]) + ")\nGrey = ("
                             + str(pixel[0]) + ", " + str(pixel[1]) + ", " + str(pixel[2])
                             + ")\nstr_pos = " + str(src_pos) + "\n")

            greyscale_pixels_list[src_pos: src_pos + bytes_per_pixel] = array('B', pixel)

    greyscale_region[0:width, 0:height] = greyscale_pixels_list.tostring()
    greyscale_layer.flush()
    greyscale_layer.merge_shadow(True)
    greyscale_layer.update(0, 0, width, height)

    return greyscale_pixels_list


# calculating dilatation_pixels with element: 1 |1| 1
def dilate(img, lay, bytes_per_pixel, input_pixel_list):
    dilatation_layer = gimp.Layer(img, '2. Black Tophat - dilatation', lay.width, lay.height, lay.type, lay.opacity, lay.mode)
    img.add_layer(dilatation_layer, 0)
    width = dilatation_layer.width
    height = dilatation_layer.height
    dilatation_region = dilatation_layer.get_pixel_rgn(0, 0, width, height, True, True)
    dilatation_pixels_list = array('B', "\x00" * (width * height * bytes_per_pixel))
    i = 0
    for y in range(0, height):
        for x in range(0, width):
            grey_pos = i * bytes_per_pixel

            # not checking the x-1 pixel
            if x == 0:
                pixel = input_pixel_list[grey_pos: grey_pos + bytes_per_pixel * 2]
                pixel_copy = pixel[:]
                pixel[0] = max(pixel_copy)
                pixel[1] = max(pixel_copy)
                pixel[2] = max(pixel_copy)
                dilatation_pixels_list[grey_pos: grey_pos + bytes_per_pixel] = array('B', pixel[0: 3])

            # not checking the x+1 pixel
            elif x == width - 1:
                pixel = input_pixel_list[grey_pos - bytes_per_pixel: grey_pos + bytes_per_pixel]
                pixel_copy = pixel[:]
                pixel[3] = max(pixel_copy)
                pixel[4] = max(pixel_copy)
                pixel[5] = max(pixel_copy)
                dilatation_pixels_list[grey_pos: grey_pos + bytes_per_pixel] = array('B', pixel[3: 6])

            # check the x-1, x and x+1 position
            else:
                pixel = input_pixel_list[grey_pos - bytes_per_pixel: grey_pos + bytes_per_pixel * 2]
                pixel_copy = pixel[:]
                pixel[3] = max(pixel_copy)
                pixel[4] = max(pixel_copy)
                pixel[5] = max(pixel_copy)
                dilatation_pixels_list[grey_pos: grey_pos + bytes_per_pixel] = array('B', pixel[3: 6])

            i = i + 1

    dilatation_region[0:width, 0:height] = dilatation_pixels_list.tostring()
    dilatation_layer.flush()
    dilatation_layer.merge_shadow(True)
    dilatation_layer.update(0, 0, width, height)

    return dilatation_pixels_list


# calculating erosion_pixels with element: 1 |1| 1
def erode(img, lay, bytes_per_pixel, input_pixel_list):
    erosion_layer = gimp.Layer(img, '3. Black Tophat - erosion', lay.width, lay.height, lay.type, lay.opacity, lay.mode)
    img.add_layer(erosion_layer, 0)
    width = erosion_layer.width
    height = erosion_layer.height
    erosion_region = erosion_layer.get_pixel_rgn(0, 0, width, height, True, True)
    erosion_pixels = array('B', "\x00" * (width * height * bytes_per_pixel))
    i = 0
    for y in range(0, height):
        for x in range(0, width):
            dilate_pos = i * bytes_per_pixel

            # not checking the x-1 pixel
            if x == 0:
                pixel = input_pixel_list[dilate_pos: dilate_pos + bytes_per_pixel * 2]
                pixel_copy = pixel[:]
                pixel[0] = min(pixel_copy)
                pixel[1] = min(pixel_copy)
                pixel[2] = min(pixel_copy)
                erosion_pixels[dilate_pos: dilate_pos + bytes_per_pixel] = array('B', pixel[0: 3])

            # not checking the x+1 pixel
            elif x == width - 1:
                pixel = input_pixel_list[dilate_pos - bytes_per_pixel: dilate_pos + bytes_per_pixel]
                pixel_copy = pixel[:]
                pixel[3] = min(pixel_copy)
                pixel[4] = min(pixel_copy)
                pixel[5] = min(pixel_copy)
                erosion_pixels[dilate_pos: dilate_pos + bytes_per_pixel] = array('B', pixel[3: 6])

            # check the x-1, x and x+1 position
            else:
                pixel = input_pixel_list[dilate_pos - bytes_per_pixel: dilate_pos + bytes_per_pixel * 2]
                pixel_copy = pixel[:]
                pixel[3] = min(pixel_copy)
                pixel[4] = min(pixel_copy)
                pixel[5] = min(pixel_copy)
                erosion_pixels[dilate_pos: dilate_pos + bytes_per_pixel] = array('B', pixel[3: 6])

            i = i + 1

    erosion_region[0:width, 0:height] = erosion_pixels.tostring()
    erosion_layer.flush()
    erosion_layer.merge_shadow(True)
    erosion_layer.update(0, 0, width, height)

    return erosion_pixels


#   Black Top-Hat transform
def black_tophat(img, lay, bytes_per_pixel, input_pixels):
    greyscale_pixels = convert_to_greyscale(img, lay, bytes_per_pixel, input_pixels)
    dilatation_pixels = dilate(img, lay, bytes_per_pixel, greyscale_pixels)
    erosion_pixels = erode(img, lay, bytes_per_pixel, dilatation_pixels)

    black_tophat_layer = gimp.Layer(img, '4. Black Tophat - result', lay.width, lay.height, lay.type, lay.opacity, lay.mode)
    img.add_layer(black_tophat_layer, 0)
    width = black_tophat_layer.width
    height = black_tophat_layer.height
    black_tophat_region = black_tophat_layer.get_pixel_rgn(0, 0, width, height, True, True)
    black_tophat_pixels_list = array('B', "\x00" * (width * height * bytes_per_pixel))

    for x in range(0, width):
        for y in range(0, height):
            tophat_pos = (x + width * y) * bytes_per_pixel
            pixel_greyscale = greyscale_pixels[tophat_pos: tophat_pos + bytes_per_pixel]
            pixel = pixel_greyscale[:]
            pixel_erode = erosion_pixels[tophat_pos: tophat_pos + bytes_per_pixel]

            for k in range(0, bytes_per_pixel):
                pixel[k] = abs(pixel_erode[k] - pixel_greyscale[k])

            black_tophat_pixels_list[tophat_pos: tophat_pos + bytes_per_pixel] = array('B', pixel)

    black_tophat_region[0:width, 0:height] = black_tophat_pixels_list.tostring()
    black_tophat_layer.flush()
    black_tophat_layer.merge_shadow(True)
    black_tophat_layer.update(0, 0, width, height)

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
