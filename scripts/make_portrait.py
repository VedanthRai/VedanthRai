"""Turn the source portrait into a monochrome halftone tone map (portrait-halftone.png, white dots on black)."""
import cv2, numpy as np
from PIL import Image, ImageFilter

SRC = "scripts/portrait-source.png"
W, H = 480, 632          # output portrait size (source aspect 618:813)
SS = 3                   # supersample for crisp dots
CELL = 4.0               # halftone cell (output px)

img = cv2.imread(SRC)
img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)

# --- subject mask via GrabCut (rect init) so the flat wall falls to black
mask = np.zeros((H, W), np.uint8)
rect = (int(W*0.02), int(H*0.04), int(W*0.96), int(H*0.95))
bgd, fgd = np.zeros((1,65)), np.zeros((1,65))
mask[:] = cv2.GC_PR_BGD
mask[int(H*0.06):, int(W*0.18):int(W*0.82)] = cv2.GC_PR_FGD
mask[int(H*0.35):, :] = cv2.GC_PR_FGD
mask[int(H*0.18):int(H*0.55), int(W*0.33):int(W*0.67)] = cv2.GC_FGD   # face core
mask[:int(H*0.03), :] = cv2.GC_BGD
mask[:int(H*0.5), :int(W*0.08)] = cv2.GC_BGD
mask[:int(H*0.5), int(W*0.92):] = cv2.GC_BGD
cv2.grabCut(img, mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
fg = np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9,9),np.uint8))
fg = cv2.GaussianBlur(fg, (0,0), 4).astype(np.float32)/255.0

# --- tone: grayscale, contrast, subject-only
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)/255.0
g = (g - np.percentile(g, 2)) / (np.percentile(g, 99) - np.percentile(g, 2))
g = np.clip(g, 0, 1)
g = np.clip((g-0.5)*1.15+0.5, 0, 1) ** 1.45
# lift deep shadows slightly so dark jacket/hair keep texture on a black screen
g = 0.30 + 0.70*g
tone = g*fg*1.0 + 0.0
# soft fade toward bottom edge so the portrait dissolves into the page
fade = np.clip((H - np.arange(H))/ (H*0.10), 0, 1)[:,None]
tone = tone*fade

# --- rotated (45deg) halftone grid, drawn supersampled
big = cv2.resize(tone, (W*SS, H*SS), interpolation=cv2.INTER_CUBIC)
canvas = np.zeros((H*SS, W*SS), np.uint8)
c = CELL*SS; ang = np.deg2rad(45); ca, sa = np.cos(ang), np.sin(ang)
n = int(max(W,H)*SS/c*1.6)
cx0, cy0 = W*SS/2, H*SS/2
for i in range(-n, n):
    for j in range(-n, n):
        x = cx0 + (i*ca - j*sa)*c
        y = cy0 + (i*sa + j*ca)*c
        if x<0 or y<0 or x>=W*SS or y>=H*SS: continue
        t = big[int(y), int(x)]
        r = c*0.62*np.sqrt(np.clip(t,0,1))
        if r > 0.6:
            cv2.circle(canvas, (int(x), int(y)), int(round(r)), 235, -1, cv2.LINE_AA)
dots = cv2.resize(canvas, (W,H), interpolation=cv2.INTER_AREA).astype(np.float32)/255

# blend a faint continuous tone under the dots for recognisability
out = np.clip(dots*0.85 + tone*0.38, 0, 1)
Image.fromarray((out*255).astype(np.uint8)).save("scripts/portrait-halftone.png")
print("ok", out.shape)
