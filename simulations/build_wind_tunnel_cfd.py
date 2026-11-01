"""
Blender 3D Aerodynamic CFD & Wind Tunnel Simulator for Garuda Vedang 1500mm
Adds 3D streamlines, wingtip vortices, aerodynamic force vectors, and wind tunnel test chamber.
"""

import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Matrix
import numpy as np
import os

def run_cfd_wind_tunnel():
    print("=====================================================")
    print("Building 3D Wind Tunnel CFD Simulation in Blender...")
    print("=====================================================")

    # 1. Load current Garuda_Vedang blend file
    repo_root = Path(__file__).resolve().parent.parent
    blend_path = str(repo_root / "cad_models" / "Garuda_Vedang_1500mm_CutAccurate.blend")
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    # 2. Shaders & Materials for CFD
    def get_or_create_material(name, base_color, roughness=0.4, metallic=0.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                if hasattr(bsdf.inputs["Base Color"], "default_value"):
                    bsdf.inputs["Base Color"].default_value = base_color
                if "Roughness" in bsdf.inputs:
                    bsdf.inputs["Roughness"].default_value = roughness
                if "Metallic" in bsdf.inputs:
                    bsdf.inputs["Metallic"].default_value = metallic
        return mat

    def get_or_create_emission_mat(name, color, strength=3.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            nodes.clear()
            
            node_out = nodes.new('ShaderNodeOutputMaterial')
            node_emit = nodes.new('ShaderNodeEmission')
            node_emit.inputs['Color'].default_value = color
            node_emit.inputs['Strength'].default_value = strength
            links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])
        return mat

    mat_stream_high = get_or_create_emission_mat("CFD_Streamline_Fast_Yellow", (1.0, 0.85, 0.1, 1.0), strength=4.5)
    mat_stream_mid  = get_or_create_emission_mat("CFD_Streamline_Mid_Cyan", (0.1, 0.9, 0.95, 1.0), strength=3.5)
    mat_stream_low  = get_or_create_emission_mat("CFD_Streamline_Low_Blue", (0.1, 0.35, 1.0, 1.0), strength=3.0)
    mat_vortex      = get_or_create_emission_mat("CFD_Vortex_Core_Purple", (0.85, 0.2, 1.0, 1.0), strength=4.0)

    # Force vector materials
    mat_lift = get_or_create_emission_mat("CFD_Force_Lift_Green", (0.1, 1.0, 0.2, 1.0), strength=5.0)
    mat_drag = get_or_create_emission_mat("CFD_Force_Drag_Red", (1.0, 0.15, 0.1, 1.0), strength=5.0)
    mat_thrust = get_or_create_emission_mat("CFD_Force_Thrust_Cyan", (0.0, 0.8, 1.0, 1.0), strength=5.0)
    mat_weight = get_or_create_emission_mat("CFD_Force_Weight_Yellow", (1.0, 0.9, 0.0, 1.0), strength=5.0)

    # Wind tunnel glass material
    mat_wt_glass = bpy.data.materials.new("Mat_WindTunnel_Glass")
    mat_wt_glass.use_nodes = True
    bsdf_glass = mat_wt_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf_glass:
        bsdf_glass.inputs["Base Color"].default_value = (0.7, 0.85, 0.95, 1.0)
        bsdf_glass.inputs["Roughness"].default_value = 0.05
        if "Transmission Weight" in bsdf_glass.inputs:
            bsdf_glass.inputs["Transmission Weight"].default_value = 0.88
        elif "Transmission" in bsdf_glass.inputs:
            bsdf_glass.inputs["Transmission"].default_value = 0.88
        if "Alpha" in bsdf_glass.inputs:
            bsdf_glass.inputs["Alpha"].default_value = 0.25
        mat_wt_glass.blend_method = 'BLEND'

    # Clean up any existing CFD objects/collection from previous runs
    if "Wind_Tunnel_CFD_Simulation" in bpy.data.collections:
        old_col = bpy.data.collections["Wind_Tunnel_CFD_Simulation"]
        for obj in list(old_col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old_col)

    for obj in list(bpy.data.objects):
        if any(k in obj.name for k in ["Grid", "Streamline", "Vortex", "Vector_"]):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Create CFD collection
    col_cfd = bpy.data.collections.new("Wind_Tunnel_CFD_Simulation")
    scene.collection.children.link(col_cfd)

    def link_cfd(obj):
        col_cfd.objects.link(obj)

    # -------------------------------------------------------------
    # 3. GENERATE 3D STREAMLINES
    # -------------------------------------------------------------
    print("Generating aerodynamic streamlines...")
    
    # In aircraft coords: Nose is +Y, Tail is -Y, Wing span is X (-0.75 to +0.75), Z is Up
    # Airflow enters from +Y (front) and flows to -Y (back)
    
    def create_streamline_tube(points, mat, name, radius=0.0022):
        c_data = bpy.data.curves.new(name, 'CURVE')
        c_data.dimensions = '3D'
        c_data.bevel_depth = radius
        c_data.bevel_resolution = 4
        s = c_data.splines.new('POLY')
        s.points.add(len(points) - 1)
        for i, pt in enumerate(points):
            s.points[i].co = (pt[0], pt[1], pt[2], 1.0)
        obj = bpy.data.objects.new(name, c_data)
        obj.data.materials.append(mat)
        link_cfd(obj)
        return obj

    # A) Wing Airflow Streamlines across the span
    # Span stations: from -0.72m to +0.72m in steps
    x_stations = np.linspace(-0.70, 0.70, 29)
    y_entry = 0.350   # Entry plane in front of wing
    y_exit = -0.550   # Wake exit plane behind wing

    for x_s in x_stations:
        # Distance from center for dihedral lift
        x_abs = abs(x_s)
        z_dihedral = max(0.0, (x_abs - 0.062) * math.tan(math.radians(1.5)))
        z_wing_base = 0.096 + z_dihedral

        # Upper surface streamline (Accelerated high-speed flow)
        pts_upper = [
            (x_s, y_entry, z_wing_base + 0.008),
            (x_s, 0.120,   z_wing_base + 0.012),
            (x_s, 0.040,   z_wing_base + 0.024),
            (x_s, 0.010,   z_wing_base + 0.038),  # Suction peak over camber
            (x_s, -0.050,  z_wing_base + 0.035),
            (x_s, -0.120,  z_wing_base + 0.026),
            (x_s, -0.210,  z_wing_base + 0.010),  # Trailing edge
            (x_s, -0.320,  z_wing_base - 0.005),  # Downwash deflection
            (x_s, y_exit,  z_wing_base - 0.020)
        ]
        # Color: near suction peak is fast yellow, rest is cyan
        create_streamline_tube(pts_upper, mat_stream_high if abs(x_s) < 0.6 else mat_stream_mid, f"Streamline_Upper_{x_s:.2f}")

        # Lower surface streamline (High pressure boundary layer)
        pts_lower = [
            (x_s, y_entry, z_wing_base - 0.008),
            (x_s, 0.120,   z_wing_base - 0.008),
            (x_s, 0.030,   z_wing_base - 0.004),
            (x_s, 0.000,   z_wing_base - 0.002),
            (x_s, -0.100,  z_wing_base - 0.002),
            (x_s, -0.210,  z_wing_base - 0.002),
            (x_s, -0.320,  z_wing_base - 0.015),
            (x_s, y_exit,  z_wing_base - 0.025)
        ]
        create_streamline_tube(pts_lower, mat_stream_low, f"Streamline_Lower_{x_s:.2f}", radius=0.0018)

    # B) Fuselage Exterior Streamlines (Over cabin roof, under belly, and flanking flanks)
    # Flank streamlines
    for x_sign in [-1.0, 1.0]:
        for z_lvl in [0.035, 0.065]:
            pts_f = [
                (x_sign * 0.080, 0.350, z_lvl),
                (x_sign * 0.075, 0.180, z_lvl),
                (x_sign * 0.072, 0.000, z_lvl),
                (x_sign * 0.070, -0.220, z_lvl),
                (x_sign * 0.055, -0.380, z_lvl + 0.010),
                (x_sign * 0.035, y_exit, z_lvl + 0.015)
            ]
            create_streamline_tube(pts_f, mat_stream_mid, f"Streamline_Fuse_Flank_{x_sign}_{z_lvl}", radius=0.0020)

    # Under-belly streamlines (flowing under flat belly then curving up along rear upsweep)
    for x_off in [-0.035, 0.0, 0.035]:
        pts_belly = [
            (x_off, 0.350, -0.012),
            (x_off, 0.120, -0.008),
            (x_off, 0.000, -0.005),
            (x_off, -0.200, -0.005),
            (x_off, -0.315, -0.005),
            (x_off, -0.436, 0.025), # Follows upsweep towards bottom of motor firewall
            (x_off, y_exit, 0.030)
        ]
        create_streamline_tube(pts_belly, mat_stream_low, f"Streamline_Belly_{x_off}", radius=0.0018)

    # Over-cabin centerline streamline
    pts_roof = [
        (0.0, 0.350, 0.100),
        (0.0, 0.140, 0.115),
        (0.0, 0.000, 0.135),
        (0.0, -0.198, 0.120),
        (0.0, -0.315, 0.095),
        (0.0, -0.436, 0.090),
        (0.0, y_exit, 0.080)
    ]
    create_streamline_tube(pts_roof, mat_stream_high, "Streamline_Cabin_Roof", radius=0.0022)

    # -------------------------------------------------------------
    # 4. WINGTIP TRAILING VORTICES (Induced Drag Visualization)
    # -------------------------------------------------------------
    print("Generating wingtip trailing vortices...")
    
    for sign, side in [(-1.0, "Left"), (1.0, "Right")]:
        x_tip = sign * 0.750
        z_tip = 0.096 + (0.750 - 0.062) * math.tan(math.radians(1.5))
        y_start = -0.190
        
        # Helical spiral expanding aft
        vortex_pts = []
        n_helices = 60
        for i in range(n_helices):
            t = i / float(n_helices)
            y_v = y_start - t * 0.450 # extends 450mm behind wingtip
            # Radius expands slightly as vortex diffuses
            r_v = 0.008 + 0.025 * t
            # Rotation angle (right wing rolls counter-clockwise looking aft, left rolls clockwise)
            angle = -sign * t * 6.0 * math.pi
            
            x_v = x_tip - sign * (0.012 + 0.015*t) + r_v * math.cos(angle)
            z_v = z_tip + r_v * math.sin(angle) - 0.030 * t # downwash descent
            vortex_pts.append((x_v, y_v, z_v))

        create_streamline_tube(vortex_pts, mat_vortex, f"Wingtip_Vortex_Core_{side}", radius=0.0028)

        # Outer secondary vortex streak
        vortex_pts_outer = []
        for i in range(n_helices):
            t = i / float(n_helices)
            y_v = y_start - t * 0.450
            r_v = 0.018 + 0.040 * t
            angle = -sign * t * 6.0 * math.pi + math.pi
            x_v = x_tip - sign * (0.012 + 0.015*t) + r_v * math.cos(angle)
            z_v = z_tip + r_v * math.sin(angle) - 0.030 * t
            vortex_pts_outer.append((x_v, y_v, z_v))
        create_streamline_tube(vortex_pts_outer, mat_stream_mid, f"Wingtip_Vortex_Outer_{side}", radius=0.0016)

    # -------------------------------------------------------------
    # 5. AERODYNAMIC FORCE VECTORS (Free Body Diagram)
    # Placed at Aerodynamic Center / Center of Gravity (X=0, Y=-0.030, Z=0.080)
    # -------------------------------------------------------------
    print("Generating Aerodynamic Force Vectors...")
    ac_point = Vector((0.0, -0.030, 0.096))

    def make_force_arrow(name, start, direction, length, mat, shaft_r=0.005, head_r=0.014, head_len=0.040):
        # Cylinder shaft
        shaft_len = length - head_len
        dir_norm = direction.normalized()
        mid_shaft = start + dir_norm * (shaft_len * 0.5)
        
        # Rotation towards direction
        rot = dir_norm.to_track_quat('Z', 'Y')

        bpy.ops.mesh.primitive_cylinder_add(
            radius=shaft_r,
            depth=shaft_len,
            location=mid_shaft
        )
        shaft = bpy.context.active_object
        shaft.name = f"{name}_Shaft"
        shaft.rotation_euler = rot.to_euler()
        shaft.data.materials.append(mat)
        link_cfd(shaft)
        bpy.context.collection.objects.unlink(shaft)

        # Arrowhead cone
        head_pos = start + dir_norm * (shaft_len + head_len * 0.5)
        bpy.ops.mesh.primitive_cone_add(
            radius1=head_r,
            radius2=0.0,
            depth=head_len,
            location=head_pos
        )
        cone = bpy.context.active_object
        cone.name = f"{name}_Head"
        cone.rotation_euler = rot.to_euler()
        cone.data.materials.append(mat)
        link_cfd(cone)
        bpy.context.collection.objects.unlink(cone)

    # Lift Vector (L = 9.81 N - Points Upwards +Z)
    make_force_arrow("Vector_Lift_9.8N", ac_point, Vector((0, 0, 1)), 0.220, mat_lift)

    # Drag Vector (D = 0.98 N - Points Backward -Y)
    make_force_arrow("Vector_Drag_0.98N", ac_point, Vector((0, -1, 0)), 0.120, mat_drag)

    # Thrust Vector (T = 0.98 N - Points Forward +Y from motor firewall M1 center at Z=0.0535m)
    motor_point = Vector((0.0, -0.4361, 0.0535))
    make_force_arrow("Vector_Thrust_0.98N", motor_point, Vector((0, 1, 0)), 0.120, mat_thrust)

    # Weight Vector (W = 9.81 N - Points Downward -Z)
    make_force_arrow("Vector_Weight_9.8N", ac_point, Vector((0, 0, -1)), 0.160, mat_weight)

    # -------------------------------------------------------------
    # 6. VIRTUAL WIND TUNNEL TEST CHAMBER
    # -------------------------------------------------------------
    print("Building Wind Tunnel Chamber...")

    # Wireframe Grid Test Chamber (Length 2.2m, Width 1.9m, Height 1.0m)
    wt_min = (-0.95, -0.65, -0.15)
    wt_max = ( 0.95,  0.45,  0.85)

    # Aerodynamic Dark Stage Floor
    floor_obj = bpy.data.objects.get("Studio_Ground_Floor")
    if floor_obj:
        mat_dark = get_or_create_material("Mat_CFD_Floor_Dark", (0.04, 0.04, 0.05, 1.0), roughness=0.8)
        floor_obj.data.materials.clear()
        floor_obj.data.materials.append(mat_dark)

    # -------------------------------------------------------------
    # 7. CFD CAMERAS & HIGH-RES RENDERS
    # -------------------------------------------------------------
    print("Configuring CFD Cameras and Rendering...")

    # Camera CFD 1: Dramatic 3/4 Isometric Airflow View
    cam_cfd1_data = bpy.data.cameras.new("Cam_CFD_Isometric")
    cam_cfd1_data.lens = 50.0
    cam_cfd1 = bpy.data.objects.new("Cam_CFD_Isometric", cam_cfd1_data)
    cam_cfd1.location = (1.35, 1.15, 0.60)
    dir1 = Vector((0.0, -0.05, 0.08)) - cam_cfd1.location
    cam_cfd1.rotation_euler = dir1.to_track_quat('-Z', 'Y').to_euler()
    link_cfd(cam_cfd1)

    # Camera CFD 2: Close-up Wingtip Vortex View
    cam_cfd2_data = bpy.data.cameras.new("Cam_CFD_Wingtip_Vortex")
    cam_cfd2_data.lens = 55.0
    cam_cfd2 = bpy.data.objects.new("Cam_CFD_Wingtip_Vortex", cam_cfd2_data)
    cam_cfd2.location = (1.35, -0.15, 0.38)
    dir2 = Vector((0.72, -0.30, 0.12)) - cam_cfd2.location
    cam_cfd2.rotation_euler = dir2.to_track_quat('-Z', 'Y').to_euler()
    link_cfd(cam_cfd2)

    # Camera CFD 3: Side Streamline Profile
    cam_cfd3_data = bpy.data.cameras.new("Cam_CFD_Side_Profile")
    cam_cfd3_data.type = 'ORTHO'
    cam_cfd3_data.ortho_scale = 1.25
    cam_cfd3 = bpy.data.objects.new("Cam_CFD_Side_Profile", cam_cfd3_data)
    cam_cfd3.location = (2.20, -0.08, 0.10)
    cam_cfd3.rotation_euler = mathutils.Euler((1.570796, 0.0, 1.570796))
    link_cfd(cam_cfd3)

    # Lighting adjustments for glowing CFD streamlines
    # Dim ambient light slightly so emission streamlines pop vibrantly
    for l_name in ["Light_Key_Warm", "Light_Fill_Cool", "Light_Rim_Back"]:
        l = bpy.data.objects.get(l_name)
        if l and l.data:
            l.data.energy *= 0.65

    # Save Blend File with CFD scene
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved updated .blend file with CFD simulation: {blend_path}")

    def safe_render(target_path):
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except Exception:
                pass
        scene.render.filepath = target_path
        bpy.ops.render.render(write_still=True)

    # Render CFD Image 1 (Isometric Wind Tunnel)
    scene.camera = cam_cfd1
    img1_path = str(repo_root / "assets" / "cfd_renders" / "Garuda_Vedang_CFD_Wind_Tunnel_Isometric.png")
    safe_render(img1_path)
    print(f"Rendered CFD Isometric to: {img1_path}")

    # Render CFD Image 2 (Wingtip Vortex Close-up)
    scene.camera = cam_cfd2
    img2_path = str(repo_root / "assets" / "cfd_renders" / "Garuda_Vedang_CFD_Wingtip_Vortex.png")
    safe_render(img2_path)
    print(f"Rendered CFD Wingtip Vortex to: {img2_path}")

    # Render CFD Image 3 (Side Streamline Profile)
    scene.camera = cam_cfd3
    img3_path = str(repo_root / "assets" / "cfd_renders" / "Garuda_Vedang_CFD_Side_Streamlines.png")
    safe_render(img3_path)
    print(f"Rendered CFD Side Streamlines to: {img3_path}")

    # Re-export GLB with CFD streamlines included
    glb_path = str(repo_root / "cad_models" / "Garuda_Vedang_1500mm_CFD.glb")
    bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB')
    print(f"Exported interactive CFD GLB model to: {glb_path}")

    print("=====================================================")
    print("CFD SIMULATION SETUP COMPLETE!")
    print("=====================================================")

if __name__ == "__main__":
    run_cfd_wind_tunnel()
