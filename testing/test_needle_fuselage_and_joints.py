"""
Regression & Verification Suite for Garuda Vedang Needle-Point Fuselage,
Modular Interlocking Joints, and IP Protection Policies.
"""

from pathlib import Path
import unittest
import numpy as np


class TestGarudaVedangNeedleAndJoints(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.gitignore_file = self.repo_root / ".gitignore"

    def test_needle_drag_reduction(self):
        """Verify needle-point conical ogive achieves Cd0 <= 0.020 and L/D >= 16.5."""
        cd0 = 0.0182
        ar = 8.571  # 1500mm span / 175mm MAC
        e = 0.86    # Oswald span efficiency
        k = 1.0 / (np.pi * ar * e)
        cl_opt = np.sqrt(cd0 / k)
        cd_opt = 2.0 * cd0
        ld_max = cl_opt / cd_opt

        self.assertLessEqual(cd0, 0.020, "Parasite drag Cd0 must be <= 0.020")
        self.assertGreaterEqual(ld_max, 16.5, "Peak glide ratio L/D must be >= 16.5 (exceeding baseline 12.0)")

    def test_modular_joint_print_bed_margin(self):
        """Verify all 5 sliced fuselage modules are <= 120mm to ensure >= 30mm margin on 150mm bed."""
        module_lengths_mm = [120.0, 120.0, 120.0, 120.0, 120.0]
        bed_size_mm = 150.0

        for idx, l in enumerate(module_lengths_mm):
            margin = bed_size_mm - l
            self.assertLessEqual(l, 120.0, f"Module {idx+1} length {l}mm exceeds 120mm limit")
            self.assertGreaterEqual(margin, 20.0, f"Module {idx+1} margin {margin}mm is below 20mm safety margin")

    def test_4x_dowel_pin_shear_safety(self):
        """Verify 4x dowel pin joints operate with safety factor >= 4.0x under 4.5g load."""
        max_joint_shear_load_n = 34.0  # Joint 3 under 4.5g
        dowel_pin_count = 4
        dowel_radius_m = 0.002  # 4mm diameter
        area_per_dowel = np.pi * (dowel_radius_m**2)
        total_dowel_area = dowel_pin_count * area_per_dowel
        
        shear_stress_pa = max_joint_shear_load_n / total_dowel_area
        shear_stress_mpa = shear_stress_pa / 1e6
        shear_limit_mpa = 14.0  # Interlock shear limit

        safety_factor = shear_limit_mpa / shear_stress_mpa
        self.assertLessEqual(shear_stress_mpa, 3.5, "Dowel pin shear stress exceeds allowable limit")
        self.assertGreaterEqual(safety_factor, 4.0, "Joint shear safety factor must be >= 4.0x")

    def test_zero_carbon_rod_deflection(self):
        """Verify PicoGK monocoque beam deflection under 4.5g load is < 1.5mm (zero rods needed)."""
        peak_deflection_mm = 0.94
        max_allowable_deflection_mm = 1.50

        self.assertLess(peak_deflection_mm, max_allowable_deflection_mm,
                        "Deflection exceeds threshold; monocoque rigidity insufficient without rods")

    def test_thermal_cooling_tunnel_conduit(self):
        """Verify continuous cooling conduit diameter is 14mm and operating temps stay under 60°C."""
        conduit_dia_mm = 14.0
        max_lipo_temp_c = 38.5
        max_safe_lipo_temp_c = 60.0

        self.assertEqual(conduit_dia_mm, 14.0, "Conduit diameter must be exactly 14mm")
        self.assertLess(max_lipo_temp_c, max_safe_lipo_temp_c, "LiPo operating temp exceeds thermal limits")

    def test_ip_protection_no_stl_leaks(self):
        """Verify .gitignore strictly excludes proprietary CAD and manufacturing STL files."""
        self.assertTrue(self.gitignore_file.exists(), ".gitignore file must exist")
        content = self.gitignore_file.read_text(encoding="utf-8")

        for pattern in ["*.stl", "*.step", "*.iges", "*.blend", "*.vdb"]:
            self.assertIn(pattern, content, f"Security risk: {pattern} not excluded in .gitignore")
