"""Build assets/portrait-reveal.gif: top-to-bottom CRT-style scan reconstruction of the halftone portrait.
Run:  python3 scripts/make_portrait.py && python3 scripts/make_reveal.py   (from repo root)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CW, CH = 1000, 660
PX, PY = 56, 14                      # portrait origin
FPS = 10
F = "/usr/share/fonts/truetype/dejavu/"
mono  = lambda s: ImageFont.truetype(F+"DejaVuSansMono.ttf", s)
monoB = lambda s: ImageFont.truetype(F+"DejaVuSansMono-Bold.ttf", s)
big   = ImageFont.truetype(F+"DejaVuSansCondensed-Bold.ttf", 70)

portrait = np.array(Image.open("scripts/portrait-halftone.png").convert("L")).astype(np.float32)
PH, PW = portrait.shape
rng = np.random.default_rng(7)
grain = rng.normal(0, 3.0, (CH, CW)).astype(np.float32)            # static -> compresses well
scan_rows = np.where(np.arange(CH) % 3 == 0, 0.90, 1.0).astype(np.float32)[:, None]

def grid():
    g = np.zeros((CH, CW), np.float32)
    g[::40, :] = 14; g[:, ::40] = 14
    return g
GRID = grid()

def ease(x): x = min(max(x, 0), 1); return x*x*(3-2*x)

def text_layer(draw_fn):
    im = Image.new("L", (CW, CH), 0); draw_fn(ImageDraw.Draw(im)); return np.array(im).astype(np.float32)

def corners(d, v):
    x0, y0, x1, y1, L = PX-14, PY-2, PX+PW+14, PY+PH+2, 22
    for (x, y, sx, sy) in [(x0,y0,1,1),(x1,y0,-1,1),(x0,y1,1,-1),(x1,y1,-1,-1)]:
        d.line([(x,y),(x+sx*L,y)], fill=v, width=1); d.line([(x,y),(x,y+sy*L)], fill=v, width=1)

def frame(t, total):
    canvas = GRID.copy() * (0.4 + 0.6*ease(t/0.6))
    scan_t = (t - 0.6) / 2.6                      # 0.6s .. 3.2s
    p = ease(scan_t)
    y = int(p * PH)
    done = scan_t >= 1

    # ---- portrait, revealed above scanline
    if scan_t > 0:
        img = np.zeros((CH, CW), np.float32)
        rows = portrait.copy()
        rows[y:] = 0
        # phosphor: rows just above the line burn brighter, then settle
        for k in range(1, 46):
            r = y - k
            if 0 <= r < PH: rows[r] = np.minimum(255, rows[r] * (1 + 0.55*np.exp(-k/12.0)))
        # tiny horizontal tear around the line
        if not done:
            for k in range(0, 16):
                r = y - k
                if 0 <= r < PH:
                    sh = int(round(5*np.sin(r*0.9 + t*40) * np.exp(-k/6.0)))
                    rows[r] = np.roll(rows[r], sh)
        img[PY:PY+PH, PX:PX+PW] = rows
        canvas = np.maximum(canvas, img)
        # scanline + glow
        if not done and 0 < y < PH:
            ly = PY + y
            glow = np.zeros((CH, CW), np.float32)
            glow[ly:ly+2, PX-30:PX+PW+30] = 255
            gb = np.array(Image.fromarray(glow.astype(np.uint8)).filter(ImageFilter.GaussianBlur(7))).astype(np.float32)
            canvas = np.maximum(canvas, glow*0.95 + gb*1.6)
            # faint ghost of what's coming: 6 rows below the line, very dim
            ghost = np.zeros((CH, CW), np.float32)
            ghost[PY+y:PY+min(PH, y+60), PX:PX+PW] = portrait[y:min(PH, y+60)] * 0.10 * np.linspace(1, 0, min(PH,y+60)-y)[:, None]
            canvas = np.maximum(canvas, ghost)

    # ---- overlays
    def labels(d):
        tx = 600
        a = ease(t/0.5)
        d.text((tx, 40), "PORTRAIT RECONSTRUCTION", font=mono(15), fill=int(150*a))
        d.line([(tx, 66), (CW-56, 66)], fill=int(70*a), width=1)
        if t < 0.6:
            n = int(t/0.6*18); d.text((tx, 84), ("INITIALIZING VISION")[:n] + ("_" if int(t*8)%2==0 else ""), font=mono(15), fill=170)
        else:
            pct = int(round(100*min(1, max(0, scan_t))))
            d.text((tx, 84), "SCAN", font=mono(15), fill=150)
            d.text((tx+80, 84), f"{pct:03d}%", font=monoB(15), fill=235)
            d.text((tx, 108), "ROW", font=mono(15), fill=150)
            d.text((tx+80, 108), f"{min(PH, y):04d} / {PH:04d}", font=mono(15), fill=200)
            bw = CW-56-tx; d.rectangle([tx, 140, tx+bw, 143], outline=70)
            d.rectangle([tx, 140, tx+int(bw*min(1,max(0,scan_t))), 143], fill=235)
    canvas = np.maximum(canvas, text_layer(labels))

    if scan_t > 0.02:
        canvas = np.maximum(canvas, text_layer(lambda d: corners(d, 110)))

    # ---- identity block (3.8s .. 4.6s)
    ia = ease((t - 3.9)/0.7)
    if ia > 0:
        def ident(d):
            tx = 600
            d.text((tx-3, 262), "VEDANTH", font=big, fill=int(250*ia))
            d.text((tx-3, 342), "RAI", font=big, fill=int(250*ia))
            d.text((tx, 462), "AI / SOFTWARE SYSTEMS", font=monoB(21), fill=int(230*ia))
            d.text((tx, 498), "BANGALORE · INDIA", font=mono(16), fill=int(150*ia))
            d.line([(tx, 540), (CW-56, 540)], fill=int(90*ia), width=1)
            d.text((tx, 560), "IDENTITY LOADED.", font=monoB(19), fill=int(245*ia))
            if ia >= 1 and int(t*2) % 2 == 0:
                d.rectangle([tx+232, 562, tx+244, 580], fill=235)
        canvas = np.maximum(canvas, text_layer(ident))

    out = canvas * scan_rows + grain
    q = (np.clip(out,0,255)/255*39).round()/39*255
    return Image.fromarray(q.astype(np.uint8), "L")

frames, durs = [], []
T_ACTIVE = 5.0
n = int(T_ACTIVE*FPS)
for i in range(n):
    frames.append(frame(i/FPS, T_ACTIVE)); durs.append(int(1000/FPS))
# hold complete identity (cursor blinks at 2 Hz), then fade to black and loop
hold = 5.0
for i in range(int(hold*FPS)):
    frames.append(frame(T_ACTIVE + i/FPS, T_ACTIVE)); durs.append(int(1000/FPS))
last = np.array(frames[-1]).astype(np.float32)
for i in range(1, 6):
    frames.append(Image.fromarray((last*(1-i/5)).astype(np.uint8), "L")); durs.append(int(1000/FPS))

frames[0].save("assets/portrait-reveal.gif", save_all=True, append_images=frames[1:], duration=durs,
               loop=0, optimize=True, disposal=1)
print(len(frames), "frames", sum(durs)/1000, "s")
