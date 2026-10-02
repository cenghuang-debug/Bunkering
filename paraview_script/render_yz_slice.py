"""
render_yz_slice.py — H2 volume-concentration field on a cross-section
(y-z plane, cut at a fixed x = X0) for a given Bunkering case.

Companion view to render_hull_overview.py: that script slices along the
nozzle's y=0 plane and looks along y, giving a side view (x-z, ship length vs
height). This script instead slices along a x=X0 plane (default X0=0, the
nozzle/gap location) and looks along x, giving a cross-section view (y-z,
quay-to-ship gap width vs height) -- how far the plume has spread sideways
across the gap at that point along the ship.

Context geometry follows the same drawing convention as render_hull_overview.py
but adapted to a cross-section:
  - quay: still just its top edge (a horizontal line) -- the quay is a simple
    rectangular block, so its cross-section at any x is the same rectangle;
    only the top matters (the floor z=0 is already the domain boundary).
  - ship: unlike the side view (where the hull was approximated as a dashed
    bounding box, because that view spans the whole 130 m length), here the
    true hull cross-section is what's interesting -- it's sliced out of the
    actual hull STL at x=X0 and its outline drawn as a dashed contour.

Usage (headless):
    pvpython render_yz_slice.py <case_name> [--x0 0.0] [--cmax 0.04] [--zmax 40] [--debug]
    e.g.:
    pvpython render_yz_slice.py Bunkering_07
    pvpython render_yz_slice.py Bunkering_09 --x0 0.0 --debug
"""

import argparse, os, math

CASE_NAME  = 'Bunkering_07'
IMG_HEIGHT = 1200

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

# Cross-section frame. Y spans the full lateral domain width (quay/ship gap
# and beyond); Z spans the same near-ground window used by
# render_hull_overview.py (full domain height isn't needed for a gap-scale
# view and would waste vertical resolution).
ENC_Y_MIN = -40.0
ENC_Y_MAX =  40.0
ENC_Z_MIN =  -2.0
ENC_Z_MAX =  40.0

parser = argparse.ArgumentParser(description='Cross-section (y-z, cut at x=X0) H2 volume concentration for a Bunkering case.')
parser.add_argument('case_name', nargs='?', default=CASE_NAME)
parser.add_argument('--x0', type=float, default=0.0,
                     help='x location of the y-z cut plane [m] (default 0.0 = nozzle/gap location)')
parser.add_argument('--cmax', type=float, default=CMAX,
                     help='Upper bound of the X_H2 colour scale (default 0.04 = 4 vol%%, LFL)')
parser.add_argument('--zmax', type=float, default=ENC_Z_MAX,
                     help='Top of the plotted z range [m] (default 40)')
parser.add_argument('--debug', action='store_true', default=False,
                     help='Only render the last time step (quick framing check)')
args, _ = parser.parse_known_args()

CMAX  = args.cmax
X0    = args.x0
ENC_Z_MAX = args.zmax
DEBUG = args.debug

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
case_dir  = os.path.join(BASE_PATH, args.case_name)
foam_file = os.path.join(case_dir, 'open.foam')

print(f'Case  : {args.case_name}')
print(f'X0    : {X0}')
print(f'Cmax  : {CMAX}')
print(f'Debug : {DEBUG}')
print(f'File  : {foam_file}')

from paraview.simple import *
from paraview import servermanager as sm
import vtk
paraview.simple._DisableFirstRenderCameraReset()

# ── Reader: internal mesh (for the H2 concentration slice) ───────────────────
mesh = OpenFOAMReader(registrationName='open.foam', FileName=foam_file)
mesh.MeshRegions = ['internalMesh']
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()
mesh.UpdatePipeline(time=0.0)

# ── Context geometry: hull, quay, nozzle ──────────────────────────────────────
hull = OpenFOAMReader(registrationName='hull', FileName=foam_file)
hull.MeshRegions = ['patch/bunkering-boat_m']
hull.UpdatePipeline(time=0.0)

quay = OpenFOAMReader(registrationName='quay', FileName=foam_file)
quay.MeshRegions = ['patch/bunkering-quay_m']
quay.UpdatePipeline(time=0.0)
QUAY_BOUNDS = quay.GetDataInformation().GetBounds()

nozzle = OpenFOAMReader(registrationName='nozzle', FileName=foam_file)
nozzle.MeshRegions = ['patch/nozzle']
nozzle.UpdatePipeline(time=0.0)

# ── Slice the hull surface at x=X0 to get its true cross-sectional contour ───
hullSlice = Slice(registrationName='HullSlice', Input=hull)
hullSlice.SliceType        = 'Plane'
hullSlice.SliceType.Origin = [X0, 0.0, 0.0]
hullSlice.SliceType.Normal = [1.0, 0.0, 0.0]
hullSlice.Triangulatetheslice = 0
hullSlice.UpdatePipeline(time=0.0)

def fetch_polylines(sliceFilter):
    """Fetch a Slice filter's output client-side and return its line cells
    as a list of polylines, each a list of (x,y,z) point tuples."""
    data = sm.Fetch(sliceFilter)
    polys = []

    def handle_polydata(pd):
        if pd is None or pd.GetNumberOfPoints() == 0:
            return
        pts = pd.GetPoints()
        lines = pd.GetLines()
        if lines is None or lines.GetNumberOfCells() == 0:
            return
        lines.InitTraversal()
        idlist = vtk.vtkIdList()
        while lines.GetNextCell(idlist):
            coords = [pts.GetPoint(idlist.GetId(i)) for i in range(idlist.GetNumberOfIds())]
            polys.append(coords)

    if hasattr(data, 'GetNumberOfBlocks'):
        it = data.NewIterator()
        it.InitTraversal()
        while not it.IsDoneWithTraversal():
            handle_polydata(it.GetCurrentDataObject())
            it.GoToNextItem()
    else:
        handle_polydata(data)
    return polys

def stitch_polylines(polys, tol=1e-6):
    """Chain a set of possibly-disconnected polylines (as VTK's Cut/Slice
    filter emits: one 2-point segment per cut triangle edge, unstitched)
    into longer connected contours by matching shared endpoints. Needed so
    a dash pattern can be drawn with the phase tracked continuously along
    each actual contour, instead of resetting at every tiny triangle-edge
    fragment (which renders as a solid line)."""
    from collections import defaultdict

    def key(pt):
        return (round(pt[0] / tol), round(pt[1] / tol), round(pt[2] / tol))

    segs = [list(p) for p in polys]
    used = [False] * len(segs)
    adjacency = defaultdict(list)
    for i, s in enumerate(segs):
        adjacency[key(s[0])].append((i, 0))
        adjacency[key(s[-1])].append((i, 1))

    def pop_match(pt_key, exclude_i):
        for (j, end) in adjacency[pt_key]:
            if not used[j] and j != exclude_i:
                return j, end
        return None

    chains = []
    for i in range(len(segs)):
        if used[i]:
            continue
        used[i] = True
        chain = list(segs[i])
        while True:
            m = pop_match(key(chain[-1]), -1)
            if m is None:
                break
            j, end = m
            seg = segs[j]
            chain.extend((list(reversed(seg)) if end == 1 else seg)[1:])
            used[j] = True
        while True:
            m = pop_match(key(chain[0]), -1)
            if m is None:
                break
            j, end = m
            seg = segs[j]
            chain[0:0] = (list(reversed(seg)) if end == 0 else seg)[:-1]
            used[j] = True
        chains.append(chain)
    return chains

HULL_SLICE_POLYS = fetch_polylines(hullSlice)
if HULL_SLICE_POLYS:
    all_y = [p[1] for poly in HULL_SLICE_POLYS for p in poly]
    all_z = [p[2] for poly in HULL_SLICE_POLYS for p in poly]
    HULL_SLICE_BOUNDS = (min(all_y), max(all_y), min(all_z), max(all_z))
    HULL_SLICE_POLYS_STITCHED = stitch_polylines(HULL_SLICE_POLYS)
    print(f'Hull cross-section at x={X0}: y[{HULL_SLICE_BOUNDS[0]:.2f},{HULL_SLICE_BOUNDS[1]:.2f}] '
          f'z[{HULL_SLICE_BOUNDS[2]:.2f},{HULL_SLICE_BOUNDS[3]:.2f}]  '
          f'({len(HULL_SLICE_POLYS)} fragment(s) -> {len(HULL_SLICE_POLYS_STITCHED)} contour(s))')
else:
    HULL_SLICE_BOUNDS = None
    HULL_SLICE_POLYS_STITCHED = []
    print(f'WARNING: hull slice at x={X0} produced no geometry -- is x0 within the hull length?')

y_half   = (ENC_Y_MAX - ENC_Y_MIN) / 2.0
z_half   = (ENC_Z_MAX - ENC_Z_MIN) / 2.0
y_center = (ENC_Y_MIN + ENC_Y_MAX) / 2.0
z_center = (ENC_Z_MIN + ENC_Z_MAX) / 2.0 + z_half * (MARGIN_TOP - MARGIN_BOT)

# Pick IMG_WIDTH so the frame is filled in both directions (no wasted
# vertical space).
needed_aspect = (y_half * (1 + 2 * MARGIN_SIDE)) / (z_half * (1 + MARGIN_TOP + MARGIN_BOT))
IMG_WIDTH = max(1600, round(IMG_HEIGHT * needed_aspect))

# Scale font sizes / line widths to this frame width (see module docstring
# in render_hull_overview.py for why this scaling exists).
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

# Bottom padding stacks (top to bottom): y ticks+labels, y-axis title, a
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

print(f'Frame: y[{ENC_Y_MIN:.1f},{ENC_Y_MAX:.1f}]  z[{ENC_Z_MIN:.1f},{ENC_Z_MAX:.1f}]  '
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

# Nozzle patch — red highlight (tiny at this scale, marked again in 2D below)
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

# ── Slice through the cross-section plane (x = X0) ────────────────────────────
slice1 = Slice(registrationName='Slice1', Input=cellDataToPointData1)
slice1.SliceType        = 'Plane'
slice1.SliceType.Origin = [X0, 0.0, 0.0]
slice1.SliceType.Normal = [1.0, 0.0, 0.0]
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

# Camera looks along -x (positioned at +x, looking back toward the slice) so
# that +y projects to the right of the image (quay at negative y on the
# left, ship at positive y on the right — matches the physical gap layout).
renderView1.CameraParallelProjection = 1
renderView1.CameraPosition   = [X0 + 500.0, y_center, z_center]
renderView1.CameraFocalPoint = [X0,         y_center, z_center]
renderView1.CameraViewUp     = [0.0, 0.0, 1.0]
renderView1.CameraParallelScale = max(z_half * (1 + MARGIN_TOP + MARGIN_BOT),
                                       y_half * (1 + 2 * MARGIN_SIDE) / (IMG_WIDTH / IMG_HEIGHT))
CAM_PS = renderView1.CameraParallelScale
CAM_ASPECT = IMG_WIDTH / IMG_HEIGHT

# Time annotation is drawn in add_axes() (PIL), anchored to the axis box's
# top-left corner — ParaView's fraction-based Text positioning doesn't know
# about the padded-canvas geometry we add afterwards, and collided with the
# box border at larger font sizes.

# ── 2D line annotations (quay top edge; sliced hull contour; axis scales) ────
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

def world_y_to_px(y):
    return IMG_WIDTH * (y - (y_center - CAM_PS * CAM_ASPECT)) / (2 * CAM_PS * CAM_ASPECT)

def world_z_to_py(z):
    return IMG_HEIGHT * ((z_center + CAM_PS) - z) / (2 * CAM_PS)

def world_to_pixel(y, z):
    return world_y_to_px(y), world_z_to_py(z)

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
    """Pad the saved screenshot with a matplotlib-style axis frame (y-axis
    crossing at z=ENC_Z_MIN), y/z tick marks + labels (metres), axis titles,
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

    box_left   = ox + world_y_to_px(ENC_Y_MIN)
    box_right  = ox + world_y_to_px(ENC_Y_MAX)
    box_top    = oy + world_z_to_py(ENC_Z_MAX)
    box_bottom = oy + world_z_to_py(ENC_Z_MIN)
    draw.rectangle([box_left, box_top, box_right, box_bottom], outline=(0, 0, 0), width=2)

    time_label = f't = {t:.2f} s   (x = {X0:.1f} m)'
    tb = draw.textbbox((0, 0), time_label, font=font_time)
    draw.text((box_left, box_top - (tb[3] - tb[1]) - TIME_LABEL_GAP_PX), time_label, fill=(0, 0, 0), font=font_time)

    # "quay"/"ship" context labels.
    font_annot = ImageFont.truetype(FONT_PATH, ANNOT_FONT_SIZE)
    qz_top = QUAY_BOUNDS[5]
    qy = oy + world_z_to_py(qz_top)
    qtb = draw.textbbox((0, 0), 'quay', font=font_annot)
    draw.text((box_left + round(10 * SCALE), qy - (qtb[3] - qtb[1]) - QUAY_ANNOT_GAP_PX), 'quay', fill=(0, 0, 0), font=font_annot)

    if HULL_SLICE_BOUNDS is not None:
        hy_mid = (HULL_SLICE_BOUNDS[0] + HULL_SLICE_BOUNDS[1]) / 2.0
        hz_top = HULL_SLICE_BOUNDS[3]
        hx_px = ox + world_y_to_px(hy_mid)
        hy_px = oy + world_z_to_py(hz_top)
        stb = draw.textbbox((0, 0), 'ship', font=font_annot)
        stw = stb[2] - stb[0]
        draw.text((hx_px - stw / 2, hy_px - (stb[3] - stb[1]) - ANNOT_GAP_PX), 'ship', fill=(0, 0, 0), font=font_annot)

    # y-axis ticks, anchored at z=ENC_Z_MIN (not the bottom image edge)
    for yv in nice_ticks(ENC_Y_MIN, ENC_Y_MAX):
        px = ox + world_y_to_px(yv)
        draw.line([(px, box_bottom), (px, box_bottom + TICK_LEN_PX)], fill=(0, 0, 0), width=2)
        label = fmt_tick(yv)
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
    ylabel = 'y (m)'
    tb = draw.textbbox((0, 0), ylabel, font=font_axis)
    tw = tb[2] - tb[0]
    ylabel_y = box_bottom + TICK_LEN_PX + GAP + TICK_LABEL_H + GAP
    draw.text((box_left + (box_right - box_left) / 2 - tw / 2, ylabel_y), ylabel, fill=(0, 0, 0), font=font_axis)

    zlabel = 'z (m)'
    tb = draw.textbbox((0, 0), zlabel, font=font_axis)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    zlabel_img = Image.new('RGBA', (tw + 4, th + 4), (255, 255, 255, 0))
    ImageDraw.Draw(zlabel_img).text((2, 2), zlabel, fill=(0, 0, 0, 255), font=font_axis)
    zlabel_img = zlabel_img.rotate(90, expand=True)
    zlabel_x = box_left - TICK_LEN_PX - GAP - z_tick_label_max_w - GAP - zlabel_img.size[0]
    canvas.paste(zlabel_img, (round(zlabel_x), int((box_top + box_bottom) / 2 - zlabel_img.size[1] / 2)), zlabel_img)

    # standalone colorbar, well below the axis box (outside it)
    cb_top_y = ylabel_y + AXIS_TITLE_H + GAP_LARGE
    draw_colorbar(canvas, draw, font_tick, font_axis, box_left, box_right, cb_top_y)

    canvas.save(fname)

def polyline_length_map(pts):
    """Cumulative arc length at each vertex of a polyline."""
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    return cum

def point_at_length(pts, cum, s):
    for i in range(1, len(cum)):
        if cum[i] >= s:
            seg_len = cum[i] - cum[i - 1]
            t = 0.0 if seg_len < 1e-9 else (s - cum[i - 1]) / seg_len
            return (pts[i - 1][0] + t * (pts[i][0] - pts[i - 1][0]),
                    pts[i - 1][1] + t * (pts[i][1] - pts[i - 1][1]))
    return pts[-1]

def draw_dashed_polyline(draw, pts, fill, width, dash=HULL_DASH_PX, gap=HULL_GAP_PX):
    """Draw a polyline as a dash pattern with the dash phase tracked
    continuously along the FULL polyline (not reset at every vertex) —
    otherwise a fine STL-triangulated contour (many sub-dash-length
    segments) renders as a solid line, since every segment restarts in
    the "on" phase."""
    if len(pts) < 2:
        return
    cum = polyline_length_map(pts)
    total = cum[-1]
    if total < 1e-6:
        return
    s = 0.0
    while s < total:
        e = min(s + dash, total)
        seg_pts = [point_at_length(pts, cum, s)]
        seg_pts += [pts[i] for i in range(1, len(cum)) if s < cum[i] < e]
        seg_pts.append(point_at_length(pts, cum, e))
        draw.line(seg_pts, fill=fill, width=width)
        s = e + gap

ANNOT_GAP_PX      = round(4 * SCALE)    # ship label — small gap, sits close to the dashed contour
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

    # Quay — top edge only (the quay is a simple rectangular block, so its
    # cross-section at any x is this same rectangle; the floor is already
    # the domain boundary, so only the top line is drawn).
    qy0, qy1 = QUAY_BOUNDS[2], QUAY_BOUNDS[3]
    qz_top   = QUAY_BOUNDS[5]
    draw.line([world_to_pixel(qy0, qz_top), world_to_pixel(qy1, qz_top)],
              fill=(0, 0, 0), width=QUAY_LINE_PX)

    # Ship — true hull cross-section, sliced out of the hull STL at x=X0.
    # Drawn on a separate overlay and composited only over background
    # (white) pixels, so it reads as sitting BEHIND the H2 concentration
    # field rather than on top of it.
    if HULL_SLICE_POLYS:
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        for poly in HULL_SLICE_POLYS_STITCHED:
            pts = [world_to_pixel(p[1], p[2]) for p in poly]
            draw_dashed_polyline(odraw, pts, fill=(0, 0, 0, 255), width=HULL_LINE_PX)

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
    output_dir = os.path.join(case_dir, f'H2_vol_con_yz_x{X0:g}')
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
        fname = os.path.join(output_dir, f'yz_slice_t{t:010.3f}s.png')
        SaveScreenshot(fname, renderView1,
                        ImageResolution=[IMG_WIDTH, IMG_HEIGHT],
                        TransparentBackground=0)
        annotate_frame(fname)
        add_axes(fname, t)
        print(f'  Saved t={t:.3f}s -> {os.path.basename(fname)}')

save_all_timesteps()
