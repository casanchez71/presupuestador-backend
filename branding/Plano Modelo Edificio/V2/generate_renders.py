#!/usr/bin/env python3
"""
Generate architectural renders for a 3-story residential building + rooftop terrace.
Top half: Isometric exterior view. Bottom half: 1-point perspective interior view.
"""

import math
from PIL import Image, ImageDraw, ImageFont

# --- Canvas ---
W, H = 2000, 2400
HALF = H // 2
img = Image.new("RGB", (W, H), "#FFFFFF")
draw = ImageDraw.Draw(img)

# --- Fonts ---
FONT_DIR = "/Users/carlossanchez/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/e09fb916-12e4-41ff-8ae4-db2feebaefca/79f14b77-b8e8-4bfc-8ce4-43aff6c6e981/skills/canvas-design/canvas-fonts/"
font_bold_lg = ImageFont.truetype(FONT_DIR + "BigShoulders-Bold.ttf", 42)
font_bold_md = ImageFont.truetype(FONT_DIR + "BigShoulders-Bold.ttf", 30)
font_bold_sm = ImageFont.truetype(FONT_DIR + "InstrumentSans-Bold.ttf", 22)
font_reg = ImageFont.truetype(FONT_DIR + "InstrumentSans-Regular.ttf", 20)
font_reg_sm = ImageFont.truetype(FONT_DIR + "InstrumentSans-Regular.ttf", 16)
font_mono = ImageFont.truetype(FONT_DIR + "DMMono-Regular.ttf", 16)
font_mono_lg = ImageFont.truetype(FONT_DIR + "DMMono-Regular.ttf", 20)
font_title = ImageFont.truetype(FONT_DIR + "BigShoulders-Bold.ttf", 52)

# --- Colors ---
COL_FRONT = (232, 224, 208)       # #E8E0D0
COL_SIDE = (208, 200, 184)        # #D0C8B8
COL_WINDOW = (96, 144, 176)       # #6090B0
COL_WINDOW_LIGHT = (140, 180, 210)
COL_BALCONY = (100, 100, 100)
COL_GROUND = (160, 160, 160)      # #A0A0A0
COL_DARK = (80, 80, 80)
COL_SHADOW = (210, 210, 210)
COL_GLASS_DOOR = (120, 170, 200)
COL_RAILING = (70, 70, 70)
COL_SLAB = (140, 130, 120)
COL_ROOF = (190, 185, 175)
COL_MECH = (170, 165, 155)
COL_TREE_TRUNK = (120, 90, 60)
COL_TREE_CANOPY = (90, 140, 80)
COL_PERSON = (60, 60, 60)
COL_GROUND_PLANE = (235, 232, 225)
COL_BORDER = (180, 175, 165)
COL_TEXT = (50, 50, 50)

# =============================================================================
# TOP HALF: ISOMETRIC EXTERIOR
# =============================================================================

# Page title
draw.text((W // 2, 30), "EDIFICIO RESIDENCIAL 3P+T \u2014 RENDERS ARQUITECT\u00d3NICOS",
          fill=COL_TEXT, font=font_title, anchor="mt")

# Frame for top half
draw.rectangle([30, 70, W - 30, HALF - 15], outline=COL_BORDER, width=2)

# Section title
draw.text((W // 2, 90), "RENDER EXTERIOR \u2014 VISTA AXONOM\u00c9TRICA NE",
          fill=COL_TEXT, font=font_bold_md, anchor="mt")

# --- Isometric helpers ---
CX, CY = W // 2 - 50, 750  # Center of isometric view
SCALE = 28  # pixels per meter
COS30 = math.cos(math.radians(30))
SIN30 = math.sin(math.radians(30))

def iso(x, y, z):
    """Convert 3D (x right, y depth, z up) to 2D isometric."""
    px = CX + (x - y) * COS30 * SCALE
    py = CY - z * SCALE + (x + y) * SIN30 * SCALE
    return (px, py)

def iso_poly(points, fill=None, outline=None, width=1):
    """Draw a filled polygon from 3D points."""
    pts_2d = [iso(*p) for p in points]
    if fill:
        draw.polygon(pts_2d, fill=fill, outline=outline or fill)
    if outline and not fill:
        draw.polygon(pts_2d, outline=outline)
    if outline and width > 1:
        for i in range(len(pts_2d)):
            j = (i + 1) % len(pts_2d)
            draw.line([pts_2d[i], pts_2d[j]], fill=outline, width=width)

def iso_rect_front(x, z, w, h, y_pos, fill=None, outline=None, lw=1):
    """Front-facing rectangle at depth y_pos."""
    pts = [(x, y_pos, z), (x + w, y_pos, z), (x + w, y_pos, z + h), (x, y_pos, z + h)]
    iso_poly(pts, fill=fill, outline=outline, width=lw)

def iso_rect_side(y, z, d, h, x_pos, fill=None, outline=None, lw=1):
    """Side-facing rectangle at x_pos."""
    pts = [(x_pos, y, z), (x_pos, y + d, z), (x_pos, y + d, z + h), (x_pos, y, z + h)]
    iso_poly(pts, fill=fill, outline=outline, width=lw)

# Building dimensions
BW = 15.0   # width (x)
BD = 12.0   # depth (y)
FH = 3.2    # floor height
FLOORS = 3
TOTAL_H = FLOORS * FH
RAILING_H = 1.1

# --- Ground plane shadow ---
shadow_offset = 3.0
shadow_pts = [
    iso(shadow_offset, shadow_offset, 0),
    iso(BW + shadow_offset, shadow_offset, 0),
    iso(BW + shadow_offset, BD + shadow_offset, 0),
    iso(shadow_offset, BD + shadow_offset, 0),
]
draw.polygon(shadow_pts, fill=COL_SHADOW)

# --- Ground plane ---
gp_pts = [
    iso(-3, -2, 0),
    iso(BW + 5, -2, 0),
    iso(BW + 5, BD + 5, 0),
    iso(-3, BD + 5, 0),
]
draw.polygon(gp_pts, fill=COL_GROUND_PLANE, outline=(200, 195, 188))

# --- Draw building faces ---

# SIDE face (right side, x = BW)
iso_poly(
    [(BW, 0, 0), (BW, BD, 0), (BW, BD, TOTAL_H), (BW, 0, TOTAL_H)],
    fill=COL_SIDE, outline=COL_DARK, width=2
)

# TOP face (roof)
iso_poly(
    [(0, 0, TOTAL_H), (BW, 0, TOTAL_H), (BW, BD, TOTAL_H), (0, BD, TOTAL_H)],
    fill=COL_ROOF, outline=COL_DARK, width=2
)

# FRONT face (y = 0)
iso_poly(
    [(0, 0, 0), (BW, 0, 0), (BW, 0, TOTAL_H), (0, 0, TOTAL_H)],
    fill=COL_FRONT, outline=COL_DARK, width=2
)

# --- Floor slab lines ---
for floor in range(1, FLOORS + 1):
    z = floor * FH
    # Front slab line
    p1 = iso(0, 0, z)
    p2 = iso(BW, 0, z)
    draw.line([p1, p2], fill=COL_SLAB, width=3)
    # Side slab line
    p1 = iso(BW, 0, z)
    p2 = iso(BW, BD, z)
    draw.line([p1, p2], fill=COL_SLAB, width=3)

# --- GROUND FLOOR (PB) ---
pb_z = 0.0
pb_h = FH

# Ground floor base/plinth (darker strip at bottom)
plinth_h = 0.6
iso_rect_front(0, 0, BW, plinth_h, 0, fill=COL_GROUND, outline=COL_DARK)

# Garage door (left side of front)
iso_rect_front(0.5, 0.2, 3.0, 2.6, 0, fill=(140, 140, 140), outline=COL_DARK)
# Garage horizontal lines
for gz in [0.8, 1.4, 2.0]:
    p1, p2 = iso(0.5, 0, pb_z + gz), iso(3.5, 0, pb_z + gz)
    draw.line([p1, p2], fill=COL_DARK, width=1)

# Commercial storefront V1 (left)
iso_rect_front(4.0, 0.2, 4.5, 2.8, 0, fill=COL_WINDOW, outline=COL_DARK)
# Mullion
p1, p2 = iso(6.25, 0, 0.2), iso(6.25, 0, 3.0)
draw.line([p1, p2], fill=COL_DARK, width=2)
# Horizontal bar
p1, p2 = iso(4.0, 0, 1.6), iso(8.5, 0, 1.6)
draw.line([p1, p2], fill=COL_DARK, width=1)

# Central entrance
iso_rect_front(9.0, 0.2, 2.5, 2.8, 0, fill=COL_GLASS_DOOR, outline=COL_DARK)
# Door frame
p1, p2 = iso(10.25, 0, 0.2), iso(10.25, 0, 3.0)
draw.line([p1, p2], fill=COL_DARK, width=2)
# Entrance canopy
canopy_pts = [
    iso(8.5, 0, 3.0), iso(12.0, 0, 3.0), iso(12.0, -0.8, 3.0), iso(8.5, -0.8, 3.0)
]
draw.polygon(canopy_pts, fill=(160, 155, 148), outline=COL_DARK)
# Canopy front edge
canopy_front = [
    iso(8.5, -0.8, 3.0), iso(12.0, -0.8, 3.0), iso(12.0, -0.8, 2.85), iso(8.5, -0.8, 2.85)
]
draw.polygon(canopy_front, fill=COL_SLAB, outline=COL_DARK)

# Commercial storefront V2 (right)
iso_rect_front(12.0, 0.2, 2.5, 2.8, 0, fill=COL_WINDOW, outline=COL_DARK)
# Mullion
p1, p2 = iso(13.25, 0, 0.2), iso(13.25, 0, 3.0)
draw.line([p1, p2], fill=COL_DARK, width=2)

# Side facade - garage entrance
iso_rect_side(0.5, 0.2, 3.0, 2.6, 0, fill=(130, 130, 130), outline=COL_DARK)

# Side facade - PB windows
iso_rect_side(5.0, 0.5, 1.8, 2.0, BW, fill=COL_WINDOW, outline=COL_DARK)
iso_rect_side(8.0, 0.5, 1.8, 2.0, BW, fill=COL_WINDOW, outline=COL_DARK)

# --- TYPICAL FLOORS (P1, P2) ---
for fi in range(1, 3):
    fz = fi * FH

    # Front windows / balconies - LEFT apartment
    # Balcony slab projection
    balc_proj = 1.2
    balc_pts_top = [
        iso(1.0, 0, fz), iso(6.5, 0, fz),
        iso(6.5, -balc_proj, fz), iso(1.0, -balc_proj, fz)
    ]
    draw.polygon(balc_pts_top, fill=(200, 195, 188), outline=COL_DARK)
    # Balcony front face
    balc_front = [
        iso(1.0, -balc_proj, fz), iso(6.5, -balc_proj, fz),
        iso(6.5, -balc_proj, fz - 0.15), iso(1.0, -balc_proj, fz - 0.15)
    ]
    draw.polygon(balc_front, fill=COL_SLAB, outline=COL_DARK)
    # Balcony side
    balc_side_l = [
        iso(1.0, 0, fz), iso(1.0, -balc_proj, fz),
        iso(1.0, -balc_proj, fz - 0.15), iso(1.0, 0, fz - 0.15)
    ]
    draw.polygon(balc_side_l, fill=(180, 175, 168), outline=COL_DARK)

    # Railing on balcony (front)
    rail_h = 1.0
    for rx in [1.0, 2.5, 4.0, 5.5]:
        p1 = iso(rx, -balc_proj, fz)
        p2 = iso(rx, -balc_proj, fz + rail_h)
        draw.line([p1, p2], fill=COL_RAILING, width=2)
    # Top rail
    p1 = iso(1.0, -balc_proj, fz + rail_h)
    p2 = iso(6.5, -balc_proj, fz + rail_h)
    draw.line([p1, p2], fill=COL_RAILING, width=2)
    # Bottom rail
    p1 = iso(1.0, -balc_proj, fz + 0.3)
    p2 = iso(6.5, -balc_proj, fz + 0.3)
    draw.line([p1, p2], fill=COL_RAILING, width=1)

    # Windows behind balcony (V5)
    iso_rect_front(1.5, fz + 0.3, 4.5, 2.2, 0, fill=COL_WINDOW, outline=COL_DARK)
    # Mullions
    for mx in [3.0, 4.5]:
        p1, p2 = iso(mx, 0, fz + 0.3), iso(mx, 0, fz + 2.5)
        draw.line([p1, p2], fill=COL_DARK, width=1)

    # Balcony RIGHT apartment
    balc_pts_top_r = [
        iso(8.5, 0, fz), iso(14.0, 0, fz),
        iso(14.0, -balc_proj, fz), iso(8.5, -balc_proj, fz)
    ]
    draw.polygon(balc_pts_top_r, fill=(200, 195, 188), outline=COL_DARK)
    balc_front_r = [
        iso(8.5, -balc_proj, fz), iso(14.0, -balc_proj, fz),
        iso(14.0, -balc_proj, fz - 0.15), iso(8.5, -balc_proj, fz - 0.15)
    ]
    draw.polygon(balc_front_r, fill=COL_SLAB, outline=COL_DARK)
    balc_side_r = [
        iso(14.0, 0, fz), iso(14.0, -balc_proj, fz),
        iso(14.0, -balc_proj, fz - 0.15), iso(14.0, 0, fz - 0.15)
    ]
    draw.polygon(balc_side_r, fill=(180, 175, 168), outline=COL_DARK)

    # Railing right
    for rx in [8.5, 10.0, 11.5, 13.0]:
        p1 = iso(rx, -balc_proj, fz)
        p2 = iso(rx, -balc_proj, fz + rail_h)
        draw.line([p1, p2], fill=COL_RAILING, width=2)
    p1 = iso(8.5, -balc_proj, fz + rail_h)
    p2 = iso(14.0, -balc_proj, fz + rail_h)
    draw.line([p1, p2], fill=COL_RAILING, width=2)
    p1 = iso(8.5, -balc_proj, fz + 0.3)
    p2 = iso(14.0, -balc_proj, fz + 0.3)
    draw.line([p1, p2], fill=COL_RAILING, width=1)

    # Windows behind balcony (V6)
    iso_rect_front(9.0, fz + 0.3, 4.5, 2.2, 0, fill=COL_WINDOW, outline=COL_DARK)
    for mx in [10.5, 12.0]:
        p1, p2 = iso(mx, 0, fz + 0.3), iso(mx, 0, fz + 2.5)
        draw.line([p1, p2], fill=COL_DARK, width=1)

    # Side windows (V7/V8)
    iso_rect_side(2.0, fz + 0.5, 1.5, 2.0, BW, fill=COL_WINDOW, outline=COL_DARK)
    iso_rect_side(5.0, fz + 0.5, 1.5, 2.0, BW, fill=COL_WINDOW, outline=COL_DARK)
    iso_rect_side(8.0, fz + 0.5, 1.5, 2.0, BW, fill=COL_WINDOW, outline=COL_DARK)
    iso_rect_side(10.5, fz + 0.5, 1.2, 1.0, BW, fill=COL_WINDOW_LIGHT, outline=COL_DARK)

# --- TERRACE ---
tz = TOTAL_H

# Terrace railing - front
for rx_pos in range(0, 16, 2):
    rx = float(rx_pos)
    if rx > BW:
        break
    p1 = iso(rx, 0, tz)
    p2 = iso(rx, 0, tz + RAILING_H)
    draw.line([p1, p2], fill=COL_RAILING, width=2)
p1 = iso(0, 0, tz + RAILING_H)
p2 = iso(BW, 0, tz + RAILING_H)
draw.line([p1, p2], fill=COL_RAILING, width=2)
# Mid rail front
p1 = iso(0, 0, tz + 0.5)
p2 = iso(BW, 0, tz + 0.5)
draw.line([p1, p2], fill=COL_RAILING, width=1)

# Terrace railing - side (x=BW)
for ry_pos in range(0, 13, 2):
    ry = float(ry_pos)
    if ry > BD:
        break
    p1 = iso(BW, ry, tz)
    p2 = iso(BW, ry, tz + RAILING_H)
    draw.line([p1, p2], fill=COL_RAILING, width=2)
p1 = iso(BW, 0, tz + RAILING_H)
p2 = iso(BW, BD, tz + RAILING_H)
draw.line([p1, p2], fill=COL_RAILING, width=2)
p1 = iso(BW, 0, tz + 0.5)
p2 = iso(BW, BD, tz + 0.5)
draw.line([p1, p2], fill=COL_RAILING, width=1)

# Mechanical room box (top-left corner of terrace = near x=0, y=BD)
mech_w, mech_d, mech_h = 3.0, 3.0, 2.2
mx0, my0 = 0.5, BD - 3.5
# Top
iso_poly(
    [(mx0, my0, tz + mech_h), (mx0 + mech_w, my0, tz + mech_h),
     (mx0 + mech_w, my0 + mech_d, tz + mech_h), (mx0, my0 + mech_d, tz + mech_h)],
    fill=(175, 170, 162), outline=COL_DARK
)
# Front of mech room
iso_poly(
    [(mx0, my0, tz), (mx0 + mech_w, my0, tz),
     (mx0 + mech_w, my0, tz + mech_h), (mx0, my0, tz + mech_h)],
    fill=COL_MECH, outline=COL_DARK
)
# Side of mech room
iso_poly(
    [(mx0 + mech_w, my0, tz), (mx0 + mech_w, my0 + mech_d, tz),
     (mx0 + mech_w, my0 + mech_d, tz + mech_h), (mx0 + mech_w, my0, tz + mech_h)],
    fill=(155, 150, 142), outline=COL_DARK
)

# Water tank on mech room
tank_w, tank_d, tank_h = 1.5, 1.5, 1.0
tx0 = mx0 + 0.5
ty0 = my0 + 0.5
iso_poly(
    [(tx0, ty0, tz + mech_h), (tx0 + tank_w, ty0, tz + mech_h),
     (tx0 + tank_w, ty0 + tank_d, tz + mech_h), (tx0, ty0 + tank_d, tz + mech_h),],
    fill=(130, 160, 180), outline=COL_DARK
)
iso_poly(
    [(tx0, ty0, tz + mech_h), (tx0 + tank_w, ty0, tz + mech_h),
     (tx0 + tank_w, ty0, tz + mech_h + tank_h), (tx0, ty0, tz + mech_h + tank_h)],
    fill=(140, 170, 190), outline=COL_DARK
)
iso_poly(
    [(tx0 + tank_w, ty0, tz + mech_h), (tx0 + tank_w, ty0 + tank_d, tz + mech_h),
     (tx0 + tank_w, ty0 + tank_d, tz + mech_h + tank_h), (tx0 + tank_w, ty0, tz + mech_h + tank_h)],
    fill=(120, 150, 170), outline=COL_DARK
)
# Tank top
iso_poly(
    [(tx0, ty0, tz + mech_h + tank_h), (tx0 + tank_w, ty0, tz + mech_h + tank_h),
     (tx0 + tank_w, ty0 + tank_d, tz + mech_h + tank_h), (tx0, ty0 + tank_d, tz + mech_h + tank_h)],
    fill=(150, 180, 200), outline=COL_DARK
)

# --- Floor level labels ---
labels = [
    (0, "PB \u00b10.00"),
    (FH, "P1 +3.20"),
    (2 * FH, "P2 +6.40"),
    (TOTAL_H, "TERRAZA +9.60"),
]
for z_lev, label in labels:
    px, py = iso(-1.5, 0, z_lev)
    draw.text((px - 10, py - 8), label, fill=COL_TEXT, font=font_mono, anchor="rm")
    # Small tick
    p1 = iso(-0.5, 0, z_lev)
    p2 = iso(0, 0, z_lev)
    draw.line([p1, p2], fill=COL_DARK, width=1)

# --- Human figure for scale ---
hx, hy = 17.0, -1.5
h_base = iso(hx, hy, 0)
h_head_z = 1.70
h_head = iso(hx, hy, h_head_z)
# Body line
draw.line([h_base, h_head], fill=COL_PERSON, width=3)
# Head circle
hx2, hy2 = iso(hx, hy, h_head_z + 0.15)
draw.ellipse([hx2 - 6, hy2 - 6, hx2 + 6, hy2 + 6], fill=COL_PERSON)
# Arms
h_shoulder = iso(hx, hy, 1.35)
h_lhand = iso(hx - 0.4, hy, 0.9)
h_rhand = iso(hx + 0.4, hy, 0.9)
draw.line([h_lhand, h_shoulder], fill=COL_PERSON, width=2)
draw.line([h_rhand, h_shoulder], fill=COL_PERSON, width=2)
# Legs
h_hip = iso(hx, hy, 0.85)
h_lfoot = iso(hx - 0.3, hy, 0)
h_rfoot = iso(hx + 0.3, hy, 0)
draw.line([h_lfoot, h_hip], fill=COL_PERSON, width=2)
draw.line([h_rfoot, h_hip], fill=COL_PERSON, width=2)
# Label
draw.text((h_base[0], h_base[1] + 8), "1.70m", fill=COL_TEXT, font=font_reg_sm, anchor="mt")

# --- Tree ---
tree_x, tree_y = -2.0, -1.0
trunk_base = iso(tree_x, tree_y, 0)
trunk_top = iso(tree_x, tree_y, 3.0)
draw.line([trunk_base, trunk_top], fill=COL_TREE_TRUNK, width=5)
# Canopy (3 overlapping circles)
for tz_off, r in [(4.0, 28), (3.5, 24), (4.5, 22)]:
    cx_t, cy_t = iso(tree_x, tree_y, tz_off)
    draw.ellipse([cx_t - r, cy_t - r, cx_t + r, cy_t + r], fill=COL_TREE_CANOPY, outline=(70, 120, 60))

# --- Window labels on front ---
# V1
v1p = iso(6.25, -0.3, 1.5)
draw.text((v1p[0], v1p[1] - 20), "V1", fill=(100, 60, 60), font=font_reg_sm, anchor="mm")
# V2
v2p = iso(13.25, -0.3, 1.5)
draw.text((v2p[0], v2p[1] - 20), "V2", fill=(100, 60, 60), font=font_reg_sm, anchor="mm")
# V5 (P1)
v5p = iso(3.75, -0.3, FH + 1.4)
draw.text((v5p[0], v5p[1] - 20), "V5", fill=(100, 60, 60), font=font_reg_sm, anchor="mm")
# V6 (P1)
v6p = iso(11.25, -0.3, FH + 1.4)
draw.text((v6p[0], v6p[1] - 20), "V6", fill=(100, 60, 60), font=font_reg_sm, anchor="mm")


# =============================================================================
# BOTTOM HALF: INTERIOR PERSPECTIVE
# =============================================================================

# Frame
draw.rectangle([30, HALF + 15, W - 30, H - 30], outline=COL_BORDER, width=2)

# Section title
draw.text((W // 2, HALF + 35),
          "RENDER INTERIOR \u2014 DEPTO TIPO A \u2014 LIVING-COMEDOR 25m\u00b2",
          fill=COL_TEXT, font=font_bold_md, anchor="mt")

# 1-point perspective parameters
VP_X = W // 2          # vanishing point X
VP_Y = HALF + 550      # vanishing point Y
# Room bounding box in screen coords
ROOM_L = 150            # left wall screen x
ROOM_R = W - 150        # right wall screen x
ROOM_T = HALF + 80      # ceiling screen y
ROOM_B = H - 100        # floor screen y

# Colors
COL_FLOOR = (200, 168, 130)    # #C8A882
COL_FLOOR_DARK = (180, 148, 110)
COL_WALL = (240, 237, 232)     # #F0EDE8
COL_CEILING = (248, 248, 248)
COL_SKY = (208, 232, 255)      # #D0E8FF
COL_BASEBOARD = (180, 175, 168)

def persp_point(x_frac, y_frac, vx=VP_X, vy=VP_Y):
    """Interpolate between room edge and vanishing point.
    x_frac: 0=left wall, 1=right wall
    y_frac: 0=front (viewer), 1=back wall (VP)
    Returns (px, py) at floor level interpolated."""
    pass

# Draw room using perspective lines from corners to VP

# Back wall
bw_margin = 0.35  # how far back wall is from VP (0=at VP, 1=at room edges)
bw_l = int(VP_X + (ROOM_L - VP_X) * bw_margin)
bw_r = int(VP_X + (ROOM_R - VP_X) * bw_margin)
bw_t = int(VP_Y + (ROOM_T - VP_Y) * bw_margin)
bw_b = int(VP_Y + (ROOM_B - VP_Y) * bw_margin)

# --- CEILING ---
ceil_pts = [(ROOM_L, ROOM_T), (ROOM_R, ROOM_T), (bw_r, bw_t), (bw_l, bw_t)]
draw.polygon(ceil_pts, fill=COL_CEILING)

# --- FLOOR ---
floor_pts = [(ROOM_L, ROOM_B), (ROOM_R, ROOM_B), (bw_r, bw_b), (bw_l, bw_b)]
draw.polygon(floor_pts, fill=COL_FLOOR)

# Floor tile lines (horizontal perspective lines)
for i in range(1, 10):
    t = i / 10.0
    y1 = int(ROOM_B + (bw_b - ROOM_B) * t)
    x_l = int(ROOM_L + (bw_l - ROOM_L) * t)
    x_r = int(ROOM_R + (bw_r - ROOM_R) * t)
    draw.line([(x_l, y1), (x_r, y1)], fill=COL_FLOOR_DARK, width=1)

# Floor tile vertical lines (converging to VP)
for i in range(0, 11):
    t = i / 10.0
    bx = int(ROOM_L + (ROOM_R - ROOM_L) * t)
    # Line from bottom edge to back wall
    bx_back = int(bw_l + (bw_r - bw_l) * t)
    y_back = bw_b
    draw.line([(bx, ROOM_B), (bx_back, y_back)], fill=COL_FLOOR_DARK, width=1)

# --- LEFT WALL ---
lwall_pts = [(ROOM_L, ROOM_T), (ROOM_L, ROOM_B), (bw_l, bw_b), (bw_l, bw_t)]
draw.polygon(lwall_pts, fill=COL_WALL)
# Baseboard
draw.line([(ROOM_L, ROOM_B), (bw_l, bw_b)], fill=COL_BASEBOARD, width=4)

# --- RIGHT WALL ---
rwall_pts = [(ROOM_R, ROOM_T), (ROOM_R, ROOM_B), (bw_r, bw_b), (bw_r, bw_t)]
draw.polygon(rwall_pts, fill=COL_WALL)
draw.line([(ROOM_R, ROOM_B), (bw_r, bw_b)], fill=COL_BASEBOARD, width=4)

# --- BACK WALL ---
draw.rectangle([bw_l, bw_t, bw_r, bw_b], fill=COL_WALL, outline=(200, 197, 192))

# --- Balcony door/window on back wall (V13) ---
door_l = bw_l + int((bw_r - bw_l) * 0.15)
door_r = bw_l + int((bw_r - bw_l) * 0.55)
door_t = bw_t + int((bw_b - bw_t) * 0.05)
door_b = bw_b - int((bw_b - bw_t) * 0.02)
draw.rectangle([door_l, door_t, door_r, door_b], fill=COL_SKY, outline=COL_DARK)
# Door mullion
door_mid = (door_l + door_r) // 2
draw.line([(door_mid, door_t), (door_mid, door_b)], fill=COL_DARK, width=3)
# Horizontal bar
door_hmid = door_t + int((door_b - door_t) * 0.6)
draw.line([(door_l, door_hmid), (door_r, door_hmid)], fill=COL_DARK, width=2)
# Light rays from window (subtle)
for ray in range(0, 5):
    t = ray / 4.0
    rx = int(door_l + (door_r - door_l) * t)
    floor_rx = int(rx + (rx - VP_X) * 1.5)
    draw.line([(rx, door_b), (floor_rx, ROOM_B)], fill=(220, 230, 240, 80), width=1)
# Label
draw.text(((door_l + door_r) // 2, door_t - 8), "V13 \u2014 Balc\u00f3n",
          fill=COL_TEXT, font=font_reg_sm, anchor="mb")

# --- Kitchen opening on right wall ---
# Opening in right wall (back portion)
kit_top_wall = bw_t + int((bw_b - bw_t) * 0.0)
kit_bot_wall = bw_b
kit_l_frac = 0.3
kit_r_frac = 0.7

# Kitchen opening in right wall - trapezoidal
kit_y_top = int(ROOM_T + (bw_t - ROOM_T) * kit_l_frac)
kit_y_bot = int(ROOM_B + (bw_b - ROOM_B) * kit_l_frac)
kit_y_top2 = int(ROOM_T + (bw_t - ROOM_T) * kit_r_frac)
kit_y_bot2 = int(ROOM_B + (bw_b - ROOM_B) * kit_r_frac)
kit_x_l = int(ROOM_R + (bw_r - ROOM_R) * kit_l_frac)
kit_x_r = int(ROOM_R + (bw_r - ROOM_R) * kit_r_frac)

# Archway / opening
opening_top_l = kit_y_top + int((kit_y_bot - kit_y_top) * 0.05)
opening_top_r = kit_y_top2 + int((kit_y_bot2 - kit_y_top2) * 0.05)
# Draw opening as darker rectangle suggesting depth
draw.polygon(
    [(kit_x_l, opening_top_l), (kit_x_r, opening_top_r),
     (kit_x_r, kit_y_bot2), (kit_x_l, kit_y_bot)],
    fill=(225, 222, 215)
)
# Kitchen interior elements visible through opening
# Counter
counter_h = int((kit_y_bot - opening_top_l) * 0.4)
counter_top = kit_y_bot - counter_h
xl, xr = min(kit_x_l + 5, kit_x_r - 2), max(kit_x_l + 5, kit_x_r - 2)
if xr > xl:
    draw.rectangle([xl, counter_top, xr, kit_y_bot2],
                   fill=(180, 175, 168), outline=(150, 145, 138))
    # Upper cabinets
    cab_h = int((kit_y_bot - opening_top_l) * 0.25)
    draw.rectangle([xl, opening_top_l + 10, xr, opening_top_l + 10 + cab_h],
                   fill=(195, 190, 183), outline=(170, 165, 158))
# Opening frame
draw.line([(kit_x_l, opening_top_l), (kit_x_l, kit_y_bot)], fill=COL_DARK, width=3)
draw.line([(kit_x_r, opening_top_r), (kit_x_r, kit_y_bot2)], fill=COL_DARK, width=3)
draw.line([(kit_x_l, opening_top_l), (kit_x_r, opening_top_r)], fill=COL_DARK, width=3)

# --- Hallway on back wall (left side) ---
hall_l = bw_l + int((bw_r - bw_l) * 0.68)
hall_r = bw_l + int((bw_r - bw_l) * 0.88)
hall_t = bw_t + int((bw_b - bw_t) * 0.05)
hall_b = bw_b
draw.rectangle([hall_l, hall_t, hall_r, hall_b], fill=(215, 212, 207), outline=(180, 177, 172))
# Hallway depth suggestion
draw.rectangle([hall_l + 8, hall_t + 8, hall_r - 8, hall_b],
               fill=(200, 197, 192))
# Label
draw.text(((hall_l + hall_r) // 2, hall_t + 20), "Pasillo",
          fill=(120, 120, 120), font=font_reg_sm, anchor="mt")
draw.text(((hall_l + hall_r) // 2, hall_t + 38), "\u2192 Dormitorio",
          fill=(120, 120, 120), font=font_reg_sm, anchor="mt")
draw.text(((hall_l + hall_r) // 2, hall_t + 56), "\u2192 Ba\u00f1o",
          fill=(120, 120, 120), font=font_reg_sm, anchor="mt")

# --- Furniture: Sofa (left side of room) ---
# Sofa in perspective - on left side, facing right
sofa_depth = 0.45  # how far back (0=front, 1=back)
sofa_x_l = ROOM_L + int((bw_l - ROOM_L) * sofa_depth) + 20
sofa_x_r = sofa_x_l + 60
sofa_y_t = int(ROOM_B + (bw_b - ROOM_B) * sofa_depth) - 55
sofa_y_b = int(ROOM_B + (bw_b - ROOM_B) * sofa_depth) - 10
# Sofa body
draw.rounded_rectangle([sofa_x_l, sofa_y_t, sofa_x_r, sofa_y_b],
                        radius=5, fill=(140, 135, 128), outline=(110, 105, 98))
# Sofa back
draw.rounded_rectangle([sofa_x_l, sofa_y_t - 15, sofa_x_l + 12, sofa_y_b],
                        radius=3, fill=(130, 125, 118), outline=(110, 105, 98))
# Cushions
draw.rounded_rectangle([sofa_x_l + 14, sofa_y_t + 4, sofa_x_r - 4, sofa_y_b - 4],
                        radius=3, fill=(155, 150, 143), outline=(130, 125, 118))
# Second sofa section (L-shape going toward back wall)
sofa2_x_l = sofa_x_l
sofa2_x_r = sofa_x_l + 35
sofa2_y_t = sofa_y_t - 45
sofa2_y_b = sofa_y_t
draw.rounded_rectangle([sofa2_x_l, sofa2_y_t, sofa2_x_r, sofa2_y_b],
                        radius=5, fill=(140, 135, 128), outline=(110, 105, 98))

# --- Furniture: Dining table (center-right) ---
dt_cx = VP_X + 80
dt_cy = VP_Y + 130
dt_w, dt_h = 90, 50
draw.rounded_rectangle([dt_cx - dt_w // 2, dt_cy - dt_h // 2,
                         dt_cx + dt_w // 2, dt_cy + dt_h // 2],
                        radius=4, fill=(170, 140, 110), outline=(140, 110, 80))
# Chairs
for cx_off, cy_off in [(-55, 0), (55, 0), (0, -30), (0, 30)]:
    ch_x = dt_cx + cx_off
    ch_y = dt_cy + cy_off
    draw.rounded_rectangle([ch_x - 10, ch_y - 8, ch_x + 10, ch_y + 8],
                            radius=3, fill=(150, 145, 138), outline=(120, 115, 108))

# --- Ceiling light fixtures ---
for lx in [VP_X - 150, VP_X + 150]:
    ly = VP_Y - 40
    # Pendant line
    draw.line([(lx, ROOM_T + int((bw_t - ROOM_T) * 0.3)), (lx, ly)],
              fill=(180, 178, 175), width=1)
    # Light shade
    draw.ellipse([lx - 20, ly - 8, lx + 20, ly + 8], fill=(240, 235, 220), outline=(200, 195, 185))

# Center pendant light
draw.line([(VP_X, bw_t - 5), (VP_X, VP_Y - 80)], fill=(180, 178, 175), width=2)
draw.ellipse([VP_X - 25, VP_Y - 95, VP_X + 25, VP_Y - 70],
             fill=(245, 240, 225), outline=(200, 195, 185))

# --- Perspective edge lines (room edges to VP) ---
# Top-left corner
draw.line([(ROOM_L, ROOM_T), (bw_l, bw_t)], fill=(170, 165, 158), width=2)
# Top-right corner
draw.line([(ROOM_R, ROOM_T), (bw_r, bw_t)], fill=(170, 165, 158), width=2)
# Bottom-left corner
draw.line([(ROOM_L, ROOM_B), (bw_l, bw_b)], fill=(170, 165, 158), width=2)
# Bottom-right corner
draw.line([(ROOM_R, ROOM_B), (bw_r, bw_b)], fill=(170, 165, 158), width=2)

# --- Room frame lines ---
draw.line([(ROOM_L, ROOM_T), (ROOM_R, ROOM_T)], fill=COL_DARK, width=2)
draw.line([(ROOM_L, ROOM_B), (ROOM_R, ROOM_B)], fill=COL_DARK, width=2)
draw.line([(ROOM_L, ROOM_T), (ROOM_L, ROOM_B)], fill=COL_DARK, width=2)
draw.line([(ROOM_R, ROOM_T), (ROOM_R, ROOM_B)], fill=COL_DARK, width=2)

# --- Labels ---
# Room dimensions
draw.text((ROOM_L + 20, ROOM_B + 15),
          "Living-Comedor 6.75 \u00d7 5.00 = 25 m\u00b2",
          fill=COL_TEXT, font=font_bold_sm)

draw.text((ROOM_R - 20, ROOM_B + 15),
          "Cocina (al fondo der.) 8 m\u00b2",
          fill=COL_TEXT, font=font_reg, anchor="ra")

# Ceiling height label (on left wall)
ch_x = ROOM_L + 15
ch_y1 = int(ROOM_B + (bw_b - ROOM_B) * 0.2)
ch_y2 = int(ROOM_T + (bw_t - ROOM_T) * 0.2)
ch_x2 = int(ROOM_L + (bw_l - ROOM_L) * 0.2)
draw.line([(ch_x2, ch_y1), (ch_x2, ch_y2)], fill=(150, 100, 100), width=1)
draw.line([(ch_x2 - 5, ch_y1), (ch_x2 + 5, ch_y1)], fill=(150, 100, 100), width=1)
draw.line([(ch_x2 - 5, ch_y2), (ch_x2 + 5, ch_y2)], fill=(150, 100, 100), width=1)
draw.text((ch_x2 + 8, (ch_y1 + ch_y2) // 2), "h=2.60m",
          fill=(150, 100, 100), font=font_mono, anchor="lm")

# Balcony label
balc_label_y = door_b + 15
draw.text(((door_l + door_r) // 2, balc_label_y), "Balc\u00f3n 4 m\u00b2",
          fill=COL_TEXT, font=font_reg_sm, anchor="mt")

# --- Save ---
OUTPUT = "/Users/carlossanchez/Downloads/presupuestador-backend/renders_edificio.png"
img.save(OUTPUT, "PNG", dpi=(150, 150))
print(f"Saved: {OUTPUT}")
print(f"Size: {img.size}")
