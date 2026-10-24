import os
from collections import Counter
from PIL import Image

OUT = r"C:\Users\Administrator\Documents\zqeslwyz-homepage-preview"
LIGHT = ((255,255,255), (246,247,249))     # --bg / --bg-alt
DARK  = ((15,18,22), (20,24,29))           # --bg / --bg-alt

def run(name, backgrounds):
    im = Image.open(os.path.join(OUT, name)).convert("RGB")
    w, h = im.size
    px = im.load()
    def is_bg(p):
        return any(abs(p[0]-b[0]) + abs(p[1]-b[1]) + abs(p[2]-b[2]) <= 20 for b in backgrounds)
    band, blanks = 100, []
    for top in range(0, h - band + 1, band):
        total = content = 0
        for y in range(top, top + band, 3):
            for x in range(0, w, 3):
                total += 1
                if not is_bg(px[x, y]):
                    content += 1
        ratio = content / max(total, 1)
        if ratio < 0.004:
            blanks.append((top, top + band))
    # merge adjacent
    merged = []
    for a, b in blanks:
        if merged and merged[-1][1] == a:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    print(f"{name}: {w}x{h}")
    print(f"   empty runs >=100px: {merged if merged else 'none'}")
    print(f"   longest empty run: {max((b-a for a,b in merged), default=0)}px")

run("preview-desktop-light.png", LIGHT)
run("preview-desktop-dark.png", DARK)
run("preview-mobile-light.png", LIGHT)
