#!/usr/bin/env python3
"""
Technical Lineature v3 — Edificio Residencial 3P+T
Compact layout: 4 floors in 2x2 grid + tables below
Final output: 2000x1500px target (or slightly taller for tables)
"""
from PIL import Image, ImageDraw, ImageFont
import os

FONTS_DIR = "/Users/carlossanchez/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/e09fb916-12e4-41ff-8ae4-db2feebaefca/79f14b77-b8e8-4bfc-8ce4-43aff6c6e981/skills/canvas-design/canvas-fonts"

def lf(name, size):
    try: return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)
    except: return ImageFont.load_default()

f_header = lf("BigShoulders-Bold.ttf", 40)
f_title = lf("BigShoulders-Bold.ttf", 24)
f_room = lf("InstrumentSans-Bold.ttf", 12)
f_area = lf("DMMono-Regular.ttf", 10)
f_dim = lf("DMMono-Regular.ttf", 9)
f_ref = lf("DMMono-Regular.ttf", 9)
f_note = lf("InstrumentSans-Regular.ttf", 10)
f_tbl = lf("DMMono-Regular.ttf", 11)
f_tbl_b = lf("GeistMono-Bold.ttf", 11)
f_title2 = lf("BigShoulders-Bold.ttf", 20)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (185,30,30)
GRAY = (160,160,160)
DGRAY = (100,100,100)

S = 28  # 1m = 28px
WE = 6
WI = 3

def m(v): return int(v*S)

W, H = 2000, 2800
img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)

# ── Helpers ────────────────────────────────────────────
def wh(x,y,l,t=WE): d.rectangle([x,y,x+l,y+t], fill=BLACK)
def wv(x,y,l,t=WE): d.rectangle([x,y,x+t,y+l], fill=BLACK)
def fr(x,y,w,h,c): d.rectangle([x+1,y+1,x+w-1,y+h-1], fill=c)
def ro(x,y,w,h,ext=True):
    t=WE if ext else WI
    wh(x,y,w,t); wh(x,y+h-t,w,t); wv(x,y,h,t); wv(x+w-t,y,h,t)

def lr(x,y,w,h,name,area,small=False):
    cx,cy=x+w//2,y+h//2
    fn = f_room
    bb=d.textbbox((0,0),name,font=fn); tw=bb[2]-bb[0]
    # Truncate if too wide
    if tw > w - 6:
        fn = f_ref
        bb=d.textbbox((0,0),name,font=fn); tw=bb[2]-bb[0]
    d.text((cx-tw//2,cy-12),name,fill=BLACK,font=fn)
    if area:
        at=f"{area} m²"
        bb2=d.textbbox((0,0),at,font=f_area); tw2=bb2[2]-bb2[0]
        d.text((cx-tw2//2,cy+1),at,fill=DGRAY,font=f_area)

def dh(x1,x2,y,val,above=True):
    off=-20 if above else 20
    ly=y+off
    d.line([(x1,y),(x1,ly)],fill=RED,width=1)
    d.line([(x2,y),(x2,ly)],fill=RED,width=1)
    d.line([(x1+2,ly),(x2-2,ly)],fill=RED,width=1)
    for ax in[x1,x2]: d.line([(ax,ly-3),(ax,ly+3)],fill=RED,width=2)
    txt=f"{val:.2f}"
    bb=d.textbbox((0,0),txt,font=f_dim);tw=bb[2]-bb[0];th=bb[3]-bb[1]
    tx=(x1+x2)//2-tw//2
    ty=ly-th-2 if above else ly+2
    d.rectangle([tx-2,ty-1,tx+tw+2,ty+th+1],fill=WHITE)
    d.text((tx,ty),txt,fill=RED,font=f_dim)

def dv(x,y1,y2,val,left=True):
    off=-24 if left else 24
    lx=x+off
    d.line([(x,y1),(lx,y1)],fill=RED,width=1)
    d.line([(x,y2),(lx,y2)],fill=RED,width=1)
    d.line([(lx,y1+2),(lx,y2-2)],fill=RED,width=1)
    for ay in[y1,y2]: d.line([(lx-3,ay),(lx+3,ay)],fill=RED,width=2)
    txt=f"{val:.2f}"
    bb=d.textbbox((0,0),txt,font=f_dim);tw=bb[2]-bb[0];th=bb[3]-bb[1]
    ty=(y1+y2)//2-th//2
    tx=lx-tw-3 if left else lx+3
    d.rectangle([tx-2,ty-1,tx+tw+2,ty+th+1],fill=WHITE)
    d.text((tx,ty),txt,fill=RED,font=f_dim)

def door_h(x,y,wpx,label,down=True):
    d.rectangle([x-1,y-WI,x+wpx+1,y+WI],fill=WHITE)
    if down:
        d.arc([x,y,x+wpx,y+wpx],180,270,fill=BLACK,width=1)
        d.line([(x,y),(x,y+wpx)],fill=BLACK,width=1)
    else:
        d.arc([x,y-wpx,x+wpx,y],90,180,fill=BLACK,width=1)
        d.line([(x+wpx,y),(x+wpx,y-wpx)],fill=BLACK,width=1)
    bb=d.textbbox((0,0),label,font=f_ref);tw=bb[2]-bb[0]
    d.text((x+wpx//2-tw//2,y-WI-11),label,fill=DGRAY,font=f_ref)

def door_v(x,y,wpx,label,right=True):
    d.rectangle([x-WI,y-1,x+WI,y+wpx+1],fill=WHITE)
    if right:
        d.arc([x,y,x+wpx,y+wpx],270,360,fill=BLACK,width=1)
        d.line([(x,y),(x+wpx,y)],fill=BLACK,width=1)
    else:
        d.arc([x-wpx,y,x,y+wpx],0,90,fill=BLACK,width=1)
        d.line([(x,y+wpx),(x-wpx,y+wpx)],fill=BLACK,width=1)
    d.text((x+6,y+wpx//2-4),label,fill=DGRAY,font=f_ref)

def win_h(x,y,wpx,label):
    d.rectangle([x,y-WE//2-1,x+wpx,y+WE//2+1],fill=WHITE)
    d.line([(x,y-2),(x+wpx,y-2)],fill=BLACK,width=2)
    d.line([(x,y+2),(x+wpx,y+2)],fill=BLACK,width=2)
    d.line([(x+wpx//2,y-4),(x+wpx//2,y+4)],fill=BLACK,width=1)
    bb=d.textbbox((0,0),label,font=f_ref);tw=bb[2]-bb[0]
    d.text((x+wpx//2-tw//2,y+WE//2+3),label,fill=DGRAY,font=f_ref)

def win_v(x,y,wpx,label):
    d.rectangle([x-WE//2-1,y,x+WE//2+1,y+wpx],fill=WHITE)
    d.line([(x-2,y),(x-2,y+wpx)],fill=BLACK,width=2)
    d.line([(x+2,y),(x+2,y+wpx)],fill=BLACK,width=2)
    d.line([(x-4,y+wpx//2),(x+4,y+wpx//2)],fill=BLACK,width=1)
    d.text((x+WE//2+3,y+wpx//2-4),label,fill=DGRAY,font=f_ref)

def stair(x,y,w,h):
    n=10
    th_=h//n
    for i in range(n):
        d.line([(x,y+i*th_),(x+w,y+i*th_)],fill=BLACK,width=1)
    d.rectangle([x,y,x+w,y+h],outline=BLACK,width=1)
    mx=x+w//2
    d.line([(mx,y+h-3),(mx,y+8)],fill=BLACK,width=1)
    d.polygon([(mx,y+4),(mx-4,y+12),(mx+4,y+12)],fill=BLACK)

def elev(x,y,w,h):
    d.rectangle([x,y,x+w,y+h],outline=BLACK,width=2)
    d.line([(x,y),(x+w,y+h)],fill=BLACK,width=1)
    d.line([(x+w,y),(x,y+h)],fill=BLACK,width=1)

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
d.rectangle([0,0,W,65],fill=(248,248,248))
d.line([(0,65),(W,65)],fill=BLACK,width=3)
d.text((60,14),"EDIFICIO RESIDENCIAL — PLANO GENERAL DE PLANTAS",fill=BLACK,font=f_header)
# North arrow
nx,ny=1940,35
d.polygon([(nx,ny-20),(nx-7,ny+5),(nx+7,ny+5)],outline=BLACK,width=2)
d.polygon([(nx,ny-20),(nx-7,ny+5),(nx,ny-3)],fill=BLACK)
d.text((nx-3,ny+8),"N",fill=BLACK,font=f_room)
d.text((60,52),"3P+T | 660 m² | ESC 1:100 | ABR 2026",fill=DGRAY,font=f_note)

# ══════════════════════════════════════════════════════════════
# 2x2 GRID LAYOUT
# Left column: PB + Terraza
# Right column: P1 + P2
# ══════════════════════════════════════════════════════════════

COL1_X = 60   # left column start
COL2_X = 1020 # right column start
ROW1_Y = 85   # first row
ROW2_Y = 600  # second row

BW = m(15)  # 420
BH = m(12)  # 336

# ──────────────────────────────────────────────────────────────
# PLANTA BAJA (top-left)
# ──────────────────────────────────────────────────────────────
d.text((COL1_X, ROW1_Y), "PLANTA BAJA — 180 m²", fill=BLACK, font=f_title)
d.line([(COL1_X, ROW1_Y+26), (COL1_X+200, ROW1_Y+26)], fill=RED, width=2)

ox, oy = COL1_X+50, ROW1_Y+55

# Fills
fr(ox+WE, oy+WE, m(6)-WE, m(7.5)-WE, (255,252,242))  # Local 1
fr(ox+m(6), oy+WE, m(3), m(5)-WE, (245,245,255))  # Hall
fr(ox+m(9), oy+WE, m(6)-WE, m(7.5)-WE, (255,252,242))  # Local 2
fr(ox+WE, oy+m(7.5), m(6)-WE, m(4.5)-WE, (242,242,242))  # Cochera
fr(ox+m(6), oy+m(5), m(3), m(7)-WE, (248,245,238))  # Core
fr(ox+m(9), oy+m(7.5), m(6)-WE, m(4.5)-WE, (245,252,245))  # Patio

# Walls
ro(ox,oy,BW,BH,True)
wv(ox+m(6),oy,m(5),WI)
wv(ox+m(9)-WI,oy,m(5),WI)
wh(ox,oy+m(7.5),m(6),WI)
wh(ox+m(9),oy+m(7.5),m(6),WI)
wh(ox+m(6),oy+m(5),m(3),WI)
wv(ox+m(6),oy+m(5),m(7),WI)
wv(ox+m(9)-WI,oy+m(5),m(7),WI)

# Labels
lr(ox,oy,m(6),m(7.5),"LOCAL 1",45)
lr(ox+m(6),oy,m(3),m(5),"HALL",15)
lr(ox+m(9),oy,m(6),m(7.5),"LOCAL 2",45)
lr(ox,oy+m(7.5),m(6),m(4.5),"COCHERA",30)
lr(ox+m(9),oy+m(7.5),m(6),m(4.5),"PATIO SERV.",28)

# Stair/Elev
stair(ox+m(6)+WI+4, oy+m(5)+WI+4, m(2.4)-8, m(2.8)-8)
elev(ox+m(6.8), oy+m(8.8), m(1.3), m(1.5))

# Doors
door_h(ox+m(7),oy,m(0.9),"P1",True)
door_h(ox+m(2),oy,m(1.0),"P2",True)
door_h(ox+m(11),oy,m(1.0),"P3",True)
door_h(ox+m(2.5),oy+m(7.5),m(0.9),"P4",False)

# Windows
win_h(ox+m(3.5),oy,m(1.2),"V1")
win_h(ox+m(12),oy,m(1.2),"V2")
win_v(ox,oy+m(3),m(1.2),"V3")
win_v(ox+BW,oy+m(3),m(1.2),"V4")

# Dims
dh(ox,ox+BW,oy,15.00,True)
dv(ox,oy,oy+BH,12.00,True)
dh(ox,ox+m(6),oy+BH,6.00,False)
dh(ox+m(6),ox+m(9),oy+BH,3.00,False)
dh(ox+m(9),ox+BW,oy+BH,6.00,False)
dv(ox+BW,oy,oy+m(5),5.00,False)
dv(ox+BW,oy+m(5),oy+m(7.5),2.50,False)
dv(ox+BW,oy+m(7.5),oy+BH,4.50,False)


# ──────────────────────────────────────────────────────────────
# PISO 1 TIPO (top-right)
# ──────────────────────────────────────────────────────────────
d.text((COL2_X, ROW1_Y), "PISO 1 (TIPO) — 160 m²", fill=BLACK, font=f_title)
d.line([(COL2_X, ROW1_Y+26), (COL2_X+200, ROW1_Y+26)], fill=RED, width=2)

p1x, p1y = COL2_X+50, ROW1_Y+55
px_l = p1x+m(6.75)
px_r = p1x+m(8.25)
pw = m(1.5)

# Fills
fr(p1x+WE,p1y+WE,m(6.75)-WE,m(5)-WE,(250,250,255))  # Living A
fr(p1x+WE,p1y+m(5),m(4.5)-WE,m(3.5),(255,250,245))  # Dorm A
fr(p1x+m(4.5),p1y+m(5),m(2.25),m(3.5),(245,250,255))  # Cocina A
fr(p1x+WE,p1y+m(8.5),m(4.5)-WE,m(2.5),(255,250,245))  # Dorm2 A
fr(p1x+m(4.5),p1y+m(8.5),m(2.25),m(2.5),(238,245,255))  # Baño A
fr(p1x+WE,p1y+m(11),m(6.75)-WE,m(1)-WE,(242,255,245))  # Balcón A

fr(px_r,p1y+WE,m(6.75)-WE,m(5)-WE,(250,250,255))  # Living B
fr(px_r,p1y+m(5),m(2.25),m(3.5),(245,250,255))  # Cocina B
fr(p1x+m(10.5),p1y+m(5),m(4.5)-WE,m(3.5),(255,250,245))  # Dorm B
fr(px_r,p1y+m(8.5),m(2.25),m(2.5),(238,245,255))  # Baño B
fr(p1x+m(10.5),p1y+m(8.5),m(4.5)-WE,m(2.5),(255,250,245))  # Dorm2 B
fr(px_r,p1y+m(11),m(6.75)-WE,m(1)-WE,(242,255,245))  # Balcón B

fr(px_l,p1y+WE,pw,BH-WE*2,(245,242,235))  # Pasillo

# Walls
ro(p1x,p1y,BW,BH,True)
wv(px_l,p1y,BH,WI); wv(px_r-WI,p1y,BH,WI)
wh(p1x,p1y+m(5),m(6.75),WI)
wv(p1x+m(4.5),p1y+m(5),m(6),WI)
wh(p1x,p1y+m(8.5),m(6.75),WI)
wh(p1x,p1y+m(11),m(6.75),WI)
wh(px_r,p1y+m(5),m(6.75),WI)
wv(p1x+m(10.5)-WI,p1y+m(5),m(6),WI)
wh(px_r,p1y+m(8.5),m(6.75),WI)
wh(px_r,p1y+m(11),m(6.75),WI)

# Labels
lr(p1x,p1y,m(6.75),m(5),"LIVING-COMEDOR",25)
lr(p1x,p1y+m(5),m(4.5),m(3.5),"DORMITORIO 1",14)
lr(p1x+m(4.5),p1y+m(5),m(2.25),m(3.5),"COCINA",8)
lr(p1x,p1y+m(8.5),m(4.5),m(2.5),"DORMITORIO 2",10)
lr(p1x+m(4.5),p1y+m(8.5),m(2.25),m(2.5),"BAÑO",5)
lr(p1x,p1y+m(11),m(6.75),m(1),"BALCÓN",4)

lr(px_r,p1y,m(6.75),m(5),"LIVING-COMEDOR",25)
lr(p1x+m(10.5),p1y+m(5),m(4.5),m(3.5),"DORMITORIO 1",14)
lr(px_r,p1y+m(5),m(2.25),m(3.5),"COCINA",8)
lr(p1x+m(10.5),p1y+m(8.5),m(4.5),m(2.5),"DORMITORIO 2",10)
lr(px_r,p1y+m(8.5),m(2.25),m(2.5),"BAÑO",5)
lr(px_r,p1y+m(11),m(6.75),m(1),"BALCÓN",4)

d.text((p1x+m(2),p1y-16),"DEPTO A",fill=RED,font=f_room)
d.text((p1x+m(11),p1y-16),"DEPTO B",fill=RED,font=f_room)

# Pasillo vertical text
for i,ch in enumerate("PASILLO"):
    d.text((px_l+4,p1y+m(0.8)+i*14),ch,fill=DGRAY,font=f_ref)

stair(px_l+WI+3,p1y+m(5)+WI+3,pw-WI*2-6,m(2.8)-6)
elev(px_l+WI+3,p1y+m(8.8),m(1.1),m(1.3))

# Doors
door_v(px_l,p1y+m(1.5),m(0.8),"P5",False)
door_v(px_r,p1y+m(1.5),m(0.8),"P6",True)
door_h(p1x+m(2),p1y+m(5),m(0.7),"P7",True)
door_v(p1x+m(4.5),p1y+m(5.8),m(0.6),"P8",True)
door_v(p1x+m(4.5),p1y+m(9),m(0.6),"P9",True)
door_h(p1x+m(12),p1y+m(5),m(0.7),"P10",True)
door_v(p1x+m(10.5),p1y+m(5.8),m(0.6),"P11",False)
door_v(p1x+m(10.5),p1y+m(9),m(0.6),"P12",False)

# Windows
win_h(p1x+m(2),p1y,m(1.5),"V5")
win_h(p1x+m(12),p1y,m(1.5),"V6")
win_v(p1x,p1y+m(6.5),m(1.2),"V7")
win_v(p1x+BW,p1y+m(6.5),m(1.2),"V8")

# Dims
dh(p1x,p1x+BW,p1y,15.00,True)
dv(p1x,p1y,p1y+BH,12.00,True)
dh(p1x,px_l,p1y+BH,6.75,False)
dh(px_l,px_r,p1y+BH,1.50,False)
dh(px_r,p1x+BW,p1y+BH,6.75,False)
dv(p1x+BW,p1y,p1y+m(5),5.00,False)
dv(p1x+BW,p1y+m(5),p1y+m(8.5),3.50,False)
dv(p1x+BW,p1y+m(8.5),p1y+m(11),2.50,False)
dv(p1x+BW,p1y+m(11),p1y+BH,1.00,False)


# ──────────────────────────────────────────────────────────────
# PISO 2 TIPO (bottom-left)
# ──────────────────────────────────────────────────────────────
d.text((COL1_X, ROW2_Y), "PISO 2 (TIPO) — 160 m²", fill=BLACK, font=f_title)
d.text((COL1_X+230, ROW2_Y+4), "idéntico a Piso 1", fill=DGRAY, font=f_note)
d.line([(COL1_X, ROW2_Y+26), (COL1_X+200, ROW2_Y+26)], fill=RED, width=2)

p2x, p2y = COL1_X+50, ROW2_Y+55
p2_px_l = p2x+m(6.75)
p2_px_r = p2x+m(8.25)

# Same fills
fr(p2x+WE,p2y+WE,m(6.75)-WE,m(5)-WE,(250,250,255))
fr(p2x+WE,p2y+m(5),m(4.5)-WE,m(3.5),(255,250,245))
fr(p2x+m(4.5),p2y+m(5),m(2.25),m(3.5),(245,250,255))
fr(p2x+WE,p2y+m(8.5),m(4.5)-WE,m(2.5),(255,250,245))
fr(p2x+m(4.5),p2y+m(8.5),m(2.25),m(2.5),(238,245,255))
fr(p2x+WE,p2y+m(11),m(6.75)-WE,m(1)-WE,(242,255,245))
fr(p2_px_r,p2y+WE,m(6.75)-WE,m(5)-WE,(250,250,255))
fr(p2_px_r,p2y+m(5),m(2.25),m(3.5),(245,250,255))
fr(p2x+m(10.5),p2y+m(5),m(4.5)-WE,m(3.5),(255,250,245))
fr(p2_px_r,p2y+m(8.5),m(2.25),m(2.5),(238,245,255))
fr(p2x+m(10.5),p2y+m(8.5),m(4.5)-WE,m(2.5),(255,250,245))
fr(p2_px_r,p2y+m(11),m(6.75)-WE,m(1)-WE,(242,255,245))
fr(p2_px_l,p2y+WE,pw,BH-WE*2,(245,242,235))

ro(p2x,p2y,BW,BH,True)
wv(p2_px_l,p2y,BH,WI); wv(p2_px_r-WI,p2y,BH,WI)
wh(p2x,p2y+m(5),m(6.75),WI)
wv(p2x+m(4.5),p2y+m(5),m(6),WI)
wh(p2x,p2y+m(8.5),m(6.75),WI)
wh(p2x,p2y+m(11),m(6.75),WI)
wh(p2_px_r,p2y+m(5),m(6.75),WI)
wv(p2x+m(10.5)-WI,p2y+m(5),m(6),WI)
wh(p2_px_r,p2y+m(8.5),m(6.75),WI)
wh(p2_px_r,p2y+m(11),m(6.75),WI)

lr(p2x,p2y,m(6.75),m(5),"LIVING-COMEDOR",25)
lr(p2x,p2y+m(5),m(4.5),m(3.5),"DORMITORIO 1",14)
lr(p2x+m(4.5),p2y+m(5),m(2.25),m(3.5),"COCINA",8)
lr(p2x,p2y+m(8.5),m(4.5),m(2.5),"DORMITORIO 2",10)
lr(p2x+m(4.5),p2y+m(8.5),m(2.25),m(2.5),"BAÑO",5)
lr(p2x,p2y+m(11),m(6.75),m(1),"BALCÓN",4)
lr(p2_px_r,p2y,m(6.75),m(5),"LIVING-COMEDOR",25)
lr(p2x+m(10.5),p2y+m(5),m(4.5),m(3.5),"DORMITORIO 1",14)
lr(p2_px_r,p2y+m(5),m(2.25),m(3.5),"COCINA",8)
lr(p2x+m(10.5),p2y+m(8.5),m(4.5),m(2.5),"DORMITORIO 2",10)
lr(p2_px_r,p2y+m(8.5),m(2.25),m(2.5),"BAÑO",5)
lr(p2_px_r,p2y+m(11),m(6.75),m(1),"BALCÓN",4)

d.text((p2x+m(2),p2y-16),"DEPTO A",fill=RED,font=f_room)
d.text((p2x+m(11),p2y-16),"DEPTO B",fill=RED,font=f_room)
for i,ch in enumerate("PASILLO"):
    d.text((p2_px_l+4,p2y+m(0.8)+i*14),ch,fill=DGRAY,font=f_ref)
stair(p2_px_l+WI+3,p2y+m(5)+WI+3,pw-WI*2-6,m(2.8)-6)
elev(p2_px_l+WI+3,p2y+m(8.8),m(1.1),m(1.3))

dh(p2x,p2x+BW,p2y,15.00,True)
dv(p2x,p2y,p2y+BH,12.00,True)


# ──────────────────────────────────────────────────────────────
# TERRAZA (bottom-right)
# ──────────────────────────────────────────────────────────────
d.text((COL2_X, ROW2_Y), "TERRAZA — 160 m²", fill=BLACK, font=f_title)
d.line([(COL2_X, ROW2_Y+26), (COL2_X+200, ROW2_Y+26)], fill=RED, width=2)

tx, ty = COL2_X+50, ROW2_Y+55

# Open space
fr(tx+4,ty+4,BW-8,BH-8,(245,252,245))

# Sala máquinas 4x3
mq_w,mq_h=m(4),m(3)
fr(tx+WI,ty+WI,mq_w-WI*2,mq_h-WI*2,(252,242,238))
ro(tx,ty,mq_w,mq_h,False)

# Tanque 3x2
tq_x=tx+m(4)+8
tq_w,tq_h=m(3),m(2)
fr(tq_x+WI,ty+WI,tq_w-WI*2,tq_h-WI*2,(238,248,255))
ro(tq_x,ty,tq_w,tq_h,False)

# Railing dashed
for i in range(0,BW,14):
    x1=tx+i; x2=min(tx+i+9,tx+BW)
    d.rectangle([x1,ty,x2,ty+3],fill=BLACK)
    d.rectangle([x1,ty+BH-3,x2,ty+BH],fill=BLACK)
for i in range(0,BH,14):
    y1=ty+i; y2=min(ty+i+9,ty+BH)
    d.rectangle([tx,y1,tx+3,y2],fill=BLACK)
    d.rectangle([tx+BW-3,y1,tx+BW,y2],fill=BLACK)

lr(tx,ty,mq_w,mq_h,"SALA MÁQ.",12)
lr(tq_x,ty,tq_w,tq_h,"TANQUE",6)

# Open space label
d.text((tx+m(6),ty+m(5.5)),"ESPACIO COMÚN",fill=BLACK,font=f_room)
d.text((tx+m(6.5),ty+m(5.5)+15),"ABIERTO",fill=BLACK,font=f_room)
d.text((tx+m(6.8),ty+m(5.5)+30),"142 m²",fill=DGRAY,font=f_area)

# Stair arrival
stair(tx+m(6.75)+WI+3,ty+m(5)+3,pw-WI*2-6,m(2.8)-6)
elev(tx+m(6.75)+WI+3,ty+m(8.8),m(1.1),m(1.3))

d.text((tx,ty+BH+8),"— — — Baranda h=1.10m",fill=DGRAY,font=f_ref)

dh(tx,tx+BW,ty,15.00,True)
dv(tx,ty,ty+BH,12.00,True)
dh(tx,tx+mq_w,ty+mq_h,4.00,False)
dv(tx+mq_w,ty,ty+mq_h,3.00,False)
dh(tq_x,tq_x+tq_w,ty+tq_h,3.00,False)
dv(tq_x+tq_w,ty,ty+tq_h,2.00,False)


# ══════════════════════════════════════════════════════════════
# TABLES SECTION
# ══════════════════════════════════════════════════════════════
TBL_Y = ROW2_Y + 470
d.line([(40,TBL_Y),(1960,TBL_Y)],fill=BLACK,width=2)

# ── Left: Surface summary + Legend ──
d.text((60,TBL_Y+10),"RESUMEN DE SUPERFICIES",fill=BLACK,font=f_title2)

ty_ = TBL_Y + 40
cols = [180,100,360]
rows_ = [
    ("NIVEL","SUP.(m²)","PROGRAMA"),
    ("Planta Baja","180","Hall + 2 Locales Comerciales + Cochera + Esc/Asc"),
    ("Piso 1 (Tipo)","160","2 Deptos 2 amb. (A+B espejados) + Pasillo + Esc/Asc"),
    ("Piso 2 (Tipo)","160","2 Deptos 2 amb. (A+B espejados) + Pasillo + Esc/Asc"),
    ("Terraza","160","Sala Máquinas + Tanque + Espacio Común"),
    ("TOTAL","660","3 pisos + terraza accesible"),
]
rh_=24
for ri,row in enumerate(rows_):
    ry=ty_+ri*rh_
    ft=f_tbl_b if ri==0 or ri==5 else f_tbl
    if ri==0: d.rectangle([60,ry,60+sum(cols),ry+rh_],fill=(35,35,35))
    if ri==5:
        d.rectangle([60,ry,60+sum(cols),ry+rh_],fill=(240,240,240))
        d.line([(60,ry),(60+sum(cols),ry)],fill=BLACK,width=2)
    cx_=60
    for ci,(cell,cw) in enumerate(zip(row,cols)):
        d.rectangle([cx_,ry,cx_+cw,ry+rh_],outline=GRAY,width=1)
        clr = WHITE if ri==0 else (RED if ri==5 and ci==1 else BLACK)
        d.text((cx_+6,ry+5),cell,fill=clr,font=ft)
        cx_+=cw

# Legend below surface table
leg_y = ty_ + len(rows_)*rh_ + 20
d.text((60,leg_y),"REFERENCIAS",fill=BLACK,font=f_title2)
leg_y += 28
legs = [
    ("████","Muro ext. 0.20m",BLACK),
    ("███","Muro int. 0.10m",BLACK),
    ("— — —","Baranda h=1.10m",BLACK),
    ("████","Cotas (metros)",RED),
    ("╳","Ascensor",BLACK),
    ("▲","Escalera (subida)",BLACK),
]
for i,(sym,desc,clr) in enumerate(legs):
    ly=leg_y+i*20
    d.text((60,ly),sym,fill=clr,font=f_tbl)
    d.text((140,ly),desc,fill=BLACK,font=f_tbl)

# ── Right: Aberturas table ──
d.text((COL2_X,TBL_Y+10),"TABLA DE ABERTURAS",fill=BLACK,font=f_title2)
at_y = TBL_Y + 40
acols = [80,90,110,230]
arows = [
    ("REF","TIPO","MEDIDA (m)","UBICACIÓN"),
    ("P1","Puerta","0.90×2.10","Hall de entrada — PB"),
    ("P2","Puerta","1.20×2.10","Local comercial 1 — PB"),
    ("P3","Puerta","1.20×2.10","Local comercial 2 — PB"),
    ("P4","Puerta","0.90×2.10","Cochera — PB"),
    ("P5–P6","Puerta","0.90×2.10","Ingreso Deptos A/B — P.Tipo"),
    ("P7–P10","Puerta","0.80×2.10","Dormitorios — P.Tipo"),
    ("P8–P11","Puerta","0.70×2.10","Cocinas — P.Tipo"),
    ("P9–P12","Puerta","0.70×2.10","Baños — P.Tipo"),
    ("V1–V2","Ventana","1.50×1.20","Frente locales — PB"),
    ("V3–V4","Ventana","1.50×1.20","Laterales — PB"),
    ("V5–V6","Ventana","1.80×1.50","Living — P.Tipo"),
    ("V7–V8","Ventana","1.50×1.20","Dormitorios — P.Tipo"),
]
arh=22
for ri,row in enumerate(arows):
    ry=at_y+ri*arh
    ft=f_tbl_b if ri==0 else f_tbl
    if ri==0: d.rectangle([COL2_X,ry,COL2_X+sum(acols),ry+arh],fill=(35,35,35))
    cx_=COL2_X
    for ci,(cell,cw) in enumerate(zip(row,acols)):
        d.rectangle([cx_,ry,cx_+cw,ry+arh],outline=GRAY,width=1)
        clr=WHITE if ri==0 else BLACK
        d.text((cx_+5,ry+4),cell,fill=clr,font=ft)
        cx_+=cw

# ── Title block ──
tb_y = max(leg_y + len(legs)*20 + 20, at_y + len(arows)*arh + 20)
tb_y += 10
d.line([(40,tb_y),(1960,tb_y)],fill=BLACK,width=3)
d.rectangle([40,tb_y,1960,tb_y+70],fill=(248,248,248))
d.text((60,tb_y+8),"PROYECTO: EDIFICIO RESIDENCIAL 3P+T",fill=BLACK,font=f_title2)
d.text((60,tb_y+32),"ESC 1:100 | PLANTAS GENERALES | HOJA 1/1 | SUP. TOTAL: 660 m² | ABR 2026",fill=DGRAY,font=f_tbl)
d.text((60,tb_y+52),"Technical Lineature — Generado con Claude Code",fill=GRAY,font=f_note)
d.line([(40,tb_y+70),(1960,tb_y+70)],fill=BLACK,width=3)

# ── Crop & save ──
final_h = tb_y + 80
img_f = img.crop((0,0,W,final_h))

out = "/Users/carlossanchez/Downloads/eos-saas/.claude/worktrees/competent-varahamihira/edificio_residencial_plano.png"
img_f.save(out,"PNG",dpi=(150,150))
print(f"OK → {out}")
print(f"Tamaño: {img_f.size[0]}×{img_f.size[1]}px")
