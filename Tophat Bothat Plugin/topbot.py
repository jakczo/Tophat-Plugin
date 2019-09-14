from gimpfu import *
import math


def python_topbot(img, layer):
    #pdb.gim_image_undo_group_start(img)
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
    "Uses morphological operations such as top-hat and bot-hat to manipulate picture converted to monochromatic type "
    "- grey scale",
    "Jakub Czachor",
    "Jakub Czachor",
    "2019",
    "<Image>/Filters/Generic/Top-hat, bot-hat..."
    "*",
    [
        #(PF_FLOAT, "angle", "Angle of rotation", 90),
        #(PF_INT, "steps", "Number of steps", 10),
        #(PF_FLOAT, "xCenter", "Horizontal center of rotation", 0),
        #(PF_FLOAT, "yCenter", "Vertical center of rotation", 0)
    ],
    [],
    python_topbot)

main()
