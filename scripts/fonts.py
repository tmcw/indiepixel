"""Bdf font parsing."""
#
# ruff: noqa: D103
#
# The Python Imaging Library
# $Id$
#
# PIL raster font compiler
#
# history:
# 1997-08-25 fl   created
# 2002-03-10 fl   use "from PIL import"
#

import glob
import sys

# drivers
from PIL import BdfFontFile, PcfFontFile

VERSION = "0.4"

if len(sys.argv) <= 1:
    sys.exit(1)

files = []
for f in sys.argv[1:]:
    files = files + glob.glob(f)

for f in files:
    try:
        with open(f, "rb") as fp:
            try:
                p = PcfFontFile.PcfFontFile(fp)
            except SyntaxError:
                fp.seek(0)
                p = BdfFontFile.BdfFontFile(fp)

            p.save(f)

    except (OSError, SyntaxError):
        pass

    else:
        pass
