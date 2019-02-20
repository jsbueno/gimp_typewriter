#!/usr/bin/env python2
# coding: utf-8

import colorsys
import math
import random

from gimpfu import *

import gtk
import gtk.gdk

numbersrow = "0123456789"
toprow = "qwertyuiop"
middlerow = "asdfghjkl"
bottomrow = "zxcvbnm,."

keys = [numbersrow, toprow, middlerow, bottomrow]

manual_chars = {
    'dead_acute': '´',
    'dead_grave': '`',
    'dead_tilde': '~',
    'dead_circumflex':'^',
    'ccedilla': 'ç',

}

def build_control(label, container, type_=gtk.HScrollbar, controls=()):
    hbox = gtk.HBox()
    label = gtk.Label(u"%s: " % label)
    hbox.pack_start(label)
    if issubclass(type_, gtk.Range):
        start, end, step, digits = controls
        ad = gtk.Adjustment(start, start, end, step, step * 3, 0)
        widget = type_(ad)
        widget.set_can_focus(True)
        result = ad
    else:
        result = widget = type_(*controls)

    hbox.pack_start(widget)
    container.pack_start(hbox)
    return result


def get_layer_pos(img, drw):
    return img.layers.index(drw)


class TypeWriter(object):
    def __init__(self, image, drw):

        self.x = self.y = self.line_start = 0
        self.image = image
        self.drw = drw

        self.window = w = gtk.Window()
        vbox = gtk.VBox()
        self.window.add(vbox)

        self.fontenize_ad = build_control(u"Fontenize", vbox, controls=(0, 1, 0.1, 1))

        self.dance_ad = build_control(u"Dance", vbox,controls=(0, 1, 0.1, 1) )
        self.twist_ad = build_control(u"Twist", vbox, controls=(0, 1, 0.1, 1))
        self.size_ad = build_control(u"Size", vbox, controls=(3, 170, 1, 0))
        self.size_ad.set_value(30)
        self.hue_ad = build_control(u"Hue", vbox, controls=(0, 1, 0.1, 1))
        self.lightness_ad = build_control(u"Light", vbox, controls=(0, 1, 0.1, 1))


        self.area = build_control(u"Type here", vbox, type_ = gtk.Button, controls=("Press and Type",))
        w.show_all()
        self.area.connect("key-press-event", self.keychain)

        gtk.main()

    fontenize = property(lambda self: self.fontenize_ad.get_value())
    dance = property(lambda self: self.dance_ad.get_value())
    twist = property(lambda self: self.twist_ad.get_value())
    vsize = size = property(lambda self: self.size_ad.get_value())
    hue = property(lambda self: self.hue_ad.get_value())
    lightness = property(lambda self: self.lightness_ad.get_value())

    def get_hsl(self, key):
        pos = None
        for i, row in enumerate(keys):
            if row.find(key) != -1:
                pos = row.find(key)
                break
        else:
            i = ord(key[0]) % 3
            row = keys[0]
            pos = ord(key[0]) % 8
        hue = pos * 1.0 / len(row)
        if i == 1:
            lit = 0.75
            sat = 1
        elif i == 3:
            lit = 0.6
            sat = 0.75
        elif i == 2:
            lit = 0.5
            sat = 1
        else:
            lit = 0.5
            sat = 1
        hue = (hue + self.hue) % 1
        lit = (lit + self.lightness) % 1
        # Force bright yellow hue
        if 0.12 < hue < 0.24:
            hue = 0.17
        return hue, sat, lit

    def hsl_to_rgb(self, H, S, L):
        r_, g_, b_ = colorsys.hls_to_rgb(H, L, S)
        r, g, b = (int(comp * 255) for comp in (r_, g_, b_))
        return r, g, b

    def paint(self):
        pdb.gimp_ellipse_select(
            self.image,
            self.x, self.y,
            self.size, self.vsize,
            CHANNEL_OP_REPLACE, True, True, 20
        )
        pdb.gimp_context_set_foreground(self.color)
        if self.drawing:
            border = 6
            pdb.gimp_edit_bucket_fill(
                self.drw,
                BUCKET_FILL_FG,
                self.mode,
                100 * (1 - self.fontenize), 255, False, 0, 0
            )
            if self.fontenize and len(self.key_name) <= 2:
                pdb.gimp_selection_clear(self.image)
                font_name = pdb.gimp_context_get_font()
                y =  self.y + (self.vsize - self.size) // 2 - border + self.y_compensation
                x = self.x
                if self.dance:
                    get_range = lambda size: random.randrange(int(-size * self.dance), int(size * self.dance))
                    x +=  get_range(self.size)
                    y +=  get_range(self.vsize)
                text_layer = pdb.gimp_text_fontname(
                    self.image, None,
                    x, y,
                    self.key_name,
                    border, True, self.size, 0, font_name
                )
                blur_amount = 2 + 4 * (1 - self.fontenize)
                pdb.plug_in_gauss(self.image, text_layer, blur_amount, blur_amount, 1)
                pdb.gimp_layer_set_opacity(text_layer, 100 * self.fontenize)

                text_layer.mode = self.mode

                if self.twist:
                    pdb.gimp_item_transform_rotate(
                        text_layer,
                        math.radians(random.randrange(int(-180 * self.twist), int(180 * self.twist))),
                        True, 0, 0
                    )


                # Position text layer just above active layer:
                while True:
                    drw_pos = get_layer_pos(self.image, self.drw)
                    text_pos = get_layer_pos(self.image, text_layer)

                    if (text_pos - drw_pos) == -1:
                        break
                    if text_pos > drw_pos:
                        pdb.gimp_image_raise_item(self.image, text_layer)
                    else:
                        pdb.gimp_image_lower_item(self.image, text_layer)

                self.drw = pdb.gimp_image_merge_down(self.image, text_layer, CLIP_TO_BOTTOM_LAYER)

        pdb.gimp_displays_flush()


    def keychain(self, window, event):

        val = event.keyval
        self.key_name = key_name = gtk.gdk.keyval_name(val)

        self.x_compensation = 0
        self.y_compensation = 0
        if val < 128 and len(key_name) > 1:
            self.key_name = key_name = chr(val)
        if key_name.startswith("dead_") or key_name=="ccedilla":
            if key_name.startswith("dead_"):
                self.x_compensation = -self.size // 2
                if 'tilde' in key_name:
                    self.y_compensation = -self.size // 2
            self.key_name = key_name = manual_chars[key_name]



        print(key_name, val)

        if key_name == "Escape":
            pdb.gimp_selection_clear(self.image)
            gtk.mainquit()

        self.mode = LAYER_MODE_MULTIPLY

        if key_name in "Left Right Down Up Escape Return Shift_L Shift_R".split():
            self.drawing = False
            self.color = (0, 0, 0)
        else:
            self.drawing = True
        if key_name == "Left":
            self.x -= self.size // 4
            self.line_start = self.x
        if key_name == "Right":
            self.x += self.size // 4
            self.line_start = self.x
        if key_name == "Down":
            self.y += self.vsize // 2
        if key_name == "Up":
            self.y -= self.vsize // 2
        if key_name == "Return":
            self.x = self.line_start
            self.y += self.size
        if key_name == "Tab":
            # Switch focus
            return False

        if key_name.isupper():
            key_name = key_name.lower()
            self.mode = LAYER_MODE_ADDITION

        self.color = self.hsl_to_rgb(*self.get_hsl(key_name))

        if key_name == "space":
            self.mode = LAYER_MODE_ADDITION
            self.color = 255, 255, 255

        if key_name == "BackSpace":
            self.mode = LAYER_MODE_NORMAL
            self.x -= self.size
            self.color = pdb.gimp_context_get_background()

        self.paint()
        if self.drawing:
            self.x += self.size // 2 + self.x_compensation
            if self.x > self.image.width:
                self.y += self.vsize
                self.x = 0
        return True

register(
        "typewriter",
        "typewriter",
        """typewriter
        """,
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2019. GPL applies.",
        "Color Typewriter",
        "*",
        [(PF_IMAGE, "Image", "Image", None), (PF_DRAWABLE, "Drawable", "Drawable", None), ],
        [],
        TypeWriter,
        menu="<Image>/Filters")

main()
