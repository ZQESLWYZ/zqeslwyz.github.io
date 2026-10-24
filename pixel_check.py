import os, sys
from collections import Counter
from PIL import Image

OUT = r"C:\Users\Administrator\Documents\zqeslwyz-homepage-preview"
for name in ("preview-desktop-light.png", "preview-desktop-dark.png", "preview-mobile-light.png"):
    path = os.path.join(OUT, name)
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    # background = most common colour in the top-left 20x300 strip
    bg = Counter(px[x, y] for x in range(0, 20) for y in range(0, 300)).most_common(1)[0][0]
    # content extent per 100px band
    blank_bands = []
    band = 100
    for top in range(0, h, band):
        bottom = min(top + band, h)
        content = 0
        total = 0
        for y in range(top, bottom, 4):
            for x in range(0, w, 4):
                total += 1
                p = px[x, y]
                if abs(p[0]-bg[0]) + abs(p[1]-bg[1]) + abs(p[2]-bg[2]) > 24:
                    content += 1
        ratio = content / max(total, 1)
        if ratio < 0.006:
            blank_bands.append((top, bottom, round(ratio, 4)))
        if y if False else False:
            pass
    # horizontal extents of any content
    lefts, rights = [], []
    for y in range(0, h, 7):
        row = [x for x in range(0, w, 2) if abs(px[x, y][0]-bg[0]) + abs(px[x, y][1]-bg[1]) + abs(px[x, y][2]-bg[2]) > 24]
        if row:
            lefts.append(min(row)); rights.append(max(row))
    print(f"{name}: {w}x{h}  bg={bg}")
    if lefts:
        print(f"   content x-range: {min(lefts)}..{max(rights)} (page width {w}); margin L={min(lefts)} R={w-max(rights)}")
    if blank_bands:
        print(f"   suspicious empty bands ({len(blank_bands)}): "
              + ", ".join(f"{a}-{b}" for a, b, _ in blank_bands[:8]))
    else:
        print("   no empty band >= 100px")
