#!/usr/bin/env python3
"""
PLANO ARQUITECTÓNICO PROFESIONAL — Edificio Residencial 3P+T
Incluye: cotas completas, instalaciones sanitarias, eléctricas,
ejes estructurales, columnas, artefactos, corte esquemático.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

FONTS = "/Users/carlossanchez/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/e09fb916-12e4-41ff-8ae4-db2feebaefca/79f14b77-b8e8-4bfc-8ce4-43aff6c6e981/skills/canvas-design/canvas-fonts"

def lf(n,s):
    try: return ImageFont.truetype(os.path.join(FONTS,n),s)
    except: return ImageFont.load_default()

# Fonts
FH = lf("BigShoulders-Bold.ttf",48)
FT = lf("BigShoulders-Bold.ttf",30)
FT2 = lf("BigShoulders-Bold.ttf",22)
FR = lf("InstrumentSans-Bold.ttf",13)
FRS = lf("InstrumentSans-Regular.ttf",11)
FA = lf("DMMono-Regular.ttf",11)
FD = lf("DMMono-Regular.ttf",10)
FDS = lf("DMMono-Regular.ttf",9)
FREF = lf("DMMono-Regular.ttf",9)
FTBL = lf("DMMono-Regular.ttf",12)
FTBLB = lf("GeistMono-Bold.ttf",12)
FNOTE = lf("InstrumentSans-Regular.ttf",11)
FAXIS = lf("InstrumentSans-Bold.ttf",14)
FAXIS_S = lf("InstrumentSans-Bold.ttf",11)
FLEVEL = lf("DMMono-Regular.ttf",11)

# Colors
W_ = (255,255,255)
BK = (0,0,0)
RD = (185,25,25)
BL = (30,90,180)   # plumbing
GR = (40,150,60)    # electrical
GY = (150,150,150)
DG = (90,90,90)
LG = (235,235,235)
CYAN = (0,160,200)  # structural axes

# Scale
S = 32  # 1m = 32px
WE = 7  # ext wall
WI = 4  # int wall
COL_SIZE = 8  # structural column

def mp(v): return int(v*S)

# Canvas — each floor gets full page, then tables + corte
W = 2000
FLOOR_H = 980
N_FLOORS = 4
TABLES_H = 900
CORTE_H = 600
H_TOTAL = FLOOR_H * N_FLOORS + TABLES_H + CORTE_H + 200
img = Image.new("RGB", (W, H_TOTAL), W_)
d = ImageDraw.Draw(img)

# ══════════════════════════════════════════════════════════════
# PROFESSIONAL DRAWING HELPERS
# ══════════════════════════════════════════════════════════════

def wall_h(x,y,length,t=WE):
    d.rectangle([x,y,x+length,y+t],fill=BK)

def wall_v(x,y,length,t=WE):
    d.rectangle([x,y,x+t,y+length],fill=BK)

def fill_r(x,y,w,h,c):
    d.rectangle([x+1,y+1,x+w-1,y+h-1],fill=c)

def outline(x,y,w,h,ext=True):
    t=WE if ext else WI
    wall_h(x,y,w,t); wall_h(x,y+h-t,w,t)
    wall_v(x,y,h,t); wall_v(x+w-t,y,h,t)

def struct_column(x,y):
    """Draw structural column (filled black square)"""
    hs = COL_SIZE//2
    d.rectangle([x-hs,y-hs,x+hs,y+hs],fill=BK)

def label_room(x,y,w,h,name,area_m2,dims_txt=None):
    """Label with name, area, and room dimensions"""
    cx,cy = x+w//2, y+h//2
    lines = []
    lines.append((name, FR, BK))
    if area_m2:
        lines.append((f"{area_m2} m²", FA, DG))
    if dims_txt:
        lines.append((dims_txt, FDS, RD))

    total_h = len(lines) * 16
    start_y = cy - total_h//2
    for i,(txt,font,color) in enumerate(lines):
        bb = d.textbbox((0,0),txt,font=font)
        tw = bb[2]-bb[0]
        # ensure text fits
        if tw > w - 4:
            font = FREF
            bb = d.textbbox((0,0),txt,font=font)
            tw = bb[2]-bb[0]
        d.text((cx-tw//2, start_y + i*16), txt, fill=color, font=font)

def dim_h(x1,x2,y,val,above=True,font=FD):
    """Horizontal dimension with tick marks"""
    off = -22 if above else 22
    ly = y+off
    # extension lines
    ey = y-2 if above else y+2
    d.line([(x1,ey),(x1,ly-2 if above else ly+2)],fill=RD,width=1)
    d.line([(x2,ey),(x2,ly-2 if above else ly+2)],fill=RD,width=1)
    # dim line
    d.line([(x1+2,ly),(x2-2,ly)],fill=RD,width=1)
    # oblique ticks (45 degree - architectural style)
    for ax in [x1,x2]:
        d.line([(ax-3,ly+3),(ax+3,ly-3)],fill=RD,width=2)
    # text
    txt = f"{val:.2f}"
    bb = d.textbbox((0,0),txt,font=font)
    tw,th = bb[2]-bb[0], bb[3]-bb[1]
    tx = (x1+x2)//2 - tw//2
    ty = ly-th-2 if above else ly+3
    d.rectangle([tx-2,ty-1,tx+tw+2,ty+th+1],fill=W_)
    d.text((tx,ty),txt,fill=RD,font=font)

def dim_v(x,y1,y2,val,left=True,font=FD):
    """Vertical dimension with tick marks"""
    off = -26 if left else 26
    lx = x+off
    ex = x-2 if left else x+2
    d.line([(ex,y1),(lx-2 if left else lx+2,y1)],fill=RD,width=1)
    d.line([(ex,y2),(lx-2 if left else lx+2,y2)],fill=RD,width=1)
    d.line([(lx,y1+2),(lx,y2-2)],fill=RD,width=1)
    for ay in [y1,y2]:
        d.line([(lx-3,ay+3),(lx+3,ay-3)],fill=RD,width=2)
    txt = f"{val:.2f}"
    bb = d.textbbox((0,0),txt,font=font)
    tw,th = bb[2]-bb[0], bb[3]-bb[1]
    ty = (y1+y2)//2 - th//2
    tx = lx-tw-3 if left else lx+4
    d.rectangle([tx-2,ty-1,tx+tw+2,ty+th+1],fill=W_)
    d.text((tx,ty),txt,fill=RD,font=font)

def dim_chain_h(x_start, positions, y, above=True):
    """Chain dimensioning (professional architectural standard)"""
    for i in range(len(positions)-1):
        x1 = x_start + positions[i]
        x2 = x_start + positions[i+1]
        val = (positions[i+1] - positions[i]) / S
        dim_h(x1, x2, y, val, above, FDS)

def dim_chain_v(y_start, positions, x, left=True):
    for i in range(len(positions)-1):
        y1 = y_start + positions[i]
        y2 = y_start + positions[i+1]
        val = (positions[i+1] - positions[i]) / S
        dim_v(x, y1, y2, val, left, FDS)

def axis_circle(x, y, label, horizontal=True):
    """Structural axis marker (circle with letter/number)"""
    r = 14
    d.ellipse([x-r,y-r,x+r,y+r],outline=CYAN,width=2)
    bb = d.textbbox((0,0),label,font=FAXIS_S)
    tw,th = bb[2]-bb[0], bb[3]-bb[1]
    d.text((x-tw//2, y-th//2), label, fill=CYAN, font=FAXIS_S)

def draw_axes(ox, oy, bw, bh, h_positions, v_positions, h_labels, v_labels):
    """Draw structural axis grid"""
    # Horizontal axes (bottom)
    for pos, label in zip(h_positions, h_labels):
        x = ox + pos
        # dashed vertical line
        for yy in range(oy, oy+bh, 10):
            d.line([(x, yy), (x, min(yy+5, oy+bh))], fill=CYAN, width=1)
        axis_circle(x, oy+bh+22, label)
        axis_circle(x, oy-22, label)
    # Vertical axes (left)
    for pos, label in zip(v_positions, v_labels):
        y = oy + pos
        for xx in range(ox, ox+bw, 10):
            d.line([(xx, y), (min(xx+5, ox+bw), y)], fill=CYAN, width=1)
        axis_circle(ox-22, y, label)
        axis_circle(ox+bw+22, y, label)

def door_h(x,y,wpx,label,down=True):
    d.rectangle([x-1,y-WI-1,x+wpx+1,y+WI+1],fill=W_)
    if down:
        d.arc([x,y,x+wpx,y+wpx],180,270,fill=BK,width=1)
        d.line([(x,y),(x,y+wpx)],fill=BK,width=1)
    else:
        d.arc([x,y-wpx,x+wpx,y],90,180,fill=BK,width=1)
        d.line([(x+wpx,y),(x+wpx,y-wpx)],fill=BK,width=1)
    bb=d.textbbox((0,0),label,font=FREF);tw=bb[2]-bb[0]
    d.text((x+wpx//2-tw//2,y-WI-12),label,fill=DG,font=FREF)

def door_v(x,y,wpx,label,right=True):
    d.rectangle([x-WI-1,y-1,x+WI+1,y+wpx+1],fill=W_)
    if right:
        d.arc([x,y,x+wpx,y+wpx],270,360,fill=BK,width=1)
        d.line([(x,y),(x+wpx,y)],fill=BK,width=1)
    else:
        d.arc([x-wpx,y,x,y+wpx],0,90,fill=BK,width=1)
        d.line([(x,y+wpx),(x-wpx,y+wpx)],fill=BK,width=1)
    d.text((x+7,y+wpx//2-4),label,fill=DG,font=FREF)

def win_h(x,y,wpx,label):
    d.rectangle([x,y-WE//2-1,x+wpx,y+WE//2+1],fill=W_)
    d.line([(x,y-3),(x+wpx,y-3)],fill=BK,width=2)
    d.line([(x,y+3),(x+wpx,y+3)],fill=BK,width=2)
    # glass lines
    d.line([(x,y),(x+wpx,y)],fill=BK,width=1)
    cx=x+wpx//2
    d.line([(cx,y-5),(cx,y+5)],fill=BK,width=1)
    bb=d.textbbox((0,0),label,font=FREF);tw=bb[2]-bb[0]
    d.text((cx-tw//2,y+WE//2+3),label,fill=DG,font=FREF)

def win_v(x,y,wpx,label):
    d.rectangle([x-WE//2-1,y,x+WE//2+1,y+wpx],fill=W_)
    d.line([(x-3,y),(x-3,y+wpx)],fill=BK,width=2)
    d.line([(x+3,y),(x+3,y+wpx)],fill=BK,width=2)
    d.line([(x,y),(x,y+wpx)],fill=BK,width=1)
    cy=y+wpx//2
    d.line([(x-5,cy),(x+5,cy)],fill=BK,width=1)
    d.text((x+WE//2+4,cy-4),label,fill=DG,font=FREF)

def stair_sym(x,y,w,h):
    n=12; th_=h//n
    for i in range(n):
        d.line([(x,y+i*th_),(x+w,y+i*th_)],fill=BK,width=1)
    d.rectangle([x,y,x+w,y+h],outline=BK,width=1)
    mx=x+w//2
    d.line([(mx,y+h-3),(mx,y+8)],fill=BK,width=2)
    d.polygon([(mx,y+4),(mx-5,y+14),(mx+5,y+14)],fill=BK)
    d.text((x+2,y+h-12),"SUBE",fill=DG,font=FREF)

def elev_sym(x,y,w,h):
    d.rectangle([x,y,x+w,y+h],outline=BK,width=2)
    d.line([(x,y),(x+w,y+h)],fill=BK,width=1)
    d.line([(x+w,y),(x,y+h)],fill=BK,width=1)
    bb=d.textbbox((0,0),"ASC",font=FREF);tw=bb[2]-bb[0]
    d.text((x+w//2-tw//2,y+h+3),"ASC",fill=DG,font=FREF)

# ── Plumbing fixtures ──
def toilet(x,y,rotation=0):
    """WC symbol (plan view)"""
    # tank
    d.rectangle([x-6,y-10,x+6,y-4],outline=BL,width=1)
    # bowl
    d.ellipse([x-7,y-4,x+7,y+10],outline=BL,width=1)
    d.text((x-5,y+12),"WC",fill=BL,font=FREF)

def sink(x,y):
    """Lavabo symbol"""
    d.rectangle([x-6,y-4,x+6,y+6],outline=BL,width=1)
    d.ellipse([x-4,y-2,x+4,y+4],outline=BL,width=1)
    d.text((x-5,y+8),"Lv",fill=BL,font=FREF)

def shower(x,y):
    """Ducha symbol"""
    d.rectangle([x-10,y-10,x+10,y+10],outline=BL,width=1)
    # diagonal lines (floor drain pattern)
    d.line([(x-10,y-10),(x+10,y+10)],fill=BL,width=1)
    d.line([(x+10,y-10),(x-10,y+10)],fill=BL,width=1)
    d.text((x-5,y+12),"Du",fill=BL,font=FREF)

def kitchen_sink(x,y):
    """Pileta cocina double"""
    d.rectangle([x-12,y-5,x+12,y+5],outline=BL,width=1)
    d.line([(x,y-5),(x,y+5)],fill=BL,width=1)
    d.text((x-8,y+7),"Pil.",fill=BL,font=FREF)

def laundry(x,y):
    """Lavarropas"""
    d.rectangle([x-7,y-7,x+7,y+7],outline=BL,width=1)
    d.ellipse([x-4,y-4,x+4,y+4],outline=BL,width=1)
    d.text((x-6,y+9),"Lv",fill=BL,font=FREF)

# ── Plumbing pipes ──
def pipe_h(x1,x2,y):
    d.line([(x1,y),(x2,y)],fill=BL,width=2)

def pipe_v(x,y1,y2):
    d.line([(x,y1),(x,y2)],fill=BL,width=2)

def pipe_node(x,y):
    d.ellipse([x-3,y-3,x+3,y+3],fill=BL)

def drain_line(x1,y1,x2,y2):
    """Desagüe (dashed blue)"""
    dx = x2-x1; dy = y2-y1
    length = math.sqrt(dx*dx+dy*dy)
    n = max(1,int(length/8))
    for i in range(0,n,2):
        t1 = i/n; t2 = min((i+1)/n, 1.0)
        d.line([(x1+dx*t1,y1+dy*t1),(x1+dx*t2,y1+dy*t2)],fill=BL,width=1)

# ── Electrical symbols ──
def outlet(x,y):
    """Tomacorriente (circle with line)"""
    d.ellipse([x-4,y-4,x+4,y+4],outline=GR,width=1)
    d.line([(x,y-4),(x,y-8)],fill=GR,width=1)

def light_fixture(x,y,label=""):
    """Boca de luz (circle with X)"""
    r=5
    d.ellipse([x-r,y-r,x+r,y+r],outline=GR,width=1)
    d.line([(x-3,y-3),(x+3,y+3)],fill=GR,width=1)
    d.line([(x+3,y-3),(x-3,y+3)],fill=GR,width=1)
    if label:
        d.text((x+8,y-5),label,fill=GR,font=FREF)

def switch(x,y):
    """Interruptor"""
    d.ellipse([x-3,y-3,x+3,y+3],fill=GR)
    d.line([(x+3,y),(x+10,y-6)],fill=GR,width=1)

def elec_panel(x,y):
    """Tablero eléctrico"""
    d.rectangle([x-8,y-12,x+8,y+12],outline=GR,width=2)
    d.line([(x-4,y-6),(x+4,y-6)],fill=GR,width=1)
    d.line([(x-4,y),(x+4,y)],fill=GR,width=1)
    d.line([(x-4,y+6),(x+4,y+6)],fill=GR,width=1)
    d.text((x-6,y+14),"TE",fill=GR,font=FREF)

def elec_wire(points):
    """Circuito eléctrico"""
    for i in range(len(points)-1):
        d.line([points[i],points[i+1]],fill=GR,width=1)

# ── Level marker ──
def level_marker(x, y, level_text, height_text):
    """Nivel marker (triangle with level info)"""
    d.polygon([(x,y),(x-8,y+10),(x+8,y+10)],outline=BK,width=1)
    d.text((x+12,y),level_text,fill=BK,font=FLEVEL)
    d.text((x+12,y+12),height_text,fill=RD,font=FLEVEL)

def scale_bar(x, y, meters=5):
    """Escala gráfica"""
    total_w = mp(meters)
    d.line([(x,y),(x+total_w,y)],fill=BK,width=2)
    for i in range(meters+1):
        px = x + mp(i)
        d.line([(px,y-5),(px,y+5)],fill=BK,width=1)
        d.text((px-3,y+8),str(i),fill=BK,font=FREF)
    d.text((x+total_w+8,y-4),"m",fill=BK,font=FR)
    d.text((x,y-16),"ESCALA 1:100",fill=BK,font=FREF)


# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
d.rectangle([0,0,W,80],fill=(245,245,245))
d.line([(0,80),(W,80)],fill=BK,width=3)
d.text((60,16),"EDIFICIO RESIDENCIAL 3P+T — PLANOS ARQUITECTÓNICOS",fill=BK,font=FH)
d.text((60,62),"PLANTAS GENERALES | INSTALACIONES SANITARIAS | INSTALACIONES ELÉCTRICAS | CORTE ESQUEMÁTICO",fill=DG,font=FNOTE)
# North
nx=1930; ny=40
d.polygon([(nx,ny-25),(nx-8,ny+5),(nx+8,ny+5)],outline=BK,width=2)
d.polygon([(nx,ny-25),(nx-8,ny+5),(nx,ny-3)],fill=BK)
d.text((nx-3,ny+8),"N",fill=BK,font=FR)

# Building dimensions
BW = mp(15)  # 480
BH = mp(12)  # 384

# Structural axes positions (from origin)
# Horizontal: A=0, B=6, C=7.5(pasillo start), D=9, E=15
H_AXES = [0, mp(6), mp(6.75), mp(8.25), mp(9), mp(15)]
H_LABELS = ["A","B","C","D","E","F"]
# Vertical: 1=0, 2=5, 3=7.5, 4=12
V_AXES = [0, mp(5), mp(7.5), mp(8.5), mp(11), mp(12)]
V_LABELS = ["1","2","3","4","5","6"]


# ══════════════════════════════════════════════════════════════
# FLOOR 1: PLANTA BAJA — 180 m²
# ══════════════════════════════════════════════════════════════
F1_Y = 90
d.rectangle([40,F1_Y,1960,F1_Y+FLOOR_H],outline=LG,width=1)
d.text((60,F1_Y+10),"PLANTA BAJA — N.P.T. ±0.00 — 180 m²",fill=BK,font=FT)
d.line([(60,F1_Y+42),(350,F1_Y+42)],fill=RD,width=3)
level_marker(380, F1_Y+18, "NPT ±0.00", "h=3.20m (piso a piso)")

ox, oy = 160, F1_Y+80
BW_pb = mp(15); BH_pb = mp(12)

# Structural axes
draw_axes(ox, oy, BW_pb, BH_pb,
    [0, mp(6), mp(9), mp(15)],
    [0, mp(5), mp(7.5), mp(12)],
    ["A","B","C","D"],
    ["1","2","3","4"])

# Structural columns at intersections
for cx_ in [0, mp(6), mp(9), mp(15)]:
    for cy_ in [0, mp(5), mp(7.5), mp(12)]:
        struct_column(ox+cx_, oy+cy_)

# Room fills
fill_r(ox+WE,oy+WE,mp(6)-WE,mp(7.5)-WE,(255,252,240))     # Local 1
fill_r(ox+mp(6),oy+WE,mp(3),mp(5)-WE,(242,242,252))         # Hall
fill_r(ox+mp(9),oy+WE,mp(6)-WE,mp(7.5)-WE,(255,252,240))   # Local 2
fill_r(ox+WE,oy+mp(7.5),mp(6)-WE,mp(4.5)-WE,(240,240,240)) # Cochera
fill_r(ox+mp(6),oy+mp(5),mp(3),mp(7)-WE,(248,245,235))      # Core
fill_r(ox+mp(9),oy+mp(7.5),mp(6)-WE,mp(4.5)-WE,(242,250,242)) # Patio

# Exterior walls
outline(ox,oy,BW_pb,BH_pb,True)

# Interior walls
wall_v(ox+mp(6),oy,mp(5),WI)
wall_v(ox+mp(9)-WI,oy,mp(5),WI)
wall_h(ox,oy+mp(7.5),mp(6),WI)
wall_h(ox+mp(9),oy+mp(7.5),mp(6),WI)
wall_h(ox+mp(6),oy+mp(5),mp(3),WI)
wall_v(ox+mp(6),oy+mp(5),mp(7),WI)
wall_v(ox+mp(9)-WI,oy+mp(5),mp(7),WI)

# Labels with dimensions
label_room(ox,oy,mp(6),mp(7.5),"LOCAL COMERCIAL 1",45,"6.00 × 7.50")
label_room(ox+mp(6),oy,mp(3),mp(5),"HALL",15,"3.00 × 5.00")
label_room(ox+mp(9),oy,mp(6),mp(7.5),"LOCAL COMERCIAL 2",45,"6.00 × 7.50")
label_room(ox,oy+mp(7.5),mp(6),mp(4.5),"COCHERA",30,"6.00 × 5.00")
label_room(ox+mp(9),oy+mp(7.5),mp(6),mp(4.5),"PATIO SERVICIO",28,"6.00 × 4.50")

# Stair/elevator
stair_sym(ox+mp(6)+WI+4, oy+mp(5)+WI+4, mp(2.4)-8, mp(3)-8)
elev_sym(ox+mp(6.8), oy+mp(9), mp(1.4), mp(1.6))

# Doors PB
door_h(ox+mp(6.8),oy,mp(1.0),"P1",True)
door_h(ox+mp(2),oy,mp(1.2),"P2",True)
door_h(ox+mp(11),oy,mp(1.2),"P3",True)
door_h(ox+mp(2.5),oy+mp(7.5),mp(1.0),"P4",False)

# Windows PB
win_h(ox+mp(3.5),oy,mp(1.5),"V1 1.50×1.20")
win_h(ox+mp(12),oy,mp(1.5),"V2 1.50×1.20")
win_v(ox,oy+mp(3),mp(1.5),"V3")
win_v(ox+BW_pb,oy+mp(3),mp(1.5),"V4")
win_v(ox,oy+mp(9),mp(1.5),"V9")   # cochera window
win_v(ox+BW_pb,oy+mp(9),mp(1.5),"V10") # patio window

# ── CHAIN DIMENSIONING PB ──
# Top chain
dim_chain_h(ox, [0, mp(6), mp(9), mp(15)], oy, True)
# Total top
dim_h(ox, ox+BW_pb, oy-25, 15.00, True)
# Left chain
dim_chain_v(oy, [0, mp(5), mp(7.5), mp(12)], ox, True)
# Total left
dim_v(ox-30, oy, oy+BH_pb, 12.00, True)
# Bottom chain
dim_chain_h(ox, [0, mp(6), mp(9), mp(15)], oy+BH_pb, False)
# Right chain
dim_chain_v(oy, [0, mp(5), mp(7.5), mp(12)], ox+BW_pb, False)

# ── PLUMBING PB ──
# Cochera floor drain
pipe_node(ox+mp(3), oy+mp(10))
d.text((ox+mp(3)+5, oy+mp(10)-4),"BD",fill=BL,font=FREF)  # boca desagüe

# ── ELECTRICAL PB ──
# Lights
light_fixture(ox+mp(3), oy+mp(3.5), "2×36W")    # Local 1
light_fixture(ox+mp(12), oy+mp(3.5), "2×36W")   # Local 2
light_fixture(ox+mp(7.5), oy+mp(2.5), "LED 18W") # Hall
light_fixture(ox+mp(3), oy+mp(9.5), "LED 18W")   # Cochera
light_fixture(ox+mp(7.5), oy+mp(7), "LED 12W")    # Escalera

# Outlets
outlet(ox+mp(1), oy+mp(1))
outlet(ox+mp(5), oy+mp(1))
outlet(ox+mp(10), oy+mp(1))
outlet(ox+mp(14), oy+mp(1))

# Panel
elec_panel(ox+mp(7.5), oy+mp(4.5))

# Switches
switch(ox+mp(6.2), oy+mp(0.5))  # Hall
switch(ox+mp(0.5), oy+mp(0.5))  # Local 1
switch(ox+mp(9.5), oy+mp(0.5))  # Local 2

# Scale bar
scale_bar(ox, oy+BH_pb+60, 5)

# ── RIGHT PANEL: Aberturas PB ──
rpx = ox + BW_pb + 80
d.text((rpx,oy),"ABERTURAS PB:",fill=BK,font=FR)
refs = [
    "P1 Pta. hall      0.90×2.10 h",
    "P2 Pta. local 1   1.20×2.10 h",
    "P3 Pta. local 2   1.20×2.10 h",
    "P4 Pta. cochera    0.90×2.10 h",
    "V1 Vent. local 1   1.50×1.20 h=1.00",
    "V2 Vent. local 2   1.50×1.20 h=1.00",
    "V3 Vent. lat. L1   1.50×1.20 h=1.00",
    "V4 Vent. lat. L2   1.50×1.20 h=1.00",
    "V9 Vent. cochera    1.50×1.20 h=1.60",
    "V10 Vent. patio     1.50×1.20 h=1.00",
]
for i,t in enumerate(refs):
    d.text((rpx,oy+20+i*16),t,fill=DG,font=FREF)

d.text((rpx,oy+20+len(refs)*16+15),"INST. SANITARIA:",fill=BL,font=FR)
d.text((rpx,oy+20+len(refs)*16+32),"BD = Boca desagüe pluvial",fill=BL,font=FREF)
d.text((rpx,oy+20+len(refs)*16+46),"Cañería ø110mm PVC",fill=BL,font=FREF)

d.text((rpx,oy+20+len(refs)*16+70),"INST. ELÉCTRICA:",fill=GR,font=FR)
d.text((rpx,oy+20+len(refs)*16+87),"TE = Tablero eléctrico gral.",fill=GR,font=FREF)
d.text((rpx,oy+20+len(refs)*16+101),"⊕ = Boca de luz (techo)",fill=GR,font=FREF)
d.text((rpx,oy+20+len(refs)*16+115),"○ = Tomacorriente",fill=GR,font=FREF)
d.text((rpx,oy+20+len(refs)*16+129),"● = Interruptor",fill=GR,font=FREF)


# ══════════════════════════════════════════════════════════════
# FLOOR 2: PISO 1 (TIPO) — 160 m²
# ══════════════════════════════════════════════════════════════
F2_Y = F1_Y + FLOOR_H
d.rectangle([40,F2_Y,1960,F2_Y+FLOOR_H],outline=LG,width=1)
d.text((60,F2_Y+10),"PISO 1 (TIPO) — N.P.T. +3.20 — 160 m²",fill=BK,font=FT)
d.line([(60,F2_Y+42),(350,F2_Y+42)],fill=RD,width=3)
level_marker(380, F2_Y+18, "NPT +3.20", "h=2.80m (piso a piso)")

p1x, p1y = 160, F2_Y+80
px_l = p1x+mp(6.75)
px_r = p1x+mp(8.25)
pw = mp(1.5)

# Axes
draw_axes(p1x, p1y, BW, BH,
    [0, mp(6.75), mp(8.25), mp(15)],
    [0, mp(5), mp(8.5), mp(11), mp(12)],
    ["A","B","C","D"],
    ["1","2","3","4","5"])

# Columns
for cx_ in [0, mp(6.75), mp(8.25), mp(15)]:
    for cy_ in [0, mp(5), mp(8.5), mp(11), mp(12)]:
        struct_column(p1x+cx_, p1y+cy_)

# Fills
fill_r(p1x+WE,p1y+WE,mp(6.75)-WE,mp(5)-WE,(248,248,255))   # Living A
fill_r(p1x+WE,p1y+mp(5),mp(4.5)-WE,mp(3.5),(255,250,242))    # Dorm1 A
fill_r(p1x+mp(4.5),p1y+mp(5),mp(2.25),mp(3.5),(242,248,255)) # Cocina A
fill_r(p1x+WE,p1y+mp(8.5),mp(4.5)-WE,mp(2.5),(255,250,242)) # Dorm2 A
fill_r(p1x+mp(4.5),p1y+mp(8.5),mp(2.25),mp(2.5),(235,242,255)) # Baño A
fill_r(p1x+WE,p1y+mp(11),mp(6.75)-WE,mp(1)-WE,(240,255,242))   # Balcón A

fill_r(px_r,p1y+WE,mp(6.75)-WE,mp(5)-WE,(248,248,255))
fill_r(px_r,p1y+mp(5),mp(2.25),mp(3.5),(242,248,255))
fill_r(p1x+mp(10.5),p1y+mp(5),mp(4.5)-WE,mp(3.5),(255,250,242))
fill_r(px_r,p1y+mp(8.5),mp(2.25),mp(2.5),(235,242,255))
fill_r(p1x+mp(10.5),p1y+mp(8.5),mp(4.5)-WE,mp(2.5),(255,250,242))
fill_r(px_r,p1y+mp(11),mp(6.75)-WE,mp(1)-WE,(240,255,242))

fill_r(px_l,p1y+WE,pw,BH-WE*2,(245,242,232))  # Pasillo

# Walls
outline(p1x,p1y,BW,BH,True)
wall_v(px_l,p1y,BH,WI); wall_v(px_r-WI,p1y,BH,WI)

# Depto A walls
wall_h(p1x,p1y+mp(5),mp(6.75),WI)
wall_v(p1x+mp(4.5),p1y+mp(5),mp(6),WI)
wall_h(p1x,p1y+mp(8.5),mp(6.75),WI)
wall_h(p1x,p1y+mp(11),mp(6.75),WI)

# Depto B walls
wall_h(px_r,p1y+mp(5),mp(6.75),WI)
wall_v(p1x+mp(10.5)-WI,p1y+mp(5),mp(6),WI)
wall_h(px_r,p1y+mp(8.5),mp(6.75),WI)
wall_h(px_r,p1y+mp(11),mp(6.75),WI)

# Labels with room dims
label_room(p1x,p1y,mp(6.75),mp(5),"LIVING-COMEDOR",25,"6.75 × 5.00")
label_room(p1x,p1y+mp(5),mp(4.5),mp(3.5),"DORMITORIO 1",14,"4.50 × 3.50")
label_room(p1x+mp(4.5),p1y+mp(5),mp(2.25),mp(3.5),"COCINA",8,"2.25 × 3.50")
label_room(p1x,p1y+mp(8.5),mp(4.5),mp(2.5),"DORMITORIO 2",10,"4.50 × 2.50")
label_room(p1x+mp(4.5),p1y+mp(8.5),mp(2.25),mp(2.5),"BAÑO",5,"2.25 × 2.50")
label_room(p1x,p1y+mp(11),mp(6.75),mp(1),"BALCÓN",4,"6.75 × 1.00")

label_room(px_r,p1y,mp(6.75),mp(5),"LIVING-COMEDOR",25,"6.75 × 5.00")
label_room(p1x+mp(10.5),p1y+mp(5),mp(4.5),mp(3.5),"DORMITORIO 1",14,"4.50 × 3.50")
label_room(px_r,p1y+mp(5),mp(2.25),mp(3.5),"COCINA",8,"2.25 × 3.50")
label_room(p1x+mp(10.5),p1y+mp(8.5),mp(4.5),mp(2.5),"DORMITORIO 2",10,"4.50 × 2.50")
label_room(px_r,p1y+mp(8.5),mp(2.25),mp(2.5),"BAÑO",5,"2.25 × 2.50")
label_room(px_r,p1y+mp(11),mp(6.75),mp(1),"BALCÓN",4,"6.75 × 1.00")

d.text((p1x+mp(2.5),p1y-18),"DEPTO A",fill=RD,font=FR)
d.text((p1x+mp(11),p1y-18),"DEPTO B",fill=RD,font=FR)

# Pasillo
for i,ch in enumerate("PASILLO"):
    d.text((px_l+5,p1y+mp(0.5)+i*14),ch,fill=DG,font=FREF)

stair_sym(px_l+WI+3,p1y+mp(5)+WI+3,pw-WI*2-6,mp(3)-6)
elev_sym(px_l+WI+3,p1y+mp(9),mp(1.2),mp(1.4))

# Doors
door_v(px_l,p1y+mp(1.5),mp(0.8),"P5",False)
door_v(px_r,p1y+mp(1.5),mp(0.8),"P6",True)
door_h(p1x+mp(2),p1y+mp(5),mp(0.8),"P7",True)
door_v(p1x+mp(4.5),p1y+mp(5.8),mp(0.7),"P8",True)
door_v(p1x+mp(4.5),p1y+mp(9.2),mp(0.6),"P9",True)
door_h(p1x+mp(12),p1y+mp(5),mp(0.8),"P10",True)
door_v(p1x+mp(10.5),p1y+mp(5.8),mp(0.7),"P11",False)
door_v(p1x+mp(10.5),p1y+mp(9.2),mp(0.6),"P12",False)

# Windows
win_h(p1x+mp(2),p1y,mp(1.8),"V5 1.80×1.50")
win_h(p1x+mp(12),p1y,mp(1.8),"V6 1.80×1.50")
win_v(p1x,p1y+mp(6),mp(1.5),"V7")
win_v(p1x+BW,p1y+mp(6),mp(1.5),"V8")
# Kitchen windows
win_v(p1x+mp(6.75),p1y+mp(5.5),mp(1.0),"V11")  # cocina A
win_v(p1x+mp(8.25),p1y+mp(5.5),mp(1.0),"V12")  # cocina B
# Balcón openings
win_h(p1x+mp(1),p1y+mp(11),mp(1.5),"V13")
win_h(p1x+mp(12),p1y+mp(11),mp(1.5),"V14")

# ── CHAIN DIMENSIONING P1 ──
dim_chain_h(p1x, [0, mp(4.5), mp(6.75), mp(8.25), mp(10.5), mp(15)], p1y, True)
dim_h(p1x, p1x+BW, p1y-25, 15.00, True)
dim_chain_v(p1y, [0, mp(5), mp(8.5), mp(11), mp(12)], p1x, True)
dim_v(p1x-30, p1y, p1y+BH, 12.00, True)
dim_chain_v(p1y, [0, mp(5), mp(8.5), mp(11), mp(12)], p1x+BW, False)

# ── PLUMBING P1 ──
# Depto A
toilet(p1x+mp(5.5), p1y+mp(9.2))
sink(p1x+mp(5.5), p1y+mp(10.2))
shower(p1x+mp(6.2), p1y+mp(9.5))
kitchen_sink(p1x+mp(5.5), p1y+mp(6.5))

# Bajada sanitaria (vertical pipe)
pipe_node(p1x+mp(5.8), p1y+mp(8.5))
d.text((p1x+mp(5.8)+5,p1y+mp(8.5)-4),"BS",fill=BL,font=FREF)

# Depto B (mirror)
toilet(p1x+mp(9.5), p1y+mp(9.2))
sink(p1x+mp(9.5), p1y+mp(10.2))
shower(p1x+mp(8.8), p1y+mp(9.5))
kitchen_sink(p1x+mp(9.5), p1y+mp(6.5))

pipe_node(p1x+mp(9.2), p1y+mp(8.5))
d.text((p1x+mp(9.2)+5,p1y+mp(8.5)-4),"BS",fill=BL,font=FREF)

# Drain lines
drain_line(p1x+mp(5.5),p1y+mp(9.2)+10, p1x+mp(5.8),p1y+mp(8.5))
drain_line(p1x+mp(5.5),p1y+mp(6.5)+5, p1x+mp(5.8),p1y+mp(8.5))

drain_line(p1x+mp(9.5),p1y+mp(9.2)+10, p1x+mp(9.2),p1y+mp(8.5))
drain_line(p1x+mp(9.5),p1y+mp(6.5)+5, p1x+mp(9.2),p1y+mp(8.5))

# ── ELECTRICAL P1 ──
# Depto A
light_fixture(p1x+mp(3.3), p1y+mp(2.5))   # Living
light_fixture(p1x+mp(2.2), p1y+mp(6.5))   # Dorm1
light_fixture(p1x+mp(5.5), p1y+mp(5.5))   # Cocina
light_fixture(p1x+mp(2.2), p1y+mp(9.5))   # Dorm2
light_fixture(p1x+mp(5.5), p1y+mp(9.5)+15)   # Baño

# Depto B
light_fixture(p1x+mp(11.7), p1y+mp(2.5))
light_fixture(p1x+mp(12.8), p1y+mp(6.5))
light_fixture(p1x+mp(9.5), p1y+mp(5.5))
light_fixture(p1x+mp(12.8), p1y+mp(9.5))
light_fixture(p1x+mp(9.5), p1y+mp(9.5)+15)

# Outlets
for ox_ in [mp(1),mp(4),mp(5.5)]:
    outlet(p1x+ox_, p1y+mp(4.5))
for ox_ in [mp(10),mp(11),mp(14)]:
    outlet(p1x+ox_, p1y+mp(4.5))
outlet(p1x+mp(1), p1y+mp(6))
outlet(p1x+mp(14), p1y+mp(6))
outlet(p1x+mp(1), p1y+mp(9))
outlet(p1x+mp(14), p1y+mp(9))

# Switches
switch(p1x+mp(6.5), p1y+mp(1.8))  # A entry
switch(p1x+mp(8.5), p1y+mp(1.8))  # B entry

# Panel
elec_panel(px_l+pw//2, p1y+mp(4))

# ── Right panel refs ──
rpx = p1x+BW+80
d.text((rpx,p1y),"ABERTURAS PISO TIPO:",fill=BK,font=FR)
arefs = [
    "P5–P6  Pta. ingreso    0.90×2.10 h",
    "P7–P10 Pta. dorm.      0.80×2.10 h",
    "P8–P11 Pta. cocina     0.70×2.10 h",
    "P9–P12 Pta. baño       0.60×2.10 h",
    "V5–V6  Vent. living    1.80×1.50 h=0.80",
    "V7–V8  Vent. dorm.     1.50×1.20 h=1.00",
    "V11–12 Vent. cocina    1.00×0.60 h=1.40",
    "V13–14 Pta-vent balcón 1.50×2.10 h",
]
for i,t in enumerate(arefs):
    d.text((rpx,p1y+18+i*15),t,fill=DG,font=FREF)

d.text((rpx,p1y+18+len(arefs)*15+12),"INSTALACIÓN SANITARIA:",fill=BL,font=FR)
san_refs = [
    "WC = Inodoro",
    "Lv = Lavabo",
    "Du = Ducha (plato 0.80×0.80)",
    "Pil = Pileta cocina doble",
    "BS = Bajada sanitaria ø110",
    "--- = Desagüe ø50/63mm PVC",
    "Agua fría: PPFusión ø20mm",
    "Agua caliente: PPFusión ø20mm",
    "Ventilación: ø63mm a terraza",
]
for i,t in enumerate(san_refs):
    d.text((rpx,p1y+18+len(arefs)*15+30+i*14),t,fill=BL,font=FREF)

d.text((rpx,p1y+18+len(arefs)*15+30+len(san_refs)*14+12),"INSTALACIÓN ELÉCTRICA:",fill=GR,font=FR)
elec_refs = [
    "⊕ Boca de luz (techo)",
    "○ Tomacorriente 10A",
    "● Interruptor simple",
    "TE Tablero seccional",
    "Circuito 1: Iluminación 10A",
    "Circuito 2: Tomas 15A",
    "Circuito 3: Cocina 20A",
    "Circuito 4: Baño (GFCI) 15A",
    "Acometida: 3×6mm² + T 6mm²",
]
for i,t in enumerate(elec_refs):
    d.text((rpx,p1y+18+len(arefs)*15+30+len(san_refs)*14+30+i*14),t,fill=GR,font=FREF)


# ══════════════════════════════════════════════════════════════
# FLOOR 3: PISO 2 (TIPO) — 160 m²
# ══════════════════════════════════════════════════════════════
F3_Y = F2_Y + FLOOR_H
d.rectangle([40,F3_Y,1960,F3_Y+FLOOR_H],outline=LG,width=1)
d.text((60,F3_Y+10),"PISO 2 (TIPO) — N.P.T. +6.00 — 160 m²",fill=BK,font=FT)
d.line([(60,F3_Y+42),(350,F3_Y+42)],fill=RD,width=3)
level_marker(380, F3_Y+18, "NPT +6.00", "h=2.80m (piso a piso)")
d.text((60,F3_Y+50),"Distribución idéntica a Piso 1 — se repiten instalaciones sanitarias y eléctricas",fill=DG,font=FNOTE)

p2x, p2y = 160, F3_Y+80
p2_px_l = p2x+mp(6.75)
p2_px_r = p2x+mp(8.25)

# Axes
draw_axes(p2x, p2y, BW, BH,
    [0, mp(6.75), mp(8.25), mp(15)],
    [0, mp(5), mp(8.5), mp(11), mp(12)],
    ["A","B","C","D"],
    ["1","2","3","4","5"])

for cx_ in [0, mp(6.75), mp(8.25), mp(15)]:
    for cy_ in [0, mp(5), mp(8.5), mp(11), mp(12)]:
        struct_column(p2x+cx_, p2y+cy_)

# Fills (same as P1)
fill_r(p2x+WE,p2y+WE,mp(6.75)-WE,mp(5)-WE,(248,248,255))
fill_r(p2x+WE,p2y+mp(5),mp(4.5)-WE,mp(3.5),(255,250,242))
fill_r(p2x+mp(4.5),p2y+mp(5),mp(2.25),mp(3.5),(242,248,255))
fill_r(p2x+WE,p2y+mp(8.5),mp(4.5)-WE,mp(2.5),(255,250,242))
fill_r(p2x+mp(4.5),p2y+mp(8.5),mp(2.25),mp(2.5),(235,242,255))
fill_r(p2x+WE,p2y+mp(11),mp(6.75)-WE,mp(1)-WE,(240,255,242))

fill_r(p2_px_r,p2y+WE,mp(6.75)-WE,mp(5)-WE,(248,248,255))
fill_r(p2_px_r,p2y+mp(5),mp(2.25),mp(3.5),(242,248,255))
fill_r(p2x+mp(10.5),p2y+mp(5),mp(4.5)-WE,mp(3.5),(255,250,242))
fill_r(p2_px_r,p2y+mp(8.5),mp(2.25),mp(2.5),(235,242,255))
fill_r(p2x+mp(10.5),p2y+mp(8.5),mp(4.5)-WE,mp(2.5),(255,250,242))
fill_r(p2_px_r,p2y+mp(11),mp(6.75)-WE,mp(1)-WE,(240,255,242))
fill_r(p2_px_l,p2y+WE,pw,BH-WE*2,(245,242,232))

# Walls
outline(p2x,p2y,BW,BH,True)
wall_v(p2_px_l,p2y,BH,WI); wall_v(p2_px_r-WI,p2y,BH,WI)
wall_h(p2x,p2y+mp(5),mp(6.75),WI)
wall_v(p2x+mp(4.5),p2y+mp(5),mp(6),WI)
wall_h(p2x,p2y+mp(8.5),mp(6.75),WI)
wall_h(p2x,p2y+mp(11),mp(6.75),WI)
wall_h(p2_px_r,p2y+mp(5),mp(6.75),WI)
wall_v(p2x+mp(10.5)-WI,p2y+mp(5),mp(6),WI)
wall_h(p2_px_r,p2y+mp(8.5),mp(6.75),WI)
wall_h(p2_px_r,p2y+mp(11),mp(6.75),WI)

# Labels
label_room(p2x,p2y,mp(6.75),mp(5),"LIVING-COMEDOR",25,"6.75 × 5.00")
label_room(p2x,p2y+mp(5),mp(4.5),mp(3.5),"DORMITORIO 1",14,"4.50 × 3.50")
label_room(p2x+mp(4.5),p2y+mp(5),mp(2.25),mp(3.5),"COCINA",8,"2.25 × 3.50")
label_room(p2x,p2y+mp(8.5),mp(4.5),mp(2.5),"DORMITORIO 2",10,"4.50 × 2.50")
label_room(p2x+mp(4.5),p2y+mp(8.5),mp(2.25),mp(2.5),"BAÑO",5,"2.25 × 2.50")
label_room(p2x,p2y+mp(11),mp(6.75),mp(1),"BALCÓN",4,"6.75 × 1.00")
label_room(p2_px_r,p2y,mp(6.75),mp(5),"LIVING-COMEDOR",25,"6.75 × 5.00")
label_room(p2x+mp(10.5),p2y+mp(5),mp(4.5),mp(3.5),"DORMITORIO 1",14,"4.50 × 3.50")
label_room(p2_px_r,p2y+mp(5),mp(2.25),mp(3.5),"COCINA",8,"2.25 × 3.50")
label_room(p2x+mp(10.5),p2y+mp(8.5),mp(4.5),mp(2.5),"DORMITORIO 2",10,"4.50 × 2.50")
label_room(p2_px_r,p2y+mp(8.5),mp(2.25),mp(2.5),"BAÑO",5,"2.25 × 2.50")
label_room(p2_px_r,p2y+mp(11),mp(6.75),mp(1),"BALCÓN",4,"6.75 × 1.00")

d.text((p2x+mp(2.5),p2y-18),"DEPTO A",fill=RD,font=FR)
d.text((p2x+mp(11),p2y-18),"DEPTO B",fill=RD,font=FR)

for i,ch in enumerate("PASILLO"):
    d.text((p2_px_l+5,p2y+mp(0.5)+i*14),ch,fill=DG,font=FREF)

stair_sym(p2_px_l+WI+3,p2y+mp(5)+WI+3,pw-WI*2-6,mp(3)-6)
elev_sym(p2_px_l+WI+3,p2y+mp(9),mp(1.2),mp(1.4))

# Plumbing (same as P1)
toilet(p2x+mp(5.5), p2y+mp(9.2))
sink(p2x+mp(5.5), p2y+mp(10.2))
shower(p2x+mp(6.2), p2y+mp(9.5))
kitchen_sink(p2x+mp(5.5), p2y+mp(6.5))
pipe_node(p2x+mp(5.8), p2y+mp(8.5))
toilet(p2x+mp(9.5), p2y+mp(9.2))
sink(p2x+mp(9.5), p2y+mp(10.2))
shower(p2x+mp(8.8), p2y+mp(9.5))
kitchen_sink(p2x+mp(9.5), p2y+mp(6.5))
pipe_node(p2x+mp(9.2), p2y+mp(8.5))

# Electrical (same as P1)
light_fixture(p2x+mp(3.3), p2y+mp(2.5))
light_fixture(p2x+mp(2.2), p2y+mp(6.5))
light_fixture(p2x+mp(5.5), p2y+mp(5.5))
light_fixture(p2x+mp(2.2), p2y+mp(9.5))
light_fixture(p2x+mp(11.7), p2y+mp(2.5))
light_fixture(p2x+mp(12.8), p2y+mp(6.5))
light_fixture(p2x+mp(9.5), p2y+mp(5.5))
light_fixture(p2x+mp(12.8), p2y+mp(9.5))
elec_panel(p2_px_l+pw//2, p2y+mp(4))

# Dims
dim_chain_h(p2x, [0, mp(4.5), mp(6.75), mp(8.25), mp(10.5), mp(15)], p2y, True)
dim_h(p2x, p2x+BW, p2y-25, 15.00, True)
dim_chain_v(p2y, [0, mp(5), mp(8.5), mp(11), mp(12)], p2x, True)
dim_v(p2x-30, p2y, p2y+BH, 12.00, True)


# ══════════════════════════════════════════════════════════════
# FLOOR 4: TERRAZA — 160 m²
# ══════════════════════════════════════════════════════════════
F4_Y = F3_Y + FLOOR_H
d.rectangle([40,F4_Y,1960,F4_Y+FLOOR_H],outline=LG,width=1)
d.text((60,F4_Y+10),"TERRAZA ACCESIBLE — N.P.T. +8.80 — 160 m²",fill=BK,font=FT)
d.line([(60,F4_Y+42),(400,F4_Y+42)],fill=RD,width=3)
level_marker(420, F4_Y+18, "NPT +8.80", "h baranda=1.10m")

ttx, tty = 160, F4_Y+80

# Open space fill
fill_r(ttx+4,tty+4,BW-8,BH-8,(245,252,242))

# Sala máquinas
mq_w,mq_h = mp(4),mp(3)
fill_r(ttx+WI,tty+WI,mq_w-WI*2,mq_h-WI*2,(252,240,235))
outline(ttx,tty,mq_w,mq_h,False)

# Tanque
tq_x = ttx+mp(4)+10
tq_w,tq_h = mp(3),mp(2)
fill_r(tq_x+WI,tty+WI,tq_w-WI*2,tq_h-WI*2,(235,245,255))
outline(tq_x,tty,tq_w,tq_h,False)

# Railing (dashed)
for i in range(0,BW,14):
    x1_=ttx+i; x2_=min(ttx+i+9,ttx+BW)
    d.rectangle([x1_,tty,x2_,tty+3],fill=BK)
    d.rectangle([x1_,tty+BH-3,x2_,tty+BH],fill=BK)
for i in range(0,BH,14):
    y1_=tty+i; y2_=min(tty+i+9,tty+BH)
    d.rectangle([ttx,y1_,ttx+3,y2_],fill=BK)
    d.rectangle([ttx+BW-3,y1_,ttx+BW,y2_],fill=BK)

label_room(ttx,tty,mq_w,mq_h,"SALA MÁQUINAS",12,"4.00 × 3.00")
label_room(tq_x,tty,tq_w,tq_h,"TANQUE",6,"3.00 × 2.00")

cx_t = ttx+BW//2
cy_t = tty+BH//2+mp(1)
d.text((cx_t-70,cy_t-20),"ESPACIO COMÚN ABIERTO",fill=BK,font=FR)
d.text((cx_t-20,cy_t),"142 m²",fill=DG,font=FA)
d.text((cx_t-55,cy_t+16),"15.00 × 12.00 (bruto)",fill=RD,font=FDS)

stair_sym(ttx+mp(6.75)+WI+3,tty+mp(5)+3,pw-WI*2-6,mp(3)-6)
elev_sym(ttx+mp(6.75)+WI+3,tty+mp(9),mp(1.2),mp(1.4))

d.text((ttx,tty+BH+10),"— — — Baranda perimetral h=1.10m s/código edificación",fill=DG,font=FREF)

# Dims
dim_h(ttx,ttx+BW,tty,15.00,True)
dim_v(ttx,tty,tty+BH,12.00,True)
dim_h(ttx,ttx+mq_w,tty+mq_h,4.00,False)
dim_v(ttx+mq_w,tty,tty+mq_h,3.00,False)
dim_h(tq_x,tq_x+tq_w,tty+tq_h,3.00,False)
dim_v(tq_x+tq_w,tty,tty+tq_h,2.00,False)

# Plumbing on terrace
pipe_node(ttx+mp(2), tty+mp(1.5))
d.text((ttx+mp(2)+6,tty+mp(1.5)-4),"VC ø63",fill=BL,font=FREF)  # ventilación cañería
pipe_node(ttx+mp(5.8), tty+mp(1))
d.text((ttx+mp(5.8)+6,tty+mp(1)-4),"BS ø110",fill=BL,font=FREF)  # bajada sanitaria
pipe_node(ttx+mp(9.2), tty+mp(1))
d.text((ttx+mp(9.2)+6,tty+mp(1)-4),"BS ø110",fill=BL,font=FREF)

# Tanque connections
pipe_h(tq_x+mp(1.5), tq_x+mp(1.5)+mp(3), tty+mp(1))
d.text((tq_x+mp(3)+mp(1.5)+5,tty+mp(1)-5),"Alim. ø25",fill=BL,font=FREF)

# Electrical
light_fixture(ttx+mp(2), tty+mp(1.5)+20)  # sala maq
light_fixture(ttx+mp(7.5), tty+mp(6))       # espacio común
light_fixture(ttx+mp(7.5), tty+mp(9))       # espacio común 2
outlet(ttx+mp(1), tty+mp(2.5))
outlet(ttx+mp(7.5), tty+mp(11))

# ── Terraza refs ──
rpx = ttx+BW+80
d.text((rpx,tty),"INST. TERRAZA:",fill=BK,font=FR)
trefs = [
    "Sala máquinas:",
    "  - Bomba presurizadora",
    "  - Tablero ascensor",
    "  - Tablero bombas",
    "",
    "Tanque de agua:",
    "  - Cap. 2000 lts",
    "  - Alimentación ø25mm",
    "  - Flotante automático",
    "  - Bajada ø25mm a deptos",
    "",
    "Bajadas sanitarias:",
    "  - 2× BS ø110 PVC (A+B)",
    "  - Ventilación ø63 PVC",
    "",
    "Desagüe pluvial:",
    "  - 4 bocas ø100mm",
    "  - Pendiente 1% al centro",
    "",
    "Baranda:",
    "  - h=1.10m s/código",
    "  - Caño estructural ø2\"",
]
for i,t in enumerate(trefs):
    d.text((rpx,tty+18+i*14),t,fill=DG,font=FREF)


# ══════════════════════════════════════════════════════════════
# CORTE ESQUEMÁTICO
# ══════════════════════════════════════════════════════════════
CORTE_Y = F4_Y + FLOOR_H + 10
d.rectangle([40,CORTE_Y,1960,CORTE_Y+CORTE_H],outline=LG,width=1)
d.text((60,CORTE_Y+10),"CORTE ESQUEMÁTICO A-A — ALTURAS",fill=BK,font=FT)
d.line([(60,CORTE_Y+42),(350,CORTE_Y+42)],fill=RD,width=3)

# Section drawing
sx, sy = 200, CORTE_Y+70
floor_h_px = 100  # height per floor in section
total_floors = 4
section_w = mp(15)

# Ground
d.rectangle([sx-30, sy+floor_h_px*4, sx+section_w+30, sy+floor_h_px*4+15], fill=(200,190,170))
d.text((sx-60, sy+floor_h_px*4+2), "TERRENO", fill=DG, font=FREF)

# Draw each floor
floors_data = [
    ("TERRAZA", "+8.80", "2.60m libre", 0),
    ("PISO 2", "+6.00", "2.60m libre", 1),
    ("PISO 1", "+3.20", "2.60m libre", 2),
    ("PB", "±0.00", "3.00m libre", 3),
]

for name, npt, libre, idx in floors_data:
    fy = sy + idx * floor_h_px
    # Floor slab
    d.rectangle([sx, fy, sx+section_w, fy+8], fill=(180,180,180))
    d.rectangle([sx, fy, sx+section_w, fy+8], outline=BK, width=1)
    # Walls (left and right)
    d.rectangle([sx, fy+8, sx+WE, fy+floor_h_px], fill=BK)
    d.rectangle([sx+section_w-WE, fy+8, sx+section_w, fy+floor_h_px], fill=BK)
    # Center wall (core)
    d.rectangle([sx+mp(6.75), fy+8, sx+mp(6.75)+WI, fy+floor_h_px], fill=BK)
    d.rectangle([sx+mp(8.25)-WI, fy+8, sx+mp(8.25), fy+floor_h_px], fill=BK)

    # Level text
    d.text((sx-80, fy), f"NPT {npt}", fill=RD, font=FLEVEL)
    # Name
    d.text((sx+section_w+15, fy+floor_h_px//2-8), name, fill=BK, font=FR)

    # Height dimension
    if idx < 3:
        dim_v(sx+section_w+60, fy+8, fy+floor_h_px, float(libre.replace("m libre","")), False, FDS)
    else:
        dim_v(sx+section_w+60, fy+8, fy+floor_h_px, 3.00, False, FDS)

    # Free height label
    d.text((sx+section_w+85, fy+floor_h_px//2-5), libre, fill=DG, font=FREF)

# Total height
dim_v(sx+section_w+120, sy, sy+floor_h_px*4, 11.80, False)
d.text((sx+section_w+148, sy+floor_h_px*2-5), "TOTAL", fill=RD, font=FR)

# Foundation hint
d.rectangle([sx-5, sy+floor_h_px*4+8, sx+section_w+5, sy+floor_h_px*4+25], fill=(190,180,160))
d.text((sx+10, sy+floor_h_px*4+10), "CIMENTACIÓN (base + zapatas)", fill=DG, font=FREF)

# Terrace railing
d.rectangle([sx, sy-15, sx+3, sy], fill=BK)
d.rectangle([sx+section_w-3, sy-15, sx+section_w, sy], fill=BK)
d.line([(sx, sy-15), (sx+section_w, sy-15)], fill=BK, width=2)
d.text((sx+section_w//2-30, sy-28), "Baranda h=1.10", fill=DG, font=FREF)

# ── Heights table ──
ht_x = sx + section_w + 200
d.text((ht_x, CORTE_Y+70), "TABLA DE ALTURAS:", fill=BK, font=FR)
htrows = [
    ("NIVEL","NPT","H.LIBRE","H.LOSA","USO"),
    ("PB","±0.00","3.00m","0.20m","Comercial"),
    ("P1","+3.20","2.60m","0.20m","Vivienda"),
    ("P2","+6.00","2.60m","0.20m","Vivienda"),
    ("Terraza","+8.80","—","0.20m","Accesible"),
    ("Cumbrera","+11.80","","",""),
]
htcols = [80,70,70,70,80]
htrh = 22
for ri,row in enumerate(htrows):
    ry = CORTE_Y+90 + ri*htrh
    ft = FTBLB if ri==0 else FTBL
    if ri==0:
        d.rectangle([ht_x,ry,ht_x+sum(htcols),ry+htrh],fill=(35,35,35))
    cx_ = ht_x
    for ci,(cell,cw) in enumerate(zip(row,htcols)):
        d.rectangle([cx_,ry,cx_+cw,ry+htrh],outline=GY,width=1)
        clr = W_ if ri==0 else BK
        d.text((cx_+4,ry+4),cell,fill=clr,font=ft)
        cx_+=cw


# ══════════════════════════════════════════════════════════════
# SUMMARY TABLES
# ══════════════════════════════════════════════════════════════
TBL_Y = CORTE_Y + CORTE_H + 10
d.line([(40,TBL_Y),(1960,TBL_Y)],fill=BK,width=3)

# ── Surface summary ──
d.text((60,TBL_Y+10),"RESUMEN GENERAL DE SUPERFICIES",fill=BK,font=FT)
d.line([(60,TBL_Y+42),(380,TBL_Y+42)],fill=RD,width=3)

ty_ = TBL_Y+55
cols = [200,100,120,420]
srows = [
    ("NIVEL","SUP.(m²)","NPT","PROGRAMA"),
    ("Planta Baja","180","±0.00","Hall 15 + Local1 45 + Local2 45 + Cochera 30 + Patio 28 + Core 17"),
    ("Piso 1 (Tipo)","160","+3.20","Depto A: Liv 25+Dorm1 14+Coc 8+Dorm2 10+Baño 5+Balc 4 = 66 | Depto B: ídem | Pasillo 28"),
    ("Piso 2 (Tipo)","160","+6.00","Depto A: Liv 25+Dorm1 14+Coc 8+Dorm2 10+Baño 5+Balc 4 = 66 | Depto B: ídem | Pasillo 28"),
    ("Terraza","160","+8.80","Sala Máq. 12 + Tanque 6 + Espacio Común 142"),
    ("TOTAL","660","","4 niveles — 3 pisos habitables + terraza accesible"),
]
rh_ = 26
for ri,row in enumerate(srows):
    ry=ty_+ri*rh_
    ft=FTBLB if ri==0 or ri==5 else FTBL
    if ri==0: d.rectangle([60,ry,60+sum(cols),ry+rh_],fill=(35,35,35))
    if ri==5:
        d.rectangle([60,ry,60+sum(cols),ry+rh_],fill=(240,240,240))
        d.line([(60,ry),(60+sum(cols),ry)],fill=BK,width=2)
    cx_=60
    for ci,(cell,cw) in enumerate(zip(row,cols)):
        d.rectangle([cx_,ry,cx_+cw,ry+rh_],outline=GY,width=1)
        clr = W_ if ri==0 else (RD if ri==5 and ci==1 else BK)
        d.text((cx_+6,ry+5),cell,fill=clr,font=ft)
        cx_+=cw

# ── Aberturas table ──
abr_y = ty_ + len(srows)*rh_ + 30
d.text((60,abr_y),"PLANILLA DE ABERTURAS COMPLETA",fill=BK,font=FT2)
abr_y += 30

acols = [70,90,120,100,200,160]
arows = [
    ("REF","TIPO","MEDIDA (m)","ANTEPECHO","UBICACIÓN","MATERIAL"),
    ("P1","Puerta","0.90 × 2.10","—","Hall entrada PB","Vidrio templado"),
    ("P2","Puerta","1.20 × 2.10","—","Local 1 PB","Vidrio templado"),
    ("P3","Puerta","1.20 × 2.10","—","Local 2 PB","Vidrio templado"),
    ("P4","Puerta","0.90 × 2.10","—","Cochera PB","Chapa reforzada"),
    ("P5–P6","Puerta","0.90 × 2.10","—","Ingreso Dptos","Madera 45mm"),
    ("P7–P10","Puerta","0.80 × 2.10","—","Dormitorios","Placa 36mm"),
    ("P8–P11","Puerta","0.70 × 2.10","—","Cocinas","Placa 36mm"),
    ("P9–P12","Puerta","0.60 × 2.10","—","Baños","Placa 36mm"),
    ("V1–V2","Ventana","1.50 × 1.20","h=1.00","Frente locales","Aluminio A30"),
    ("V3–V4","Ventana","1.50 × 1.20","h=1.00","Laterales locales","Aluminio A30"),
    ("V5–V6","Ventana","1.80 × 1.50","h=0.80","Living pisos tipo","Aluminio A30"),
    ("V7–V8","Ventana","1.50 × 1.20","h=1.00","Dorm pisos tipo","Aluminio A30"),
    ("V9–V10","Ventana","1.50 × 1.20","h=1.60","Cochera/Patio","Aluminio A30"),
    ("V11–V12","Ventana","1.00 × 0.60","h=1.40","Cocinas tipo","Aluminio A30"),
    ("V13–V14","Pta-vent","1.50 × 2.10","h=0.00","Balcones tipo","Aluminio A30 DVH"),
]
arh_ = 22
for ri,row in enumerate(arows):
    ry=abr_y+ri*arh_
    ft=FTBLB if ri==0 else FTBL
    if ri==0: d.rectangle([60,ry,60+sum(acols),ry+arh_],fill=(35,35,35))
    cx_=60
    for ci,(cell,cw) in enumerate(zip(row,acols)):
        d.rectangle([cx_,ry,cx_+cw,ry+arh_],outline=GY,width=1)
        clr = W_ if ri==0 else BK
        d.text((cx_+4,ry+4),cell,fill=clr,font=ft)
        cx_+=cw

# ── Legend completa ──
leg_y = abr_y + len(arows)*arh_ + 25
d.text((60,leg_y),"REFERENCIAS GENERALES",fill=BK,font=FT2)
leg_y += 28

# Three columns of references
col1x, col2x, col3x = 60, 380, 700

# Architectural
d.text((col1x,leg_y),"ARQUITECTÓNICAS:",fill=BK,font=FR)
arch_refs = [
    ("████ negro","Muro ext. e=0.20m H°A°"),
    ("███ negro","Muro int. e=0.10m ladrillo"),
    ("■ negro","Columna estructural 0.20×0.20"),
    ("— — —","Baranda perimetral h=1.10"),
    ("╳","Hueco ascensor"),
    ("▲","Escalera (dir. subida)"),
    ("━━ rojo","Líneas de cota (metros)"),
    ("- - cyan","Ejes estructurales"),
]
for i,(sym,desc) in enumerate(arch_refs):
    d.text((col1x,leg_y+18+i*16),sym,fill=BK,font=FREF)
    d.text((col1x+100,leg_y+18+i*16),desc,fill=DG,font=FREF)

# Sanitary
d.text((col2x,leg_y),"SANITARIAS (azul):",fill=BL,font=FR)
san_refs2 = [
    ("WC","Inodoro c/mochila"),
    ("Lv","Lavamanos"),
    ("Du","Ducha (plato 0.80×0.80)"),
    ("Pil","Pileta cocina doble"),
    ("BS","Bajada sanitaria ø110mm"),
    ("VC","Ventilación cañería ø63mm"),
    ("BD","Boca desagüe pluvial"),
    ("---","Desagüe ø50-63mm PVC"),
]
for i,(sym,desc) in enumerate(san_refs2):
    d.text((col2x,leg_y+18+i*16),sym,fill=BL,font=FREF)
    d.text((col2x+40,leg_y+18+i*16),desc,fill=BL,font=FREF)

# Electrical
d.text((col3x,leg_y),"ELÉCTRICAS (verde):",fill=GR,font=FR)
elec_refs2 = [
    ("⊕","Boca de luz (techo)"),
    ("○","Tomacorriente 10/15A"),
    ("●","Interruptor simple"),
    ("TE","Tablero eléctrico"),
    ("","Circ.1: Iluminación 10A"),
    ("","Circ.2: Tomacorrientes 15A"),
    ("","Circ.3: Cocina 20A"),
    ("","Circ.4: Baño GFCI 15A"),
]
for i,(sym,desc) in enumerate(elec_refs2):
    d.text((col3x,leg_y+18+i*16),sym,fill=GR,font=FREF)
    d.text((col3x+30,leg_y+18+i*16),desc,fill=GR,font=FREF)


# ── Title block final ──
tb_y = leg_y + 165
d.line([(40,tb_y),(1960,tb_y)],fill=BK,width=3)
d.rectangle([40,tb_y,1960,tb_y+90],fill=(245,245,245))
d.rectangle([40,tb_y,1960,tb_y+90],outline=BK,width=2)

# Columns in title block
d.line([(500,tb_y),(500,tb_y+90)],fill=BK,width=1)
d.line([(1200,tb_y),(1200,tb_y+90)],fill=BK,width=1)

d.text((60,tb_y+8),"PROYECTO:",fill=DG,font=FREF)
d.text((60,tb_y+22),"EDIFICIO RESIDENCIAL 3P+T",fill=BK,font=FT2)
d.text((60,tb_y+48),"SUP. TOTAL: 660 m²",fill=RD,font=FR)
d.text((60,tb_y+66),"LOTE: 15.00 × 12.00 m",fill=DG,font=FREF)

d.text((520,tb_y+8),"PLANO:",fill=DG,font=FREF)
d.text((520,tb_y+22),"PLANTAS GENERALES + INSTALACIONES",fill=BK,font=FR)
d.text((520,tb_y+40),"ESCALA: 1:100",fill=BK,font=FR)
d.text((520,tb_y+58),"HOJA: 1/1",fill=DG,font=FREF)
d.text((520,tb_y+72),"FECHA: ABRIL 2026",fill=DG,font=FREF)

d.text((1220,tb_y+8),"CONTENIDO:",fill=DG,font=FREF)
d.text((1220,tb_y+22),"Planta Baja + Piso 1 + Piso 2 + Terraza",fill=BK,font=FREF)
d.text((1220,tb_y+36),"Corte esquemático + Tabla alturas",fill=BK,font=FREF)
d.text((1220,tb_y+50),"Inst. sanitarias + Inst. eléctricas",fill=BK,font=FREF)
d.text((1220,tb_y+64),"Planilla aberturas + Referencias",fill=BK,font=FREF)
d.text((1220,tb_y+78),"Generado con Claude Code",fill=GY,font=FREF)

d.line([(40,tb_y+90),(1960,tb_y+90)],fill=BK,width=3)


# ── Crop & save ──
final_h = tb_y + 100
img_f = img.crop((0,0,W,final_h))

out = "/Users/carlossanchez/Downloads/presupuestador-backend/edificio_residencial_plano.png"
img_f.save(out,"PNG",dpi=(150,150))
print(f"OK → {out}")
print(f"Tamaño: {img_f.size[0]}×{img_f.size[1]}px")
