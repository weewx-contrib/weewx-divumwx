#!/usr/bin/env python3
"""Build divumwx/img/meteoalarm/meteoalarm_<symbol>_<level>.svg: a black symbol in a
triangle filled with the warning level's colour, with a black border.
meteoalarm_<symbol>.svg (no level) is written as the yellow version.

    python3 make_meteoalarm_icons.py            # from the repository root

Reads the original white symbols from meteoalarm_icon_sources/ (not installed)
and writes divumwx/img/meteoalarm/, so it can be re-run safely.
"""
import os
import re
here = os.path.dirname(os.path.abspath(__file__))
sources = os.path.join(here, "meteoalarm_icon_sources")
folder = os.path.join(here, "divumwx", "img", "meteoalarm")

# Same colours as LEVEL_COLORS in bin/user/divumwx_meteoalarm.py
LEVELS = {1: "#29d660", 2: "#FFDB23", 3: "#FF9500", 4: "#FF0100"}
# Rounded triangle, 64 x 58, black border. The symbol sits in the triangle's widest part.
TRIANGLE = ('<path d="M32 2.5 L62 55.5 H2 Z" fill="{color}" stroke="#000" '
            'stroke-width="3" stroke-linejoin="round"/>')
GLYPH_BOX = (18, 22.5, 28, 28)        # x, y, width, height of the 64x64 symbol
EXCLAIM = ('<g fill="#000"><rect x="29" y="22" width="6" height="18" rx="3"/>'
           '<circle cx="32" cy="46" r="3.4"/></g>')

TEMPLATE = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="58" viewBox="0 0 64 58">\n'
            '<title>{title}</title>\n{triangle}\n{glyph}\n</svg>\n')


def original(name):
    with open(os.path.join(sources, name), encoding="utf-8", errors="replace") as fh:
        return fh.read()


for name in sorted(os.listdir(sources)):
    if not re.fullmatch(r"meteoalarm_[0-9a-z]+\.svg", name):
        continue
    stem = name[len("meteoalarm_"):-4]
    src = original(name)
    title = (re.search(r"<title>(.*?)</title>", src) or [None, stem])[1]
    if stem == "000":       # "other / unknown": its own art is already a warning triangle
        glyph = EXCLAIM
        title = "warning"
    else:
        viewbox = re.search(r'viewBox="([^"]+)"', src).group(1)
        body = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)
        body = re.sub(r"<title>.*?</title>|<desc>.*?</desc>|<!--.*?-->|<g>\s*</g>", "", body, flags=re.S)
        # every symbol is drawn black
        body = re.sub(r'fill="#[0-9A-Fa-f]{3,6}"', 'fill="#000000"', body)
        x, y, w, h = GLYPH_BOX
        glyph = ('<svg x="%g" y="%g" width="%g" height="%g" viewBox="%s" fill="#000000">%s</svg>'
                 % (x, y, w, h, viewbox, "\n".join(l for l in body.strip().splitlines() if l.strip())))
    for level, color in [(None, LEVELS[2])] + sorted(LEVELS.items()):
        out = name if level is None else "meteoalarm_%s_%d.svg" % (stem, level)
        with open(os.path.join(folder, out), "w", encoding="utf-8") as fh:
            fh.write(TEMPLATE.format(title=title, triangle=TRIANGLE.format(color=color), glyph=glyph))
    print("wrote", name, "and levels 1-4")
