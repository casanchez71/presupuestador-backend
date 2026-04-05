#!/usr/bin/env python3
"""
Generate planos_arquitectonicos.png with 3 sections:
1. Architectural floor plans
2. Sanitary installations
3. Electrical installations
"""

from PIL import Image, ImageDraw, ImageFont
import math

# --- CONFIG ---
CANVAS_W = 2000
SCALE = 32  # 1m = 32px
FONTS_DIR = "/Users/carlossanchez/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/e09fb916-12e4-41ff-8ae4-db2feebaefca/79f14b77-b8e8-4bfc-8ce4-43aff6c6e981/skills/canvas-design/canvas-fonts/"
OUTPUT = "/Users/carlossanchez/Downloads/presupuestador-backend/planos_arquitectonicos.png"

# Fonts
def load_font(name, size):
    try:
        return ImageFont.truetype(FONTS_DIR + name, size)
    except:
        return ImageFont.load_default()

font_title = load_font("BigShoulders-Bold.ttf", 28)
font_subtitle = load_font("BigShoulders-Bold.ttf", 22)
font_label = load_font("InstrumentSans-Bold.ttf", 13)
font_small = load_font("InstrumentSans-Regular.ttf", 11)
font_dim = load_font("DMMono-Regular.ttf", 10)
font_dim_sm = load_font("DMMono-Regular.ttf", 9)
font_room = load_font("InstrumentSans-Bold.ttf", 11)
font_room_sm = load_font("InstrumentSans-Regular.ttf", 9)
font_axis = load_font("GeistMono-Bold.ttf", 12)
font_table = load_font("DMMono-Regular.ttf", 9)
font_table_header = load_font("GeistMono-Bold.ttf", 10)
font_legend = load_font("InstrumentSans-Regular.ttf", 10)
font_legend_bold = load_font("InstrumentSans-Bold.ttf", 10)
font_section_title = load_font("BigShoulders-Bold.ttf", 36)
font_npt = load_font("DMMono-Regular.ttf", 10)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
CYAN = (0, 180, 220)
BLUE = (0, 80, 200)
BLUE_LIGHT = (100, 160, 240)
GREEN = (0, 140, 50)
GREEN_LIGHT = (80, 200, 100)
GRAY = (180, 180, 180)
GRAY_LIGHT = (220, 220, 220)
GRAY_DARK = (100, 100, 100)
ORANGE = (220, 120, 0)

# Building dimensions
BLDG_W = 15  # meters
BLDG_H = 12  # meters
EXT_WALL = 0.20
INT_WALL = 0.10

def m2px(m):
    return int(m * SCALE)

def draw_dashed_line(draw, x1, y1, x2, y2, fill, width=1, dash_len=8, gap_len=4):
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    ux, uy = dx/length, dy/length
    pos = 0
    while pos < length:
        sx = x1 + ux * pos
        sy = y1 + uy * pos
        end = min(pos + dash_len, length)
        ex = x1 + ux * end
        ey = y1 + uy * end
        draw.line([(sx, sy), (ex, ey)], fill=fill, width=width)
        pos = end + gap_len

def draw_rect(draw, x, y, w, h, outline=BLACK, width=1, fill=None):
    draw.rectangle([x, y, x+w, y+h], outline=outline, width=width, fill=fill)

def draw_wall(draw, x, y, w, h, thickness=2):
    draw.rectangle([x, y, x+w, y+h], outline=BLACK, width=thickness, fill=WHITE)

def draw_text_centered(draw, x, y, text, font, fill=BLACK):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x - tw//2, y - th//2), text, font=font, fill=fill)

def draw_axis_circle(draw, cx, cy, label, font, color=CYAN):
    r = 12
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color, width=2)
    draw_text_centered(draw, cx, cy, label, font, fill=color)

def draw_door(draw, x, y, w, opening_dir='right', swing='up', label='P1'):
    """Draw door with swing arc"""
    dw = m2px(0.9) if w == 0 else w
    draw.rectangle([x, y-2, x+dw, y+2], fill=WHITE, outline=BLACK, width=1)
    # Swing arc
    if swing == 'up':
        for i in range(0, 90, 3):
            rad = math.radians(i)
            ex = x + int(dw * math.cos(rad))
            ey = y - int(dw * math.sin(rad))
            if i > 0:
                draw.line([(px, py), (ex, ey)], fill=BLACK, width=1)
            px, py = ex, ey
    elif swing == 'down':
        for i in range(0, 90, 3):
            rad = math.radians(i)
            ex = x + int(dw * math.cos(rad))
            ey = y + int(dw * math.sin(rad))
            if i > 0:
                draw.line([(px, py), (ex, ey)], fill=BLACK, width=1)
            px, py = ex, ey
    draw.text((x, y - 15), label, font=font_dim_sm, fill=RED)

def draw_window(draw, x, y, length, vertical=False, label='V1'):
    """Draw window symbol"""
    if vertical:
        draw.rectangle([x-3, y, x+3, y+length], fill=WHITE, outline=BLACK, width=1)
        draw.line([(x-3, y), (x+3, y+length)], fill=CYAN, width=1)
        draw.line([(x+3, y), (x-3, y+length)], fill=CYAN, width=1)
        draw.text((x+6, y + length//2 - 5), label, font=font_dim_sm, fill=RED)
    else:
        draw.rectangle([x, y-3, x+length, y+3], fill=WHITE, outline=BLACK, width=1)
        draw.line([(x, y-3), (x+length, y+3)], fill=CYAN, width=1)
        draw.line([(x+length, y-3), (x, y+3)], fill=CYAN, width=1)
        draw.text((x + length//2 - 8, y+6), label, font=font_dim_sm, fill=RED)

def draw_dim_h(draw, x1, x2, y, text, offset=20):
    """Horizontal dimension line"""
    ly = y + offset
    draw.line([(x1, y), (x1, ly+4)], fill=RED, width=1)
    draw.line([(x2, y), (x2, ly+4)], fill=RED, width=1)
    draw.line([(x1, ly), (x2, ly)], fill=RED, width=1)
    # arrows
    for dx, d in [(x1, 1), (x2, -1)]:
        draw.polygon([(dx, ly), (dx + d*6, ly-3), (dx + d*6, ly+3)], fill=RED)
    draw_text_centered(draw, (x1+x2)//2, ly - 10, text, font_dim, fill=RED)

def draw_dim_v(draw, y1, y2, x, text, offset=20):
    """Vertical dimension line"""
    lx = x + offset
    draw.line([(x, y1), (lx+4, y1)], fill=RED, width=1)
    draw.line([(x, y2), (lx+4, y2)], fill=RED, width=1)
    draw.line([(lx, y1), (lx, y2)], fill=RED, width=1)
    for dy, d in [(y1, 1), (y2, -1)]:
        draw.polygon([(lx, dy), (lx-3, dy + d*6), (lx+3, dy + d*6)], fill=RED)
    # Rotated text approximation - just place it
    draw.text((lx + 5, (y1+y2)//2 - 5), text, font=font_dim, fill=RED)

def draw_stairs(draw, x, y, w, h, direction='up'):
    """Draw stair symbol"""
    steps = 10
    step_h = h // steps
    for i in range(steps):
        sy = y + i * step_h
        draw.line([(x, sy), (x + w, sy)], fill=BLACK, width=1)
    draw.rectangle([x, y, x+w, y+h], outline=BLACK, width=2)
    # Arrow
    mid_x = x + w // 2
    draw.line([(mid_x, y + h), (mid_x, y + 10)], fill=BLACK, width=2)
    draw.polygon([(mid_x, y+5), (mid_x-5, y+15), (mid_x+5, y+15)], fill=BLACK)
    draw.text((x + 2, y + h//2), "SUBE", font=font_dim_sm, fill=BLACK)

def draw_elevator(draw, x, y, w, h):
    """Draw elevator symbol with X"""
    draw.rectangle([x, y, x+w, y+h], outline=BLACK, width=2)
    draw.line([(x, y), (x+w, y+h)], fill=BLACK, width=1)
    draw.line([(x+w, y), (x, y+h)], fill=BLACK, width=1)
    draw_text_centered(draw, x+w//2, y+h//2 + 12, "ASC", font_dim_sm, BLACK)

def draw_structural_axes(draw, ox, oy, bw, bh):
    """Draw structural axes A-F horizontal, 1-6 vertical"""
    # Vertical axes (A-F) - 6 axes across 15m
    ax_positions_x = [0, 3, 6, 9, 12, 15]
    ax_labels_x = ['A', 'B', 'C', 'D', 'E', 'F']
    for i, (pos, lab) in enumerate(zip(ax_positions_x, ax_labels_x)):
        px = ox + m2px(pos)
        draw_dashed_line(draw, px, oy - 25, px, oy + bh + 5, CYAN, 1, 6, 4)
        draw_axis_circle(draw, px, oy - 35, lab, font_axis, CYAN)

    # Horizontal axes (1-6) - 6 axes across 12m
    ax_positions_y = [0, 2.5, 5, 7.5, 9.5, 12]
    ax_labels_y = ['1', '2', '3', '4', '5', '6']
    for i, (pos, lab) in enumerate(zip(ax_positions_y, ax_labels_y)):
        py = oy + m2px(pos)
        draw_dashed_line(draw, ox - 25, py, ox + bw + 5, py, CYAN, 1, 6, 4)
        draw_axis_circle(draw, ox - 38, py, lab, font_axis, CYAN)

def draw_column(draw, x, y, size=6):
    """Draw structural column"""
    draw.rectangle([x-size, y-size, x+size, y+size], fill=BLACK, outline=BLACK)

def draw_columns_at_axes(draw, ox, oy):
    """Place columns at key grid intersections"""
    ax_x = [0, 3, 6, 9, 12, 15]
    ax_y = [0, 5, 12]
    for mx in ax_x:
        for my in ax_y:
            draw_column(draw, ox + m2px(mx), oy + m2px(my))

# ============================================================
# SECTION 1: ARCHITECTURAL PLANS
# ============================================================

def draw_pb(draw, ox, oy):
    """Draw Planta Baja"""
    bw = m2px(BLDG_W)
    bh = m2px(BLDG_H)

    # Title
    draw_text_centered(draw, ox + bw//2, oy - 65, "PLANTA BAJA — 180 m²", font_subtitle, BLACK)
    draw_text_centered(draw, ox + bw//2, oy - 48, "NPT ±0.00  h=3.20m", font_npt, GRAY_DARK)

    # Structural axes
    draw_structural_axes(draw, ox, oy, bw, bh)

    # Columns
    draw_columns_at_axes(draw, ox, oy)

    # Exterior walls
    draw.rectangle([ox, oy, ox+bw, oy+bh], outline=BLACK, width=4)

    # --- Interior walls ---
    # Core area: x=6 to x=9 (3m wide), full height top section
    # Vertical wall at x=6m (core left)
    cx6 = ox + m2px(6)
    cx9 = ox + m2px(9)

    # Hall: 0-3m x, 0-5m y => 3×5=15m²
    # Local1: 3-9m x, 0-7.5m y => 6×7.5=45m² (left of core + core area on left)
    # Actually let me reinterpret the layout:
    # PB (15m×12m): Hall 3×5=15m², Local1 6×7.5=45m², Local2 6×7.5=45m², Cochera 6×5=30m², Patio serv 6×4.5=28m², Core 3×7

    # Layout:
    # Left side (0-6m): Local1 top (6×7.5), Cochera bottom (6×5) -- wait 7.5+5=12.5 > 12
    # Let me do: Left(0-6), Center core(6-9), Right(9-15)
    # Core (6-9, 0-7): stairs+elevator
    # Hall (6-9, 7-12): 3×5=15m²
    # Local1 (0-6, 0-7.5): 6×7.5=45m²
    # Cochera (0-6, 7.5-12): 6×4.5=27m² ≈28m²
    # Local2 (9-15, 0-7.5): 6×7.5=45m²
    # Patio serv (9-15, 7.5-12): 6×4.5=27m² ≈28m²

    y_mid = m2px(7.5)
    y_core_end = m2px(7)

    # Vertical wall at x=6
    draw.line([(cx6, oy), (cx6, oy + bh)], fill=BLACK, width=4)
    # Vertical wall at x=9
    draw.line([(cx9, oy), (cx9, oy + bh)], fill=BLACK, width=4)

    # Horizontal wall at y=7.5 (left and right)
    draw.line([(ox, oy + y_mid), (cx6, oy + y_mid)], fill=BLACK, width=3)
    draw.line([(cx9, oy + y_mid), (ox + bw, oy + y_mid)], fill=BLACK, width=3)

    # Core: horizontal wall at y=7 (core bottom)
    draw.line([(cx6, oy + y_core_end), (cx9, oy + y_core_end)], fill=BLACK, width=3)
    # Core internal: split stairs (6-7.5) and elevator (7.5-9) at x=7.5
    cx75 = ox + m2px(7.5)
    draw.line([(cx75, oy), (cx75, oy + y_core_end)], fill=BLACK, width=2)

    # Stairs
    draw_stairs(draw, cx6 + 4, oy + 4, m2px(1.4), y_core_end - 8)
    # Elevator
    draw_elevator(draw, cx75 + 4, oy + m2px(1), m2px(1.4), m2px(1.8))

    # Room labels
    # Local 1
    draw_text_centered(draw, ox + m2px(3), oy + m2px(3.5), "LOCAL 1", font_room, BLACK)
    draw_text_centered(draw, ox + m2px(3), oy + m2px(3.5) + 14, "45 m²", font_room_sm, BLACK)
    draw_text_centered(draw, ox + m2px(3), oy + m2px(3.5) + 26, "6.00 × 7.50", font_dim_sm, RED)

    # Local 2
    draw_text_centered(draw, ox + m2px(12), oy + m2px(3.5), "LOCAL 2", font_room, BLACK)
    draw_text_centered(draw, ox + m2px(12), oy + m2px(3.5) + 14, "45 m²", font_room_sm, BLACK)
    draw_text_centered(draw, ox + m2px(12), oy + m2px(3.5) + 26, "6.00 × 7.50", font_dim_sm, RED)

    # Cochera
    draw_text_centered(draw, ox + m2px(3), oy + m2px(9.5), "COCHERA", font_room, BLACK)
    draw_text_centered(draw, ox + m2px(3), oy + m2px(9.5) + 14, "30 m²", font_room_sm, BLACK)
    draw_text_centered(draw, ox + m2px(3), oy + m2px(9.5) + 26, "6.00 × 4.50", font_dim_sm, RED)

    # Patio servicio
    draw_text_centered(draw, ox + m2px(12), oy + m2px(9.5), "PATIO SERV.", font_room, BLACK)
    draw_text_centered(draw, ox + m2px(12), oy + m2px(9.5) + 14, "28 m²", font_room_sm, BLACK)
    draw_text_centered(draw, ox + m2px(12), oy + m2px(9.5) + 26, "6.00 × 4.50", font_dim_sm, RED)

    # Hall
    draw_text_centered(draw, ox + m2px(7.5), oy + m2px(9.5), "HALL", font_room, BLACK)
    draw_text_centered(draw, ox + m2px(7.5), oy + m2px(9.5) + 14, "15 m²", font_room_sm, BLACK)
    draw_text_centered(draw, ox + m2px(7.5), oy + m2px(9.5) + 26, "3.00 × 5.00", font_dim_sm, RED)

    # Core label
    draw_text_centered(draw, ox + m2px(7.5), oy + m2px(3.5), "CORE", font_room_sm, GRAY_DARK)
    draw_text_centered(draw, ox + m2px(7.5), oy + m2px(3.5) + 12, "3.00 × 7.00", font_dim_sm, RED)

    # Doors
    draw_door(draw, cx6 + 10, oy + y_core_end + m2px(0.5), m2px(0.9), label='P1')
    draw_door(draw, ox + m2px(2), oy + bh - 4, m2px(1.2), swing='down', label='P2')
    draw_door(draw, ox + m2px(11), oy + bh - 4, m2px(1.2), swing='down', label='P3')
    draw_door(draw, ox + m2px(2), oy + y_mid - 4, m2px(0.9), swing='down', label='P4')

    # Windows
    draw_window(draw, ox + m2px(1.5), oy, m2px(2), vertical=False, label='V1')
    draw_window(draw, ox + m2px(10), oy, m2px(2), vertical=False, label='V2')
    draw_window(draw, ox, oy + m2px(3), m2px(2), vertical=True, label='V3')
    draw_window(draw, ox + bw, oy + m2px(3), m2px(2), vertical=True, label='V4')

    # Dimensions - bottom
    draw_dim_h(draw, ox, ox + m2px(6), oy + bh, "6.00", 25)
    draw_dim_h(draw, ox + m2px(6), ox + m2px(9), oy + bh, "3.00", 25)
    draw_dim_h(draw, ox + m2px(9), ox + bw, oy + bh, "6.00", 25)
    draw_dim_h(draw, ox, ox + bw, oy + bh, "15.00", 45)

    # Dimensions - right
    draw_dim_v(draw, oy, oy + m2px(7.5), ox + bw, "7.50", 25)
    draw_dim_v(draw, oy + m2px(7.5), oy + bh, ox + bw, "4.50", 25)
    draw_dim_v(draw, oy, oy + bh, ox + bw, "12.00", 50)


def draw_piso_tipo(draw, ox, oy, floor_name, npt_text):
    """Draw Piso Tipo (Depto A + Depto B)"""
    bw = m2px(BLDG_W)
    bh = m2px(BLDG_H)

    draw_text_centered(draw, ox + bw//2, oy - 65, f"{floor_name} — 160 m²", font_subtitle, BLACK)
    draw_text_centered(draw, ox + bw//2, oy - 48, npt_text, font_npt, GRAY_DARK)

    draw_structural_axes(draw, ox, oy, bw, bh)
    draw_columns_at_axes(draw, ox, oy)

    # Exterior walls
    draw.rectangle([ox, oy, ox+bw, oy+bh], outline=BLACK, width=4)

    # Core (6-9, 0-7)
    cx6 = ox + m2px(6)
    cx9 = ox + m2px(9)
    cx75 = ox + m2px(7.5)
    y_core = m2px(7)

    draw.line([(cx6, oy), (cx6, oy + bh)], fill=BLACK, width=4)
    draw.line([(cx9, oy), (cx9, oy + bh)], fill=BLACK, width=4)
    draw.line([(cx6, oy + y_core), (cx9, oy + y_core)], fill=BLACK, width=3)
    draw.line([(cx75, oy), (cx75, oy + y_core)], fill=BLACK, width=2)

    # Pasillo central y=7 to y=8.5 (1.5m wide)
    y_pasillo_top = m2px(7)
    y_pasillo_bot = m2px(8.5)
    draw.line([(ox, oy + y_pasillo_bot), (cx6, oy + y_pasillo_bot)], fill=BLACK, width=2)
    draw.line([(cx9, oy + y_pasillo_bot), (ox + bw, oy + y_pasillo_bot)], fill=BLACK, width=2)

    # Stairs and elevator
    draw_stairs(draw, cx6 + 4, oy + 4, m2px(1.4), y_core - 8)
    draw_elevator(draw, cx75 + 4, oy + m2px(1), m2px(1.4), m2px(1.8))

    # --- DEPTO A (left, 0-6m) ---
    # Living 6.75×5 at top? Let's adapt:
    # Balcón: 0-6, 0-1 (y) => 6×1=6m² (on facade)
    # Actually: balcón outside at y<0, so:
    # Living: 0-6, 0-5 => actually let's lay out by y from top
    # Balcón strip: 0-6, 11-12 => 6×1=6m² (on exterior facade bottom)
    # Living: 0-4.5, 8.5-12 => but pasillo is at 7-8.5...

    # Better layout for Depto A (left half, 0 to 6m wide, 0 to 12m tall):
    # Top area (0 to 7 on y):
    #   Dorm1: 0-4.5, 0-3.5 => 4.5×3.5=15.75≈14m² (after wall adjust)
    #   Cocina: 4.5-6, 0-3.5 => 1.5... too narrow.

    # Let me simplify the layout to match given areas:
    # Depto A spans x=0..6, with rooms:
    # Row 1 (y=0..3.5): Dorm1 (4.5×3.5=~14m²) | Baño (1.5×3.5≈5m²... close to 2.25×2.5)
    # Hmm areas don't perfectly tile. Let me just place them reasonably:

    # Depto A:
    # Dorm1: 0-4, 0-3.5 = ~14m²
    # Cocina: 4-6, 0-3.5 = ~7m² (close to 8)
    # Living: 0-6, 3.5-7 = ~21m² (close to 25 with balcón contribution)
    # Dorm2: 0-4, 8.5-11 = ~10m²
    # Baño: 4-6, 8.5-11 = ~5m²
    # Balcón: 0-6, 11-12 = 6m²

    # Depto A interior walls
    # Horizontal at y=3.5 (between dorm/cocina row and living)
    draw.line([(ox, oy + m2px(3.5)), (cx6, oy + m2px(3.5))], fill=BLACK, width=2)
    # Vertical at x=4 (dorm1|cocina, dorm2|baño)
    draw.line([(ox + m2px(4), oy), (ox + m2px(4), oy + m2px(3.5))], fill=BLACK, width=2)
    draw.line([(ox + m2px(4), oy + y_pasillo_bot), (ox + m2px(4), oy + m2px(11))], fill=BLACK, width=2)
    # Horizontal at y=11 (balcón)
    draw.line([(ox, oy + m2px(11)), (cx6, oy + m2px(11))], fill=BLACK, width=2)

    # Depto B interior walls (mirror: x=9..15)
    draw.line([(cx9, oy + m2px(3.5)), (ox + bw, oy + m2px(3.5))], fill=BLACK, width=2)
    draw.line([(ox + m2px(11), oy), (ox + m2px(11), oy + m2px(3.5))], fill=BLACK, width=2)
    draw.line([(ox + m2px(11), oy + y_pasillo_bot), (ox + m2px(11), oy + m2px(11))], fill=BLACK, width=2)
    draw.line([(cx9, oy + m2px(11)), (ox + bw, oy + m2px(11))], fill=BLACK, width=2)

    # Room labels - Depto A
    def rlabel(cx, cy, name, area, dims):
        draw_text_centered(draw, cx, cy, name, font_room, BLACK)
        draw_text_centered(draw, cx, cy + 13, area, font_room_sm, BLACK)
        draw_text_centered(draw, cx, cy + 24, dims, font_dim_sm, RED)

    rlabel(ox + m2px(2), oy + m2px(1.7), "DORM 1", "14 m²", "4.00×3.50")
    rlabel(ox + m2px(5), oy + m2px(1.7), "COCINA", "8 m²", "2.00×3.50")
    rlabel(ox + m2px(3), oy + m2px(5.2), "LIVING", "25 m²", "6.00×3.50")
    rlabel(ox + m2px(2), oy + m2px(9.7), "DORM 2", "10 m²", "4.00×2.50")
    rlabel(ox + m2px(5), oy + m2px(9.7), "BAÑO", "5 m²", "2.00×2.50")
    rlabel(ox + m2px(3), oy + m2px(11.5), "BALCÓN", "6 m²", "6.00×1.00")

    # Room labels - Depto B (mirror)
    rlabel(ox + m2px(13), oy + m2px(1.7), "DORM 1", "14 m²", "4.00×3.50")
    rlabel(ox + m2px(10), oy + m2px(1.7), "COCINA", "8 m²", "2.00×3.50")
    rlabel(ox + m2px(12), oy + m2px(5.2), "LIVING", "25 m²", "6.00×3.50")
    rlabel(ox + m2px(13), oy + m2px(9.7), "DORM 2", "10 m²", "4.00×2.50")
    rlabel(ox + m2px(10), oy + m2px(9.7), "BAÑO", "5 m²", "2.00×2.50")
    rlabel(ox + m2px(12), oy + m2px(11.5), "BALCÓN", "6 m²", "6.00×1.00")

    # Pasillo label
    draw_text_centered(draw, ox + m2px(7.5), oy + m2px(7.7), "PASILLO", font_room_sm, GRAY_DARK)

    # Core
    draw_text_centered(draw, ox + m2px(7.5), oy + m2px(3.5), "CORE", font_room_sm, GRAY_DARK)

    # Depto labels
    draw.text((ox + 5, oy + 5), "DEPTO A", font=font_label, fill=ORANGE)
    draw.text((ox + bw - 60, oy + 5), "DEPTO B", font=font_label, fill=ORANGE)

    # Doors
    draw_door(draw, cx6 + 8, oy + y_core + m2px(0.3), m2px(0.8), label='P5')
    draw_door(draw, ox + m2px(2), oy + m2px(3.5) - 2, m2px(0.8), swing='down', label='P6')
    draw_door(draw, ox + m2px(4.2), oy + m2px(3.5) - 2, m2px(0.7), swing='down', label='P7')
    draw_door(draw, ox + m2px(1), oy + y_pasillo_bot + 2, m2px(0.8), label='P8')
    draw_door(draw, ox + m2px(4.2), oy + y_pasillo_bot + 2, m2px(0.7), label='P9')
    # Mirror for B
    draw_door(draw, cx9 + 8, oy + y_core + m2px(0.3), m2px(0.8), label='P10')
    draw_door(draw, ox + m2px(10), oy + m2px(3.5) - 2, m2px(0.8), swing='down', label='P11')
    draw_door(draw, ox + m2px(11.2), oy + y_pasillo_bot + 2, m2px(0.8), label='P12')

    # Windows
    draw_window(draw, ox + m2px(1), oy, m2px(2), label='V5')
    draw_window(draw, ox + m2px(10), oy, m2px(2), label='V6')
    draw_window(draw, ox, oy + m2px(4.5), m2px(2), vertical=True, label='V7')
    draw_window(draw, ox + bw, oy + m2px(4.5), m2px(2), vertical=True, label='V8')

    # Dimensions
    draw_dim_h(draw, ox, ox + m2px(6), oy + bh, "6.00", 25)
    draw_dim_h(draw, ox + m2px(6), ox + m2px(9), oy + bh, "3.00", 25)
    draw_dim_h(draw, ox + m2px(9), ox + bw, oy + bh, "6.00", 25)
    draw_dim_h(draw, ox, ox + bw, oy + bh, "15.00", 45)
    draw_dim_v(draw, oy, oy + bh, ox + bw, "12.00", 50)


def draw_terraza(draw, ox, oy):
    """Draw Terraza"""
    bw = m2px(BLDG_W)
    bh = m2px(BLDG_H)

    draw_text_centered(draw, ox + bw//2, oy - 65, "TERRAZA — 160 m²", font_subtitle, BLACK)
    draw_text_centered(draw, ox + bw//2, oy - 48, "NPT +8.80", font_npt, GRAY_DARK)

    # Dashed perimeter (baranda)
    for side in [(ox, oy, ox+bw, oy), (ox+bw, oy, ox+bw, oy+bh),
                 (ox, oy+bh, ox+bw, oy+bh), (ox, oy, ox, oy+bh)]:
        draw_dashed_line(draw, *side, BLACK, 2, 10, 5)

    # Core
    cx6 = ox + m2px(6)
    cx9 = ox + m2px(9)
    draw.rectangle([cx6, oy, cx9, oy + m2px(7)], outline=BLACK, width=3)
    cx75 = ox + m2px(7.5)
    draw.line([(cx75, oy), (cx75, oy + m2px(7))], fill=BLACK, width=2)
    draw_stairs(draw, cx6 + 4, oy + 4, m2px(1.4), m2px(7) - 8)
    draw_elevator(draw, cx75 + 4, oy + m2px(1), m2px(1.4), m2px(1.8))

    # Sala máquinas (4×3)
    smx = ox + m2px(0.5)
    smy = oy + m2px(0.5)
    draw.rectangle([smx, smy, smx + m2px(4), smy + m2px(3)], outline=BLACK, width=2)
    draw_text_centered(draw, smx + m2px(2), smy + m2px(1.2), "SALA MÁQUINAS", font_room, BLACK)
    draw_text_centered(draw, smx + m2px(2), smy + m2px(1.2) + 14, "12 m²", font_room_sm, BLACK)
    draw_text_centered(draw, smx + m2px(2), smy + m2px(1.2) + 26, "4.00 × 3.00", font_dim_sm, RED)

    # Tanque agua (3×2)
    tx = ox + m2px(10)
    ty = oy + m2px(0.5)
    draw.rectangle([tx, ty, tx + m2px(3), ty + m2px(2)], outline=BLACK, width=2)
    draw_text_centered(draw, tx + m2px(1.5), ty + m2px(0.7), "TANQUE AGUA", font_room, BLACK)
    draw_text_centered(draw, tx + m2px(1.5), ty + m2px(0.7) + 14, "6 m²", font_room_sm, BLACK)
    draw_text_centered(draw, tx + m2px(1.5), ty + m2px(0.7) + 26, "3.00 × 2.00", font_dim_sm, RED)

    # Espacio común
    draw_text_centered(draw, ox + m2px(7.5), oy + m2px(9.5), "ESPACIO COMÚN ABIERTO", font_room, BLACK)
    draw_text_centered(draw, ox + m2px(7.5), oy + m2px(9.5) + 14, "142 m²", font_room_sm, BLACK)

    # Baranda label
    draw.text((ox + 5, oy + bh + 8), "--- Baranda perimetral h=1.20m", font=font_dim, fill=GRAY_DARK)

    draw_dim_h(draw, ox, ox + bw, oy + bh, "15.00", 30)
    draw_dim_v(draw, oy, oy + bh, ox + bw, "12.00", 30)


def draw_corte_esquematico(draw, ox, oy):
    """Draw schematic section showing heights"""
    draw_text_centered(draw, ox + 150, oy - 15, "CORTE ESQUEMÁTICO", font_subtitle, BLACK)

    w = 300
    floors = [
        ("PB", 3.20, "±0.00"),
        ("PISO 1", 2.80, "+3.20"),
        ("PISO 2", 2.80, "+6.00"),
        ("TERRAZA", 0, "+8.80"),
    ]

    y_cursor = oy + 280  # bottom
    total_h = 3.20 + 2.80 + 2.80
    px_per_m = 250 / total_h

    # Ground line
    draw.line([(ox - 20, y_cursor), (ox + w + 20, y_cursor)], fill=BLACK, width=3)

    for i, (name, height, npt) in enumerate(floors):
        top_y = y_cursor - int((3.20 + 2.80 * min(i, 2)) * px_per_m) if i > 0 else y_cursor
        if i == 0:
            top_y = y_cursor
            floor_top = y_cursor - int(3.20 * px_per_m)
        elif i == 1:
            top_y = y_cursor - int(3.20 * px_per_m)
            floor_top = y_cursor - int((3.20 + 2.80) * px_per_m)
        elif i == 2:
            top_y = y_cursor - int((3.20 + 2.80) * px_per_m)
            floor_top = y_cursor - int((3.20 + 2.80 + 2.80) * px_per_m)
        else:
            top_y = y_cursor - int((3.20 + 2.80 + 2.80) * px_per_m)
            floor_top = top_y

        if i < 3:
            # Floor slab
            draw.rectangle([ox, floor_top - 5, ox + w, floor_top + 5], fill=GRAY, outline=BLACK, width=1)
            # Height dimension
            draw_text_centered(draw, ox + w + 40, (top_y + floor_top) // 2, f"h={height}m", font_dim, RED)

        # Level label
        draw.line([(ox - 15, top_y), (ox + w + 15, top_y)], fill=BLACK, width=1)
        draw.text((ox - 15, top_y - 14), npt, font=font_dim, fill=RED)
        draw.text((ox + 5, top_y - 14 if i == 3 else (top_y + floor_top)//2 - 5), name, font=font_room, fill=BLACK)

    # Roof slab
    roof_y = y_cursor - int(total_h * px_per_m)
    draw.rectangle([ox, roof_y - 5, ox + w, roof_y + 5], fill=GRAY, outline=BLACK, width=2)

    # Total height
    draw.text((ox + w + 30, (y_cursor + roof_y)//2), "Total: 8.80m", font=font_label, fill=RED)


def draw_scale_bar(draw, ox, oy):
    """Draw scale bar and north arrow"""
    # Scale bar
    draw.text((ox, oy), "ESCALA 1:100  (1m = 32px)", font=font_label, fill=BLACK)
    for i in range(5):
        x1 = ox + i * m2px(1)
        x2 = ox + (i+1) * m2px(1)
        fill = BLACK if i % 2 == 0 else WHITE
        draw.rectangle([x1, oy + 18, x2, oy + 26], fill=fill, outline=BLACK, width=1)
        draw.text((x1, oy + 28), f"{i}m", font=font_dim_sm, fill=BLACK)
    draw.text((ox + 5 * m2px(1), oy + 28), "5m", font=font_dim_sm, fill=BLACK)

    # North arrow
    nx = ox + 250
    ny = oy + 5
    draw.polygon([(nx, ny), (nx-8, ny+25), (nx+8, ny+25)], fill=BLACK, outline=BLACK)
    draw.polygon([(nx, ny), (nx+8, ny+25), (nx, ny+25)], fill=WHITE, outline=BLACK)
    draw.text((nx - 3, ny - 14), "N", font=font_label, fill=BLACK)


def draw_tables(draw, ox, oy):
    """Draw summary tables"""
    # --- Resumen de superficies ---
    draw.text((ox, oy), "RESUMEN DE SUPERFICIES", font=font_subtitle, fill=BLACK)
    table_data = [
        ("NIVEL", "LOCAL", "SUP. (m²)"),
        ("PB", "Local 1", "45.00"),
        ("PB", "Local 2", "45.00"),
        ("PB", "Cochera", "30.00"),
        ("PB", "Patio serv.", "28.00"),
        ("PB", "Hall", "15.00"),
        ("PB", "Core", "17.00"),
        ("P1", "Depto A", "82.00"),
        ("P1", "Depto B", "82.00"),
        ("P2", "Depto A", "82.00"),
        ("P2", "Depto B", "82.00"),
        ("Terraza", "Sala máq.", "12.00"),
        ("Terraza", "Tanque", "6.00"),
        ("Terraza", "Común", "142.00"),
        ("", "TOTAL", "660.00"),
    ]

    ty = oy + 28
    col_w = [60, 120, 80]
    for i, row in enumerate(table_data):
        rx = ox
        for j, cell in enumerate(row):
            f = font_table_header if i == 0 or i == len(table_data)-1 else font_table
            draw.text((rx + 4, ty), cell, font=f, fill=BLACK)
            draw.rectangle([rx, ty - 2, rx + col_w[j], ty + 14], outline=GRAY, width=1)
            rx += col_w[j]
        ty += 16

    # --- Planilla de aberturas ---
    ax = ox + 300
    draw.text((ax, oy), "PLANILLA DE ABERTURAS", font=font_subtitle, fill=BLACK)
    ab_header = ("REF", "TIPO", "MEDIDA", "ANTEP.", "UBICACIÓN", "MAT.")
    ab_data = [
        ("P1", "Puerta", "0.90×2.10", "-", "Hall PB", "Chapa"),
        ("P2", "Portón", "2.40×2.40", "-", "Cochera", "Chapa"),
        ("P3", "Puerta", "0.90×2.10", "-", "Patio", "Chapa"),
        ("P4", "Puerta", "0.80×2.10", "-", "Local1", "MDF"),
        ("P5", "Puerta", "0.80×2.10", "-", "Pasillo", "MDF"),
        ("P6", "Puerta", "0.80×2.10", "-", "Dorm1", "MDF"),
        ("P7", "Puerta", "0.70×2.10", "-", "Cocina", "MDF"),
        ("P8", "Puerta", "0.80×2.10", "-", "Dorm2", "MDF"),
        ("P9", "Puerta", "0.70×2.10", "-", "Baño", "MDF"),
        ("P10-12", "Puerta", "ídem", "-", "Depto B", "MDF"),
        ("V1", "Ventana", "2.00×1.50", "0.90", "Local1", "Al."),
        ("V2", "Ventana", "2.00×1.50", "0.90", "Local2", "Al."),
        ("V3", "Ventana", "1.50×1.20", "0.90", "Local1", "Al."),
        ("V4", "Ventana", "1.50×1.20", "0.90", "Local2", "Al."),
        ("V5-V6", "Ventana", "2.00×1.50", "0.90", "Dorm1", "Al."),
        ("V7-V8", "Ventana", "1.50×1.20", "0.90", "Living", "Al."),
    ]

    ab_col_w = [55, 55, 75, 50, 70, 45]
    aty = oy + 28
    for j, cell in enumerate(ab_header):
        draw.text((ax + sum(ab_col_w[:j]) + 3, aty), cell, font=font_table_header, fill=BLACK)
        draw.rectangle([ax + sum(ab_col_w[:j]), aty - 2, ax + sum(ab_col_w[:j+1]), aty + 14], outline=GRAY, width=1)
    aty += 16

    for row in ab_data:
        for j, cell in enumerate(row):
            draw.text((ax + sum(ab_col_w[:j]) + 3, aty), cell, font=font_table, fill=BLACK)
            draw.rectangle([ax + sum(ab_col_w[:j]), aty - 2, ax + sum(ab_col_w[:j+1]), aty + 14], outline=GRAY, width=1)
        aty += 16

    # --- Tabla de alturas ---
    hx = ox + 660
    draw.text((hx, oy), "TABLA DE ALTURAS", font=font_subtitle, fill=BLACK)
    h_data = [
        ("NIVEL", "ALTURA LIBRE", "LOSA", "NPT"),
        ("PB", "3.00 m", "0.20 m", "±0.00"),
        ("Piso 1", "2.60 m", "0.20 m", "+3.20"),
        ("Piso 2", "2.60 m", "0.20 m", "+6.00"),
        ("Terraza", "-", "0.20 m", "+8.80"),
        ("", "TOTAL", "", "11.80 m"),
    ]
    h_col_w = [65, 90, 60, 60]
    hty = oy + 28
    for i, row in enumerate(h_data):
        for j, cell in enumerate(row):
            f = font_table_header if i == 0 or i == len(h_data)-1 else font_table
            draw.text((hx + sum(h_col_w[:j]) + 3, hty), cell, font=f, fill=BLACK)
            draw.rectangle([hx + sum(h_col_w[:j]), hty - 2, hx + sum(h_col_w[:j+1]), hty + 14], outline=GRAY, width=1)
        hty += 16


def draw_title_block(draw, ox, oy, w):
    """Professional title block"""
    draw.rectangle([ox, oy, ox + w, oy + 60], outline=BLACK, width=2)
    draw.line([(ox + w//3, oy), (ox + w//3, oy + 60)], fill=BLACK, width=1)
    draw.line([(ox + 2*w//3, oy), (ox + 2*w//3, oy + 60)], fill=BLACK, width=1)

    draw.text((ox + 10, oy + 5), "PROYECTO: EDIFICIO MULTIFAMILIAR 4 NIVELES", font=font_label, fill=BLACK)
    draw.text((ox + 10, oy + 22), "PLANO: ARQUITECTURA + INSTALACIONES", font=font_small, fill=BLACK)
    draw.text((ox + 10, oy + 38), "ESCALA: 1:100", font=font_small, fill=BLACK)

    draw.text((ox + w//3 + 10, oy + 5), "SUPERFICIE TOTAL: 660 m²", font=font_label, fill=BLACK)
    draw.text((ox + w//3 + 10, oy + 22), "NIVELES: PB + 2 Pisos + Terraza", font=font_small, fill=BLACK)
    draw.text((ox + w//3 + 10, oy + 38), "LOTE: 15.00 × 12.00 m", font=font_small, fill=BLACK)

    draw.text((ox + 2*w//3 + 10, oy + 5), "FECHA: ABR 2026", font=font_label, fill=BLACK)
    draw.text((ox + 2*w//3 + 10, oy + 22), "HOJA: 1/1", font=font_small, fill=BLACK)
    draw.text((ox + 2*w//3 + 10, oy + 38), "GENERADO POR: SOLE AI", font=font_small, fill=BLACK)


# ============================================================
# SECTION 2: SANITARY INSTALLATIONS
# ============================================================

def draw_outline_light(draw, ox, oy, floor_type='pb'):
    """Draw light gray building outline"""
    bw = m2px(BLDG_W)
    bh = m2px(BLDG_H)
    draw.rectangle([ox, oy, ox+bw, oy+bh], outline=GRAY, width=2)

    cx6 = ox + m2px(6)
    cx9 = ox + m2px(9)

    if floor_type == 'pb':
        draw.line([(cx6, oy), (cx6, oy + bh)], fill=GRAY, width=2)
        draw.line([(cx9, oy), (cx9, oy + bh)], fill=GRAY, width=2)
        draw.line([(ox, oy + m2px(7.5)), (cx6, oy + m2px(7.5))], fill=GRAY, width=1)
        draw.line([(cx9, oy + m2px(7.5)), (ox + bw, oy + m2px(7.5))], fill=GRAY, width=1)
        draw.line([(cx6, oy + m2px(7)), (cx9, oy + m2px(7))], fill=GRAY, width=1)
    elif floor_type == 'tipo':
        draw.line([(cx6, oy), (cx6, oy + bh)], fill=GRAY, width=2)
        draw.line([(cx9, oy), (cx9, oy + bh)], fill=GRAY, width=2)
        draw.line([(cx6, oy + m2px(7)), (cx9, oy + m2px(7))], fill=GRAY, width=1)
        draw.line([(ox, oy + m2px(3.5)), (cx6, oy + m2px(3.5))], fill=GRAY, width=1)
        draw.line([(cx9, oy + m2px(3.5)), (ox+bw, oy + m2px(3.5))], fill=GRAY, width=1)
        draw.line([(ox + m2px(4), oy), (ox + m2px(4), oy + m2px(3.5))], fill=GRAY, width=1)
        draw.line([(ox + m2px(11), oy), (ox + m2px(11), oy + m2px(3.5))], fill=GRAY, width=1)
        draw.line([(ox, oy + m2px(8.5)), (cx6, oy + m2px(8.5))], fill=GRAY, width=1)
        draw.line([(cx9, oy + m2px(8.5)), (ox+bw, oy + m2px(8.5))], fill=GRAY, width=1)
        draw.line([(ox + m2px(4), oy + m2px(8.5)), (ox + m2px(4), oy + m2px(11))], fill=GRAY, width=1)
        draw.line([(ox + m2px(11), oy + m2px(8.5)), (ox + m2px(11), oy + m2px(11))], fill=GRAY, width=1)
        draw.line([(ox, oy + m2px(11)), (cx6, oy + m2px(11))], fill=GRAY, width=1)
        draw.line([(cx9, oy + m2px(11)), (ox+bw, oy + m2px(11))], fill=GRAY, width=1)
    elif floor_type == 'terraza':
        for side in [(ox, oy, ox+bw, oy), (ox+bw, oy, ox+bw, oy+bh),
                     (ox, oy+bh, ox+bw, oy+bh), (ox, oy, ox, oy+bh)]:
            draw_dashed_line(draw, *side, GRAY, 1, 8, 4)
        draw.rectangle([cx6, oy, cx9, oy + m2px(7)], outline=GRAY, width=2)


def draw_fixture(draw, x, y, fixture_type, label, color=BLUE):
    """Draw plumbing fixture symbol"""
    if fixture_type == 'WC':
        # Toilet: oval + tank rectangle
        draw.ellipse([x-8, y-5, x+8, y+5], outline=color, width=2)
        draw.rectangle([x-6, y+5, x+6, y+12], outline=color, width=1)
        draw.text((x-8, y-16), label, font=font_dim_sm, fill=color)
    elif fixture_type == 'Lv':
        # Sink: small rectangle
        draw.rectangle([x-7, y-5, x+7, y+5], outline=color, width=2)
        draw.ellipse([x-3, y-2, x+3, y+2], outline=color, width=1)
        draw.text((x-6, y-16), label, font=font_dim_sm, fill=color)
    elif fixture_type == 'Du':
        # Shower: square with X
        s = 12
        draw.rectangle([x-s, y-s, x+s, y+s], outline=color, width=2)
        draw.line([(x-s, y-s), (x+s, y+s)], fill=color, width=1)
        draw.line([(x+s, y-s), (x-s, y+s)], fill=color, width=1)
        draw.text((x-8, y-s-12), label, font=font_dim_sm, fill=color)
    elif fixture_type == 'Pil':
        # Kitchen sink: double rectangle
        draw.rectangle([x-12, y-5, x, y+5], outline=color, width=2)
        draw.rectangle([x, y-5, x+12, y+5], outline=color, width=2)
        draw.text((x-10, y-16), label, font=font_dim_sm, fill=color)
    elif fixture_type == 'Lr':
        # Washing machine: circle in square
        draw.rectangle([x-8, y-8, x+8, y+8], outline=color, width=2)
        draw.ellipse([x-5, y-5, x+5, y+5], outline=color, width=1)
        draw.text((x-6, y-18), label, font=font_dim_sm, fill=color)
    elif fixture_type == 'BD':
        # Floor drain: circle with cross
        draw.ellipse([x-6, y-6, x+6, y+6], outline=color, width=2)
        draw.line([(x-4, y), (x+4, y)], fill=color, width=1)
        draw.line([(x, y-4), (x, y+4)], fill=color, width=1)
        draw.text((x-8, y-16), label, font=font_dim_sm, fill=color)
    elif fixture_type == 'BS':
        # Bajada sanitaria: filled circle
        draw.ellipse([x-8, y-8, x+8, y+8], fill=color, outline=color, width=2)
        draw.text((x-8, y+10), label, font=font_dim_sm, fill=color)
    elif fixture_type == 'VC':
        # Ventilación: empty circle with V
        draw.ellipse([x-8, y-8, x+8, y+8], outline=color, width=2)
        draw_text_centered(draw, x, y, "V", font_dim_sm, color)
        draw.text((x-8, y+10), label, font=font_dim_sm, fill=color)


def draw_sanitary_pb(draw, ox, oy):
    """PB sanitary installation"""
    draw_outline_light(draw, ox, oy, 'pb')
    bw = m2px(BLDG_W)
    bh = m2px(BLDG_H)

    draw_text_centered(draw, ox + bw//2, oy - 20, "PB — SANITARIAS", font_label, BLUE)

    # Patio serv has basic drainage
    # Floor drain in cochera
    draw_fixture(draw, ox + m2px(3), oy + m2px(10), 'BD', "BD1", BLUE)

    # Floor drain in patio
    draw_fixture(draw, ox + m2px(12), oy + m2px(10), 'BD', "BD2", BLUE)

    # Bajada sanitaria - in core area
    bsx = ox + m2px(8.5)
    bsy = oy + m2px(6)
    draw_fixture(draw, bsx, bsy, 'BS', "BS ø110", BLUE)

    # Ventilación
    draw_fixture(draw, bsx + 25, bsy, 'VC', "VC ø63", BLUE)

    # Pipe from BD to BS
    draw_dashed_line(draw, ox + m2px(3), oy + m2px(10), bsx, oy + m2px(10), BLUE, 2, 6, 3)
    draw_dashed_line(draw, bsx, oy + m2px(10), bsx, bsy + 10, BLUE, 2, 6, 3)
    draw.text((ox + m2px(5), oy + m2px(10) + 5), "ø110 PVC", font=font_dim_sm, fill=BLUE)

    draw_dashed_line(draw, ox + m2px(12), oy + m2px(10), ox + m2px(12), oy + m2px(7.5), BLUE, 2, 6, 3)
    draw_dashed_line(draw, ox + m2px(12), oy + m2px(7.5), bsx, oy + m2px(7.5), BLUE, 2, 6, 3)

    # Cold water supply (solid blue)
    draw.line([(ox + m2px(7.5), oy), (ox + m2px(7.5), oy + m2px(2))], fill=BLUE_LIGHT, width=2)
    draw.text((ox + m2px(7.5) + 5, oy + m2px(1)), "AF ø25", font=font_dim_sm, fill=BLUE_LIGHT)


def draw_sanitary_tipo(draw, ox, oy):
    """Piso Tipo sanitary installation"""
    draw_outline_light(draw, ox, oy, 'tipo')
    bw = m2px(BLDG_W)

    draw_text_centered(draw, ox + bw//2, oy - 20, "PISO TIPO — SANITARIAS", font_label, BLUE)

    # Bajada sanitaria in core
    bsx = ox + m2px(8.5)
    bsy = oy + m2px(6)
    draw_fixture(draw, bsx, bsy, 'BS', "BS ø110", BLUE)
    draw_fixture(draw, bsx + 25, bsy, 'VC', "VC ø63", BLUE)

    # --- Depto A (left) - Baño at x=4-6, y=8.5-11 ---
    bano_cx = ox + m2px(5)
    bano_cy = oy + m2px(9.5)

    draw_fixture(draw, bano_cx - 15, bano_cy - 15, 'WC', "WC", BLUE)
    draw_fixture(draw, bano_cx + 15, bano_cy - 15, 'Lv', "Lv", BLUE)
    draw_fixture(draw, bano_cx, bano_cy + 15, 'Du', "Du", BLUE)

    # Cocina at x=4-6, y=0-3.5
    coc_cx = ox + m2px(5)
    coc_cy = oy + m2px(1.5)
    draw_fixture(draw, coc_cx, coc_cy, 'Pil', "Pil", BLUE)
    draw_fixture(draw, coc_cx - 15, coc_cy + 25, 'Lr', "Lr", BLUE)

    # Pipes from baño to BS
    draw.line([(bano_cx, bano_cy - 20), (bano_cx, oy + m2px(8.5))], fill=BLUE, width=2)
    draw.line([(bano_cx, oy + m2px(8.5)), (bsx, oy + m2px(8.5))], fill=BLUE, width=2)
    draw_dashed_line(draw, bsx, oy + m2px(8.5), bsx, bsy + 10, BLUE, 2, 6, 3)
    draw.text((bano_cx + 5, oy + m2px(8.5) - 12), "ø110", font=font_dim_sm, fill=BLUE)

    # Pipes from cocina
    draw.line([(coc_cx, coc_cy + 8), (coc_cx, oy + m2px(3.5))], fill=BLUE, width=2)
    draw.line([(coc_cx, oy + m2px(3.5)), (bsx, oy + m2px(3.5))], fill=BLUE, width=2)
    draw_dashed_line(draw, bsx, oy + m2px(3.5), bsx, bsy, BLUE, 2, 6, 3)
    draw.text((coc_cx + 5, oy + m2px(3.5) - 12), "ø50", font=font_dim_sm, fill=BLUE)

    # Cold water (solid blue light)
    draw.line([(bsx - 20, oy), (bsx - 20, oy + m2px(12))], fill=BLUE_LIGHT, width=2)
    draw.text((bsx - 18, oy + 5), "AF ø20 PPF", font=font_dim_sm, fill=BLUE_LIGHT)

    # Hot water (dashed red-ish blue)
    draw_dashed_line(draw, bsx - 35, oy, bsx - 35, oy + m2px(12), (0, 50, 180), 2, 5, 3)
    draw.text((bsx - 55, oy + 5), "AC ø20", font=font_dim_sm, fill=(0, 50, 180))

    # Branch to baño
    draw.line([(bsx - 20, bano_cy), (bano_cx + 20, bano_cy)], fill=BLUE_LIGHT, width=1)
    # Branch to cocina
    draw.line([(bsx - 20, coc_cy), (coc_cx + 15, coc_cy)], fill=BLUE_LIGHT, width=1)

    # --- Depto B (mirror - right) ---
    bano_cx_b = ox + m2px(10)
    bano_cy_b = oy + m2px(9.5)

    draw_fixture(draw, bano_cx_b + 15, bano_cy_b - 15, 'WC', "WC", BLUE)
    draw_fixture(draw, bano_cx_b - 15, bano_cy_b - 15, 'Lv', "Lv", BLUE)
    draw_fixture(draw, bano_cx_b, bano_cy_b + 15, 'Du', "Du", BLUE)

    coc_cx_b = ox + m2px(10)
    coc_cy_b = oy + m2px(1.5)
    draw_fixture(draw, coc_cx_b, coc_cy_b, 'Pil', "Pil", BLUE)
    draw_fixture(draw, coc_cx_b + 15, coc_cy_b + 25, 'Lr', "Lr", BLUE)

    # Pipes Depto B
    draw.line([(bano_cx_b, bano_cy_b - 20), (bano_cx_b, oy + m2px(8.5))], fill=BLUE, width=2)
    draw.line([(bano_cx_b, oy + m2px(8.5)), (bsx, oy + m2px(8.5))], fill=BLUE, width=2)

    draw.line([(coc_cx_b, coc_cy_b + 8), (coc_cx_b, oy + m2px(3.5))], fill=BLUE, width=2)
    draw.line([(coc_cx_b, oy + m2px(3.5)), (bsx, oy + m2px(3.5))], fill=BLUE, width=2)


def draw_sanitary_terraza(draw, ox, oy):
    """Terraza sanitary"""
    draw_outline_light(draw, ox, oy, 'terraza')
    bw = m2px(BLDG_W)

    draw_text_centered(draw, ox + bw//2, oy - 20, "TERRAZA — SANITARIAS", font_label, BLUE)

    # Tanque agua
    tx = ox + m2px(10.5)
    ty = oy + m2px(1)
    draw.rectangle([tx - m2px(1.5), ty, tx + m2px(1.5), ty + m2px(2)], outline=BLUE, width=2)
    draw_text_centered(draw, tx, ty + m2px(1), "TANQUE", font_room, BLUE)
    draw_text_centered(draw, tx, ty + m2px(1) + 14, "2000 lts", font_dim_sm, BLUE)

    # Alimentación pipe going down
    draw.line([(tx, ty + m2px(2)), (tx, oy + m2px(7))], fill=BLUE_LIGHT, width=3)
    draw.text((tx + 5, oy + m2px(4)), "Alim. ø25", font=font_dim_sm, fill=BLUE_LIGHT)

    # Bajada sanitaria
    bsx = ox + m2px(8.5)
    draw_fixture(draw, bsx, oy + m2px(6), 'BS', "BS ø110", BLUE)
    draw_fixture(draw, bsx + 25, oy + m2px(6), 'VC', "VC ø63", BLUE)

    # Floor drains on terraza
    draw_fixture(draw, ox + m2px(3), oy + m2px(9), 'BD', "BD3", BLUE)
    draw_fixture(draw, ox + m2px(12), oy + m2px(9), 'BD', "BD4", BLUE)

    draw_dashed_line(draw, ox + m2px(3), oy + m2px(9), bsx, oy + m2px(9), BLUE, 2, 6, 3)
    draw_dashed_line(draw, ox + m2px(12), oy + m2px(9), bsx, oy + m2px(9), BLUE, 2, 6, 3)
    draw_dashed_line(draw, bsx, oy + m2px(9), bsx, oy + m2px(6) + 10, BLUE, 2, 6, 3)
    draw.text((ox + m2px(6), oy + m2px(9) + 5), "ø110 PVC pluvial", font=font_dim_sm, fill=BLUE)


def draw_sanitary_legend(draw, ox, oy):
    """Sanitary legend"""
    draw.text((ox, oy), "REFERENCIAS SANITARIAS", font=font_legend_bold, fill=BLUE)
    items = [
        ('WC', "Inodoro"),
        ('Lv', "Lavabo"),
        ('Du', "Ducha 0.80×0.80"),
        ('Pil', "Pileta cocina doble"),
        ('Lr', "Lavarropas"),
        ('BD', "Boca de desagüe"),
        ('BS', "Bajada sanitaria ø110"),
        ('VC', "Ventilación cañería ø63"),
    ]
    y = oy + 18
    for ftype, desc in items:
        draw_fixture(draw, ox + 12, y + 8, ftype, "", BLUE)
        draw.text((ox + 30, y + 2), desc, font=font_legend, fill=BLUE)
        y += 22

    y += 10
    draw.line([(ox, y), (ox + 30, y)], fill=BLUE, width=2)
    draw.text((ox + 35, y - 5), "Desagüe cloacal/pluvial (ø50/ø63/ø110 PVC)", font=font_legend, fill=BLUE)
    y += 16
    draw.line([(ox, y), (ox + 30, y)], fill=BLUE_LIGHT, width=2)
    draw.text((ox + 35, y - 5), "Agua fría (ø20mm PPFusión)", font=font_legend, fill=BLUE_LIGHT)
    y += 16
    draw_dashed_line(draw, ox, y, ox + 30, y, (0, 50, 180), 2, 5, 3)
    draw.text((ox + 35, y - 5), "Agua caliente (ø20mm PPFusión)", font=font_legend, fill=(0, 50, 180))


# ============================================================
# SECTION 3: ELECTRICAL INSTALLATIONS
# ============================================================

def draw_light(draw, x, y, label, color=GREEN):
    """Light fixture: circle with X"""
    r = 8
    draw.ellipse([x-r, y-r, x+r, y+r], outline=color, width=2)
    draw.line([(x-r+2, y-r+2), (x+r-2, y+r-2)], fill=color, width=1)
    draw.line([(x+r-2, y-r+2), (x-r+2, y+r-2)], fill=color, width=1)
    draw.text((x + r + 2, y - 6), label, font=font_dim_sm, fill=color)

def draw_outlet(draw, x, y, label, color=GREEN):
    """Outlet: circle with vertical line"""
    r = 6
    draw.ellipse([x-r, y-r, x+r, y+r], outline=color, width=2)
    draw.line([(x, y-r), (x, y+r)], fill=color, width=2)
    draw.text((x + r + 2, y - 6), label, font=font_dim_sm, fill=color)

def draw_switch(draw, x, y, label, color=GREEN):
    """Switch: filled dot with angled line"""
    r = 4
    draw.ellipse([x-r, y-r, x+r, y+r], fill=color, outline=color)
    draw.line([(x, y-r), (x+10, y-r-10)], fill=color, width=2)
    draw.text((x + 12, y - 12), label, font=font_dim_sm, fill=color)

def draw_tablero(draw, x, y, w, h, label, color=GREEN):
    """Tablero eléctrico: rectangle with horizontal lines"""
    draw.rectangle([x, y, x+w, y+h], outline=color, width=2)
    for i in range(1, 4):
        ly = y + i * h // 4
        draw.line([(x+2, ly), (x+w-2, ly)], fill=color, width=1)
    draw.text((x, y + h + 3), label, font=font_dim_sm, fill=color)


def draw_electrical_pb(draw, ox, oy):
    """PB electrical installation"""
    draw_outline_light(draw, ox, oy, 'pb')
    bw = m2px(BLDG_W)
    bh = m2px(BLDG_H)

    draw_text_centered(draw, ox + bw//2, oy - 20, "PB — ELÉCTRICAS", font_label, GREEN)

    # Tablero general in hall
    tgx = ox + m2px(7)
    tgy = oy + m2px(8)
    draw_tablero(draw, tgx, tgy, 25, 20, "TG", GREEN)

    # Medidor
    draw.rectangle([tgx - 35, tgy, tgx - 10, tgy + 20], outline=GREEN, width=2)
    draw_text_centered(draw, tgx - 22, tgy + 10, "M", font_dim_sm, GREEN)
    draw.text((tgx - 35, tgy + 22), "Medidor", font=font_dim_sm, fill=GREEN)

    # Acometida
    draw.text((tgx - 35, tgy + 35), "3×6mm²+T6mm²", font=font_dim_sm, fill=GREEN)

    # Local 1 - lights and outlets
    draw_light(draw, ox + m2px(3), oy + m2px(3), "60W", GREEN)
    draw_light(draw, ox + m2px(3), oy + m2px(5.5), "60W", GREEN)
    draw_outlet(draw, ox + m2px(1), oy + m2px(2), "10A", GREEN)
    draw_outlet(draw, ox + m2px(5), oy + m2px(2), "10A", GREEN)
    draw_outlet(draw, ox + m2px(1), oy + m2px(5), "10A", GREEN)
    draw_switch(draw, ox + m2px(0.5), oy + m2px(7), "S1", GREEN)
    # Wire from switch to light
    draw.line([(ox + m2px(0.5), oy + m2px(7)), (ox + m2px(0.5), oy + m2px(3)), (ox + m2px(3) - 8, oy + m2px(3))], fill=GREEN, width=1)

    # Local 2
    draw_light(draw, ox + m2px(12), oy + m2px(3), "60W", GREEN)
    draw_light(draw, ox + m2px(12), oy + m2px(5.5), "60W", GREEN)
    draw_outlet(draw, ox + m2px(10), oy + m2px(2), "10A", GREEN)
    draw_outlet(draw, ox + m2px(14), oy + m2px(2), "10A", GREEN)
    draw_outlet(draw, ox + m2px(14), oy + m2px(5), "10A", GREEN)
    draw_switch(draw, ox + m2px(14.5), oy + m2px(7), "S2", GREEN)

    # Cochera
    draw_light(draw, ox + m2px(3), oy + m2px(9.5), "100W", GREEN)
    draw_outlet(draw, ox + m2px(1), oy + m2px(9), "15A", GREEN)
    draw_switch(draw, ox + m2px(0.5), oy + m2px(8), "S3", GREEN)

    # Patio
    draw_light(draw, ox + m2px(12), oy + m2px(9.5), "60W", GREEN)
    draw_outlet(draw, ox + m2px(14), oy + m2px(9), "10A", GREEN)
    draw_switch(draw, ox + m2px(14.5), oy + m2px(8), "S4", GREEN)

    # Hall
    draw_light(draw, ox + m2px(7.5), oy + m2px(10.5), "40W", GREEN)
    draw_switch(draw, ox + m2px(6.5), oy + m2px(11.5), "S5", GREEN)

    # Core
    draw_light(draw, ox + m2px(7.5), oy + m2px(4), "40W", GREEN)

    # Wire runs from TG
    draw.line([(tgx + 25, tgy + 10), (tgx + 50, tgy + 10)], fill=GREEN, width=1)
    draw.line([(tgx + 50, tgy + 10), (tgx + 50, oy + m2px(3))], fill=GREEN, width=1)


def draw_electrical_tipo(draw, ox, oy):
    """Piso Tipo electrical"""
    draw_outline_light(draw, ox, oy, 'tipo')
    bw = m2px(BLDG_W)

    draw_text_centered(draw, ox + bw//2, oy - 20, "PISO TIPO — ELÉCTRICAS", font_label, GREEN)

    # Tablero seccional Depto A
    tsx_a = ox + m2px(5.5)
    tsy_a = oy + m2px(7.5)
    draw_tablero(draw, tsx_a, tsy_a, 22, 16, "TS-A", GREEN)

    # Tablero seccional Depto B
    tsx_b = ox + m2px(9.5)
    draw_tablero(draw, tsx_b, tsy_a, 22, 16, "TS-B", GREEN)

    # Circuit labels near tablero A
    draw.text((tsx_a - 80, tsy_a), "C1 Ilum 10A", font=font_dim_sm, fill=GREEN)
    draw.text((tsx_a - 80, tsy_a + 10), "C2 Tomas 15A", font=font_dim_sm, fill=GREEN)
    draw.text((tsx_a - 80, tsy_a + 20), "C3 Cocina 20A", font=font_dim_sm, fill=GREEN)
    draw.text((tsx_a - 80, tsy_a + 30), "C4 Baño GFCI 15A", font=font_dim_sm, fill=GREEN)

    # --- DEPTO A lights/outlets ---
    # Dorm 1
    draw_light(draw, ox + m2px(2), oy + m2px(1.7), "40W", GREEN)
    draw_outlet(draw, ox + m2px(0.5), oy + m2px(1), "10A", GREEN)
    draw_outlet(draw, ox + m2px(3.5), oy + m2px(1), "10A", GREEN)
    draw_switch(draw, ox + m2px(0.5), oy + m2px(3), "S", GREEN)

    # Cocina
    draw_light(draw, ox + m2px(5), oy + m2px(1.7), "60W", GREEN)
    draw_outlet(draw, ox + m2px(4.5), oy + m2px(0.5), "15A", GREEN)
    draw_outlet(draw, ox + m2px(5.5), oy + m2px(0.5), "20A", GREEN)
    draw_outlet(draw, ox + m2px(5.5), oy + m2px(2.5), "15A", GREEN)
    draw_switch(draw, ox + m2px(4.2), oy + m2px(3), "S", GREEN)

    # Living
    draw_light(draw, ox + m2px(2), oy + m2px(5.2), "60W", GREEN)
    draw_light(draw, ox + m2px(4.5), oy + m2px(5.2), "60W", GREEN)
    draw_outlet(draw, ox + m2px(0.5), oy + m2px(4.5), "10A", GREEN)
    draw_outlet(draw, ox + m2px(0.5), oy + m2px(6), "10A", GREEN)
    draw_outlet(draw, ox + m2px(5.5), oy + m2px(5), "10A", GREEN)
    draw_switch(draw, ox + m2px(2), oy + m2px(3.8), "S", GREEN)

    # Dorm 2
    draw_light(draw, ox + m2px(2), oy + m2px(9.7), "40W", GREEN)
    draw_outlet(draw, ox + m2px(0.5), oy + m2px(9), "10A", GREEN)
    draw_outlet(draw, ox + m2px(3.5), oy + m2px(9), "10A", GREEN)
    draw_switch(draw, ox + m2px(0.5), oy + m2px(8.8), "S", GREEN)

    # Baño
    draw_light(draw, ox + m2px(5), oy + m2px(9.7), "40W", GREEN)
    draw_outlet(draw, ox + m2px(5.5), oy + m2px(9), "GFCI", GREEN)
    draw_switch(draw, ox + m2px(4.2), oy + m2px(8.8), "S", GREEN)

    # Balcón
    draw_light(draw, ox + m2px(3), oy + m2px(11.5), "25W", GREEN)
    draw_switch(draw, ox + m2px(1), oy + m2px(10.8), "S", GREEN)

    # --- DEPTO B (mirror) ---
    draw_light(draw, ox + m2px(13), oy + m2px(1.7), "40W", GREEN)
    draw_outlet(draw, ox + m2px(14.5), oy + m2px(1), "10A", GREEN)
    draw_outlet(draw, ox + m2px(11.5), oy + m2px(1), "10A", GREEN)
    draw_switch(draw, ox + m2px(14.5), oy + m2px(3), "S", GREEN)

    draw_light(draw, ox + m2px(10), oy + m2px(1.7), "60W", GREEN)
    draw_outlet(draw, ox + m2px(9.5), oy + m2px(0.5), "15A", GREEN)
    draw_outlet(draw, ox + m2px(10.5), oy + m2px(2.5), "15A", GREEN)

    draw_light(draw, ox + m2px(13), oy + m2px(5.2), "60W", GREEN)
    draw_light(draw, ox + m2px(10.5), oy + m2px(5.2), "60W", GREEN)
    draw_outlet(draw, ox + m2px(14.5), oy + m2px(4.5), "10A", GREEN)
    draw_outlet(draw, ox + m2px(14.5), oy + m2px(6), "10A", GREEN)

    draw_light(draw, ox + m2px(13), oy + m2px(9.7), "40W", GREEN)
    draw_outlet(draw, ox + m2px(14.5), oy + m2px(9), "10A", GREEN)
    draw_outlet(draw, ox + m2px(11.5), oy + m2px(9), "10A", GREEN)

    draw_light(draw, ox + m2px(10), oy + m2px(9.7), "40W", GREEN)
    draw_outlet(draw, ox + m2px(10.5), oy + m2px(9), "GFCI", GREEN)

    draw_light(draw, ox + m2px(12), oy + m2px(11.5), "25W", GREEN)

    # Wire runs (simplified)
    draw.line([(tsx_a, tsy_a), (tsx_a, oy + m2px(5.2)), (ox + m2px(2) - 8, oy + m2px(5.2))], fill=GREEN, width=1)
    draw.line([(tsx_b + 22, tsy_a), (tsx_b + 22, oy + m2px(5.2)), (ox + m2px(13) + 8, oy + m2px(5.2))], fill=GREEN, width=1)


def draw_electrical_terraza(draw, ox, oy):
    """Terraza electrical"""
    draw_outline_light(draw, ox, oy, 'terraza')
    bw = m2px(BLDG_W)

    draw_text_centered(draw, ox + bw//2, oy - 20, "TERRAZA — ELÉCTRICAS", font_label, GREEN)

    # Sala máquinas - lights
    draw_light(draw, ox + m2px(2.5), oy + m2px(2), "100W", GREEN)
    draw_outlet(draw, ox + m2px(1), oy + m2px(1.5), "15A", GREEN)
    draw_outlet(draw, ox + m2px(4), oy + m2px(1.5), "15A", GREEN)
    draw_switch(draw, ox + m2px(0.5), oy + m2px(3), "S", GREEN)

    # Common area lights
    draw_light(draw, ox + m2px(4), oy + m2px(8), "60W", GREEN)
    draw_light(draw, ox + m2px(11), oy + m2px(8), "60W", GREEN)
    draw_light(draw, ox + m2px(7.5), oy + m2px(10), "60W", GREEN)
    draw_outlet(draw, ox + m2px(2), oy + m2px(10), "10A", GREEN)
    draw_outlet(draw, ox + m2px(13), oy + m2px(10), "10A", GREEN)
    draw_switch(draw, ox + m2px(6.5), oy + m2px(7.5), "S", GREEN)

    # Tablero terraza
    draw_tablero(draw, ox + m2px(6), oy + m2px(0.5), 22, 16, "TS-Tz", GREEN)


def draw_electrical_legend(draw, ox, oy):
    """Electrical legend"""
    draw.text((ox, oy), "REFERENCIAS ELÉCTRICAS", font=font_legend_bold, fill=GREEN)
    y = oy + 18

    draw_light(draw, ox + 12, y + 4, "", GREEN)
    draw.text((ox + 28, y), "Luminaria (con potencia)", font=font_legend, fill=GREEN)
    y += 20

    draw_outlet(draw, ox + 12, y + 4, "", GREEN)
    draw.text((ox + 28, y), "Tomacorriente (10A/15A/20A)", font=font_legend, fill=GREEN)
    y += 20

    draw_switch(draw, ox + 12, y + 4, "", GREEN)
    draw.text((ox + 28, y), "Interruptor", font=font_legend, fill=GREEN)
    y += 20

    draw_tablero(draw, ox + 4, y, 16, 12, "", GREEN)
    draw.text((ox + 28, y), "Tablero eléctrico", font=font_legend, fill=GREEN)
    y += 22

    draw.rectangle([ox + 4, y, ox + 20, y + 12], outline=GREEN, width=2)
    draw_text_centered(draw, ox + 12, y + 6, "M", font_dim_sm, GREEN)
    draw.text((ox + 28, y), "Medidor", font=font_legend, fill=GREEN)
    y += 22

    draw.line([(ox, y+4), (ox + 20, y+4)], fill=GREEN, width=1)
    draw.text((ox + 28, y), "Circuito eléctrico", font=font_legend, fill=GREEN)
    y += 18

    draw.text((ox, y), "CIRCUITOS POR DEPTO:", font=font_legend_bold, fill=GREEN)
    y += 14
    for c in ["C1 Iluminación 10A", "C2 Tomas generales 15A", "C3 Cocina 20A", "C4 Baño GFCI 15A"]:
        draw.text((ox + 10, y), c, font=font_legend, fill=GREEN)
        y += 14
    y += 5
    draw.text((ox, y), "Acometida: 3×6mm² + T 6mm²", font=font_legend, fill=GREEN)


# ============================================================
# MAIN — Compose all sections
# ============================================================

def main():
    # Calculate heights for each section
    plan_h = m2px(BLDG_H) + 90  # each floor plan height with margins

    section1_h = 80 + 4 * (plan_h + 30) + 320 + 120 + 80  # 4 plans + corte + tables + title block
    section2_h = 80 + 3 * (plan_h + 30) + 250  # 3 plans + legend
    section3_h = 80 + 3 * (plan_h + 30) + 300  # 3 plans + legend

    total_h = section1_h + section2_h + section3_h + 100

    img = Image.new('RGB', (CANVAS_W, total_h), WHITE)
    draw = ImageDraw.Draw(img)

    # ========== SECTION 1: ARCHITECTURAL ==========
    y_offset = 30
    draw_text_centered(draw, CANVAS_W // 2, y_offset, "PLANOS ARQUITECTÓNICOS", font_section_title, BLACK)
    draw.line([(50, y_offset + 22), (CANVAS_W - 50, y_offset + 22)], fill=BLACK, width=2)
    y_offset += 50

    # Plan origins - centered
    plan_ox = 120  # left margin for axes

    # PB
    draw_pb(draw, plan_ox, y_offset + 75)
    y_offset += plan_h + 100

    # Piso 1
    draw_piso_tipo(draw, plan_ox, y_offset + 75, "PISO 1 TIPO", "NPT +3.20  h=2.80m")
    y_offset += plan_h + 100

    # Piso 2
    draw_piso_tipo(draw, plan_ox, y_offset + 75, "PISO 2 TIPO", "NPT +6.00  h=2.80m")
    y_offset += plan_h + 100

    # Terraza
    draw_terraza(draw, plan_ox, y_offset + 75)
    y_offset += plan_h + 100

    # Corte esquemático (right side)
    draw_corte_esquematico(draw, plan_ox + m2px(BLDG_W) + 150, y_offset - plan_h - 50)

    # Scale bar and north
    draw_scale_bar(draw, plan_ox, y_offset)
    y_offset += 60

    # Tables
    draw_tables(draw, plan_ox, y_offset)
    y_offset += 300

    # Title block
    draw_title_block(draw, 50, y_offset, CANVAS_W - 100)
    y_offset += 80

    # ========== SECTION 2: SANITARY ==========
    y_offset += 40
    # Thick divider
    draw.rectangle([(0, y_offset), (CANVAS_W, y_offset + 6)], fill=BLUE)
    y_offset += 20
    draw_text_centered(draw, CANVAS_W // 2, y_offset, "INSTALACIONES SANITARIAS", font_section_title, BLUE)
    draw.line([(50, y_offset + 22), (CANVAS_W - 50, y_offset + 22)], fill=BLUE, width=2)
    y_offset += 50

    # 3 plans side by side (PB, Tipo, Terraza) - they fit at reduced conceptual layout
    # Actually let's stack them vertically for readability
    san_ox = 120

    draw_sanitary_pb(draw, san_ox, y_offset + 30)
    y_offset += plan_h + 60

    draw_sanitary_tipo(draw, san_ox, y_offset + 30)
    y_offset += plan_h + 60

    draw_sanitary_terraza(draw, san_ox, y_offset + 30)
    y_offset += plan_h + 60

    # Sanitary legend
    draw_sanitary_legend(draw, san_ox, y_offset)
    y_offset += 230

    # ========== SECTION 3: ELECTRICAL ==========
    y_offset += 20
    draw.rectangle([(0, y_offset), (CANVAS_W, y_offset + 6)], fill=GREEN)
    y_offset += 20
    draw_text_centered(draw, CANVAS_W // 2, y_offset, "INSTALACIONES ELÉCTRICAS", font_section_title, GREEN)
    draw.line([(50, y_offset + 22), (CANVAS_W - 50, y_offset + 22)], fill=GREEN, width=2)
    y_offset += 50

    elec_ox = 120

    draw_electrical_pb(draw, elec_ox, y_offset + 30)
    y_offset += plan_h + 60

    draw_electrical_tipo(draw, elec_ox, y_offset + 30)
    y_offset += plan_h + 60

    draw_electrical_terraza(draw, elec_ox, y_offset + 30)
    y_offset += plan_h + 60

    # Electrical legend
    draw_electrical_legend(draw, elec_ox, y_offset)
    y_offset += 280

    # Crop to actual content
    img_cropped = img.crop((0, 0, CANVAS_W, min(y_offset + 30, total_h)))
    img_cropped.save(OUTPUT, 'PNG')
    print(f"Saved to {OUTPUT}")
    print(f"Size: {img_cropped.size[0]}x{img_cropped.size[1]}px")


if __name__ == '__main__':
    main()
