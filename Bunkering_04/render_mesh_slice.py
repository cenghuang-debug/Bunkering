"""Render Bunkering_04 y=0 mesh slice zoomed to ship/quay/nozzle region."""
from paraview.simple import *
import os

case_file = os.path.join(os.path.dirname(__file__), "open.foam")
out_png   = os.path.join(os.path.dirname(__file__), "mesh_slice_y0.png")

# ── Reader 1: internal mesh for slice ─────────────────────────────────────
mesh = OpenFOAMReader(FileName=case_file)
mesh.MeshRegions = ["internalMesh"]
mesh.CellArrays  = []
mesh.UpdatePipeline(time=0.0)

# ── Reader 2: solid wall patches only ─────────────────────────────────────
walls = OpenFOAMReader(FileName=case_file)
walls.MeshRegions = ["patch/bunkering-boat_m",
                     "patch/bunkering-quay_m",
                     "patch/bottom",
                     "patch/nozzle_holder_wall"]
walls.CellArrays  = []
walls.UpdatePipeline(time=0.0)

# ── Reader 3: nozzle inlet patch (highlight) ──────────────────────────────
nozzle = OpenFOAMReader(FileName=case_file)
nozzle.MeshRegions = ["patch/nozzle"]
nozzle.CellArrays  = []
nozzle.UpdatePipeline(time=0.0)

# ── Slice internal mesh at y = 0 ──────────────────────────────────────────
slc = Slice(Input=mesh)
slc.SliceType        = "Plane"
slc.SliceType.Normal = [0, 1, 0]
slc.SliceType.Origin = [0, 0, 10]

# ── Render view ───────────────────────────────────────────────────────────
renderView = GetActiveViewOrCreate("RenderView")
renderView.ViewSize            = [1400, 800]
renderView.BackgroundColorMode = "Single Color"
renderView.Background          = [1.0, 1.0, 1.0]

def flat(disp):
    disp.Ambient  = 1.0
    disp.Diffuse  = 0.0
    disp.Specular = 0.0
    disp.ColorArrayName = [None, '']

# Draw walls first (solid, behind the slice)
wallDisp = Show(walls, renderView)
wallDisp.Representation = "Surface"
wallDisp.AmbientColor   = [0.40, 0.35, 0.30]
wallDisp.DiffuseColor   = [0.40, 0.35, 0.30]
wallDisp.Opacity         = 1.0
flat(wallDisp)

# Mesh slice on top — light blue cells, dark edges
slcDisplay = Show(slc, renderView)
slcDisplay.Representation = "Surface With Edges"
slcDisplay.AmbientColor   = [0.65, 0.83, 0.97]
slcDisplay.DiffuseColor   = [0.65, 0.83, 0.97]
slcDisplay.EdgeColor       = [0.10, 0.10, 0.10]
slcDisplay.LineWidth       = 0.8
flat(slcDisplay)

# Nozzle patch — red highlight
nozzDisp = Show(nozzle, renderView)
nozzDisp.Representation = "Surface"
nozzDisp.AmbientColor   = [0.85, 0.15, 0.10]
nozzDisp.DiffuseColor   = [0.85, 0.15, 0.10]
nozzDisp.Opacity         = 1.0
flat(nozzDisp)

# ── Camera: orthographic, looking in +y, focused on x[-30,35] z[0,18] ─────
# centre (2.5, -, 9), half-height ≈ 18.6 (gives ~65 m wide for 1.75 aspect)
renderView.ResetCamera()
cam = GetActiveCamera()
cam.SetParallelProjection(1)
cam.SetPosition(2.5, -500, 9)
cam.SetFocalPoint(2.5,    0, 9)
cam.SetViewUp(0, 0, 1)
cam.SetParallelScale(18.6)
renderView.Update()

SaveScreenshot(out_png, renderView,
               ImageResolution=[1400, 800],
               TransparentBackground=1)

from PIL import Image
img   = Image.open(out_png).convert("RGBA")
white = Image.new("RGBA", img.size, (255, 255, 255, 255))
white.paste(img, mask=img.split()[3])
white.convert("RGB").save(out_png)
print("Saved:", out_png)
