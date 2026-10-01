"""Generate the three project diagrams as self-contained SVGs (own dark panel, so they read in GitHub light + dark themes).
Run from repo root: python3 scripts/make_svgs.py
"""
from html import escape
W = 640
BG, LINE, DIM, TXT, HI = "#0a0a0a", "#3b3b3b", "#8c8c8c", "#d9d9d9", "#ffffff"
FONT = 'ui-monospace, SFMono-Regular, Menlo, Consolas, &quot;DejaVu Sans Mono&quot;, monospace'

class S:
    def __init__(s, h, title, desc): s.h, s.p, s.title, s.desc = h, [], title, desc
    def t(s, x, y, txt, size=14, fill=TXT, anchor="start", weight="400", ls=0):
        s.p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" letter-spacing="{ls}">{escape(txt)}</text>')
    def box(s, x, y, w, h, label, sub=None, hi=False, dashed=False):
        st = f'stroke="{HI if hi else LINE}" stroke-width="{1.5 if hi else 1}"' + (' stroke-dasharray="4 4"' if dashed else '')
        s.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{"#161616" if hi else BG}" {st}/>')
        if sub is None: s.t(x+w/2, y+h/2+5, label, 14, HI if hi else TXT, "middle", "700" if hi else "400")
        else:
            s.t(x+w/2, y+h/2-3, label, 14, HI if hi else TXT, "middle", "700")
            s.t(x+w/2, y+h/2+15, sub, 12, DIM, "middle")
    def arrow(s, x1, y1, x2, y2):
        s.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{DIM}" stroke-width="1.2"/>')
        import math
        a = math.atan2(y2-y1, x2-x1); L = 7
        pts = [(x2, y2), (x2-L*math.cos(a-0.45), y2-L*math.sin(a-0.45)), (x2-L*math.cos(a+0.45), y2-L*math.sin(a+0.45))]
        s.p.append('<polygon points="' + " ".join(f"{px:.1f},{py:.1f}" for px, py in pts) + f'" fill="{DIM}"/>')
    def line(s, x1, y1, x2, y2, c=LINE, dash=False):
        s.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="1"' + (' stroke-dasharray="3 4"' if dash else '') + '/>')
    def header(s, tag, name, sub):
        s.t(24, 38, tag, 12, DIM, ls=1)
        s.t(24, 72, name, 28, HI, weight="700", ls=2)
        s.t(24, 96, sub, 14, DIM)
        s.line(24, 112, W-24, 112)
    def footer(s, txt):
        s.line(24, s.h-44, W-24, s.h-44)
        s.t(24, s.h-18, txt, 12, DIM)
    def save(s, path):
        body = "\n".join(s.p)
        grid = f'<pattern id="g" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#161616" stroke-width="1"/></pattern>'
        ticks = "".join(f'<path d="{d}" stroke="#555" fill="none"/>' for d in [
            "M8 22V8H22", f"M{W-22} 8H{W-8}V22", f"M8 {s.h-22}V{s.h-8}H22", f"M{W-22} {s.h-8}H{W-8}V{s.h-22}"])
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {s.h}" width="100%" role="img" aria-labelledby="t d" font-family="{FONT}">\n'
               f'<title id="t">{escape(s.title)}</title><desc id="d">{escape(s.desc)}</desc>\n'
               f'<defs>{grid}</defs><rect width="{W}" height="{s.h}" fill="{BG}"/><rect width="{W}" height="{s.h}" fill="url(#g)"/>\n{ticks}\n{body}\n</svg>\n')
        open(path, "w").write(svg)

# ---------------- CODEORACLE ----------------
s = S(560, "CodeOracle architecture", "A user query goes to an orchestrator, fans out to specialised agents for retrieval, analysis, architecture, impact analysis and verification, and returns a grounded answer.")
s.header("SYSTEM 01 / MULTI-AGENT RAG", "CODEORACLE", "Codebase intelligence for GitHub repositories")
s.box(220, 132, 200, 36, "USER QUERY"); s.arrow(320, 168, 320, 190)
s.box(190, 190, 260, 40, "ORCHESTRATOR", "coordinates 7 specialised agents", hi=True)
bw, gap, x0, y0 = 116, 10, 10, 282
names = [("RETRIEVE", "hybrid search"), ("ANALYZE", "code-aware"), ("ARCHITECT", "structure"), ("IMPACT", "change analysis"), ("VERIFY", "grounding")]
s.line(320, 230, 320, 256); s.line(x0+bw/2, 256, x0+4*(bw+gap)+bw/2, 256)
for i, (n, sub) in enumerate(names):
    cx = x0+i*(bw+gap)+bw/2
    s.arrow(cx, 256, cx, y0); s.box(x0+i*(bw+gap), y0, bw, 46, n, sub)
# detail stacks
def stack(i, items, y=346):
    cx = x0+i*(bw+gap)
    for k, it in enumerate(items):
        s.box(cx+8, y+k*32, bw-16, 26, it)
    s.line(cx+bw/2, y0+46, cx+bw/2, y, dash=True)
stack(0, ["embeddings", "TF-IDF", "dep-graph"]); 
s.t(10+bw/2, 346+3*32+14, "↳ fused with RRF", 12, DIM, "middle")
stack(1, ["Python AST", "dep graphs"])
stack(4, ["LLM verify"])
s.line(40, 478, 600, 478, dash=True)
s.arrow(320, 478, 320, 498)
s.box(190, 498, 260, 38, "GROUNDED ANSWER", hi=True)
s.save("assets/codeoracle.svg")

# ---------------- DRISHTI ----------------
s = S(600, "Drishti architecture", "Economic, trade and news data feed an asynchronous multi-agent pipeline, then anomaly and statistical risk analysis, shown in a Streamlit dashboard.")
s.header("SYSTEM 02 / TRADE RISK", "DRISHTI", "Agricultural trade-risk intelligence")
sw = 190; sx = [24, 225, 426]
for x, n, sub in [(sx[0], "WORLD BANK", "economic data"), (sx[1], "TRADE", "indicators"), (sx[2], "GDELT", "news data")]:
    s.box(x, 132, sw, 44, n, sub)
for x in sx: s.line(x+sw/2, 176, x+sw/2, 196)
s.line(sx[0]+sw/2, 196, sx[2]+sw/2, 196); s.arrow(320, 196, 320, 214)
s.box(150, 214, 340, 42, "ASYNC MULTI-AGENT PIPELINE", hi=True)
s.arrow(320, 256, 320, 280)
s.p.append(f'<rect x="60" y="280" width="520" height="168" fill="none" stroke="{LINE}" stroke-dasharray="4 4"/>')
s.t(76, 300, "RISK ANALYSIS", 12, DIM, ls=1)
cells = [("ISOLATION FOREST", "with StandardScaler"), ("Z-SCORE", "analysis"), ("VOLATILITY", "metrics"), ("LINEAR REGRESSION", "trend analysis")]
for i, (a, b) in enumerate(cells):
    cx = 76+(i%2)*252; cy = 312+(i//2)*64
    s.box(cx, cy, 236, 54, a, b)
s.arrow(320, 448, 320, 474)
s.box(150, 474, 340, 42, "STREAMLIT DASHBOARD", "Docker · 30 unit + integration tests")
s.arrow(320, 516, 320, 534)
s.t(320, 556, "RISK INTELLIGENCE", 16, HI, "middle", "700", 2)
s.save("assets/drishti.svg")

# ---------------- SKILLBARTER ----------------
s = S(560, "SkillBarter architecture", "A user is matched to a skill, creates a transaction, credits are held in escrow, and the escrow ends in release, refund or dispute. Strategy, Observer, Builder and Decorator patterns structure the code.")
s.header("SYSTEM 03 / TIME-BANKING", "SKILLBARTER", "Skill exchange platform on Spring Boot MVC")
flow = [("USER", "Spring Security · RBAC"), ("SKILL MATCH", "skill matching"), ("TRANSACTION", "credits"), ("ESCROW", "Spring transactions")]
# vertical flow on left, outcomes on right
ys = [130, 192, 254, 316]
for (a, b), y in zip(flow, ys):
    s.box(40, y, 250, 44, a, b, hi=(a == "ESCROW"))
for y in ys[:-1]: s.arrow(165, y+44, 165, y+62)
s.line(290, 338, 336, 338)
oy = [300, 352, 404]
s.line(336, 321, 336, 421)
for n, y in zip(["RELEASE", "REFUND", "DISPUTE"], oy):
    s.line(336, y+22, 360, y+22); s.arrow(360, y+22, 372, y+22); s.box(372, y, 228, 44, n)
s.t(372, 292, "STATE TRANSITIONS", 12, DIM, ls=1)
s.t(24, 480, "PATTERNS", 12, DIM, ls=1)
for i, n in enumerate(["STRATEGY", "OBSERVER", "BUILDER", "DECORATOR"]):
    s.box(24+i*152, 492, 140, 30, n)
s.save("assets/skillbarter.svg")
print("svgs ok")
