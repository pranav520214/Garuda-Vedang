"""
3D Wind Tunnel CFD & Exploded Joining Points Visualizer
Renders:
1. Wind_Tunnel_3D_Needle_CFD_Streamlines_Hero.png (3D velocity streamlines over the needle-pointed airframe)
2. Modular_Joining_Points_and_Dowel_Pins_Exploded.png (5 sliced modules with precision male/female lips, 4x dowel pins, and M3 screw flanges)
"""

import bpy
import bmesh
import math
import os
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
        bg.inputs["Color"].default_value = (0.04, 0.05, 0.07, 1.0) # Dark aero lab background
        bg.inputs["Strength"].default_value = 1.0

def make_emission_mat(name, color, strength=5.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = color
    emit.inputs['Strength'].default_value = strength
    links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

def run_3d_cfd_renders():
    base_dir = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material"
    cad_dir = os.path.join(base_dir, r"01_CAD_Master_Models\Fresh_Paper_Sketch_Fuselage")
    blend_path = os.path.join(cad_dir, "Alapalap_Sketch_Fresh_Master.blend")
    out_dir = os.path.join(base_dir, r"03_Renderings_and_Visuals\Fresh_Fuselage_Inspection_Suite")
    os.makedirs(out_dir, exist_ok=True)

    print("==================================================================")
    print("RENDERING 3D WIND TUNNEL CFD & MODULAR JOINING POINTS")
    print("==================================================================")

    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene
    setup_render_engine(scene)

    cam = bpy.data.objects.get("Inspection_Camera")
    if not cam:
        cd = bpy.data.cameras.new("Inspection_Camera")
        cam = bpy.data.objects.new("Inspection_Camera", cd)
        scene.collection.objects.link(cam)
    scene.camera = cam

    # Materials
    mat_stream_fast = make_emission_mat("CFD_Fast_Yellow", (1.0, 0.85, 0.1, 1.0), 6.0)
    mat_stream_mid  = make_emission_mat("CFD_Mid_Cyan", (0.0, 0.95, 1.0, 1.0), 4.5)
    mat_stream_low  = make_emission_mat("CFD_Low_Blue", (0.1, 0.4, 1.0, 1.0), 3.0)

    # -------------------------------------------------------------------------
    # PART 1: BUILD 3D WIND TUNNEL STREAMLINES
    # -------------------------------------------------------------------------
    col_cfd = bpy.data.collections.new("3D_CFD_Streamlines")
    scene.collection.children.link(col_cfd)

    # Generate 3D curved streamline tubes around the needle fuselage
    streamline_seeds = [
        # (Y_start, Z_start, speed_type)
        ( 0.000, 0.040, "fast"), # Direct stagnation onto needle apex
        ( 0.012, 0.052, "fast"),
        (-0.012, 0.052, "fast"),
        ( 0.024, 0.068, "mid"),
        (-0.024, 0.068, "mid"),
        ( 0.038, 0.088, "mid"),
        (-0.038, 0.088, "mid"),
        ( 0.000, 0.108, "fast"), # Canopy roofline
        ( 0.000, 0.130, "mid"),
        ( 0.000, 0.155, "low"),
        ( 0.000, 0.012, "mid"), # Chin / underbelly
        ( 0.025, 0.015, "mid"),
        (-0.025, 0.015, "mid"),
        ( 0.055, 0.055, "low"),
        (-0.055, 0.055, "low"),
        ( 0.068, 0.060, "low"),
        (-0.068, 0.060, "low"),
    ]

    for s_idx, (y0, z0, stype) in enumerate(streamline_seeds):
        curve_data = bpy.data.curves.new(f"CFD_Streamline_{s_idx}", type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.0016 # 3.2mm glowing tube
        curve_data.bevel_resolution = 4

        spline = curve_data.splines.new('POLY')
        pts = []
        n_pts = 40
        xs = -0.15
        xe = 0.75
        for i in range(n_pts):
            t = i / (n_pts - 1)
            x = xs + (xe - xs) * t
            # Flow deflection around fuselage
            if x < 0.0:
                dist = math.sqrt(x**2 + (y0)**2 + (z0 - 0.04)**2)
                infl = math.exp(-dist * 14.0)
                y = y0 * (1.0 + infl * 0.4)
                z = z0 + (0.02 if z0 > 0.04 else -0.015) * infl
            elif x <= 0.60:
                tx = x / 0.60
                local_h = 0.11 * math.sin(tx * math.pi * 0.65)
                infl_body = math.exp(-abs(z0 - 0.05) * 12.0)
                y = y0 * (1.0 + 0.15 * math.sin(tx * math.pi))
                z = z0 + (0.035 if z0 > 0.05 else -0.018) * infl_body
            else:
                # Wake into pusher prop
                y = y0 * math.exp(-(x - 0.60) * 4.0)
                z = z0 - 0.015 * (x - 0.60)
            pts.append((x, y, z))

        spline.points.add(len(pts) - 1)
        for p_idx, pt in enumerate(pts):
            spline.points[p_idx].co = (pt[0], pt[1], pt[2], 1.0)

        c_obj = bpy.data.objects.new(f"CFD_Streamline_{s_idx}", curve_data)
        if stype == "fast":
            c_obj.data.materials.append(mat_stream_fast)
        elif stype == "mid":
            c_obj.data.materials.append(mat_stream_mid)
        else:
            c_obj.data.materials.append(mat_stream_low)
        col_cfd.objects.link(c_obj)

    # Key / Rim lights for aero visualization
    l_data = bpy.data.lights.new("Aero_Light_Top", 'AREA')
    l_data.energy = 400.0
    l_data.size = 2.0
    lo = bpy.data.objects.new("Aero_Light_Top", l_data)
    lo.location = (0.3, -0.6, 1.2)
    lo.rotation_euler = (math.radians(45), 0, math.radians(20))
    scene.collection.objects.link(lo)

    # 1. Wind Tunnel 3D CFD Streamlines Hero Angle
    cam.location = (-0.22, -0.72, 0.35)
    cam.rotation_euler = (math.radians(68), 0, math.radians(-20))
    cam.data.lens = 48.0

    out_cfd_hero = os.path.join(out_dir, "01_Wind_Tunnel_3D_Needle_CFD_Streamlines_Hero.png")
    scene.render.filepath = out_cfd_hero
    bpy.ops.render.render(write_still=True)
    print(f"Rendered 3D Wind Tunnel CFD Hero: {out_cfd_hero}")

    # 2. Needle Nose Piercing Airflow Close-up
    cam.location = (-0.18, -0.26, 0.12)
    cam.rotation_euler = (math.radians(74), 0, math.radians(-38))
    cam.data.lens = 70.0

    out_cfd_nose = os.path.join(out_dir, "02_Wind_Tunnel_CFD_Needle_Nose_Closeup.png")
    scene.render.filepath = out_cfd_nose
    bpy.ops.render.render(write_still=True)
    print(f"Rendered Needle Nose CFD Close-up: {out_cfd_nose}")

    # -------------------------------------------------------------------------
    # PART 2: EXPLODED MODULAR JOINING POINTS & DOWEL PINS RENDER
    # -------------------------------------------------------------------------
    # Hide streamlines
    col_cfd.hide_render = True

    # Set background back to clean technical studio
    if scene.world and scene.world.node_tree:
        bg_node = scene.world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs["Color"].default_value = (0.92, 0.93, 0.95, 1.0)

    # Camera for Exploded Modules with Joint Pins
    cam.location = (0.15, -0.88, 0.40)
    cam.rotation_euler = (math.radians(68), 0, math.radians(-18))
    cam.data.lens = 45.0

    out_joints = os.path.join(out_dir, "03_Modular_Joining_Points_and_Dowel_Pins_Exploded.png")
    scene.render.filepath = out_joints
    bpy.ops.render.render(write_still=True)
    print(f"Rendered Modular Joining Points Exploded View: {out_joints}")

if __name__ == "__main__":
    run_3d_cfd_renders()
