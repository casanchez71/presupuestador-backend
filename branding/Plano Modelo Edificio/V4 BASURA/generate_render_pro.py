#!/usr/bin/env python3
"""
TECTONIC LIGHT — Professional Architectural Renders
Edificio Residencial 3P+T — Exterior Axonometric + Interior Perspective
Museum-quality architectural illustration style
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, random

FONTS = "/Users/carlossanchez/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/e09fb916-12e4-41ff-8ae4-db2feebaefca/79f14b77-b8e8-4bfc-8ce4-43aff6c6e981/skills/canvas-design/canvas-fonts"

def lf(n, s):
    try: return ImageFont.truetype(os.path.join(FONTS, n), s)
    except: return ImageFont.load_default()

# Typography
f_title = lf("Italiana-Regular.ttf", 42)
f_subtitle = lf("InstrumentSans-Regular.ttf", 18)
f_label = lf("DMMono-Regular.ttf", 13)
f_label_sm = lf("DMMono-Regular.ttf", 11)
f_accent = lf("Jura-Light.ttf", 14)
f_dim = lf("DMMono-Regular.ttf", 10)
f_credit = lf("InstrumentSans-Regular.ttf", 10)

# ── Color Palette: Tectonic Light ──
BG = (248, 245, 240)          # warm paper
FACADE_FRONT = (226, 213, 195) # sand render
FACADE_SIDE = (200, 188, 168)  # darker sand
FACADE_DARK = (175, 162, 142)  # deep shadow
PLINTH = (160, 155, 148)       # stone base
PLINTH_DARK = (135, 130, 122)
GLASS = (138, 175, 200)        # window glass
GLASS_LIGHT = (195, 218, 235)  # glass reflection
GLASS_DARK = (95, 130, 160)    # deep glass
SKY_REFLECT = (214, 232, 240)
CONCRETE = (180, 178, 175)     # floor slabs
CONCRETE_DARK = (150, 148, 145)
RAILING = (74, 74, 80)         # aluminum
RAILING_LIGHT = (120, 120, 128)
SHADOW = (190, 182, 172)       # ground shadow
SHADOW_DEEP = (155, 145, 133)
WHITE_WALL = (245, 243, 240)
TIMBER = (195, 168, 130)       # wood floor
TIMBER_DARK = (170, 142, 105)
TIMBER_LINE = (155, 128, 90)
BLACK = (40, 38, 35)
DARK = (70, 68, 65)
MID = (130, 128, 125)
LIGHT = (210, 208, 205)
RED_DIM = (175, 60, 50)
BALCONY_GLASS = (170, 200, 220, 120)
SKY_TOP = (180, 205, 230)
SKY_BOT = (225, 238, 248)
GROUND = (215, 210, 200)
TREE_TRUNK = (100, 82, 60)
TREE_CANOPY = (85, 130, 75)
TREE_CANOPY_L = (110, 155, 95)

W, H = 2000, 2800
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)


# ══════════════════════════════════════════════════════════════
# RENDER 1: EXTERIOR — AXONOMETRIC VIEW
# ══════════════════════════════════════════════════════════════

# ── Sky gradient (top portion) ──
for y in range(0, 1300):
    t = y / 1300
    r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
    g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
    b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
    # Fade into BG at bottom
    if y > 1000:
        t2 = (y - 1000) / 300
        r = int(r + (BG[0] - r) * t2)
        g = int(g + (BG[1] - g) * t2)
        b = int(b + (BG[2] - b) * t2)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# ── Isometric projection helpers ──
# Using ~30° isometric: x-axis goes right-down, y-axis goes left-down, z goes up
ISO_SCALE = 28  # pixels per meter
CX, CY = 950, 950  # center of projection (ground level reference)

def iso(x, y, z):
    """Convert 3D coords (meters) to 2D isometric screen coords"""
    px = CX + (x - y) * ISO_SCALE * math.cos(math.radians(30))
    py = CY - z * ISO_SCALE + (x + y) * ISO_SCALE * math.sin(math.radians(30)) * 0.58
    return (int(px), int(py))

def iso_quad(x1,y1,z1, x2,y2,z2, x3,y3,z3, x4,y4,z4):
    """Return list of 4 iso-projected points"""
    return [iso(x1,y1,z1), iso(x2,y2,z2), iso(x3,y3,z3), iso(x4,y4,z4)]

def draw_face(pts, fill_color, outline_color=None):
    d.polygon(pts, fill=fill_color, outline=outline_color)

def shade(color, factor):
    """Darken or lighten a color"""
    return tuple(max(0, min(255, int(c * factor))) for c in color)

# Building dimensions
BW = 15.0   # width (x-axis)
BD = 12.0   # depth (y-axis)
FLOOR_H = 3.2  # PB height
TIPO_H = 2.8   # typical floor height
SLAB = 0.20
RAILING_H = 1.1

# Floor levels
Z_PB = 0
Z_P1 = FLOOR_H
Z_P2 = FLOOR_H + TIPO_H
Z_TERR = FLOOR_H + 2 * TIPO_H
Z_TOP = Z_TERR + RAILING_H

# ── GROUND PLANE ──
ground_pts = iso_quad(-5, -5, 0, BW+8, -5, 0, BW+8, BD+5, 0, -5, BD+5, 0)
draw_face(ground_pts, GROUND)

# Ground texture lines
for i in range(0, 30):
    gx = -3 + i * 0.8
    p1 = iso(gx, -3, 0)
    p2 = iso(gx, BD+3, 0)
    d.line([p1, p2], fill=shade(GROUND, 0.96), width=1)

# ── BUILDING SHADOW on ground ──
shadow_offset = 3.0
sh_pts = iso_quad(
    BW, 0, 0,
    BW + shadow_offset, -shadow_offset, 0,
    BW + shadow_offset, BD - shadow_offset, 0,
    BW, BD, 0
)
draw_face(sh_pts, SHADOW)
# Front shadow
sh_front = iso_quad(
    0, 0, 0,
    BW, 0, 0,
    BW + shadow_offset, -shadow_offset, 0,
    shadow_offset, -shadow_offset, 0
)
draw_face(sh_front, SHADOW)

# ── PLANTA BAJA (ground floor) ──
# Front face PB
pb_front = iso_quad(0, 0, Z_PB, BW, 0, Z_PB, BW, 0, Z_P1, 0, 0, Z_P1)
draw_face(pb_front, PLINTH)

# Side face PB (right side visible)
pb_side = iso_quad(BW, 0, Z_PB, BW, BD, Z_PB, BW, BD, Z_P1, BW, 0, Z_P1)
draw_face(pb_side, PLINTH_DARK)

# Top of PB slab
pb_top = iso_quad(0, 0, Z_P1, BW, 0, Z_P1, BW, BD, Z_P1, 0, BD, Z_P1)
draw_face(pb_top, CONCRETE)

# ── PB Windows/Doors (front face) ──
# Commercial window 1 (left): x=1 to x=5.5, z=0.3 to z=2.8
def front_window(x1, x2, z1, z2, glass_col=GLASS):
    pts = iso_quad(x1, 0, z1, x2, 0, z1, x2, 0, z2, x1, 0, z2)
    draw_face(pts, glass_col)
    # Frame
    for pt1, pt2 in [(pts[0],pts[1]), (pts[1],pts[2]), (pts[2],pts[3]), (pts[3],pts[0])]:
        d.line([pt1, pt2], fill=RAILING, width=2)
    # Mullion
    mx = (x1+x2)/2
    m1 = iso(mx, 0, z1); m2 = iso(mx, 0, z2)
    d.line([m1, m2], fill=RAILING, width=1)

def side_window(x, y1, y2, z1, z2, glass_col=GLASS):
    pts = iso_quad(x, y1, z1, x, y2, z1, x, y2, z2, x, y1, z2)
    draw_face(pts, glass_col)
    for pt1, pt2 in [(pts[0],pts[1]), (pts[1],pts[2]), (pts[2],pts[3]), (pts[3],pts[0])]:
        d.line([pt1, pt2], fill=RAILING, width=2)
    my = (y1+y2)/2
    m1 = iso(x, my, z1); m2 = iso(x, my, z2)
    d.line([m1, m2], fill=RAILING, width=1)

# PB Commercial storefronts
front_window(0.8, 5.2, 0.2, 2.8, GLASS_LIGHT)   # Local 1
front_window(9.8, 14.2, 0.2, 2.8, GLASS_LIGHT)  # Local 2
# Hall entrance (glass door)
front_window(6.5, 8.5, 0, 2.9, GLASS)
# Entrance canopy
canopy = iso_quad(6, -0.8, 3.0, 9, -0.8, 3.0, 9, 0, 3.0, 6, 0, 3.0)
draw_face(canopy, CONCRETE)
canopy_edge = iso_quad(6, -0.8, 2.9, 9, -0.8, 2.9, 9, -0.8, 3.0, 6, -0.8, 3.0)
draw_face(canopy_edge, CONCRETE_DARK)

# Side windows PB
side_window(BW, 2, 4.5, 0.5, 2.5, GLASS)
side_window(BW, 7, 9.5, 0.5, 2.5, GLASS)
# Garage door on side
garage = iso_quad(BW, 9.5, 0, BW, 12, 0, BW, 12, 2.2, BW, 9.5, 2.2)
draw_face(garage, shade(PLINTH_DARK, 0.85))
for gz in [0.5, 1.0, 1.5, 2.0]:
    g1 = iso(BW, 9.5, gz); g2 = iso(BW, 12, gz)
    d.line([g1, g2], fill=shade(PLINTH_DARK, 0.75), width=1)


# ── PISO 1 ──
p1_front = iso_quad(0, 0, Z_P1, BW, 0, Z_P1, BW, 0, Z_P2, 0, 0, Z_P2)
draw_face(p1_front, FACADE_FRONT)

p1_side = iso_quad(BW, 0, Z_P1, BW, BD, Z_P1, BW, BD, Z_P2, BW, 0, Z_P2)
draw_face(p1_side, FACADE_SIDE)

p1_top = iso_quad(0, 0, Z_P2, BW, 0, Z_P2, BW, BD, Z_P2, 0, BD, Z_P2)
draw_face(p1_top, CONCRETE)

# P1 front windows
front_window(1.5, 5.5, Z_P1+0.8, Z_P1+2.3)  # Living A
front_window(9.5, 13.5, Z_P1+0.8, Z_P1+2.3) # Living B

# P1 Balconies
# Balcony A (left) - projects 1.2m from facade
bal_a_floor = iso_quad(0.5, -1.2, Z_P1, 6.5, -1.2, Z_P1, 6.5, 0, Z_P1, 0.5, 0, Z_P1)
draw_face(bal_a_floor, CONCRETE)
bal_a_edge = iso_quad(0.5, -1.2, Z_P1-0.12, 6.5, -1.2, Z_P1-0.12, 6.5, -1.2, Z_P1, 0.5, -1.2, Z_P1)
draw_face(bal_a_edge, CONCRETE_DARK)
# Balcony railing (glass)
bal_a_rail_f = iso_quad(0.5, -1.2, Z_P1, 6.5, -1.2, Z_P1, 6.5, -1.2, Z_P1+1.0, 0.5, -1.2, Z_P1+1.0)
# Draw semi-transparent glass railing
d.polygon(bal_a_rail_f, fill=(170, 200, 220), outline=RAILING)
# Top rail
d.line([iso(0.5, -1.2, Z_P1+1.0), iso(6.5, -1.2, Z_P1+1.0)], fill=RAILING, width=2)
# Side rail
bal_a_rail_s = iso_quad(0.5, -1.2, Z_P1, 0.5, 0, Z_P1, 0.5, 0, Z_P1+1.0, 0.5, -1.2, Z_P1+1.0)
d.polygon(bal_a_rail_s, fill=(160, 190, 210), outline=RAILING)

# Balcony B (right)
bal_b_floor = iso_quad(8.5, -1.2, Z_P1, 14.5, -1.2, Z_P1, 14.5, 0, Z_P1, 8.5, 0, Z_P1)
draw_face(bal_b_floor, CONCRETE)
bal_b_edge = iso_quad(8.5, -1.2, Z_P1-0.12, 14.5, -1.2, Z_P1-0.12, 14.5, -1.2, Z_P1, 8.5, -1.2, Z_P1)
draw_face(bal_b_edge, CONCRETE_DARK)
bal_b_rail_f = iso_quad(8.5, -1.2, Z_P1, 14.5, -1.2, Z_P1, 14.5, -1.2, Z_P1+1.0, 8.5, -1.2, Z_P1+1.0)
d.polygon(bal_b_rail_f, fill=(170, 200, 220), outline=RAILING)
d.line([iso(8.5, -1.2, Z_P1+1.0), iso(14.5, -1.2, Z_P1+1.0)], fill=RAILING, width=2)
bal_b_rail_s = iso_quad(14.5, -1.2, Z_P1, 14.5, 0, Z_P1, 14.5, 0, Z_P1+1.0, 14.5, -1.2, Z_P1+1.0)
d.polygon(bal_b_rail_s, fill=(160, 190, 210), outline=RAILING)

# P1 side windows
side_window(BW, 2, 4.5, Z_P1+0.9, Z_P1+2.1)
side_window(BW, 7, 9.5, Z_P1+0.9, Z_P1+2.1)


# ── PISO 2 ──
p2_front = iso_quad(0, 0, Z_P2, BW, 0, Z_P2, BW, 0, Z_TERR, 0, 0, Z_TERR)
draw_face(p2_front, FACADE_FRONT)

p2_side = iso_quad(BW, 0, Z_P2, BW, BD, Z_P2, BW, BD, Z_TERR, BW, 0, Z_TERR)
draw_face(p2_side, FACADE_SIDE)

p2_top = iso_quad(0, 0, Z_TERR, BW, 0, Z_TERR, BW, BD, Z_TERR, 0, BD, Z_TERR)
draw_face(p2_top, CONCRETE)

# P2 front windows
front_window(1.5, 5.5, Z_P2+0.8, Z_P2+2.3)
front_window(9.5, 13.5, Z_P2+0.8, Z_P2+2.3)

# P2 Balconies (same as P1)
bal2_a_floor = iso_quad(0.5, -1.2, Z_P2, 6.5, -1.2, Z_P2, 6.5, 0, Z_P2, 0.5, 0, Z_P2)
draw_face(bal2_a_floor, CONCRETE)
bal2_a_edge = iso_quad(0.5, -1.2, Z_P2-0.12, 6.5, -1.2, Z_P2-0.12, 6.5, -1.2, Z_P2, 0.5, -1.2, Z_P2)
draw_face(bal2_a_edge, CONCRETE_DARK)
bal2_a_rail = iso_quad(0.5, -1.2, Z_P2, 6.5, -1.2, Z_P2, 6.5, -1.2, Z_P2+1.0, 0.5, -1.2, Z_P2+1.0)
d.polygon(bal2_a_rail, fill=(170, 200, 220), outline=RAILING)
d.line([iso(0.5, -1.2, Z_P2+1.0), iso(6.5, -1.2, Z_P2+1.0)], fill=RAILING, width=2)
bal2_a_s = iso_quad(0.5, -1.2, Z_P2, 0.5, 0, Z_P2, 0.5, 0, Z_P2+1.0, 0.5, -1.2, Z_P2+1.0)
d.polygon(bal2_a_s, fill=(160, 190, 210), outline=RAILING)

bal2_b_floor = iso_quad(8.5, -1.2, Z_P2, 14.5, -1.2, Z_P2, 14.5, 0, Z_P2, 8.5, 0, Z_P2)
draw_face(bal2_b_floor, CONCRETE)
bal2_b_edge = iso_quad(8.5, -1.2, Z_P2-0.12, 14.5, -1.2, Z_P2-0.12, 14.5, -1.2, Z_P2, 8.5, -1.2, Z_P2)
draw_face(bal2_b_edge, CONCRETE_DARK)
bal2_b_rail = iso_quad(8.5, -1.2, Z_P2, 14.5, -1.2, Z_P2, 14.5, -1.2, Z_P2+1.0, 8.5, -1.2, Z_P2+1.0)
d.polygon(bal2_b_rail, fill=(170, 200, 220), outline=RAILING)
d.line([iso(8.5, -1.2, Z_P2+1.0), iso(14.5, -1.2, Z_P2+1.0)], fill=RAILING, width=2)
bal2_b_s = iso_quad(14.5, -1.2, Z_P2, 14.5, 0, Z_P2, 14.5, 0, Z_P2+1.0, 14.5, -1.2, Z_P2+1.0)
d.polygon(bal2_b_s, fill=(160, 190, 210), outline=RAILING)

# P2 side windows
side_window(BW, 2, 4.5, Z_P2+0.9, Z_P2+2.1)
side_window(BW, 7, 9.5, Z_P2+0.9, Z_P2+2.1)


# ── TERRAZA ──
# Terrace floor already drawn as P2 top

# Railing - front
terr_rail_f = iso_quad(0, 0, Z_TERR, BW, 0, Z_TERR, BW, 0, Z_TOP, 0, 0, Z_TOP)
d.polygon(terr_rail_f, fill=(200, 215, 225), outline=RAILING)
# Railing posts
for rx in range(0, 16, 2):
    p1 = iso(rx, 0, Z_TERR); p2 = iso(rx, 0, Z_TOP)
    d.line([p1, p2], fill=RAILING, width=2)
# Top rail
d.line([iso(0, 0, Z_TOP), iso(BW, 0, Z_TOP)], fill=RAILING, width=3)

# Railing - side
terr_rail_s = iso_quad(BW, 0, Z_TERR, BW, BD, Z_TERR, BW, BD, Z_TOP, BW, 0, Z_TOP)
d.polygon(terr_rail_s, fill=(185, 200, 212), outline=RAILING)
for ry in range(0, 13, 2):
    p1 = iso(BW, ry, Z_TERR); p2 = iso(BW, ry, Z_TOP)
    d.line([p1, p2], fill=RAILING, width=2)
d.line([iso(BW, 0, Z_TOP), iso(BW, BD, Z_TOP)], fill=RAILING, width=3)

# Mechanical room (top-left corner of terrace)
mz = Z_TERR
mh = 2.5
# Front
mech_f = iso_quad(0.5, 0.5, mz, 4.5, 0.5, mz, 4.5, 0.5, mz+mh, 0.5, 0.5, mz+mh)
draw_face(mech_f, shade(FACADE_FRONT, 0.92))
# Side
mech_s = iso_quad(4.5, 0.5, mz, 4.5, 3.5, mz, 4.5, 3.5, mz+mh, 4.5, 0.5, mz+mh)
draw_face(mech_s, shade(FACADE_SIDE, 0.92))
# Top
mech_t = iso_quad(0.5, 0.5, mz+mh, 4.5, 0.5, mz+mh, 4.5, 3.5, mz+mh, 0.5, 3.5, mz+mh)
draw_face(mech_t, shade(CONCRETE, 0.95))
# Door
mech_door = iso_quad(1.5, 0.5, mz, 3.0, 0.5, mz, 3.0, 0.5, mz+2.1, 1.5, 0.5, mz+2.1)
draw_face(mech_door, shade(RAILING, 1.2))

# Water tank
tz = Z_TERR
th = 1.8
tank_f = iso_quad(5.5, 0.5, tz, 8.0, 0.5, tz, 8.0, 0.5, tz+th, 5.5, 0.5, tz+th)
draw_face(tank_f, (180, 195, 210))
tank_s = iso_quad(8.0, 0.5, tz, 8.0, 2.5, tz, 8.0, 2.5, tz+th, 8.0, 0.5, tz+th)
draw_face(tank_s, (165, 180, 195))
tank_t = iso_quad(5.5, 0.5, tz+th, 8.0, 0.5, tz+th, 8.0, 2.5, tz+th, 5.5, 2.5, tz+th)
draw_face(tank_t, (190, 205, 218))


# ── FACADE TEXTURE (subtle horizontal scoring lines) ──
for fz in range(1, int(Z_TOP * 10)):
    z = fz / 10.0
    if z < Z_PB or (Z_P1-0.1 < z < Z_P1+0.1) or (Z_P2-0.1 < z < Z_P2+0.1) or (Z_TERR-0.1 < z < Z_TERR+0.1):
        continue
    # Front face line
    p1 = iso(0.1, 0, z); p2 = iso(BW-0.1, 0, z)
    if Z_P1 < z < Z_P2 or Z_P2 < z < Z_TERR:
        d.line([p1, p2], fill=shade(FACADE_FRONT, 0.98), width=1)
    # Side face line
    p1s = iso(BW, 0.1, z); p2s = iso(BW, BD-0.1, z)
    if Z_P1 < z < Z_P2 or Z_P2 < z < Z_TERR:
        d.line([p1s, p2s], fill=shade(FACADE_SIDE, 0.97), width=1)

# ── PB Signage / Address ──
addr_p = iso(6.8, -0.01, 3.05)
d.text((addr_p[0]-15, addr_p[1]-8), "1247", fill=RAILING, font=f_label)

# ── BUILDING EDGES (crisp lines) ──
edges = [
    # Front vertical edges
    (0,0,0, 0,0,Z_TOP), (BW,0,0, BW,0,Z_TOP),
    # Side vertical edges
    (BW,BD,0, BW,BD,Z_TOP),
    # Front horizontal (floor lines)
    (0,0,Z_PB, BW,0,Z_PB), (0,0,Z_P1, BW,0,Z_P1),
    (0,0,Z_P2, BW,0,Z_P2), (0,0,Z_TERR, BW,0,Z_TERR),
    # Side horizontal
    (BW,0,Z_P1, BW,BD,Z_P1), (BW,0,Z_P2, BW,BD,Z_P2),
    (BW,0,Z_TERR, BW,BD,Z_TERR),
    # Top edges
    (0,0,Z_TOP, BW,0,Z_TOP),
]
for x1,y1,z1, x2,y2,z2 in edges:
    p1 = iso(x1,y1,z1); p2 = iso(x2,y2,z2)
    d.line([p1, p2], fill=DARK, width=2)

# Back top edge
d.line([iso(0,BD,Z_TOP), iso(BW,BD,Z_TOP)], fill=MID, width=1)
d.line([iso(0,0,Z_TOP), iso(0,BD,Z_TOP)], fill=MID, width=1)


# ── CONTEXT: Tree ──
tree_x, tree_y = -2.5, 2.0
# Trunk
trunk_b = iso(tree_x, tree_y, 0)
trunk_t = iso(tree_x, tree_y, 3)
d.line([trunk_b, trunk_t], fill=TREE_TRUNK, width=4)
# Canopy (layered ellipses for depth)
for cz, cr, col in [(5.5, 38, TREE_CANOPY), (5, 45, TREE_CANOPY_L), (4.5, 40, TREE_CANOPY), (4, 32, shade(TREE_CANOPY, 0.9))]:
    cp = iso(tree_x, tree_y, cz)
    d.ellipse([cp[0]-cr, cp[1]-cr, cp[0]+cr, cp[1]+cr], fill=col)

# ── CONTEXT: Human figure ──
hx, hy = BW + 3, 2
h_feet = iso(hx, hy, 0)
h_head = iso(hx, hy, 1.7)
h_shoulder = iso(hx, hy, 1.4)
h_hip = iso(hx, hy, 0.9)
# Body
d.line([h_feet, h_hip], fill=DARK, width=2)
d.line([h_hip, h_shoulder], fill=DARK, width=2)
d.line([h_shoulder, h_head], fill=DARK, width=2)
# Head
d.ellipse([h_head[0]-4, h_head[1]-6, h_head[0]+4, h_head[1]+2], fill=DARK)
# Arms
arm_l = (h_shoulder[0]-8, h_shoulder[1]+10)
arm_r = (h_shoulder[0]+8, h_shoulder[1]+10)
d.line([h_shoulder, arm_l], fill=DARK, width=1)
d.line([h_shoulder, arm_r], fill=DARK, width=1)
# Legs
d.line([h_hip, (h_feet[0]-5, h_feet[1])], fill=DARK, width=1)
d.line([h_hip, (h_feet[0]+5, h_feet[1])], fill=DARK, width=1)
# Scale label
d.text((h_head[0]+8, h_head[1]-4), "1.70m", fill=DARK, font=f_dim)


# ── LEVEL LABELS ──
label_x = -4
for z, txt in [(Z_PB, "PB  ±0.00"), (Z_P1, "P1  +3.20"), (Z_P2, "P2  +6.00"), (Z_TERR, "TERRAZA  +8.80")]:
    lp = iso(label_x, -1, z)
    d.text((lp[0]-10, lp[1]-6), txt, fill=RED_DIM, font=f_label)
    # Horizontal tick
    tick_start = iso(label_x+1.5, 0, z)
    tick_end = iso(0, 0, z)
    d.line([tick_start, tick_end], fill=RED_DIM, width=1)

# Total height
th_top = iso(label_x-1, -1, Z_TOP)
th_bot = iso(label_x-1, -1, 0)
d.line([th_top, th_bot], fill=RED_DIM, width=1)
d.line([(th_top[0]-4, th_top[1]), (th_top[0]+4, th_top[1])], fill=RED_DIM, width=2)
d.line([(th_bot[0]-4, th_bot[1]), (th_bot[0]+4, th_bot[1])], fill=RED_DIM, width=2)
mid_h = iso(label_x-1, -1, Z_TOP/2)
d.text((mid_h[0]-55, mid_h[1]-6), "11.80m", fill=RED_DIM, font=f_label)

# ── Title for render 1 ──
d.text((80, 30), "EDIFICIO RESIDENCIAL 3P+T", fill=BLACK, font=f_title)
d.text((80, 78), "RENDER EXTERIOR — VISTA AXONOMÉTRICA NORESTE", fill=MID, font=f_subtitle)
d.text((80, 102), "15.00m × 12.00m × 11.80m  |  660 m² totales  |  Fachada revoque fino + aluminio", fill=MID, font=f_accent)

# ── Subtle grid texture on terrace floor ──
for tx_ in range(1, 15):
    p1 = iso(tx_, 0.2, Z_TERR+0.01); p2 = iso(tx_, BD-0.2, Z_TERR+0.01)
    d.line([p1, p2], fill=shade(CONCRETE, 0.97), width=1)
for ty_ in range(1, 12):
    p1 = iso(0.2, ty_, Z_TERR+0.01); p2 = iso(BW-0.2, ty_, Z_TERR+0.01)
    d.line([p1, p2], fill=shade(CONCRETE, 0.97), width=1)


# ══════════════════════════════════════════════════════════════
# DIVIDER
# ══════════════════════════════════════════════════════════════
div_y = 1260
d.line([(100, div_y), (1900, div_y)], fill=LIGHT, width=1)


# ══════════════════════════════════════════════════════════════
# RENDER 2: INTERIOR — 1-POINT PERSPECTIVE
# Living-Comedor Depto Tipo A — 25m²
# ══════════════════════════════════════════════════════════════

# Title
d.text((80, div_y + 20), "DEPTO TIPO A — LIVING-COMEDOR", fill=BLACK, font=f_title)
d.text((80, div_y + 68), "RENDER INTERIOR — PERSPECTIVA 1 PUNTO", fill=MID, font=f_subtitle)
d.text((80, div_y + 92), "6.75m × 5.00m = 25 m²  |  h libre 2.60m  |  Porcelanato símil madera + carpintería aluminio", fill=MID, font=f_accent)

# Interior canvas region
IX, IY = 100, div_y + 125  # top-left of interior render
IW, IH = 1800, 1300  # interior canvas size

# Frame
d.rectangle([IX-2, IY-2, IX+IW+2, IY+IH+2], outline=MID, width=2)

# ── 1-Point Perspective Setup ──
# Vanishing point
VPX = IX + IW // 2
VPY = IY + int(IH * 0.42)  # slightly above center

# Room boundaries (screen coords)
# Back wall (around VP)
BW_L = VPX - 280  # back wall left
BW_R = VPX + 280  # back wall right
BW_T = VPY - 180  # back wall top
BW_B = VPY + 180  # back wall bottom

# Canvas edges
CL = IX           # canvas left
CR = IX + IW      # canvas right
CT = IY           # canvas top
CB = IY + IH      # canvas bottom

def lerp(a, b, t):
    return int(a + (b-a)*t)

# ── CEILING ──
ceiling_pts = [(CL, CT), (CR, CT), (BW_R, BW_T), (BW_L, BW_T)]
d.polygon(ceiling_pts, fill=(248, 247, 245))

# Ceiling detail lines (beams / panel edges)
for i in range(1, 8):
    t = i / 8
    x_left = lerp(CL, BW_L, t)
    x_right = lerp(CR, BW_R, t)
    y_top = lerp(CT, BW_T, t)
    d.line([(x_left, y_top), (x_right, y_top)], fill=(240, 238, 235), width=1)

# ── FLOOR ──
floor_pts = [(CL, CB), (CR, CB), (BW_R, BW_B), (BW_L, BW_B)]

# Floor gradient (warm timber)
for row in range(BW_B, CB):
    t = (row - BW_B) / (CB - BW_B)
    # Interpolate left and right edges
    left_x = lerp(BW_L, CL, t)
    right_x = lerp(BW_R, CR, t)
    # Color varies for wood plank effect
    plank = (row // 12) % 2
    if plank == 0:
        col = (int(195 - t*15), int(168 - t*12), int(130 - t*10))
    else:
        col = (int(188 - t*15), int(160 - t*12), int(122 - t*10))
    d.line([(left_x, row), (right_x, row)], fill=col)

# Floor plank lines (converging to VP)
for i in range(0, 20):
    px = BW_L + (BW_R - BW_L) * i / 19
    bx = CL + (CR - CL) * i / 19
    d.line([(int(px), BW_B), (int(bx), CB)], fill=TIMBER_LINE, width=1)

# Floor horizontal plank joints
for row in range(BW_B + 20, CB, 25):
    t = (row - BW_B) / (CB - BW_B)
    left_x = lerp(BW_L, CL, t)
    right_x = lerp(BW_R, CR, t)
    d.line([(left_x, row), (right_x, row)], fill=shade(TIMBER_DARK, 0.9), width=1)

# ── LEFT WALL ──
left_wall = [(CL, CT), (BW_L, BW_T), (BW_L, BW_B), (CL, CB)]
d.polygon(left_wall, fill=(242, 240, 237))
# Wall shadow gradient near corner
for i in range(20):
    t = i / 20
    x = CL + int(t * (BW_L - CL) * 0.1)
    y1 = lerp(CT, BW_T, t*0.1)
    y2 = lerp(CB, BW_B, t*0.1)
    col = shade((235, 233, 228), 0.97 + t*0.03)
    d.line([(x, y1), (x, y2)], fill=col, width=1)

# ── RIGHT WALL ──
right_wall = [(CR, CT), (BW_R, BW_T), (BW_R, BW_B), (CR, CB)]
d.polygon(right_wall, fill=(238, 236, 232))

# ── BACK WALL ──
back_wall = [(BW_L, BW_T), (BW_R, BW_T), (BW_R, BW_B), (BW_L, BW_B)]
d.polygon(back_wall, fill=WHITE_WALL)

# ── BALCONY DOOR (center of back wall) ──
# Large sliding glass door V13
door_l = VPX - 130
door_r = VPX + 130
door_t = BW_T + 15
door_b = BW_B - 5

# Sky through door
for row in range(door_t, door_b):
    t = (row - door_t) / (door_b - door_t)
    r = int(200 + (240-200)*t)
    g = int(220 + (245-220)*t)
    b_val = int(245 + (250-245)*t)
    d.line([(door_l, row), (door_r, row)], fill=(r, g, b_val))

# Balcony railing visible through glass
rail_y = VPY + 80
d.line([(door_l+10, rail_y), (door_r-10, rail_y)], fill=RAILING_LIGHT, width=3)
# Railing posts
for rx in range(door_l+20, door_r-10, 35):
    d.line([(rx, rail_y), (rx, door_b-5)], fill=RAILING_LIGHT, width=2)

# Door frame
d.rectangle([door_l, door_t, door_r, door_b], outline=RAILING, width=3)
# Center mullion
d.line([(VPX, door_t), (VPX, door_b)], fill=RAILING, width=2)
# Horizontal transom
transom_y = door_t + 30
d.line([(door_l, transom_y), (door_r, transom_y)], fill=RAILING, width=1)

# Light rays from door (subtle)
for i in range(5):
    ray_y = door_b + 10 + i * 30
    spread = (ray_y - door_b) * 0.8
    # Light patch on floor
    t = (ray_y - BW_B) / (CB - BW_B) if ray_y > BW_B else 0
    left_x = lerp(BW_L, CL, t)
    right_x = lerp(BW_R, CR, t)
    patch_l = max(left_x, int(VPX - 130 - spread))
    patch_r = min(right_x, int(VPX + 130 + spread))
    if ray_y < CB and patch_l < patch_r:
        d.line([(patch_l, ray_y), (patch_r, ray_y)], fill=(210, 198, 175), width=2)


# ── KITCHEN OPENING (right side of back wall) ──
kit_l = BW_R - 120
kit_r = BW_R
kit_t = BW_T + 20
kit_b = BW_B - 10

# Kitchen visible through opening
d.rectangle([kit_l, kit_t, kit_r, kit_b], fill=(235, 233, 228))

# Counter
counter_y = VPY + 50
d.rectangle([kit_l+5, counter_y, kit_r-5, counter_y+35], fill=(180, 175, 168))
d.rectangle([kit_l+5, counter_y, kit_r-5, counter_y+3], fill=(160, 155, 148))

# Upper cabinets
cab_y = kit_t + 20
d.rectangle([kit_l+8, cab_y, kit_r-8, cab_y+50], fill=(220, 218, 215))
d.rectangle([kit_l+8, cab_y, kit_r-8, cab_y+50], outline=(200, 198, 195), width=1)
# Cabinet division
d.line([(kit_l+60, cab_y), (kit_l+60, cab_y+50)], fill=(200, 198, 195), width=1)

# Opening frame
d.rectangle([kit_l, kit_t, kit_r, kit_b], outline=MID, width=2)

# Kitchen label
d.text((kit_l+5, kit_b+5), "COCINA", fill=MID, font=f_dim)
d.text((kit_l+5, kit_b+18), "8 m²", fill=MID, font=f_dim)


# ── HALLWAY (left side of back wall) ──
hall_l = BW_L
hall_r = BW_L + 80
hall_t = BW_T + 40
hall_b = BW_B - 10

# Dark hallway
d.rectangle([hall_l, hall_t, hall_r, hall_b], fill=(200, 198, 192))
# Door frame
d.rectangle([hall_l, hall_t, hall_r, hall_b], outline=MID, width=2)
d.text((hall_l+5, hall_b+5), "PASILLO", fill=MID, font=f_dim)
d.text((hall_l+5, hall_b+18), "→ Dorm / Baño", fill=MID, font=f_dim)


# ── FURNITURE: Sofa (bottom-left) ──
# L-shaped sofa
sofa_x = CL + 80
sofa_y = CB - 320
sofa_w = 350
sofa_d = 120

# Back cushion
d.rectangle([sofa_x, sofa_y, sofa_x+sofa_w, sofa_y+25], fill=(120, 115, 108))
# Seat
d.rectangle([sofa_x, sofa_y+25, sofa_x+sofa_w, sofa_y+sofa_d], fill=(140, 135, 125))
d.rectangle([sofa_x, sofa_y+25, sofa_x+sofa_w, sofa_y+sofa_d], outline=(115, 110, 102), width=1)
# Cushion lines
d.line([(sofa_x+sofa_w//3, sofa_y+30), (sofa_x+sofa_w//3, sofa_y+sofa_d-5)], fill=(128, 123, 115), width=1)
d.line([(sofa_x+2*sofa_w//3, sofa_y+30), (sofa_x+2*sofa_w//3, sofa_y+sofa_d-5)], fill=(128, 123, 115), width=1)
# L extension
d.rectangle([sofa_x, sofa_y+sofa_d, sofa_x+140, sofa_y+sofa_d+80], fill=(135, 130, 122))
d.rectangle([sofa_x, sofa_y+sofa_d, sofa_x+140, sofa_y+sofa_d+80], outline=(115, 110, 102), width=1)

# Shadow under sofa
d.line([(sofa_x, sofa_y+sofa_d+80+2), (sofa_x+sofa_w, sofa_y+sofa_d+2)], fill=(175, 158, 132), width=3)


# ── FURNITURE: Dining table + chairs (bottom-right) ──
table_cx = CR - 400
table_cy = CB - 250
table_w = 180
table_h = 100

# Table
d.rectangle([table_cx-table_w//2, table_cy-table_h//2, table_cx+table_w//2, table_cy+table_h//2],
    fill=(165, 140, 105), outline=(145, 120, 85), width=2)

# Chairs (4)
chair_positions = [
    (table_cx, table_cy - table_h//2 - 25),  # top
    (table_cx, table_cy + table_h//2 + 25),   # bottom
    (table_cx - table_w//2 - 20, table_cy),    # left
    (table_cx + table_w//2 + 20, table_cy),    # right
]
for cx_, cy_ in chair_positions:
    d.rectangle([cx_-15, cy_-12, cx_+15, cy_+12], fill=(150, 145, 138), outline=(130, 125, 118), width=1)


# ── LIGHTING: Pendant lamp ──
# Two pendant lights
for lamp_x in [VPX - 100, VPX + 100]:
    lamp_y = BW_T - 50
    # Cord
    d.line([(lamp_x, BW_T-80), (lamp_x, lamp_y)], fill=DARK, width=1)
    # Shade (elegant cone)
    d.polygon([(lamp_x-18, lamp_y), (lamp_x+18, lamp_y), (lamp_x+8, lamp_y-20), (lamp_x-8, lamp_y-20)],
        fill=(230, 225, 215), outline=(200, 195, 185), width=1)
    # Glow
    d.ellipse([lamp_x-25, lamp_y-5, lamp_x+25, lamp_y+15], fill=(245, 240, 220))


# ── WALL ART (left wall) ──
art_x = CL + 200
art_y = VPY - 80
d.rectangle([art_x, art_y, art_x+100, art_y+70], fill=(210, 205, 195), outline=(180, 175, 168), width=2)


# ── RUG under coffee table area ──
rug_pts = [
    (sofa_x + 50, sofa_y + sofa_d + 15),
    (sofa_x + sofa_w + 40, sofa_y + 30),
    (sofa_x + sofa_w + 40, sofa_y + sofa_d + 80),
    (sofa_x + 50, sofa_y + sofa_d + 95),
]
d.polygon(rug_pts, fill=(195, 188, 175), outline=(180, 172, 158), width=1)

# ── COFFEE TABLE ──
ct_x = sofa_x + sofa_w//2 + 20
ct_y = sofa_y + sofa_d + 30
d.rectangle([ct_x, ct_y, ct_x+100, ct_y+45], fill=(155, 135, 108), outline=(140, 120, 92), width=1)
# Books on table
d.rectangle([ct_x+10, ct_y+8, ct_x+45, ct_y+18], fill=(180, 80, 70))
d.rectangle([ct_x+50, ct_y+12, ct_x+85, ct_y+22], fill=(90, 120, 140))

# ── INDOOR PLANT (left of balcony door) ──
plant_x = BW_L + 30
plant_y = BW_B - 40
# Pot
d.polygon([(plant_x-12, plant_y), (plant_x+12, plant_y), (plant_x+10, plant_y+25), (plant_x-10, plant_y+25)],
    fill=(165, 130, 100), outline=(145, 110, 80), width=1)
# Leaves
for angle in range(-60, 70, 20):
    rad = math.radians(angle)
    lx = plant_x + int(22 * math.sin(rad))
    ly = plant_y - int(25 + 15 * abs(math.cos(rad)))
    d.ellipse([lx-6, ly-10, lx+6, ly+3], fill=(85, 135, 75))

# ── BASEBOARD ──
# Left wall baseboard
d.line([(CL, CB-1), (BW_L, BW_B-1)], fill=(200, 195, 188), width=3)
# Right wall baseboard
d.line([(CR, CB-1), (BW_R, BW_B-1)], fill=(200, 195, 188), width=3)
# Back wall baseboard
d.line([(BW_L, BW_B-1), (BW_R, BW_B-1)], fill=(200, 195, 188), width=3)

# ── CROWN MOLDING ──
d.line([(CL, CT+1), (BW_L, BW_T+1)], fill=(235, 232, 228), width=2)
d.line([(CR, CT+1), (BW_R, BW_T+1)], fill=(235, 232, 228), width=2)
d.line([(BW_L, BW_T+1), (BW_R, BW_T+1)], fill=(235, 232, 228), width=2)


# ── DIMENSION ANNOTATIONS ──
# Height
d.text((CL+15, VPY-5), "h = 2.60m", fill=RED_DIM, font=f_label)
# Red vertical line for height
d.line([(CL+12, CT+20), (CL+12, CB-20)], fill=RED_DIM, width=1)
d.line([(CL+8, CT+20), (CL+16, CT+20)], fill=RED_DIM, width=2)
d.line([(CL+8, CB-20), (CL+16, CB-20)], fill=RED_DIM, width=2)

# Balcony label
d.text((VPX-40, door_b-20), "V13 — Balcón", fill=WHITE_WALL, font=f_label_sm)
d.text((VPX-25, door_b-8), "4 m²", fill=WHITE_WALL, font=f_dim)

# Room dimensions at bottom
d.text((IX+20, IY+IH+10), "Living-Comedor  6.75 × 5.00 = 25 m²", fill=BLACK, font=f_label)
d.text((IX+IW-280, IY+IH+10), "Cocina (al fondo der.) 2.25 × 3.50 = 8 m²", fill=MID, font=f_label_sm)


# ══════════════════════════════════════════════════════════════
# FINAL CREDITS
# ══════════════════════════════════════════════════════════════
credit_y = IY + IH + 35
d.line([(100, credit_y), (1900, credit_y)], fill=LIGHT, width=1)
d.text((100, credit_y+8), "EDIFICIO RESIDENCIAL 3P+T  ·  660 m²  ·  PB ±0.00 / P1 +3.20 / P2 +6.00 / TERRAZA +8.80  ·  Altura total 11.80m", fill=MID, font=f_accent)
d.text((100, credit_y+28), "Fachada: revoque fino arena + carpintería aluminio A30 gris  ·  Balcones: baranda vidrio templado + acero  ·  Cubierta: losa H°A° + baranda h=1.10m", fill=MID, font=f_credit)
d.text((100, credit_y+44), "Interior: porcelanato símil madera + paredes al látex blanco + cielorraso liso  ·  Renders: Tectonic Light  ·  Claude Code", fill=shade(MID, 1.15), font=f_credit)


# ── Crop and save ──
final_h = credit_y + 68
img_final = img.crop((0, 0, W, final_h))

# Second pass: very subtle paper grain (every 4th pixel, ±1)
random.seed(42)
pixels = img_final.load()
for y in range(0, img_final.size[1], 2):
    for x in range(0, img_final.size[0], 4):
        r, g, b = pixels[x, y]
        n = random.randint(-1, 1)
        pixels[x, y] = (max(0,min(255,r+n)), max(0,min(255,g+n)), max(0,min(255,b+n)))

output = "/Users/carlossanchez/Downloads/presupuestador-backend/renders_edificio.png"
img_final.save(output, "PNG", dpi=(150, 150))
print(f"OK → {output}")
print(f"Size: {img_final.size[0]}×{img_final.size[1]}px")
