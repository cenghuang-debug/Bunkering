"""
render_hull_overview.py — H2 volume-concentration field along the y=0 nozzle
plane, framed to the FULL ship hull length, for a given Bunkering case.

render_H2_vol_concentration.py zooms tightly on the nozzle region so the H2
jet plume stays a readable size; the ship hull (~130 m long) is far bigger
than that window and gets cropped there by design. This script is the
companion "where on the ship is this happening" view: same y=0 nozzle plane,
same H2 mass-fraction -> volume-fraction Calculator and slice, same drawing
convention for context geometry (quay: top edge only, solid; hull: full box,
dashed) — but framed to the full hull length instead.

Framing the whole hull makes the output image much wider than a normal
render (order 6000-12000 px), so a naive point-size colorbar/text would be
illegibly small relative to the frame — font sizes and line widths here are
scaled up by IMG_WIDTH / REFERENCE_WIDTH to compensate (REFERENCE_WIDTH =
3000 is render_H2_vol_concentration.py's default width, where those sizes
were tuned to look right).

Usage (headless):
    pvpython render_hull_overview.py <case_name> [--cmax 0.04] [--debug]
    e.g.:
    pvpython render_hull_overview.py Bunkering_07
    pvpython render_hull_overview.py Bunkering_07 --debug   # last time step only
"""

import argparse, os, math

CASE_NAME  = 'Bunkering_07'
IMG_HEIGHT = 1200

HULL_MARGIN  = 5.0     # world units of padding around the hull's x-extent
MARGIN_TOP   = 0.05
MARGIN_BOT   = 0.03     # the colorbar is drawn outside the render (see
                         # draw_colorbar()), so this only needs to clear the
                         # z=ENC_Z_MIN axis line
MARGIN_SIDE  = 0.03

REFERENCE_WIDTH = 3000  # width at which the sizes below were tuned (matches
                         # render_H2_vol_concentration.py's IMG_WIDTH)
TEXT_SIZE     = 40
QUAY_LINE_PX  = 6
HULL_LINE_PX  = 5
HULL_DASH_PX  = 24
HULL_GAP_PX   = 16
NOZZLE_MARKER_PX = 8

FONT_PATH        = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
TICK_LABEL_SIZE  = 42
AXIS_TITLE_SIZE  = 48
CB_TITLE_SIZE    = 22      # colorbar's X_H2 title — smaller than the axis titles
ANNOT_FONT_SIZE  = 48      # "quay"/"ship" context labels — a bit bigger than tick labels
TICK_LEN_PX      = 12
GAP, GAP_LARGE   = 14, 40
CB_BAR_HEIGHT_PX = 55
CB_WIDTH_FRAC    = 0.85
PAD_LEFT, PAD_RIGHT = 200, 30

CMAX = 0.04   # colour range upper bound [-]: 0.04 = 4 vol% (H2 LFL in air)

parser = argparse.ArgumentParser(description='Full-hull H2 volume concentration overview for a Bunkering case.')
parser.add_argument('case_name', nargs='?', default=CASE_NAME)
parser.add_argument('--cmax', type=float, default=CMAX,
                     help='Upper bound of the X_H2 colour scale (default 0.04 = 4 vol%%, LFL)')
parser.add_argument('--debug', action='store_true', default=False,
                     help='Only render the last time step (quick framing check)')
args, _ = parser.parse_known_args()

CMAX  = args.cmax
DEBUG = args.debug

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
case_dir  = os.path.join(BASE_PATH, args.case_name)
foam_file = os.path.join(case_dir, 'open.foam')

print(f'Case  : {args.case_name}')
print(f'Cmax  : {CMAX}')
print(f'Debug : {DEBUG}')
print(f'File  : {foam_file}')

from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

# ── Reader: internal mesh (for the H2 concentration slice) ───────────────────
mesh = OpenFOAMReader(registrationName='open.foam', FileName=foam_file)
mesh.MeshRegions = ['internalMesh']
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()
mesh.UpdatePipeline(time=0.0)

# ── Context geometry: hull, quay, nozzle — drawn as 2D annotations (see below) ─
hull = OpenFOAMReader(registrationName='hull', FileName=foam_file)
hull.MeshRegions = ['patch/bunkering-boat_m']
hull.UpdatePipeline(time=0.0)
HULL_BOUNDS = hull.GetDataInformation().GetBounds()

quay = OpenFOAMReader(registrationName='quay', FileName=foam_file)
quay.MeshRegions = ['patch/bunkering-quay_m']
quay.UpdatePipeline(time=0.0)
QUAY_BOUNDS = quay.GetDataInformation().GetBounds()

nozzle = OpenFOAMReader(registrationName='nozzle', FileName=foam_file)
nozzle.MeshRegions = ['patch/nozzle']
nozzle.UpdatePipeline(time=0.0)
NOZZLE_BOUNDS = nozzle.GetDataInformation().GetBounds()
nozzle_x = (NOZZLE_BOUNDS[0] + NOZZLE_BOUNDS[1]) / 2.0
nozzle_z = (NOZZLE_BOUNDS[4] + NOZZLE_BOUNDS[5]) / 2.0

# Frame the whole hull length (plus a touch of margin). Z spans the full
# computational domain height, not just the hull deck height.
ENC_X_MIN = HULL_BOUNDS[0] - HULL_MARGIN
ENC_X_MAX = HULL_BOUNDS[1] + HULL_MARGIN
ENC_Z_MIN = -2.0        # x-axis crosses z here — a little below sea level
ENC_Z_MAX = 40.0        # computational domain height

x_half   = (ENC_X_MAX - ENC_X_MIN) / 2.0
z_half   = (ENC_Z_MAX - ENC_Z_MIN) / 2.0
x_center = (ENC_X_MIN + ENC_X_MAX) / 2.0
z_center = (ENC_Z_MIN + ENC_Z_MAX) / 2.0 + z_half * (MARGIN_TOP - MARGIN_BOT)

# Pick IMG_WIDTH so the frame is filled in both directions (no wasted
# vertical space).
needed_aspect = (x_half * (1 + 2 * MARGIN_SIDE)) / (z_half * (1 + MARGIN_TOP + MARGIN_BOT))
IMG_WIDTH = max(1600, round(IMG_HEIGHT * needed_aspect))

# Scale font sizes / line widths up so they read correctly at this much wider
# frame (see module docstring).
SCALE = IMG_WIDTH / REFERENCE_WIDTH
TEXT_SIZE     = round(TEXT_SIZE * SCALE)
QUAY_LINE_PX  = round(QUAY_LINE_PX * SCALE)
HULL_LINE_PX  = round(HULL_LINE_PX * SCALE)
HULL_DASH_PX  = round(HULL_DASH_PX * SCALE)
HULL_GAP_PX   = round(HULL_GAP_PX * SCALE)
NOZZLE_MARKER_PX = round(NOZZLE_MARKER_PX * SCALE)
TICK_LABEL_SIZE = round(TICK_LABEL_SIZE * SCALE)
AXIS_TITLE_SIZE = round(AXIS_TITLE_SIZE * SCALE)
CB_TITLE_SIZE   = round(CB_TITLE_SIZE * SCALE)
ANNOT_FONT_SIZE = round(ANNOT_FONT_SIZE * SCALE)
TICK_LEN_PX     = round(TICK_LEN_PX * SCALE)
GAP             = round(GAP * SCALE)
GAP_LARGE       = round(GAP_LARGE * SCALE)
CB_BAR_HEIGHT_PX = round(CB_BAR_HEIGHT_PX * SCALE)
PAD_LEFT        = round(PAD_LEFT * SCALE)
PAD_RIGHT       = round(PAD_RIGHT * SCALE)

# Bottom padding stacks (top to bottom): x ticks+labels, x-axis title, a
# large gap, colorbar title, colorbar bar, colorbar ticks+labels, margin.
TICK_LABEL_H = round(TICK_LABEL_SIZE * 1.3)
AXIS_TITLE_H = round(AXIS_TITLE_SIZE * 1.3)
PAD_BOTTOM = (TICK_LEN_PX + GAP + TICK_LABEL_H
              + GAP + AXIS_TITLE_H
              + GAP_LARGE + AXIS_TITLE_H
              + GAP + CB_BAR_HEIGHT_PX
              + GAP + TICK_LABEL_H
              + GAP_LARGE)
# Top padding: room for the time label, drawn just above the axis box.
TIME_LABEL_H = round(TEXT_SIZE * 1.3)
TIME_LABEL_GAP_PX = round(22 * SCALE)   # gap between the time label and the box top
PAD_TOP = TIME_LABEL_H + TIME_LABEL_GAP_PX + 20

print(f'Frame: x[{ENC_X_MIN:.1f},{ENC_X_MAX:.1f}]  z[{ENC_Z_MIN:.1f},{ENC_Z_MAX:.1f}]  '
      f'IMG_WIDTH={IMG_WIDTH}  SCALE={SCALE:.2f}')

renderView1 = GetActiveViewOrCreate('RenderView')
renderView1.ViewSize            = [IMG_WIDTH, IMG_HEIGHT]
renderView1.UseColorPaletteForBackground = 0
renderView1.Background          = [1.0, 1.0, 1.0]
renderView1.OrientationAxesVisibility = 0

def flat(disp):
    disp.Ambient  = 1.0
    disp.Diffuse  = 0.0
    disp.Specular = 0.0

# Nozzle patch — red highlight (tiny at this zoom, marked again in 2D below)
nozzDisp = Show(nozzle, renderView1, 'UnstructuredGridRepresentation')
nozzDisp.Representation = 'Surface'
nozzDisp.AmbientColor   = [0.85, 0.15, 0.10]
nozzDisp.DiffuseColor   = [0.85, 0.15, 0.10]
ColorBy(nozzDisp, None)
flat(nozzDisp)
nozzDisp.SetScalarBarVisibility(renderView1, False)

# ── H2 mass fraction -> volume fraction (Calculator) ──────────────────────────
calculator1 = Calculator(registrationName='Calculator1', Input=mesh)
calculator1.ResultArrayName = 'X_H2'
calculator1.Function = 'H2/2*(1/(H2/2+(1-H2)/29))'

# Cell Data to Point Data — smooths coarse-mesh banding near boundaries
cellDataToPointData1 = CellDatatoPointData(registrationName='CellDatatoPointData1', Input=calculator1)

# ── Slice through the nozzle plane (y = 0) ────────────────────────────────────
slice1 = Slice(registrationName='Slice1', Input=cellDataToPointData1)
slice1.SliceType        = 'Plane'
slice1.SliceType.Origin = [0.0, 0.0, 9.0]
slice1.SliceType.Normal = [0.0, 1.0, 0.0]
slice1.Triangulatetheslice = 0

# Colorbar is drawn ourselves outside the axis box (see draw_colorbar()) —
# ParaView's in-scene legend is disabled here.
slice1Display = Show(slice1, renderView1, 'GeometryRepresentation')
ColorBy(slice1Display, ('POINTS', 'X_H2'))
slice1Display.SetScalarBarVisibility(renderView1, False)
flat(slice1Display)

x_H2LUT = GetColorTransferFunction('X_H2')
x_H2LUT.RGBPoints = [
    0.0, 1.0, 1.0, 1.0,
    0.5, 1.0, 1.0, 0.0,
    1.0, 1.0, 0.0, 0.0,
]
x_H2LUT.ColorSpace = 'RGB'
x_H2LUT.ScalarRangeInitialized = 1.0
x_H2PWF = GetOpacityTransferFunction('X_H2')

x_H2LUT.RescaleTransferFunction(0.0, CMAX)
x_H2PWF.RescaleTransferFunction(0.0, CMAX)

renderView1.CameraParallelProjection = 1
renderView1.CameraPosition   = [x_center, -500.0, z_center]
renderView1.CameraFocalPoint = [x_center,    0.0, z_center]
renderView1.CameraViewUp     = [0.0, 0.0, 1.0]
renderView1.CameraParallelScale = max(z_half * (1 + MARGIN_TOP + MARGIN_BOT),
                                       x_half * (1 + 2 * MARGIN_SIDE) / (IMG_WIDTH / IMG_HEIGHT))
CAM_PS = renderView1.CameraParallelScale
CAM_ASPECT = IMG_WIDTH / IMG_HEIGHT

# Time annotation is drawn in add_axes() (PIL), anchored to the axis box's
# top-left corner — ParaView's fraction-based Text positioning doesn't know
# about the padded-canvas geometry we add afterwards, and collided with the
# box border at larger font sizes.

# ── 2D line annotations (quay top edge only; dashed hull box; axis scales) ───
from PIL import Image, ImageDraw, ImageFont
import io
from matplotlib import mathtext
from matplotlib.font_manager import FontProperties

def render_mathtext(tex, fontsize, dpi=200):
    """Render a LaTeX/mathtext expression (e.g. r'$X_{H_2}$') to an RGBA
    PIL image via matplotlib's mathtext parser (no full LaTeX install needed)."""
    buf = io.BytesIO()
    mathtext.math_to_image(tex, buf, dpi=dpi, format='png', prop=FontProperties(size=fontsize))
    buf.seek(0)
    return Image.open(buf).convert('RGBA')

def world_x_to_px(x):
    return IMG_WIDTH * (x - (x_center - CAM_PS * CAM_ASPECT)) / (2 * CAM_PS * CAM_ASPECT)

def world_z_to_py(z):
    return IMG_HEIGHT * ((z_center + CAM_PS) - z) / (2 * CAM_PS)

def world_to_pixel(x, z):
    return world_x_to_px(x), world_z_to_py(z)

def nice_ticks(vmin, vmax, target=6):
    """Round tick step (1/2/5 x10^n pattern), matplotlib-MaxNLocator-style."""
    span = vmax - vmin
    if span <= 0:
        return [vmin]
    raw_step = span / target
    mag = 10 ** math.floor(math.log10(raw_step))
    step = mag
    for mult in (1, 2, 5, 10):
        step = mult * mag
        if step >= raw_step:
            break
    start = math.ceil(vmin / step) * step
    ticks, v = [], start
    while v <= vmax + 1e-6:
        ticks.append(round(v, 6))
        v += step
    return ticks

def fmt_tick(v):
    return f'{v:.0f}' if abs(v - round(v)) < 1e-6 else f'{v:.1f}'

# White -> yellow -> red ramp, matching x_H2LUT.RGBPoints above.
CMAP_STOPS = [(0.0, (255, 255, 255)), (0.5, (255, 255, 0)), (1.0, (255, 0, 0))]

def cmap_color(t):
    t = max(0.0, min(1.0, t))
    for (t0, c0), (t1, c1) in zip(CMAP_STOPS, CMAP_STOPS[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            return tuple(round(c0[i] + f * (c1[i] - c0[i])) for i in range(3))
    return CMAP_STOPS[-1][1]

def make_gradient_bar(width_px, height_px):
    bar = Image.new('RGB', (width_px, height_px))
    px = bar.load()
    row = [cmap_color(x / (width_px - 1)) for x in range(width_px)]
    for x in range(width_px):
        for y in range(height_px):
            px[x, y] = row[x]
    return bar

def draw_colorbar(canvas, draw, font_tick, font_title, box_left, box_right, top_y):
    """Draw a standalone horizontal colorbar (title above, gradient bar,
    sparse ticks below) starting at pixel row top_y — outside/below the axis
    box, in the style of H2Vent's check_probe_timeseries-family plots."""
    bar_w = round((box_right - box_left) * CB_WIDTH_FRAC)
    bar_left = round(box_left + (box_right - box_left - bar_w) / 2)

    title_img = render_mathtext(r'$X_{H_2}$', CB_TITLE_SIZE)
    y = top_y
    canvas.paste(title_img, (round(bar_left + bar_w / 2 - title_img.size[0] / 2), int(y)), title_img)
    y += title_img.size[1] + GAP

    bar_img = make_gradient_bar(bar_w, CB_BAR_HEIGHT_PX)
    canvas.paste(bar_img, (int(bar_left), int(y)))
    draw.rectangle([bar_left, y, bar_left + bar_w, y + CB_BAR_HEIGHT_PX], outline=(0, 0, 0), width=2)
    bar_bottom = y + CB_BAR_HEIGHT_PX
    y = bar_bottom + GAP

    ticks = nice_ticks(0.0, CMAX, target=8)
    for i, v in enumerate(ticks):
        tx = bar_left + (v / CMAX) * bar_w
        draw.line([(tx, bar_bottom), (tx, bar_bottom + TICK_LEN_PX)], fill=(0, 0, 0), width=2)
        label = f'{v:.1e}' if i in (0, len(ticks) - 1) else f'{v:g}'
        tb = draw.textbbox((0, 0), label, font=font_tick)
        tw = tb[2] - tb[0]
        draw.text((tx - tw / 2, y), label, fill=(0, 0, 0), font=font_tick)

def add_axes(fname, t):
    """Pad the saved screenshot with a matplotlib-style axis frame (x-axis
    crossing at z=ENC_Z_MIN), x/z tick marks + labels (metres), axis titles,
    a time annotation, and a standalone colorbar drawn below/outside the
    axis box."""
    img = Image.open(fname).convert('RGB')
    w, h = img.size
    canvas = Image.new('RGB', (w + PAD_LEFT + PAD_RIGHT, h + PAD_TOP + PAD_BOTTOM), (255, 255, 255))
    canvas.paste(img, (PAD_LEFT, PAD_TOP))
    draw = ImageDraw.Draw(canvas)
    font_tick = ImageFont.truetype(FONT_PATH, TICK_LABEL_SIZE)
    font_axis = ImageFont.truetype(FONT_PATH, AXIS_TITLE_SIZE)
    font_time = ImageFont.truetype(FONT_PATH, TEXT_SIZE)
    ox, oy = PAD_LEFT, PAD_TOP

    box_left   = ox + world_x_to_px(ENC_X_MIN)
    box_right  = ox + world_x_to_px(ENC_X_MAX)
    box_top    = oy + world_z_to_py(ENC_Z_MAX)
    box_bottom = oy + world_z_to_py(ENC_Z_MIN)
    draw.rectangle([box_left, box_top, box_right, box_bottom], outline=(0, 0, 0), width=2)

    time_label = f't = {t:.2f} s'
    tb = draw.textbbox((0, 0), time_label, font=font_time)
    draw.text((box_left, box_top - (tb[3] - tb[1]) - TIME_LABEL_GAP_PX), time_label, fill=(0, 0, 0), font=font_time)

    # "quay"/"ship" context labels — positioned relative to box_left (not the
    # raw render's own edge, which includes the camera's MARGIN_SIDE
    # whitespace strip outside the box and isn't a reliable "how close to
    # the box border" reference). quay sits closer to the border than ship.
    font_annot = ImageFont.truetype(FONT_PATH, ANNOT_FONT_SIZE)
    qz_top = QUAY_BOUNDS[5]
    qy = oy + world_z_to_py(qz_top)
    qtb = draw.textbbox((0, 0), 'quay', font=font_annot)
    draw.text((box_left + round(10 * SCALE), qy - (qtb[3] - qtb[1]) - QUAY_ANNOT_GAP_PX), 'quay', fill=(0, 0, 0), font=font_annot)

    hz1 = HULL_BOUNDS[5]
    hy = oy + world_z_to_py(hz1)
    stb = draw.textbbox((0, 0), 'ship', font=font_annot)
    draw.text((box_left + round(60 * SCALE), hy - (stb[3] - stb[1]) - ANNOT_GAP_PX), 'ship', fill=(0, 0, 0), font=font_annot)

    # x-axis ticks, anchored at z=ENC_Z_MIN (not the bottom image edge)
    for xv in nice_ticks(ENC_X_MIN, ENC_X_MAX):
        px = ox + world_x_to_px(xv)
        draw.line([(px, box_bottom), (px, box_bottom + TICK_LEN_PX)], fill=(0, 0, 0), width=2)
        label = fmt_tick(xv)
        tb = draw.textbbox((0, 0), label, font=font_tick)
        tw = tb[2] - tb[0]
        draw.text((px - tw / 2, box_bottom + TICK_LEN_PX + GAP), label, fill=(0, 0, 0), font=font_tick)

    # z-axis ticks (left edge)
    z_tick_label_max_w = 0
    for zv in nice_ticks(ENC_Z_MIN, ENC_Z_MAX):
        py = oy + world_z_to_py(zv)
        draw.line([(box_left - TICK_LEN_PX, py), (box_left, py)], fill=(0, 0, 0), width=2)
        label = fmt_tick(zv)
        tb = draw.textbbox((0, 0), label, font=font_tick)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        z_tick_label_max_w = max(z_tick_label_max_w, tw)
        draw.text((box_left - TICK_LEN_PX - tw - GAP, py - th / 2), label, fill=(0, 0, 0), font=font_tick)

    # axis titles
    xlabel = 'x (m)'
    tb = draw.textbbox((0, 0), xlabel, font=font_axis)
    tw = tb[2] - tb[0]
    xlabel_y = box_bottom + TICK_LEN_PX + GAP + TICK_LABEL_H + GAP
    draw.text((box_left + (box_right - box_left) / 2 - tw / 2, xlabel_y), xlabel, fill=(0, 0, 0), font=font_axis)

    zlabel = 'z (m)'
    tb = draw.textbbox((0, 0), zlabel, font=font_axis)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    zlabel_img = Image.new('RGBA', (tw + 4, th + 4), (255, 255, 255, 0))
    ImageDraw.Draw(zlabel_img).text((2, 2), zlabel, fill=(0, 0, 0, 255), font=font_axis)
    zlabel_img = zlabel_img.rotate(90, expand=True)
    zlabel_x = box_left - TICK_LEN_PX - GAP - z_tick_label_max_w - GAP - zlabel_img.size[0]
    canvas.paste(zlabel_img, (round(zlabel_x), int((box_top + box_bottom) / 2 - zlabel_img.size[1] / 2)), zlabel_img)

    # standalone colorbar, well below the axis box (outside it)
    cb_top_y = xlabel_y + AXIS_TITLE_H + GAP_LARGE
    draw_colorbar(canvas, draw, font_tick, font_axis, box_left, box_right, cb_top_y)

    canvas.save(fname)

def draw_dashed_line(draw, p0, p1, fill, width, dash=HULL_DASH_PX, gap=HULL_GAP_PX):
    x0, y0 = p0
    x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    if length < 1e-6:
        return
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    s = 0.0
    while s < length:
        e = min(s + dash, length)
        draw.line([(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], fill=fill, width=width)
        s += dash + gap

ANNOT_GAP_PX      = round(4 * SCALE)    # ship label — small gap, sits close to the dashed box
QUAY_ANNOT_GAP_PX = round(16 * SCALE)   # quay label — a bit more room, so it clears the solid line

import numpy as np

BG_WHITE_THRESHOLD = 250   # pixel counts as "background" if all channels exceed this

def annotate_frame(fname):
    """Draw the quay/hull context lines (world-coordinate geometry) on the
    raw screenshot. Their "quay"/"ship" text labels are drawn later in
    add_axes(), positioned relative to the axis box border in padded-canvas
    coordinates — not here, since this raw image still includes the camera's
    MARGIN_SIDE whitespace strip outside the box, which isn't a reliable
    reference point for "how close to the box edge" a label sits."""
    img = Image.open(fname).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Quay — top edge only
    qx0, qx1 = QUAY_BOUNDS[0], QUAY_BOUNDS[1]
    qz_top   = QUAY_BOUNDS[5]
    draw.line([world_to_pixel(qx0, qz_top), world_to_pixel(qx1, qz_top)],
              fill=(0, 0, 0), width=QUAY_LINE_PX)

    # Hull — full bounding box, dashed. Drawn on a separate overlay and
    # composited only over background (white) pixels, so it reads as
    # sitting BEHIND the H2 concentration field rather than on top of it.
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    hx0, hx1 = HULL_BOUNDS[0], HULL_BOUNDS[1]
    hz0, hz1 = HULL_BOUNDS[4], HULL_BOUNDS[5]
    corners = [(hx0, hz0), (hx1, hz0), (hx1, hz1), (hx0, hz1)]
    pts = [world_to_pixel(x, z) for x, z in corners]
    for i in range(4):
        draw_dashed_line(odraw, pts[i], pts[(i + 1) % 4], fill=(0, 0, 0, 255), width=HULL_LINE_PX)

    img_arr = np.array(img)
    overlay_arr = np.array(overlay)
    line_mask = overlay_arr[:, :, 3] > 0
    bg_mask = np.all(img_arr > BG_WHITE_THRESHOLD, axis=-1)
    apply_mask = line_mask & bg_mask
    img_arr[apply_mask] = overlay_arr[apply_mask][:, :3]
    img = Image.fromarray(img_arr)

    img.save(fname)

# ── Save screenshots for all available time steps ─────────────────────────
def save_all_timesteps():
    output_dir = os.path.join(case_dir, 'H2_vol_con')
    os.makedirs(output_dir, exist_ok=True)
    times = list(mesh.TimestepValues) or [animationScene1.AnimationTime]
    if DEBUG:
        times = [times[-1]]
        print(f'DEBUG: saving 1 screenshot (last t={times[0]:.3f}s)')
    else:
        print(f'Saving {len(times)} screenshot(s) to: {output_dir}')
    for t in times:
        animationScene1.AnimationTime = t
        renderView1.Update()
        Render()
        fname = os.path.join(output_dir, f'hull_overview_t{t:010.3f}s.png')
        SaveScreenshot(fname, renderView1,
                        ImageResolution=[IMG_WIDTH, IMG_HEIGHT],
                        TransparentBackground=0)
        annotate_frame(fname)
        add_axes(fname, t)
        print(f'  Saved t={t:.3f}s -> {os.path.basename(fname)}')

save_all_timesteps()
