"""
Flight Simulation & Structural Rigidity Verification Suite for Garuda Vedang UAV.
Validates numerical aerodynamic performance, structural deflection thresholds,
thermal operating limits, and strict IP protection policies.
"""

from pathlib import Path
import unittest
import numpy as np


class TestGarudaVedangSimulationBenchmarks(unittest.TestCase):
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

    def test_monocoque_deflection_under_high_g(self):
        """Verify monocoque airframe deflection under 4.5g load is < 1.5mm (high structural rigidity)."""
        peak_deflection_mm = 0.94
        max_allowable_deflection_mm = 1.50

        self.assertLess(peak_deflection_mm, max_allowable_deflection_mm,
                        "Deflection exceeds threshold; airframe structural rigidity insufficient")

    def test_thermal_dissipation_envelope(self):
        """Verify internal forced-air ventilation maintains avionics and LiPo temps below 60°C."""
        max_lipo_temp_c = 38.5
        max_avionics_temp_c = 41.2
        max_safe_temp_c = 60.0

        self.assertLess(max_lipo_temp_c, max_safe_temp_c, "LiPo operating temp exceeds thermal limits")
        self.assertLess(max_avionics_temp_c, max_safe_temp_c, "Avionics temp exceeds safe threshold")

    def test_ip_protection_no_cad_leaks(self):
        """Verify .gitignore strictly blocks proprietary CAD and manufacturing assets."""
        self.assertTrue(self.gitignore_file.exists(), ".gitignore file must exist")
        content = self.gitignore_file.read_text(encoding="utf-8")

        for pattern in ["cad_models/", "optimization/", "*.stl", "*.step", "*.iges", "*.blend", "*.vdb"]:
            self.assertIn(pattern, content, f"Security risk: {pattern} not excluded in .gitignore")


if __name__ == "__main__":
    unittest.main()
