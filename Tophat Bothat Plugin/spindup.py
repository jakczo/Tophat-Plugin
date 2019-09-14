from gimpfu import *
import math


def python_spindup(img, layer, angle, steps, xCenter, yCenter):
    pdb.gimp_image_undo_group_start(img)
    for x in range(0, steps):
        newLayer = pdb.gimp_layer_copy(layer, pdb.gimp_drawable_has_alpha(layer))
        pdb.gimp_image_insert_layer(img, newLayer, None, -1)
        newLayer = pdb.gimp_item_transform_rotate(newLayer, angle * math.pi / 180 / steps * (x + 1),
                                                  False, xCenter, yCenter)
    pdb.gimp_image_undo_group_end(img)
    return


register(
    "python_fu_spindup",
    "Spin Duplicates",
    "Duplicates and rotates layer",
    "ABC XYZ",
    "ABC XYZ",
    "2019",
    "<Image>/Filters/Distorts/Spin Duplicates...",
    "*",
    [
        (PF_FLOAT, "angle", "Angle of rotation", 90),
        (PF_INT, "steps", "Number of steps", 10),
        (PF_FLOAT, "xCenter", "Horizontal center of rotation", 0),
        (PF_FLOAT, "yCenter", "Vertical center of rotation", 0)
    ],
    [],
    python_spindup)

main()
