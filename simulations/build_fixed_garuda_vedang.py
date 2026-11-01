import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

def build_accurate_garuda_vedang():
    print("=====================================================")
    print("Building Cut-Accurate Garuda Vedang 1500mm Airframe in Blender...")
    print("=====================================================")

    # 1. Reset Scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    scene.unit_settings.scale_length = 1.0

    # 2. Materials
    def get_or_create_material(name, color, roughness=0.5, metallic=0.0):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
        return mat

    mat_polyfoam   = get_or_create_material("Mat_Polyfoam_White", (0.95, 0.96, 0.97, 1.0), roughness=0.45)
    mat_red_stripe = get_or_create_material("Mat_Aero_Red_Stripe", (0.88, 0.06, 0.08, 1.0), roughness=0.3)
    mat_plywood    = get_or_create_material("Mat_Birch_Plywood_2mm", (0.76, 0.62, 0.44, 1.0), roughness=0.7)
    mat_carbon     = get_or_create_material("Mat_Carbon_Fiber_Boom", (0.12, 0.12, 0.14, 1.0), roughness=0.3, metallic=0.2)
    mat_camera     = get_or_create_material("Mat_FPV_Camera_Black", (0.05, 0.05, 0.05, 1.0), roughness=0.2, metallic=0.3)
    mat_lens       = get_or_create_material("Mat_Camera_Lens_Glass", (0.02, 0.08, 0.12, 1.0), roughness=0.05, metallic=0.8)
    mat_motor      = get_or_create_material("Mat_Brushless_Anodized", (0.12, 0.38, 0.78, 1.0), roughness=0.2, metallic=0.9)
    mat_prop       = get_or_create_material("Mat_APC_Propeller_Gray", (0.35, 0.36, 0.38, 1.0), roughness=0.35)
    mat_rubber     = get_or_create_material("Mat_Tire_Rubber", (0.03, 0.03, 0.03, 1.0), roughness=0.9)
    mat_wheel_hub  = get_or_create_material("Mat_Wheel_Hub_White", (0.9, 0.9, 0.9, 1.0), roughness=0.4)
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
    col_fuse = create_collection("Fuselage_Assembly", col_3d)
    col_wing = create_collection("Wing_Assembly", col_3d)
    col_tail = create_collection("Tail_Assembly", col_3d)
    col_prop = create_collection("Propulsion_System", col_3d)
    col_gear = create_collection("Landing_Gear", col_3d)

    def link_obj(obj, col):
        col.objects.link(obj)

    # Airfoil coordinate generator (Clark-Y)
    def get_airfoil_coords(chord, max_thick):
        points = []
        n_pts = 24
        # Upper surface
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

        # Lower surface (flat from 25% chord to trailing edge)
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

    # =============================================================
    # 4. FUSELAGE POD (100% Exact to Blueprint F2 Cut Template)
    # Coordinate frame:
    # Y = 0.000m at Wing Leading Edge Saddle
    # Z = 0.000m at Flat Belly Floor
    # Positive Y is Forward (towards nose)
    # Negative Y is Aft (towards motor)
    # Positive Z is Up
    # =============================================================
    FUSE_WIDTH = 0.1239  # 123.9mm from F1 / F8 templates

    def build_fuselage():
        bm = bmesh.new()

        # Exact stations based on Drawing 28 CAD coordinates:
        # y_pos, half_width, z_bottom, z_top
        stations = [
            (+0.1432, 0.0280, 0.0165, 0.0165), # 0: Nose tip apex
            (+0.1045, 0.0460, 0.0000, 0.0605), # 1: Nose facet 1 & start of flat belly
            (+0.0625, 0.0580, 0.0000, 0.0839), # 2: Nose facet 2
            (+0.0000, FUSE_WIDTH*0.5, 0.0000, 0.0958), # 3: Wing LE saddle (cabin start)
            (-0.1979, FUSE_WIDTH*0.5, 0.0000, 0.0958), # 4: Wing TE saddle (wing root end)
            (-0.1980, FUSE_WIDTH*0.5, 0.0000, 0.0736), # 5: Rear deck vertical step-down
            (-0.3148, 0.0460, 0.0003, 0.0732), # 6: End of flat belly & start of rear upsweep
            (-0.4361, 0.0278, 0.0342, 0.0729)  # 7: Motor Firewall M1 (height 38.7mm, width 55.7mm)
        ]

        rings = []
        for y_pos, hw, zb, zt in stations:
            h = zt - zb
            r = min(0.010, hw * 0.3, max(0.001, h * 0.25))
            if h <= 0.002:
                pts = [(-hw, zb), (hw, zb)]
                ring = [bm.verts.new((x, y_pos, z)) for x, z in pts]
            else:
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

        # Connect nose tip to first ring
        r0 = rings[0]
        r1 = rings[1]
        bm.faces.new([r0[0], r0[1], r1[1], r1[0]])
        bm.faces.new([r0[1], r1[2], r1[3], r1[4]])
        bm.faces.new([r0[1], r1[4], r1[5], r0[0]])
        bm.faces.new([r0[0], r1[5], r1[6], r1[7]])
        bm.faces.new([r0[0], r1[7], r1[0], r0[1]])

        # Connect intermediate rings
        for i in range(1, len(rings) - 1):
            ra = rings[i]
            rb = rings[i+1]
            for j in range(8):
                j_next = (j + 1) % 8
                bm.faces.new([ra[j], ra[j_next], rb[j_next], rb[j]])

        # Rear firewall cap
        bm.faces.new(reversed(rings[-1]))

        mesh = bpy.data.meshes.new("Fuselage_Main_Body")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Fuselage_Main_Body", mesh)
        obj.data.materials.append(mat_polyfoam)
        link_obj(obj, col_fuse)
        return obj

    build_fuselage()

    # --- Fuselage Red Racing Stripes (Snapped to fuselage surface) ---
    def build_fuselage_stripe():
        bm = bmesh.new()
        # Stripe located between Y = +0.020 and +0.045
        # Fuselage half-width here is exactly 0.060
        hw = 0.0605
        pts_r = [
            ( hw, +0.015, 0.005),
            ( hw, +0.035, 0.005),
            ( hw, +0.045, 0.088),
            ( hw, +0.025, 0.088),
        ]
        pts_l = [
            (-hw, +0.015, 0.005),
            (-hw, +0.035, 0.005),
            (-hw, +0.045, 0.088),
            (-hw, +0.025, 0.088),
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

    # --- FPV Camera on Upper Sloping Nose ---
    def build_fpv_camera():
        # Mounted at Y=+0.080m, Z=0.086m on the nose deck
        bpy.ops.mesh.primitive_cube_add(
            size=0.022,
            location=(0, +0.080, 0.084),
            scale=(0.85, 1.1, 0.85)
        )
        cam_box = bpy.context.active_object
        cam_box.name = "FPV_Camera_Body"
        cam_box.data.materials.append(mat_camera)
        col_fuse.objects.link(cam_box)
        bpy.context.collection.objects.unlink(cam_box)

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.006,
            depth=0.010,
            location=(0, +0.094, 0.084),
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
        y_pos = -0.4366
        zb = 0.0342
        zt = 0.0729

        v1 = bm.verts.new((-hw, y_pos, zb))
        v2 = bm.verts.new(( hw, y_pos, zb))
        v3 = bm.verts.new(( hw, y_pos, zt))
        v4 = bm.verts.new((-hw, y_pos, zt))
        bm.faces.new([v1, v2, v3, v4])

        mesh = bpy.data.meshes.new("Motor_Mount_M1_Plywood")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Motor_Mount_M1_Plywood", mesh)
        obj.data.materials.append(mat_plywood)
        link_obj(obj, col_fuse)

    build_motor_mount()

    # =============================================================
    # 5. FULL CONTINUOUS WING (1500mm Span, Clark-Y Airfoil)
    # Continuous across fuselage without gaps.
    # =============================================================
    SPAN_HALF    = 0.750
    CHORD_ROOT   = 0.198  # Exact match to wing saddle 197.9mm
    CHORD_TIP    = 0.160
    WING_THICK   = 0.0226
    DIHEDRAL_ANG = math.radians(1.5)

    def build_complete_wing():
        bm = bmesh.new()

        stations = [
            (-SPAN_HALF, CHORD_TIP, (SPAN_HALF - FUSE_WIDTH*0.5) * math.tan(DIHEDRAL_ANG)),
            (-0.450, 0.180, (0.450 - FUSE_WIDTH*0.5) * math.tan(DIHEDRAL_ANG)),
            (-FUSE_WIDTH*0.5, CHORD_ROOT, 0.0),
            (0.000, CHORD_ROOT, 0.0),
            (+FUSE_WIDTH*0.5, CHORD_ROOT, 0.0),
            (+0.450, 0.180, (0.450 - FUSE_WIDTH*0.5) * math.tan(DIHEDRAL_ANG)),
            (+SPAN_HALF, CHORD_TIP, (SPAN_HALF - FUSE_WIDTH*0.5) * math.tan(DIHEDRAL_ANG))
        ]

        section_rings = []
        for x_pos, chord, z_lift in stations:
            z_base = 0.0958 + z_lift
            profile = get_airfoil_coords(chord, WING_THICK)
            ring = []
            for py, pz in profile:
                vert = bm.verts.new((x_pos, py, z_base + pz))
                ring.append(vert)
            section_rings.append(ring)

        # Connect ribs spanwise
        for i in range(len(section_rings) - 1):
            r1 = section_rings[i]
            r2 = section_rings[i+1]
            n = len(r1)
            for j in range(n):
                j_next = (j + 1) % n
                bm.faces.new([r1[j], r2[j], r2[j_next], r1[j_next]])

        # Caps on wingtips
        bm.faces.new(section_rings[0])
        bm.faces.new(reversed(section_rings[-1]))
        bm.normal_update()

        mesh = bpy.data.meshes.new("Wing_Continuous_1500mm")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Wing_Continuous_1500mm", mesh)
        obj.data.materials.append(mat_polyfoam)
        link_obj(obj, col_wing)
        return obj

    build_complete_wing()

    # --- Wing Red Racing Stripes ---
    def build_wing_stripes():
        for sign in [-1.0, 1.0]:
            name = f"Aero_Stripe_{'Left' if sign < 0 else 'Right'}"
            bm = bmesh.new()
            x1 = sign * 0.320
            x2 = sign * 0.360
            chord_loc = 0.185
            z_lift = (0.340 - FUSE_WIDTH*0.5) * math.tan(DIHEDRAL_ANG)
            z_base = 0.0958 + z_lift

            profile = get_airfoil_coords(chord_loc, WING_THICK + 0.0006)
            n_sub = 14
            v1 = [bm.verts.new((x1, profile[i][0], z_base + profile[i][1] + 0.0003)) for i in range(n_sub)]
            v2 = [bm.verts.new((x2, profile[i][0], z_base + profile[i][1] + 0.0003)) for i in range(n_sub)]

            for i in range(n_sub - 1):
                if sign < 0:
                    bm.faces.new([v1[i], v1[i+1], v2[i+1], v2[i]])
                else:
                    bm.faces.new([v1[i], v2[i], v2[i+1], v1[i+1]])

            mesh = bpy.data.meshes.new(name)
            bm.to_mesh(mesh)
            bm.free()
            obj = bpy.data.objects.new(name, mesh)
            obj.data.materials.append(mat_red_stripe)
            link_obj(obj, col_wing)

    build_wing_stripes()

    # =============================================================
    # 6. TWIN TAIL BOOMS & EMPENNAGE
    # Booms attach under the wing (at Z = 0.0958m) at X = +/- 0.1605m
    # =============================================================
    BOOM_SPACING = 0.3209
    BOOM_LEN     = 0.5261
    TAIL_SPAN    = 0.3209
    TAIL_CHORD   = 0.1000
    FIN_HEIGHT   = 0.2073

    y_boom_start = -0.080
    y_boom_end   = y_boom_start - BOOM_LEN

    def build_tail_booms():
        hw = BOOM_SPACING * 0.5
        z_pos = 0.0958 # Attached directly under the wing lower surface

        for is_left in [True, False]:
            sign = -1.0 if is_left else 1.0
            name = f"Tail_Boom_{'Left' if is_left else 'Right'}_F9"

            bm = bmesh.new()
            h_start = 0.0288
            h_end   = 0.0160
            thick   = 0.008

            xc = sign * hw
            pts1 = [
                (xc - thick*0.5, y_boom_start, z_pos - h_start),
                (xc + thick*0.5, y_boom_start, z_pos - h_start),
                (xc + thick*0.5, y_boom_start, z_pos),
                (xc - thick*0.5, y_boom_start, z_pos),
            ]
            pts2 = [
                (xc - thick*0.5, y_boom_end, z_pos - h_end),
                (xc + thick*0.5, y_boom_end, z_pos - h_end),
                (xc + thick*0.5, y_boom_end, z_pos),
                (xc - thick*0.5, y_boom_end, z_pos),
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
            obj.data.materials.append(mat_polyfoam)
            link_obj(obj, col_tail)

    build_tail_booms()

    # --- Empennage: Horizontal Stabilizer S1, Elevator S3, Vertical Fins S2, Rudders S4 ---
    def build_empennage():
        hw = BOOM_SPACING * 0.5
        y_rear = y_boom_end
        y_front = y_rear + TAIL_CHORD
        z_pos = 0.0958 - 0.008
        th = 0.005 # 5mm polyfoam

        # Horizontal Stabilizer S1
        bm_s1 = bmesh.new()
        v_s1 = [
            bm_s1.verts.new((-hw, y_front, z_pos)),
            bm_s1.verts.new(( hw, y_front, z_pos)),
            bm_s1.verts.new(( hw, y_rear,  z_pos)),
            bm_s1.verts.new((-hw, y_rear,  z_pos)),
            bm_s1.verts.new((-hw, y_front, z_pos + th)),
            bm_s1.verts.new(( hw, y_front, z_pos + th)),
            bm_s1.verts.new(( hw, y_rear,  z_pos + th)),
            bm_s1.verts.new((-hw, y_rear,  z_pos + th)),
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

        # Elevator S3
        bm_s3 = bmesh.new()
        y_elev_end = y_rear - 0.0243
        v_s3 = [
            bm_s3.verts.new((-hw + 0.002, y_rear - 0.001, z_pos)),
            bm_s3.verts.new(( hw - 0.002, y_rear - 0.001, z_pos)),
            bm_s3.verts.new(( hw - 0.002, y_elev_end,     z_pos)),
            bm_s3.verts.new((-hw + 0.002, y_elev_end,     z_pos)),
            bm_s3.verts.new((-hw + 0.002, y_rear - 0.001, z_pos + th)),
            bm_s3.verts.new(( hw - 0.002, y_rear - 0.001, z_pos + th)),
            bm_s3.verts.new(( hw - 0.002, y_elev_end,     z_pos + th)),
            bm_s3.verts.new((-hw + 0.002, y_elev_end,     z_pos + th)),
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

        # Vertical Fins S2 & Rudders S4
        for is_left in [True, False]:
            sign = -1.0 if is_left else 1.0
            side_str = "Left" if is_left else "Right"
            xc = sign * hw

            bm_s2 = bmesh.new()
            p_base_front = (xc, y_front + 0.010, z_pos)
            p_base_rear  = (xc, y_rear,          z_pos)
            p_tip_rear   = (xc, y_rear - 0.020,  z_pos + FIN_HEIGHT)
            p_tip_front  = (xc, y_rear + 0.030,  z_pos + FIN_HEIGHT)

            dx = 0.0025
            v_fin = [
                bm_s2.verts.new((xc - dx, p_base_front[1], p_base_front[2])),
                bm_s2.verts.new((xc - dx, p_base_rear[1],  p_base_rear[2])),
                bm_s2.verts.new((xc - dx, p_tip_rear[1],   p_tip_rear[2])),
                bm_s2.verts.new((xc - dx, p_tip_front[1],  p_tip_front[2])),
                bm_s2.verts.new((xc + dx, p_base_front[1], p_base_front[2])),
                bm_s2.verts.new((xc + dx, p_base_rear[1],  p_base_rear[2])),
                bm_s2.verts.new((xc + dx, p_tip_rear[1],   p_tip_rear[2])),
                bm_s2.verts.new((xc + dx, p_tip_front[1],  p_tip_front[2])),
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

            # S4 Rudder
            bm_s4 = bmesh.new()
            p_rud_base_rear = (xc, p_base_rear[1] - 0.0407, z_pos)
            p_rud_tip_rear  = (xc, p_tip_rear[1] - 0.0407,  z_pos + FIN_HEIGHT)

            v_rud = [
                bm_s4.verts.new((xc - dx, p_base_rear[1] - 0.001, p_base_rear[2])),
                bm_s4.verts.new((xc - dx, p_rud_base_rear[1],    p_rud_base_rear[2])),
                bm_s4.verts.new((xc - dx, p_rud_tip_rear[1],     p_rud_tip_rear[2])),
                bm_s4.verts.new((xc - dx, p_tip_rear[1] - 0.001,  p_tip_rear[2])),
                bm_s4.verts.new((xc + dx, p_base_rear[1] - 0.001, p_base_rear[2])),
                bm_s4.verts.new((xc + dx, p_rud_base_rear[1],    p_rud_base_rear[2])),
                bm_s4.verts.new((xc + dx, p_rud_tip_rear[1],     p_rud_tip_rear[2])),
                bm_s4.verts.new((xc + dx, p_tip_rear[1] - 0.001,  p_tip_rear[2])),
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
    # 7. PROPULSION (Motor mounted on M1 at rear, centered at Z=0.0535m)
    # Pusher propeller spins cleanly between the tail booms!
    # =============================================================
    def build_propulsion():
        y_mount = -0.4371
        z_motor = 0.0535  # Exact center of rear firewall (34.2mm to 72.9mm)

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

        y_prop = y_mount - 0.034
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

        # 8x6 APC Pusher Propeller
        bm = bmesh.new()
        r_prop = 0.1016 # 8 inch diameter = 203.2mm -> radius 101.6mm
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
    # 8. TRICYCLE LANDING GEAR (Exact to Julius Perdana Plan)
    # Nose gear at Y=+0.060m, Main gear at Y=-0.130m
    # Ground plane at Z = -0.090m
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

        # Nose Gear at Y=+0.060m
        y_nose = +0.060
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

        # Main Gear at Y=-0.130m (under wing CG datum)
        y_main = -0.130
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
    # 9. STUDIO LIGHTING, FLOOR & CAMERAS
    # Soft ambient studio illumination for rich PBR presentation
    # =============================================================
    col_studio = create_collection("Studio_Setup")

    # Dark studio floor
    bpy.ops.mesh.primitive_plane_add(
        size=14.0,
        location=(0, 0, -0.090)
    )
    floor = bpy.context.active_object
    floor.name = "Studio_Ground_Floor"
    mat_floor = get_or_create_material("Mat_Studio_Floor", (0.07, 0.07, 0.08, 1.0), roughness=0.4, metallic=0.05)
    floor.data.materials.append(mat_floor)
    link_obj(floor, col_studio)
    bpy.context.collection.objects.unlink(floor)

    # Lighting: Balanced Studio Lighting with direct Side Key
    # Set world ambient light so shadows are never pitch black
    world = scene.world or bpy.data.worlds.new("Studio_World")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.75, 0.77, 0.80, 1.0)
        bg_node.inputs["Strength"].default_value = 0.65

    def add_light(name, ltype, energy, loc, color=(1.0, 1.0, 1.0)):
        ldata = bpy.data.lights.new(name=name, type=ltype)
        ldata.energy = energy
        ldata.color = color
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        lobj.location = loc
        link_obj(lobj, col_studio)
        return lobj

    # Key light (Front-Right high)
    add_light("Light_Key_Warm", 'POINT', 450.0, (1.80, 1.60, 1.40), (1.0, 0.98, 0.95))
    # Fill light (Front-Left mid)
    add_light("Light_Fill_Cool", 'POINT', 300.0, (-1.80, 1.20, 1.00), (0.95, 0.97, 1.0))
    # Rim light (Back high)
    add_light("Light_Rim_Back", 'POINT', 350.0, (-0.20, -1.90, 1.20), (1.0, 1.0, 1.0))
    # Under-wing bounce light (Soft upward fill to eliminate under-wing pitch-black shadow)
    add_light("Light_Under_Bounce", 'POINT', 120.0, (0.00, -0.05, -0.04), (1.0, 1.0, 1.0))
    # Direct Ortho Side Key lights (Level with fuselage at Z=0.06m to illuminate side wall perfectly)
    add_light("Light_Side_Profile_Main", 'POINT', 350.0, (2.10, -0.10, 0.06), (1.0, 1.0, 1.0))
    add_light("Light_Side_Profile_Nose", 'POINT', 200.0, (2.10, +0.15, 0.06), (1.0, 1.0, 1.0))
    add_light("Light_Side_Profile_Tail", 'POINT', 200.0, (2.10, -0.35, 0.06), (1.0, 1.0, 1.0))

    # Camera 1: Perspective User View (matching reference screenshot)
    cam_persp_data = bpy.data.cameras.new("Camera_User_View")
    cam_persp_data.lens = 52.0
    cam_persp_obj = bpy.data.objects.new("Camera_User_View", cam_persp_data)
    cam_persp_obj.location = (1.20, 0.95, 0.46)
    direction = Vector((0.0, -0.10, 0.06)) - cam_persp_obj.location
    cam_persp_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    link_obj(cam_persp_obj, col_studio)

    # Camera 2: Orthographic Side Profile (Engineering 2D Verification)
    cam_ortho_data = bpy.data.cameras.new("Camera_Side_Ortho")
    cam_ortho_data.type = 'ORTHO'
    cam_ortho_data.ortho_scale = 1.35
    cam_ortho_obj = bpy.data.objects.new("Camera_Side_Ortho", cam_ortho_data)
    cam_ortho_obj.location = (2.20, -0.15, 0.08)
    cam_ortho_obj.rotation_euler = (math.radians(90), 0, math.radians(90))
    link_obj(cam_ortho_obj, col_studio)

    # Camera 3: Front-Quarter Hero View
    cam_hero_data = bpy.data.cameras.new("Camera_Hero_Angle")
    cam_hero_data.lens = 45.0
    cam_hero_obj = bpy.data.objects.new("Camera_Hero_Angle", cam_hero_data)
    cam_hero_obj.location = (0.95, 1.30, 0.55)
    direction_hero = Vector((0.0, -0.05, 0.05)) - cam_hero_obj.location
    cam_hero_obj.rotation_euler = direction_hero.to_track_quat('-Z', 'Y').to_euler()
    link_obj(cam_hero_obj, col_studio)

    # Save Master Blend File
    out_blend = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_1500mm_CutAccurate.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Saved Master Blend File: {out_blend}")

    # Export Universal OBJ & GLB
    out_obj = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_1500mm.obj"
    bpy.ops.wm.obj_export(filepath=out_obj)
    print(f"Exported OBJ: {out_obj}")

    out_glb = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_1500mm.glb"
    for o in bpy.data.objects:
        o.select_set(False)
    for col in [col_fuse, col_wing, col_tail, col_prop, col_gear]:
        for o in col.objects:
            o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB', use_selection=True)
    print(f"Exported GLB: {out_glb}")

    # Render Renders
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'PNG'

    # Render 1: Side Ortho
    scene.camera = cam_ortho_obj
    img_side = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_3D_Side_Profile.png"
    scene.render.filepath = img_side
    bpy.ops.render.render(write_still=True)
    print(f"Rendered Side Profile to: {img_side}")

    # Render 2: User Perspective
    scene.camera = cam_persp_obj
    img_preview = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_3D_Preview.png"
    scene.render.filepath = img_preview
    bpy.ops.render.render(write_still=True)
    print(f"Rendered Perspective Preview to: {img_preview}")

    # Render 3: Hero View
    scene.camera = cam_hero_obj
    img_hero = r"C:\Users\RYZEN\Desktop\Project documentatin\Garuda Vedang presentation material\Garuda_Vedang_Airframe_Fixed_Persp.png"
    scene.render.filepath = img_hero
    bpy.ops.render.render(write_still=True)
    print(f"Rendered Hero View to: {img_hero}")

    print("=====================================================")
    print("AIRFRAME BUILD & FIX COMPLETE!")
    print("=====================================================")

if __name__ == "__main__":
    build_accurate_garuda_vedang()
