"""
Garuda Vedang // 3D Simulation Heatmaps Engine (Blender)
Renders 3D heatmaps directly on the fuselage:
1. Garuda_Vedang_3D_CFD_Pressure_Heatmap.png
2. Garuda_Vedang_3D_FEA_VonMises_Stress_Heatmap.png
3. Garuda_Vedang_3D_Thermal_Dissipation_Heatmap.png
4. Garuda_Vedang_3D_Vibrational_Modal_Heatmap.png
"""

import bpy
import math
import os
import shutil
from mathutils import Vector, Matrix

def setup_render_engine(scene):
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    if scene.world is None:
        scene.world = bpy.data.worlds.new("Studio_World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.05, 0.06, 0.08, 1.0)
        bg.inputs["Strength"].default_value = 1.0

def create_heatmap_material(name, heatmap_type):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['Metallic'].default_value = 0.05
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
    links.new(mapping.outputs['Vector'], sep_xyz.inputs['Vector'])

    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.color_ramp.interpolation = 'LINEAR'

    math_norm = nodes.new('ShaderNodeMapRange')
    math_norm.inputs['From Min'].default_value = 0.0
    math_norm.inputs['From Max'].default_value = 0.60
    math_norm.inputs['To Min'].default_value = 0.0
    math_norm.inputs['To Max'].default_value = 1.0
    links.new(sep_xyz.outputs['X'], math_norm.inputs['Value'])

    if heatmap_type == "pressure":
        color_ramp.color_ramp.elements[0].position = 0.00
        color_ramp.color_ramp.elements[0].color = (0.95, 0.10, 0.10, 1.0) # Red (Stagnation Cp=1.0)
        
        el1 = color_ramp.color_ramp.elements.new(0.04)
        el1.color = (1.0, 0.85, 0.10, 1.0) # Yellow (Decay)

        el2 = color_ramp.color_ramp.elements.new(0.18)
        el2.color = (0.0, 0.90, 0.95, 1.0) # Cyan (Suction peak Cp=-0.45)

        el3 = color_ramp.color_ramp.elements.new(0.55)
        el3.color = (0.05, 0.35, 0.90, 1.0) # Deep Blue (Canopy)

        color_ramp.color_ramp.elements[-1].position = 1.00
        color_ramp.color_ramp.elements[-1].color = (0.10, 0.80, 0.35, 1.0) # Green (Boattail Recovery)

    elif heatmap_type == "stress":
        color_ramp.color_ramp.elements[0].position = 0.00
        color_ramp.color_ramp.elements[0].color = (0.05, 0.25, 0.85, 1.0) # Blue (1.2 MPa)

        el1 = color_ramp.color_ramp.elements.new(0.35)
        el1.color = (0.95, 0.20, 0.10, 1.0) # Peak Red (8.42 MPa Battery Bay)

        el2 = color_ramp.color_ramp.elements.new(0.60)
        el2.color = (0.95, 0.70, 0.10, 1.0) # Orange (6.8 MPa Wing Saddle Anchors)

        color_ramp.color_ramp.elements[-1].position = 1.00
        color_ramp.color_ramp.elements[-1].color = (0.10, 0.50, 0.80, 1.0) # Blue-Teal

    elif heatmap_type == "thermal":
        color_ramp.color_ramp.elements[0].position = 0.00
        color_ramp.color_ramp.elements[0].color = (0.05, 0.40, 0.90, 1.0) # 22°C Ambient Intake

        el1 = color_ramp.color_ramp.elements.new(0.35)
        el1.color = (0.95, 0.65, 0.10, 1.0) # 38°C LiPo Bay

        el2 = color_ramp.color_ramp.elements.new(0.60)
        el2.color = (0.95, 0.30, 0.05, 1.0) # 48°C ESC / Avionics

        color_ramp.color_ramp.elements[-1].position = 1.00
        color_ramp.color_ramp.elements[-1].color = (1.00, 0.05, 0.05, 1.0) # 58°C Motor Stator

    elif heatmap_type == "modal":
        color_ramp.color_ramp.elements[0].position = 0.00
        color_ramp.color_ramp.elements[0].color = (0.95, 0.10, 0.10, 1.0) # Antinode Nose (Red)

        el1 = color_ramp.color_ramp.elements.new(0.30)
        el1.color = (0.05, 0.30, 0.85, 1.0) # Node Rigid Floor Deck (Blue)

        el2 = color_ramp.color_ramp.elements.new(0.75)
        el2.color = (0.10, 0.85, 0.45, 1.0) # Green Mid-span

        color_ramp.color_ramp.elements[-1].position = 1.00
        color_ramp.color_ramp.elements[-1].color = (0.95, 0.55, 0.10, 1.0) # Antinode Tail (Orange)

    links.new(math_norm.outputs['Result'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

    if "Emission Color" in bsdf.inputs:
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 0.15

    return mat

def run_blender_heatmaps():
    base_dir = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material"
    cad_dir = os.path.join(base_dir, r"01_CAD_Master_Models\Fresh_Paper_Sketch_Fuselage")
    blend_path = os.path.join(cad_dir, "Alapalap_Sketch_Fresh_Master.blend")
    out_dir = os.path.join(base_dir, r"03_Renderings_and_Visuals\Garuda_Vedang_Simulation_Heatmaps")
    git_dir = r"C:\Users\RYZEN\Desktop\Garuda-Vedang\assets\simulation_heatmaps"
    art_dir = r"C:\Users\RYZEN\.gemini\antigravity\brain\d4ad7151-bb82-48bd-8a4a-2e6446755332"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(git_dir, exist_ok=True)

    print("==================================================================")
    print("GARUDA VEDANG // RENDERING 3D SIMULATION HEATMAPS IN BLENDER")
    print("==================================================================")

    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene
    setup_render_engine(scene)

    hull = bpy.data.objects.get("Fresh_Sketch_Aerodynamic_Hull")
    if not hull:
        print("ERROR: Hull not found!")
        return

    cam = bpy.data.objects.get("Inspection_Camera")
    if not cam:
        cd = bpy.data.cameras.new("Inspection_Camera")
        cam = bpy.data.objects.new("Inspection_Camera", cd)
        scene.collection.objects.link(cam)
    scene.camera = cam

    # Set Camera to Clean Hero CAE Angle
    cam.location = (-0.20, -0.68, 0.32)
    cam.rotation_euler = (math.radians(68), 0, math.radians(-20))
    cam.data.lens = 50.0

    heatmaps = [
        ("Garuda_Vedang_3D_CFD_Pressure_Heatmap.png", "pressure", "Aerodynamic Surface Pressure Cp"),
        ("Garuda_Vedang_3D_FEA_VonMises_Stress_Heatmap.png", "stress", "Von Mises Structural Stress (4.5G Pull-Up)"),
        ("Garuda_Vedang_3D_Thermal_Dissipation_Heatmap.png", "thermal", "Thermal Dissipation & Ventilation Profile"),
        ("Garuda_Vedang_3D_Vibrational_Modal_Heatmap.png", "modal", "Resonant Modal Vibration Amplitude")
    ]

    for fname, htype, desc in heatmaps:
        print(f"\nRendering 3D Heatmap: {desc} -> {fname}...")
        mat = create_heatmap_material(f"Mat_Heatmap_{htype}", htype)
        hull.data.materials.clear()
        hull.data.materials.append(mat)

        fpath = os.path.join(out_dir, fname)
        scene.render.filepath = fpath
        bpy.ops.render.render(write_still=True)
        print(f"Saved: {fpath}")

        # Sync to git assets and artifacts
        git_path = os.path.join(git_dir, fname)
        art_path = os.path.join(art_dir, fname)
        if os.path.exists(fpath):
            shutil.copy2(fpath, git_path)
            shutil.copy2(fpath, art_path)

    print("\nAll 3D Heatmap Renders Completed!")

if __name__ == "__main__":
    run_blender_heatmaps()
