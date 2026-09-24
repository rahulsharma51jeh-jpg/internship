"""
Colour quantisation for the generated graphics.

The charts are flat art, but anti-aliasing blends every edge, so a truecolour
PNG carries thousands of near-duplicate colours that defeat Flate compression.
Reducing each image to a 256-entry palette turns three bytes per pixel into one
and makes the remaining data highly repetitive, which shrinks the embedded
images by roughly three quarters with no visible loss on flat artwork.

Median cut is used because it allocates palette entries in proportion to how
much of the image actually uses each region of colour space, so the handful of
brand colours and their anti-aliased blends all survive.
"""


def histogram(rgb, width, height):
    """Unique colours and their frequencies."""
    hist = {}
    for i in range(0, width * height * 3, 3):
        key = rgb[i] << 16 | rgb[i + 1] << 8 | rgb[i + 2]
        hist[key] = hist.get(key, 0) + 1
    return hist


def _box_stats(colours):
    """(ranges, longest axis) for a list of packed colours."""
    lo = [255, 255, 255]
    hi = [0, 0, 0]
    for c in colours:
        comp = ((c >> 16) & 255, (c >> 8) & 255, c & 255)
        for a in range(3):
            if comp[a] < lo[a]:
                lo[a] = comp[a]
            if comp[a] > hi[a]:
                hi[a] = comp[a]
    # Weight the axes the way the eye does, so greens split before blues.
    spread = [(hi[0] - lo[0]) * 1.00,
              (hi[1] - lo[1]) * 1.30,
              (hi[2] - lo[2]) * 0.70]
    axis = spread.index(max(spread))
    return max(spread), axis


def median_cut(hist, max_colours=256):
    """
    Return (palette, mapping) where palette is a list of (r, g, b) and mapping
    takes a packed colour to its palette index.
    """
    colours = list(hist.keys())
    if len(colours) <= max_colours:
        palette = [((c >> 16) & 255, (c >> 8) & 255, c & 255) for c in colours]
        return palette, {c: i for i, c in enumerate(colours)}

    boxes = [colours]
    # Split the box with the widest colour spread until the budget is used up.
    while len(boxes) < max_colours:
        best = -1
        best_i = -1
        best_axis = 0
        for i, bx in enumerate(boxes):
            if len(bx) < 2:
                continue
            spread, axis = _box_stats(bx)
            if spread > best:
                best, best_i, best_axis = spread, i, axis
        if best_i < 0 or best <= 0:
            break
        bx = boxes.pop(best_i)
        shift = (16, 8, 0)[best_axis]
        bx.sort(key=lambda c: (c >> shift) & 255)
        # Split at the weighted median so both halves carry similar pixel mass.
        half = sum(hist[c] for c in bx) / 2.0
        run = 0
        cut = 1
        for k, c in enumerate(bx):
            run += hist[c]
            if run >= half:
                cut = max(1, min(k, len(bx) - 1))
                break
        boxes.append(bx[:cut])
        boxes.append(bx[cut:])

    palette = []
    mapping = {}
    for idx, bx in enumerate(boxes):
        tr = tg = tb = 0
        total = 0
        for c in bx:
            n = hist[c]
            tr += ((c >> 16) & 255) * n
            tg += ((c >> 8) & 255) * n
            tb += (c & 255) * n
            total += n
            mapping[c] = idx
        if total == 0:
            total = 1
        palette.append((int(round(tr / total)), int(round(tg / total)),
                        int(round(tb / total))))
    return palette, mapping


def index_image(rgb, width, height, max_colours=256):
    """
    Quantise raw RGB bytes.

    Returns (palette, index_bytes, exact) where `exact` reports whether the
    image needed no quantisation at all, i.e. the conversion was lossless.
    """
    hist = histogram(rgb, width, height)
    exact = len(hist) <= max_colours
    palette, mapping = median_cut(hist, max_colours)
    out = bytearray(width * height)
    j = 0
    for i in range(0, width * height * 3, 3):
        out[j] = mapping[rgb[i] << 16 | rgb[i + 1] << 8 | rgb[i + 2]]
        j += 1
    return palette, bytes(out), exact
