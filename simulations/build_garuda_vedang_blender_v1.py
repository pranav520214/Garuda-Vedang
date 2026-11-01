"""
Procedural Cut-Accurate 3D Model Generator for Garuda Vedang 1500mm RC Plane (v4 - Inverted Fuselage to User Specification)
"""

import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Matrix

def run():
    print("=====================================================")
    print("Building Garuda Vedang 1500mm 3D Model (Inverted Fuselage)...")
    print("=====================================================")

    # 1. Reset Scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'MILLIMETERS'

    # 2. Materials
    def get_or_create_material(name, base_color, roughness=0.4, metallic=0.0, alpha=1.0):
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
                if alpha < 1.0 and "Alpha" in bsdf.inputs:
                    bsdf.inputs["Alpha"].default_value = alpha
                    mat.blend_method = 'BLEND'
        return mat

    mat_polyfoam = get_or_create_material("Mat_Polyfoam_White", (0.95, 0.96, 0.97, 1.0), roughness=0.55)
    mat_red_stripe = get_or_create_material("Mat_Aero_Red_Stripe", (0.88, 0.06, 0.08, 1.0), roughness=0.3)
    mat_plywood = get_or_create_material("Mat_Birch_Plywood_2mm", (0.76, 0.62, 0.44, 1.0), roughness=0.7)
    mat_carbon = get_or_create_material("Mat_Carbon_Fiber_Boom", (0.08, 0.08, 0.09, 1.0), roughness=0.3, metallic=0.1)
    mat_camera = get_or_create_material("Mat_FPV_Camera_Black", (0.05, 0.05, 0.05, 1.0), roughness=0.2, metallic=0.3)
    mat_lens = get_or_create_material("Mat_Camera_Lens_Glass", (0.02, 0.08, 0.12, 1.0), roughness=0.05, metallic=0.8)
    mat_motor = get_or_create_material("Mat_Brushless_Anodized", (0.12, 0.38, 0.78, 1.0), roughness=0.2, metallic=0.9)
    mat_prop = get_or_create_material("Mat_APC_Propeller_Gray", (0.35, 0.36, 0.38, 1.0), roughness=0.35)
    mat_rubber = get_or_create_material("Mat_Tire_Rubber", (0.03, 0.03, 0.03, 1.0), roughness=0.9)
    mat_wheel_hub = get_or_create_material("Mat_Wheel_Hub_White", (0.9, 0.9, 0.9, 1.0), roughness=0.4)
    mat_metal_wire = get_or_create_material("Mat_Spring_Steel_Wire", (0.80, 0.82, 0.85, 1.0), roughness=0.2, metallic=0.95)

    # 3. Collections
    def create_collection(name, parent_col=None):
        col = bpy.data.collections.new(name)
        if parent_col:
            parent_col.children.link(col)
        else:
            scene.collection.children.link(col)
        return col

    col_3d = create_collection("Assembled_Airframe_3D")
    col_wing = create_collection("Wing_Assembly", col_3d)
    col_fuse = create_collection("Fuselage_Assembly", col_3d)
    col_tail = create_collection("Tail_Assembly", col_3d)
    col_prop = create_collection("Propulsion_System", col_3d)
    col_gear = create_collection("Landing_Gear", col_3d)
    col_flat = create_collection("Cut_Parts_Templates_Flat")
    col_flat.hide_render = True

    def link_obj(obj, col):
        col.objects.link(obj)

    # Airfoil profile generator
    def get_airfoil_coords(chord, max_thick):
        points = []
        n_pts = 24
        for i in range(n_pts + 1):
            s = i / float(n_pts)
            xc = 0.5 * (1.0 - math.cos(s * math.pi))
            y = -xc * chord
            zu = max_thick * (
                2.969 * math.sqrt(xc)
                - 1.260 * xc
                - 3.516 * (xc**2)
                + 2.843 * (xc**3)
                - 1.036 * (xc**4)
            )
            zu = max(0.0, zu)
            points.append((y, zu))

        for i in range(n_pts, -1, -1):
            s = i / float(n_pts)
            xc = 0.5 * (1.0 - math.cos(s * math.pi))
            y = -xc * chord
            if xc >= 0.25:
                zl = 0.0
            else:
                zl = max_thick * 0.15 * math.cos(xc / 0.25 * math.pi * 0.5)
            if i != n_pts and i != 0:
                points.append((y, zl))
        return points

    # Dimensions
    SPAN_HALF = 0.750
    CHORD_ROOT = 0.226
    CHORD_TIP = 0.202
    WING_THICK = 0.0226
    FUSE_WIDTH = 0.1239
    FUSE_HEIGHT = 0.0960
    BOOM_LEN = 0.5261
    BOOM_SPACING = 0.3209
    TAIL_SPAN = 0.3209
    TAIL_CHORD = 0.1000
    FIN_HEIGHT = 0.2073

    # =============================================================
    # 4. FUSELAGE (UPSIDE DOWN AS REQUESTED)
    # Bottom is flat at Z = 0.000m.
    # Nose slopes downward towards the front.
    # Rear top steps/slopes down towards the firewall.
    # =============================================================
    def build_fuselage():
        bm = bmesh.new()

        # Flipped upside down relative to previous:
        # Flat bottom belly at Z = 0.000m
        # Sloping nose wedge on top
        # Stepped/sloping rear deck
        stations = [
            # y_pos,   half_width,      z_bottom, z_top
            ( 0.180,   0.028,           0.008,    0.032), # Nose tip
            ( 0.140,   0.045,           0.000,    0.066), # Sloping nose wedge
            ( 0.080,   FUSE_WIDTH*0.5,  0.000,    0.096), # Cabin start
            ( 0.020,   FUSE_WIDTH*0.5,  0.000,    0.096), # Wing leading edge saddle
            (-0.206,   FUSE_WIDTH*0.5,  0.000,    0.096), # Wing trailing edge saddle
            (-0.320,   0.045,           0.000,    0.068), # Rear deck slope/step
            (-0.400,   0.028,           0.000,    0.044), # Firewall M1 (width 56mm, height 44mm)
        ]

        rings = []
        for y_pos, hw, zb, zt in stations:
            r = min(0.012, hw * 0.3)
            pts = [
                (-hw + r, zb),
                ( hw - r, zb),
                ( hw,     zb + r),
                ( hw,     zt - r),
                ( hw - r, zt),
                (-hw + r, zt),
                (-hw,     zt - r),
                (-hw,     zb + r)
            ]
            ring = [bm.verts.new((x, y_pos, z)) for x, z in pts]
            rings.append(ring)

        for i in range(len(rings) - 1):
            r1 = rings[i]
            r2 = rings[i+1]
            for j in range(8):
                j_next = (j + 1) % 8
                bm.faces.new([r1[j], r1[j_next], r2[j_next], r2[j]])

        bm.faces.new(rings[0])
        bm.faces.new(reversed(rings[-1]))

        mesh = bpy.data.meshes.new("Fuselage_Main_Body")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Fuselage_Main_Body", mesh)
        obj.data.materials.append(mat_polyfoam)
        link_obj(obj, col_fuse)
        return obj

    build_fuselage()

    # --- Fuselage Red Racing Stripe ---
    def build_fuselage_stripe():
        bm = bmesh.new()
        hw = FUSE_WIDTH * 0.5 + 0.0008
        pts_r = [
            ( hw,  0.040, 0.005),
            ( hw,  0.060, 0.005),
            ( hw,  0.075, 0.093),
            ( hw,  0.055, 0.093),
        ]
        pts_l = [
            (-hw,  0.040, 0.005),
            (-hw,  0.060, 0.005),
            (-hw,  0.075, 0.093),
            (-hw,  0.055, 0.093),
        ]
        vr = [bm.verts.new(p) for p in pts_r]
        vl = [bm.verts.new(p) for p in pts_l]
        bm.faces.new(vr)
        bm.faces.new(reversed(vl))

        mesh = bpy.data.meshes.new("Fuselage_Red_Decal")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new("Fuselage_Red_Decal", mesh)
        obj.data.materials.append(mat_red_stripe)
        link_obj(obj, col_fuse)

    build_fuselage_stripe()

    # --- FPV Camera Pod on Nose Wedge ---
    def build_fpv_camera():
        # Mounted on the upper sloping nose
        bpy.ops.mesh.primitive_cube_add(
            size=0.026,
            location=(0, 0.120, 0.075),
            scale=(0.8, 1.1, 0.8)
        )
        cam_box = bpy.context.active_object
        cam_box.name = "FPV_Camera_Body"
        cam_box.data.materials.append(mat_camera)
        col_fuse.objects.link(cam_box)
        bpy.context.collection.objects.unlink(cam_box)

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.006,
            depth=0.010,
            location=(0, 0.138, 0.075),
            rotation=(math.radians(90), 0, 0)
        )
        lens = bpy.context.active_object
        lens.name = "FPV_Camera_Lens"
        lens.data.materials.append(mat_lens)
        col_fuse.objects.link(lens)
        bpy.context.collection.objects.unlink(lens)

    build_fpv_camera()

    # --- Motor Mount Firewall M1 (2mm Plywood at rear) ---
    def build_motor_mount():
        bm = bmesh.new()
        hw = 0.0557 * 0.5
        hh = 0.0440 * 0.5
        y_pos = -0.4005
        z_center = 0.022 # Centered on the 44mm firewall

        v1 = bm.verts.new((-hw, y_pos, z_center - hh))
        v2 = bm.verts.new(( hw, y_pos, z_center - hh))
        v3 = bm.verts.new(( hw, y_pos, z_center + hh))
        v4 = bm.verts.new((-hw, y_pos, z_center + hh))
        bm.faces.new([v1, v2, v3, v4])

        mesh = bpy.data.meshes.new("Motor_Mount_M1_Plywood")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Motor_Mount_M1_Plywood", mesh)
        obj.data.materials.append(mat_plywood)
        link_obj(obj, col_fuse)

    build_motor_mount()

    # =============================================================
    # 5. WINGS (Mounted on top deck, Y from +0.020 to -0.206)
    # =============================================================
    def build_wing_half(is_left=False):
        sign = -1.0 if is_left else 1.0
        name = "Wing_Left" if is_left else "Wing_Right"

        bm = bmesh.new()
        stations = [
            (FUSE_WIDTH * 0.5, CHORD_ROOT, 0.0),
            (0.250, 0.218, math.radians(1.5)),
            (0.500, 0.210, math.radians(1.5)),
            (SPAN_HALF, CHORD_TIP, math.radians(1.5))
        ]

        section_rings = []
        for x_dist, chord, dihedral_ang in stations:
            x_pos = sign * x_dist
            z_lift = (x_dist - FUSE_WIDTH * 0.5) * math.tan(dihedral_ang)
            z_base = FUSE_HEIGHT + z_lift

            profile = get_airfoil_coords(chord, WING_THICK)
            ring = []
            for py, pz in profile:
                vert = bm.verts.new((x_pos, +0.020 + py, z_base + pz))
                ring.append(vert)
            section_rings.append(ring)

        for i in range(len(section_rings) - 1):
            r1 = section_rings[i]
            r2 = section_rings[i+1]
            n = len(r1)
            for j in range(n):
                j_next = (j + 1) % n
                if is_left:
                    bm.faces.new([r1[j], r1[j_next], r2[j_next], r2[j]])
                else:
                    bm.faces.new([r1[j], r2[j], r2[j_next], r1[j_next]])

        if is_left:
            bm.faces.new(reversed(section_rings[0]))
            bm.faces.new(section_rings[-1])
        else:
            bm.faces.new(section_rings[0])
            bm.faces.new(reversed(section_rings[-1]))

        bm.normal_update()

        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(name, mesh)
        obj.data.materials.append(mat_polyfoam)
        link_obj(obj, col_wing)
        return obj

    build_wing_half(is_left=True)
    build_wing_half(is_left=False)

    # --- Wing Red Stripes ---
    def build_wing_stripe(is_left=False):
        sign = -1.0 if is_left else 1.0
        name = "Aero_Stripe_Left" if is_left else "Aero_Stripe_Right"
        bm = bmesh.new()

        x1 = sign * 0.280
        x2 = sign * 0.320
        z_base = FUSE_HEIGHT + 0.005

        profile1 = get_airfoil_coords(0.215, WING_THICK + 0.001)
        n_sub = 12
        verts1 = [bm.verts.new((x1, +0.020 + profile1[i][0], z_base + profile1[i][1] + 0.0006)) for i in range(n_sub)]
        verts2 = [bm.verts.new((x2, +0.020 + profile1[i][0], z_base + profile1[i][1] + 0.0006)) for i in range(n_sub)]

        for i in range(n_sub - 1):
            if is_left:
                bm.faces.new([verts1[i], verts1[i+1], verts2[i+1], verts2[i]])
            else:
                bm.faces.new([verts1[i], verts2[i], verts2[i+1], verts1[i+1]])

        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        obj.data.materials.append(mat_red_stripe)
        link_obj(obj, col_wing)

    build_wing_stripe(is_left=True)
    build_wing_stripe(is_left=False)

    # =============================================================
    # 6. TWIN TAIL BOOMS & EMPENNAGE
    # =============================================================
    def build_tail_booms():
        hw = BOOM_SPACING * 0.5
        y_start = -0.060
        y_end = y_start - BOOM_LEN
        z_pos = FUSE_HEIGHT + 0.002

        for is_left in [True, False]:
            sign = -1.0 if is_left else 1.0
            name = "Tail_Boom_Left_F9" if is_left else "Tail_Boom_Right_F9"

            bm = bmesh.new()
            h_start = 0.0288
            h_end = 0.0160
            thick = 0.006

            x_c = sign * hw
            pts1 = [
                (x_c - thick*0.5, y_start, z_pos - h_start),
                (x_c + thick*0.5, y_start, z_pos - h_start),
                (x_c + thick*0.5, y_start, z_pos),
                (x_c - thick*0.5, y_start, z_pos),
            ]
            pts2 = [
                (x_c - thick*0.5, y_end, z_pos - h_end),
                (x_c + thick*0.5, y_end, z_pos - h_end),
                (x_c + thick*0.5, y_end, z_pos),
                (x_c - thick*0.5, y_end, z_pos),
            ]
            v1 = [bm.verts.new(p) for p in pts1]
            v2 = [bm.verts.new(p) for p in pts2]

            for i in range(4):
                bm.faces.new([v1[i], v1[(i+1)%4], v2[(i+1)%4], v2[i]])
            bm.faces.new(reversed(v1))
            bm.faces.new(v2)

            mesh = bpy.data.meshes.new(name)
            bm.to_mesh(mesh)
            bm.free()

            obj = bpy.data.objects.new(name, mesh)
            obj.data.materials.append(mat_carbon)
            link_obj(obj, col_tail)

    build_tail_booms()

    def build_empennage():
        y_rear = -0.060 - BOOM_LEN
        y_front = y_rear + TAIL_CHORD
        z_pos = FUSE_HEIGHT - 0.005
        hw = TAIL_SPAN * 0.5
        thick = 0.005

        # S1 Horizontal Stabilizer
        bm_s1 = bmesh.new()
        v_s1 = [
            bm_s1.verts.new((-hw, y_front, z_pos)),
            bm_s1.verts.new(( hw, y_front, z_pos)),
            bm_s1.verts.new(( hw, y_rear,  z_pos)),
            bm_s1.verts.new((-hw, y_rear,  z_pos)),
            bm_s1.verts.new((-hw, y_front, z_pos + thick)),
            bm_s1.verts.new(( hw, y_front, z_pos + thick)),
            bm_s1.verts.new(( hw, y_rear,  z_pos + thick)),
            bm_s1.verts.new((-hw, y_rear,  z_pos + thick)),
        ]
        bm_s1.faces.new([v_s1[0], v_s1[1], v_s1[2], v_s1[3]])
        bm_s1.faces.new([v_s1[7], v_s1[6], v_s1[5], v_s1[4]])
        bm_s1.faces.new([v_s1[0], v_s1[4], v_s1[5], v_s1[1]])
        bm_s1.faces.new([v_s1[1], v_s1[5], v_s1[6], v_s1[2]])
        bm_s1.faces.new([v_s1[2], v_s1[6], v_s1[7], v_s1[3]])
        bm_s1.faces.new([v_s1[3], v_s1[7], v_s1[4], v_s1[0]])

        mesh_s1 = bpy.data.meshes.new("Horizontal_Stabilizer_S1")
        bm_s1.to_mesh(mesh_s1)
        bm_s1.free()
        obj_s1 = bpy.data.objects.new("Horizontal_Stabilizer_S1", mesh_s1)
        obj_s1.data.materials.append(mat_polyfoam)
        link_obj(obj_s1, col_tail)

        # S3 Elevator
        bm_s3 = bmesh.new()
        y_elev_rear = y_rear - 0.0243
        hw_elev = 0.3162 * 0.5
        v_s3 = [
            bm_s3.verts.new((-hw_elev, y_rear - 0.001, z_pos)),
            bm_s3.verts.new(( hw_elev, y_rear - 0.001, z_pos)),
            bm_s3.verts.new(( hw_elev, y_elev_rear,   z_pos)),
            bm_s3.verts.new((-hw_elev, y_elev_rear,   z_pos)),
            bm_s3.verts.new((-hw_elev, y_rear - 0.001, z_pos + thick)),
            bm_s3.verts.new(( hw_elev, y_rear - 0.001, z_pos + thick)),
            bm_s3.verts.new(( hw_elev, y_elev_rear,   z_pos + thick)),
            bm_s3.verts.new((-hw_elev, y_elev_rear,   z_pos + thick)),
        ]
        bm_s3.faces.new([v_s3[0], v_s3[1], v_s3[2], v_s3[3]])
        bm_s3.faces.new([v_s3[7], v_s3[6], v_s3[5], v_s3[4]])
        bm_s3.faces.new([v_s3[0], v_s3[4], v_s3[5], v_s3[1]])
        bm_s3.faces.new([v_s3[1], v_s3[5], v_s3[6], v_s3[2]])
        bm_s3.faces.new([v_s3[2], v_s3[6], v_s3[7], v_s3[3]])
        bm_s3.faces.new([v_s3[3], v_s3[7], v_s3[4], v_s3[0]])

        mesh_s3 = bpy.data.meshes.new("Elevator_S3")
        bm_s3.to_mesh(mesh_s3)
        bm_s3.free()
        obj_s3 = bpy.data.objects.new("Elevator_S3", mesh_s3)
        obj_s3.data.materials.append(mat_polyfoam)
        link_obj(obj_s3, col_tail)

        # S2 Vertical Fins & S4 Rudders
        for is_left in [True, False]:
            sign = -1.0 if is_left else 1.0
            side_str = "Left" if is_left else "Right"
            x_pos = sign * hw

            bm_s2 = bmesh.new()
            p_base_front = (x_pos, y_front + 0.010, z_pos)
            p_base_rear  = (x_pos, y_rear,          z_pos)
            p_tip_rear   = (x_pos, y_rear - 0.020,  z_pos + FIN_HEIGHT)
            p_tip_front  = (x_pos, y_rear + 0.030,  z_pos + FIN_HEIGHT)

            dx = 0.0025
            v_fin = [
                bm_s2.verts.new((x_pos - dx, p_base_front[1], p_base_front[2])),
                bm_s2.verts.new((x_pos - dx, p_base_rear[1],  p_base_rear[2])),
                bm_s2.verts.new((x_pos - dx, p_tip_rear[1],   p_tip_rear[2])),
                bm_s2.verts.new((x_pos - dx, p_tip_front[1],  p_tip_front[2])),
                bm_s2.verts.new((x_pos + dx, p_base_front[1], p_base_front[2])),
                bm_s2.verts.new((x_pos + dx, p_base_rear[1],  p_base_rear[2])),
                bm_s2.verts.new((x_pos + dx, p_tip_rear[1],   p_tip_rear[2])),
                bm_s2.verts.new((x_pos + dx, p_tip_front[1],  p_tip_front[2])),
            ]
            bm_s2.faces.new([v_fin[0], v_fin[1], v_fin[2], v_fin[3]])
            bm_s2.faces.new([v_fin[7], v_fin[6], v_fin[5], v_fin[4]])
            bm_s2.faces.new([v_fin[0], v_fin[3], v_fin[7], v_fin[4]])
            bm_s2.faces.new([v_fin[3], v_fin[2], v_fin[6], v_fin[7]])
            bm_s2.faces.new([v_fin[2], v_fin[1], v_fin[5], v_fin[6]])
            bm_s2.faces.new([v_fin[1], v_fin[0], v_fin[4], v_fin[5]])

            mesh_s2 = bpy.data.meshes.new(f"Vertical_Fin_{side_str}_S2")
            bm_s2.to_mesh(mesh_s2)
            bm_s2.free()
            obj_s2 = bpy.data.objects.new(f"Vertical_Fin_{side_str}_S2", mesh_s2)
            obj_s2.data.materials.append(mat_polyfoam)
            link_obj(obj_s2, col_tail)

            bm_s4 = bmesh.new()
            p_rud_base_rear = (x_pos, p_base_rear[1] - 0.0407, z_pos)
            p_rud_tip_rear  = (x_pos, p_tip_rear[1] - 0.0407,  z_pos + FIN_HEIGHT)

            v_rud = [
                bm_s4.verts.new((x_pos - dx, p_base_rear[1] - 0.001, p_base_rear[2])),
                bm_s4.verts.new((x_pos - dx, p_rud_base_rear[1],    p_rud_base_rear[2])),
                bm_s4.verts.new((x_pos - dx, p_rud_tip_rear[1],     p_rud_tip_rear[2])),
                bm_s4.verts.new((x_pos - dx, p_tip_rear[1] - 0.001,  p_tip_rear[2])),
                bm_s4.verts.new((x_pos + dx, p_base_rear[1] - 0.001, p_base_rear[2])),
                bm_s4.verts.new((x_pos + dx, p_rud_base_rear[1],    p_rud_base_rear[2])),
                bm_s4.verts.new((x_pos + dx, p_rud_tip_rear[1],     p_rud_tip_rear[2])),
                bm_s4.verts.new((x_pos + dx, p_tip_rear[1] - 0.001,  p_tip_rear[2])),
            ]
            bm_s4.faces.new([v_rud[0], v_rud[1], v_rud[2], v_rud[3]])
            bm_s4.faces.new([v_rud[7], v_rud[6], v_rud[5], v_rud[4]])
            bm_s4.faces.new([v_rud[0], v_rud[3], v_rud[7], v_rud[4]])
            bm_s4.faces.new([v_rud[3], v_rud[2], v_rud[6], v_rud[7]])
            bm_s4.faces.new([v_rud[2], v_rud[1], v_rud[5], v_rud[6]])
            bm_s4.faces.new([v_rud[1], v_rud[0], v_rud[4], v_rud[5]])

            mesh_s4 = bpy.data.meshes.new(f"Rudder_{side_str}_S4")
            bm_s4.to_mesh(mesh_s4)
            bm_s4.free()
            obj_s4 = bpy.data.objects.new(f"Rudder_{side_str}_S4", mesh_s4)
            obj_s4.data.materials.append(mat_polyfoam)
            link_obj(obj_s4, col_tail)

    build_empennage()

    # =============================================================
    # 7. PROPULSION (Motor mounted on M1 at rear)
    # =============================================================
    def build_propulsion():
        y_mount = -0.401
        z_motor = 0.022 # Centered on rear firewall

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.014,
            depth=0.030,
            location=(0, y_mount - 0.015, z_motor),
            rotation=(math.radians(90), 0, 0)
        )
        motor_obj = bpy.context.active_object
        motor_obj.name = "Brushless_Motor_BR2212"
        motor_obj.data.materials.append(mat_motor)
        col_prop.objects.link(motor_obj)
        bpy.context.collection.objects.unlink(motor_obj)

        y_prop = y_mount - 0.032
        bpy.ops.mesh.primitive_cone_add(
            radius1=0.011,
            radius2=0.003,
            depth=0.018,
            location=(0, y_prop - 0.009, z_motor),
            rotation=(math.radians(-90), 0, 0)
        )
        spinner_obj = bpy.context.active_object
        spinner_obj.name = "Propeller_Spinner"
        spinner_obj.data.materials.append(mat_prop)
        col_prop.objects.link(spinner_obj)
        bpy.context.collection.objects.unlink(spinner_obj)

        bm = bmesh.new()
        r_prop = 0.1016
        for sign in [-1.0, 1.0]:
            pts = [
                (sign * 0.010, y_prop, z_motor - 0.003),
                (sign * 0.060, y_prop + 0.003, z_motor - 0.008),
                (sign * r_prop, y_prop + 0.002, z_motor - 0.003),
                (sign * r_prop, y_prop - 0.002, z_motor + 0.003),
                (sign * 0.060, y_prop - 0.003, z_motor + 0.008),
                (sign * 0.010, y_prop, z_motor + 0.003),
            ]
            verts = [bm.verts.new(p) for p in pts]
            bm.faces.new(verts)

        mesh_prop = bpy.data.meshes.new("Propeller_8x6_Pusher")
        bm.to_mesh(mesh_prop)
        bm.free()
        obj_prop = bpy.data.objects.new("Propeller_8x6_Pusher", mesh_prop)
        obj_prop.data.materials.append(mat_prop)
        link_obj(obj_prop, col_prop)

    build_propulsion()

    # =============================================================
    # 8. LANDING GEAR (Under flat belly)
    # =============================================================
    def build_landing_gear():
        wheel_r = 0.0524 * 0.5
        wheel_w = 0.018
        ground_z = -0.090

        def make_wheel(name, loc):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=wheel_r,
                depth=wheel_w,
                location=loc,
                rotation=(0, math.radians(90), 0)
            )
            tire_obj = bpy.context.active_object
            tire_obj.name = name
            tire_obj.data.materials.append(mat_rubber)
            col_gear.objects.link(tire_obj)
            bpy.context.collection.objects.unlink(tire_obj)

            bpy.ops.mesh.primitive_cylinder_add(
                radius=wheel_r * 0.5,
                depth=wheel_w + 0.002,
                location=loc,
                rotation=(0, math.radians(90), 0)
            )
            hub_obj = bpy.context.active_object
            hub_obj.name = f"{name}_Hub"
            hub_obj.data.materials.append(mat_wheel_hub)
            col_gear.objects.link(hub_obj)
            bpy.context.collection.objects.unlink(hub_obj)

            return tire_obj

        # Nose Gear
        y_nose = 0.090
        make_wheel("Nose_Wheel", (0, y_nose, ground_z + wheel_r))

        c_nose = bpy.data.curves.new("NoseStrutCurve", 'CURVE')
        c_nose.dimensions = '3D'
        c_nose.bevel_depth = 0.0018
        c_nose.bevel_resolution = 4
        s_nose = c_nose.splines.new('POLY')
        s_nose.points.add(1)
        s_nose.points[0].co = (0.0, y_nose, 0.000, 1.0)
        s_nose.points[1].co = (0.0, y_nose, ground_z + wheel_r, 1.0)
        obj_ns = bpy.data.objects.new("Nose_Gear_Wire_Strut", c_nose)
        obj_ns.data.materials.append(mat_metal_wire)
        link_obj(obj_ns, col_gear)

        # Main Gear
        y_main = -0.040
        track_w = 0.240
        x_wl = -track_w * 0.5
        x_wr =  track_w * 0.5

        make_wheel("Main_Wheel_Left", (x_wl, y_main, ground_z + wheel_r))
        make_wheel("Main_Wheel_Right", (x_wr, y_main, ground_z + wheel_r))

        c_main = bpy.data.curves.new("MainGearCurve", 'CURVE')
        c_main.dimensions = '3D'
        c_main.bevel_depth = 0.0018
        c_main.bevel_resolution = 4
        s_main = c_main.splines.new('POLY')
        s_main.points.add(2)
        s_main.points[0].co = (x_wl, y_main, ground_z + wheel_r, 1.0)
        s_main.points[1].co = (0.0,  y_main, 0.000, 1.0)
        s_main.points[2].co = (x_wr, y_main, ground_z + wheel_r, 1.0)
        obj_ms = bpy.data.objects.new("Main_Gear_Wire_Strut", c_main)
        obj_ms.data.materials.append(mat_metal_wire)
        link_obj(obj_ms, col_gear)

    build_landing_gear()

    # =============================================================
    # 9. FLAT CUT PATTERN KIT
    # =============================================================
    Y_BED_OFFSET = 1.400

    def make_cut_plate(name, w_mm, h_mm, thick_mm, x_offset_mm, y_offset_mm, mat):
        w = w_mm * 0.001
        h = h_mm * 0.001
        th = thick_mm * 0.001
        x0 = x_offset_mm * 0.001
        y0 = Y_BED_OFFSET + y_offset_mm * 0.001

        bm = bmesh.new()
        v = [
            bm.verts.new((x0,     y0,     0.0)),
            bm.verts.new((x0 + w, y0,     0.0)),
            bm.verts.new((x0 + w, y0 + h, 0.0)),
            bm.verts.new((x0,     y0 + h, 0.0)),
            bm.verts.new((x0,     y0,     th)),
            bm.verts.new((x0 + w, y0,     th)),
            bm.verts.new((x0 + w, y0 + h, th)),
            bm.verts.new((x0,     y0 + h, th)),
        ]
        bm.faces.new([v[0], v[1], v[2], v[3]])
        bm.faces.new([v[7], v[6], v[5], v[4]])
        bm.faces.new([v[0], v[4], v[5], v[1]])
        bm.faces.new([v[1], v[5], v[6], v[2]])
        bm.faces.new([v[2], v[6], v[7], v[3]])
        bm.faces.new([v[3], v[7], v[4], v[0]])

        mesh = bpy.data.meshes.new(f"CutPart_{name}")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(f"CutPart_{name}", mesh)
        obj.data.materials.append(mat)
        link_obj(obj, col_flat)
        return obj

    make_cut_plate("A0_Cutting_Bed_Surface", 1189.0, 841.0, 1.0, -594.5, -420.5, mat_carbon)
    make_cut_plate("W1_Wing_Base_Half", 750.4, 226.3, 5.0, -560.0, 160.0, mat_polyfoam)
    make_cut_plate("W5_Wing_Upper_Skin", 750.5, 234.0, 5.0, -560.0, -100.0, mat_polyfoam)
    make_cut_plate("W2_Airfoil_Ribs_x2", 202.1, 22.6, 5.0, 220.0, 260.0, mat_polyfoam)
    make_cut_plate("W3_W4_Wing_Spars", 745.0, 45.0, 5.0, -560.0, -170.0, mat_polyfoam)
    make_cut_plate("F2_Fuselage_Sides_x2", 579.5, 96.0, 5.0, -560.0, -290.0, mat_polyfoam)
    make_cut_plate("F1_Fuselage_Bottom", 420.1, 123.9, 5.0, 80.0, 10.0, mat_polyfoam)
    make_cut_plate("F8_Fuselage_Top", 370.3, 123.9, 5.0, 80.0, 150.0, mat_polyfoam)
    make_cut_plate("S1_Horizontal_Stab", 320.9, 100.0, 5.0, 80.0, -120.0, mat_polyfoam)
    make_cut_plate("S3_Elevator", 316.2, 24.3, 5.0, 80.0, -160.0, mat_polyfoam)
    make_cut_plate("S2_Vertical_Fins_x2", 100.4, 207.3, 5.0, 420.0, -100.0, mat_polyfoam)
    make_cut_plate("S4_Rudders_x2", 40.7, 207.3, 5.0, 420.0, 120.0, mat_polyfoam)
    make_cut_plate("W6_Wing_Dihedral_Joiner", 335.3, 32.4, 2.0, -560.0, -340.0, mat_plywood)
    make_cut_plate("F9_Tail_Booms_x2", 526.1, 28.8, 2.0, -200.0, -380.0, mat_plywood)
    make_cut_plate("M1_Motor_Firewall", 55.7, 44.0, 2.0, 440.0, -200.0, mat_plywood)
    make_cut_plate("G1_G2_Gear_Mounts", 118.6, 71.2, 2.0, 440.0, -300.0, mat_plywood)

    # =============================================================
    # 10. STUDIO LIGHTING & RENDERS
    # =============================================================
    col_studio = create_collection("Studio_Setup")

    # Camera matching user's perspective angle exactly
    cam_data = bpy.data.cameras.new("Camera_User_View")
    cam_data.lens = 55.0
    cam_obj = bpy.data.objects.new("Camera_User_View", cam_data)
    cam_obj.location = (1.20, 0.90, 0.40)
    target_pos = Vector((0.0, -0.05, 0.05))
    direction = target_pos - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    link_obj(cam_obj, col_studio)
    scene.camera = cam_obj

    # Camera 2: Side Orthographic
    cam_side_data = bpy.data.cameras.new("Camera_Side_Ortho")
    cam_side_data.type = 'ORTHO'
    cam_side_data.ortho_scale = 1.05
    cam_side_obj = bpy.data.objects.new("Camera_Side_Ortho", cam_side_data)
    cam_side_obj.location = (2.0, -0.12, 0.06)
    cam_side_obj.rotation_euler = mathutils.Euler((1.570796, 0.0, 1.570796))
    link_obj(cam_side_obj, col_studio)

    # Lights
    def add_light(name, light_type, energy, color, loc):
        l_data = bpy.data.lights.new(name, light_type)
        l_data.energy = energy
        l_data.color = color
        l_obj = bpy.data.objects.new(name, l_data)
        l_obj.location = loc
        link_obj(l_obj, col_studio)
        return l_obj

    add_light("Light_Key_Warm", 'POINT', 500.0, (1.0, 0.96, 0.92), (1.6, 1.5, 1.8))
    add_light("Light_Fill_Cool", 'POINT', 280.0, (0.88, 0.94, 1.0), (-1.8, 1.0, 1.4))
    add_light("Light_Rim_Back", 'POINT', 420.0, (1.0, 1.0, 1.0), (-0.4, -1.8, 1.6))

    # Floor plane
    bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0, 0, -0.090))
    floor = bpy.context.active_object
    floor.name = "Studio_Ground_Floor"
    mat_floor = get_or_create_material("Mat_Studio_Floor", (0.16, 0.17, 0.20, 1.0), roughness=0.6)
    floor.data.materials.append(mat_floor)
    col_studio.objects.link(floor)
    bpy.context.collection.objects.unlink(floor)

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    # Save Blend File
    output_blend = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_1500mm_CutAccurate.blend"
    bpy.ops.wm.save_as_mainfile(filepath=output_blend)
    print(f"Saved complete .blend file to: {output_blend}")

    # Render User Perspective Angle
    scene.camera = cam_obj
    output_img = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_3D_Preview.png"
    scene.render.filepath = output_img
    bpy.ops.render.render(write_still=True)
    print(f"Rendered perspective preview to: {output_img}")

    # Render Side Profile
    scene.camera = cam_side_obj
    output_side_img = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_3D_Side_Profile.png"
    scene.render.filepath = output_side_img
    bpy.ops.render.render(write_still=True)
    print(f"Rendered side profile to: {output_side_img}")

    # Export GLB and OBJ
    glb_path = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_1500mm.glb"
    bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB')
    print(f"Exported GLB to: {glb_path}")

    obj_path = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_1500mm.obj"
    bpy.ops.wm.obj_export(filepath=obj_path)
    print(f"Exported OBJ to: {obj_path}")

    print("=====================================================")
    print("FINISHED SUCCESSFULLY!")
    print("=====================================================")

if __name__ == "__main__":
    run()
