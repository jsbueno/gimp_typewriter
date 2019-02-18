#!/usr/bin/env python2

import colorsys
import random

from gimpfu import *

import gtk
import gtk.gdk

numbersrow = "0123456789"
toprow = "qwertyuiop"
middlerow = "asdfghjkl"
bottomrow = "zxcvbnm,."

keys = [numbersrow, toprow, middlerow, bottomrow]
def get_hsl(key):
    pos = None
    for i, row in enumerate(keys):
        if row.find(key) != -1:
            pos = row.find(key)
            break
    else:
        return 0, ord(key[0]) % 2, 0
    hue = pos * 1.0 / len(row)
    if i == 1:
        lit = 0.9
        sat = 1
    elif i == 3:
        lit = 0.6
        sat = 0.75
    elif i == 2:
        lit = 0.5
        sat = 1
    else:
        lit = 0.3
        sat = 1
    # Force bright yellow hue
    if 0.12 < hue < 0.33:
        hue = 0.17
    return hue, sat, lit

def hsl_to_rgb(H, S, L):
    r_, g_, b_ = colorsys.hls_to_rgb(H, L, S)
    r, g, b = (int(comp * 255) for comp in (r_, g_, b_))
    return r, g, b


def paint(color, drawing):
    pdb.gimp_ellipse_select(image, x, y, size, vsize, CHANNEL_OP_REPLACE, True, True, 20)
    pdb.gimp_context_set_foreground(color)
    if drawing:
        # pdb.gimp_edit_fill(drw, FILL_FOREGROUND)
        pdb.gimp_edit_bucket_fill(
            drw,
            BUCKET_FILL_FG,
            mode,
            100,
            255,
            False,
            0,
            0
        )
    pdb.gimp_displays_flush()


def keychain(window, event):
    global x, y, line_start, mode

    val = event.keyval
    name = gtk.gdk.keyval_name(val)

    print(name)

    if name == "Escape":
        pdb.gimp_selection_clear(image)
        gtk.mainquit()

    mode = LAYER_MODE_MULTIPLY

    if name in "Left Right Down Up Escape Return Shift_L Shift_R".split():
        drawing = False
        color = (0, 0, 0)
    else:
        drawing = True
    if name == "Left":
        x -= size // 2
        line_start = x
    if name == "Right":
        x += size // 2
        line_start = x
    if name == "Down":
        y += size
    if name == "Up":
        y -= size
    if name == "Return":
        x = line_start
        y += size

    if name.isupper():
        name = name.lower()
        mode = LAYER_MODE_ADDITION

    color = hsl_to_rgb(*get_hsl(name))

    if name == "space":
        mode = LAYER_MODE_ADDITION
        color = 255, 255, 255

    if name == "BackSpace":
        mode = LAYER_MODE_NORMAL
        x -= size
        color = pdb.gimp_context_get_background()

    cval = (val - 32) & 0x7

    paint(color, drawing)
    if drawing:
        x += size // 2
        if x > image.width:
            y += vsize
            x = 0


def typewriter(par_image, par_drw):
    global image, drw
    global x, y, line_start
    global size, vsize
    size, vsize=30, 60
    x = y = line_start = 0
    image = par_image
    drw = par_drw

    w = gtk.Window()
    w.show()
    w.connect("key-press-event", keychain)
    gtk.main()


register(
        "typewriter",
        "typewriter",
        """typewriter
        """,
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2019. GPL applies.",
        "Filters/typewriter",
        "*",
        [(PF_IMAGE, "Image", "Image", None), (PF_DRAWABLE, "Drawable", "Drawable", None), ],
        [],
        typewriter,
        menu="<Image>")

main()
