#!/usr/bin/env python
from gimpfu import *
from array import array

def region_test (image, layer):

	target_layer = gimp.Layer(image, 'target_layer', layer.width, layer.height, layer.type, layer.opacity, layer.mode)
	image.add_layer(target_layer, 0)

	source_width = layer.width
	source_height = layer.height
	source_region = layer.get_pixel_rgn(0, 0, source_width, source_height, False, False)
	bytes_pp = source_region.bpp
	target_region = target_layer.get_pixel_rgn(0, 0, source_width, source_height, True, True)
	pdb.gimp_message("bytes_pp = " + str(bytes_pp))
	source_pixels = array("B", source_region[0:source_width, 0:source_height])
	target_pixels = array("B", "\x00" * (source_width * source_height * bytes_pp))

	for x in range(0, source_width):
		for y in range(0, source_height):
			src_pos = (x + source_width * y) * bytes_pp
			pixel = source_pixels[src_pos: src_pos + bytes_pp]

#			temp1 = pixel[0]
#			temp2 = pixel[1]
#			temp3 = pixel[2]
#			pixel[0] = temp1 * 0.3 + temp2 * 0.59 + temp3 * 0.11
#			pixel[1] = temp1 * 0.3 + temp2 * 0.59 + temp3 * 0.11
#			pixel[2] = temp1 * 0.3 + temp2 * 0.59 + temp3 * 0.11
#			pixel[3] sets transparency if image has alpha channel

			temp = pixel[0]
			pixel[0] = pixel[2]
			pixel[2] = temp

			pdb.gimp_message("( " + str(x) + ", " + str(y) + "): Value of R: " 
			+ str(pixel[0]) + ", value of G: " + str(pixel[1]) + ", value of B: " 
			+ str(pixel[2]) + "\nstr_pos = " + str(src_pos) + "\n")
			
			dest_pos = (x + source_width * y) * bytes_pp

			target_pixels[dest_pos : dest_pos + bytes_pp] = array('B', pixel)

	target_region[0:source_width, 0:source_height] = target_pixels.tostring()

	target_layer.flush()
	target_layer.merge_shadow(True)
	target_layer.update(0, 0, source_width, source_height)

register(
	"python_fu_region_test",
	"Description 1",
	"Description 2",
	"",
	"",
	"",
	"<Image>/On test/Region test",
	"RGB*",
	[],
	[],
	region_test,
			)
main()
