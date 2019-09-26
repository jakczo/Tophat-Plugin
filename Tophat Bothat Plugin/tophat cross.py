#!/usr/bin/env python

from gimpfu import *
from array import array

def python_topbot_cross(image, layer):
    width = layer.width
    height = layer.height
    source_region = layer.get_pixel_rgn(0, 0, width, height, False, False)
    bytes_pp = source_region.bpp
    source_pixels = array('B', source_region[0:width, 0:height])
    pdb.gimp_message("bytes_pp = " + str(bytes_pp))

#   Black Top-Hat transform (using close morphological operator)
    black_tophat(image, layer, bytes_pp, source_pixels)
    white_tophat(image, layer, bytes_pp, source_pixels)
    return


#   calculating greyscale_pixels
def convert_to_greyscale(img, lay, bytes_per_pixel, input_pixel_list):
    greyscale_layer = gimp.Layer(img, 'Greyscale', lay.width, lay.height, lay.type, lay.opacity, lay.mode)
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

            greyscale_pixels_list[src_pos: src_pos + bytes_per_pixel] = array('B', pixel)

    greyscale_region[0:width, 0:height] = greyscale_pixels_list.tostring()
    greyscale_layer.flush()
    greyscale_layer.merge_shadow(True)
    greyscale_layer.update(0, 0, width, height)

    return greyscale_pixels_list


# calculating dilatation_pixels with element: 1 |1| 1
def dilate(img, lay, bytes_per_pixel, input_pixel_list):
    dilatation_layer = gimp.Layer(img, 'Dilatation', lay.width, lay.height, lay.type, lay.opacity, lay.mode)
    img.add_layer(dilatation_layer, 0)
    width = dilatation_layer.width
    height = dilatation_layer.height
    dilatation_region = dilatation_layer.get_pixel_rgn(0, 0, width, height, True, True)
    dilatation_pixels_list = array('B', "\x00" * (width * height * bytes_per_pixel))
    for y in range(0, height):
        for x in range(0, width):
            position_by_x = (x + y * width) * bytes_per_pixel

            if x == 0:

                # check the (x,y), (x+1, y) and (x, y+1) pixels
                if y == 0:
                    chosen_pixels = input_pixel_list[position_by_x: position_by_x + bytes_per_pixel * 2]
                    position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = max(chosen_pixels)
                    chosen_pixels_copy[1] = max(chosen_pixels)
                    chosen_pixels_copy[2] = max(chosen_pixels)
                    dilatation_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

                # check the (x,y), (x+1, y) and (x, y-1) pixels
                elif y == height - 1:
                    chosen_pixels = input_pixel_list[position_by_x: position_by_x + bytes_per_pixel * 2]
                    position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = max(chosen_pixels)
                    chosen_pixels_copy[1] = max(chosen_pixels)
                    chosen_pixels_copy[2] = max(chosen_pixels)
                    dilatation_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

                # checking the (x,y), (x+1, y), (x, y-1) and (x, y+1) pixels
                else:
                    chosen_pixels = input_pixel_list[position_by_x: position_by_x + bytes_per_pixel * 2]
                    position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = max(chosen_pixels)
                    chosen_pixels_copy[1] = max(chosen_pixels)
                    chosen_pixels_copy[2] = max(chosen_pixels)
                    dilatation_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

            # check the (x,y), (x-1, y) and (x, y+1) pixels
            elif x == width - 1:
                if y == 0:
                    chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel]
                    position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = max(chosen_pixels)
                    chosen_pixels_copy[1] = max(chosen_pixels)
                    chosen_pixels_copy[2] = max(chosen_pixels)
                    dilatation_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

                # check the (x,y), (x-1, y) and (x, y-1) pixels
                elif y == height - 1:
                    chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel]
                    position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = max(chosen_pixels)
                    chosen_pixels_copy[1] = max(chosen_pixels)
                    chosen_pixels_copy[2] = max(chosen_pixels)
                    dilatation_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

                # check the (x,y), (x-1, y), (x, y-1) and (x, y+1) pixels
                else:
                    chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel]
                    position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = max(chosen_pixels)
                    chosen_pixels_copy[1] = max(chosen_pixels)
                    chosen_pixels_copy[2] = max(chosen_pixels)
                    dilatation_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

            # check the (x-1,y), (x, y), (x+1, y) and (x, y+1) pixels
            elif y == 0:
                chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel * 2]
                position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                chosen_pixels_copy = chosen_pixels[:]
                chosen_pixels_copy[0] = max(chosen_pixels)
                chosen_pixels_copy[1] = max(chosen_pixels)
                chosen_pixels_copy[2] = max(chosen_pixels)
                dilatation_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

            # check the (x-1,y), (x, y), (x+1, y) and (x, y-1) pixels
            elif y == height - 1:
                chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel * 2]
                position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                chosen_pixels_copy = chosen_pixels[:]
                chosen_pixels_copy[0] = max(chosen_pixels)
                chosen_pixels_copy[1] = max(chosen_pixels)
                chosen_pixels_copy[2] = max(chosen_pixels)
                dilatation_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

            # check the (x-1,y), (x, y), (x+1, y), (x, y-1) and (x, y+1) pixels
            else:
                chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel * 2]
                position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                chosen_pixels_copy = chosen_pixels[:]
                chosen_pixels_copy[0] = max(chosen_pixels)
                chosen_pixels_copy[1] = max(chosen_pixels)
                chosen_pixels_copy[2] = max(chosen_pixels)
                dilatation_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

    dilatation_region[0:width, 0:height] = dilatation_pixels_list.tostring()
    dilatation_layer.flush()
    dilatation_layer.merge_shadow(True)
    dilatation_layer.update(0, 0, width, height)

    return dilatation_pixels_list


# calculating erosion_pixels with element: 1 |1| 1
def erode(img, lay, bytes_per_pixel, input_pixel_list):
    erosion_layer = gimp.Layer(img, 'Erosion', lay.width, lay.height, lay.type, lay.opacity, lay.mode)
    img.add_layer(erosion_layer, 0)
    width = erosion_layer.width
    height = erosion_layer.height
    erosion_region = erosion_layer.get_pixel_rgn(0, 0, width, height, True, True)
    erosion_pixels_list = array('B', "\x00" * (width * height * bytes_per_pixel))
    for y in range(0, height):
        for x in range(0, width):
            position_by_x = (x + y * width) * bytes_per_pixel

            if x == 0:

                # check the (x,y), (x+1, y) and (x, y+1) pixels
                if y == 0:
                    chosen_pixels = input_pixel_list[position_by_x: position_by_x + bytes_per_pixel * 2]
                    position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = min(chosen_pixels)
                    chosen_pixels_copy[1] = min(chosen_pixels)
                    chosen_pixels_copy[2] = min(chosen_pixels)
                    erosion_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

                # check the (x,y), (x+1, y) and (x, y-1) pixels
                elif y == height - 1:
                    chosen_pixels = input_pixel_list[position_by_x: position_by_x + bytes_per_pixel * 2]
                    position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = min(chosen_pixels)
                    chosen_pixels_copy[1] = min(chosen_pixels)
                    chosen_pixels_copy[2] = min(chosen_pixels)
                    erosion_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

                # checking the (x,y), (x+1, y), (x, y-1) and (x, y+1) pixels
                else:
                    chosen_pixels = input_pixel_list[position_by_x: position_by_x + bytes_per_pixel * 2]
                    position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = min(chosen_pixels)
                    chosen_pixels_copy[1] = min(chosen_pixels)
                    chosen_pixels_copy[2] = min(chosen_pixels)
                    erosion_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

            # check the (x,y), (x-1, y) and (x, y+1) pixels
            elif x == width - 1:
                if y == 0:
                    chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel]
                    position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = min(chosen_pixels)
                    chosen_pixels_copy[1] = min(chosen_pixels)
                    chosen_pixels_copy[2] = min(chosen_pixels)
                    erosion_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

                # check the (x,y), (x-1, y) and (x, y-1) pixels
                elif y == height - 1:
                    chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel]
                    position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = min(chosen_pixels)
                    chosen_pixels_copy[1] = min(chosen_pixels)
                    chosen_pixels_copy[2] = min(chosen_pixels)
                    erosion_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

                # check the (x,y), (x-1, y), (x, y-1) and (x, y+1) pixels
                else:
                    chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel]
                    position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                    chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                    chosen_pixels_copy = chosen_pixels[:]
                    chosen_pixels_copy[0] = min(chosen_pixels)
                    chosen_pixels_copy[1] = min(chosen_pixels)
                    chosen_pixels_copy[2] = min(chosen_pixels)
                    erosion_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

            # check the (x-1,y), (x, y), (x+1, y) and (x, y+1) pixels
            elif y == 0:
                chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel * 2]
                position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                chosen_pixels_copy = chosen_pixels[:]
                chosen_pixels_copy[0] = min(chosen_pixels)
                chosen_pixels_copy[1] = min(chosen_pixels)
                chosen_pixels_copy[2] = min(chosen_pixels)
                erosion_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

            # check the (x-1,y), (x, y), (x+1, y) and (x, y-1) pixels
            elif y == height - 1:
                chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel * 2]
                position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                chosen_pixels_copy = chosen_pixels[:]
                chosen_pixels_copy[0] = min(chosen_pixels)
                chosen_pixels_copy[1] = min(chosen_pixels)
                chosen_pixels_copy[2] = min(chosen_pixels)
                erosion_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

            # check the (x-1,y), (x, y), (x+1, y), (x, y-1) and (x, y+1) pixels
            else:
                chosen_pixels = input_pixel_list[position_by_x - bytes_per_pixel: position_by_x + bytes_per_pixel * 2]
                position_by_y = (x + (y - 1) * width) * bytes_per_pixel
                chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                position_by_y = (x + (y + 1) * width) * bytes_per_pixel
                chosen_pixels.extend(input_pixel_list[position_by_y: position_by_y + bytes_per_pixel])
                chosen_pixels_copy = chosen_pixels[:]
                chosen_pixels_copy[0] = min(chosen_pixels)
                chosen_pixels_copy[1] = min(chosen_pixels)
                chosen_pixels_copy[2] = min(chosen_pixels)
                erosion_pixels_list[position_by_x: position_by_x + bytes_per_pixel] = array('B', chosen_pixels_copy[0: 3])

    erosion_region[0:width, 0:height] = erosion_pixels_list.tostring()
    erosion_layer.flush()
    erosion_layer.merge_shadow(True)
    erosion_layer.update(0, 0, width, height)

    return erosion_pixels_list


#   Black Top-Hat transform
def black_tophat(img, lay, bytes_per_pixel, input_pixels):
    greyscale_pixels = convert_to_greyscale(img, lay, bytes_per_pixel, input_pixels)
    dilatation_pixels = dilate(img, lay, bytes_per_pixel, greyscale_pixels)
    erosion_pixels = erode(img, lay, bytes_per_pixel, dilatation_pixels)

    black_tophat_layer = gimp.Layer(img, 'Black Tophat', lay.width, lay.height, lay.type, lay.opacity, lay.mode)
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


#   White Top-Hat transform
def white_tophat(img, lay, bytes_per_pixel, input_pixels):
    greyscale_pixels = convert_to_greyscale(img, lay, bytes_per_pixel, input_pixels)
    erosion_pixels = erode(img, lay, bytes_per_pixel, greyscale_pixels)
    dilatation_pixels = dilate(img, lay, bytes_per_pixel, erosion_pixels)

    white_tophat_layer = gimp.Layer(img, 'White Tophat', lay.width, lay.height, lay.type, lay.opacity, lay.mode)
    img.add_layer(white_tophat_layer, 0)
    width = white_tophat_layer.width
    height = white_tophat_layer.height
    white_tophat_region = white_tophat_layer.get_pixel_rgn(0, 0, width, height, True, True)
    white_tophat_pixels_list = array('B', "\x00" * (width * height * bytes_per_pixel))

    for x in range(0, width):
        for y in range(0, height):
            tophat_pos = (x + width * y) * bytes_per_pixel
            pixel_greyscale = greyscale_pixels[tophat_pos: tophat_pos + bytes_per_pixel]
            pixel = pixel_greyscale[:]
            pixel_dilate = dilatation_pixels[tophat_pos: tophat_pos + bytes_per_pixel]

            for k in range(0, bytes_per_pixel):
                pixel[k] = abs(pixel_greyscale[k] - pixel_dilate[k])

            white_tophat_pixels_list[tophat_pos: tophat_pos + bytes_per_pixel] = array('B', pixel)

    white_tophat_region[0:width, 0:height] = white_tophat_pixels_list.tostring()
    white_tophat_layer.flush()
    white_tophat_layer.merge_shadow(True)
    white_tophat_layer.update(0, 0, width, height)

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
    python_topbot_cross)

main()
