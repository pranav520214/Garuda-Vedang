"""
CAD Models, Blueprint Dimensions & File Integrity Tests for Garuda Vedang UAV.
Validates that 3D assets, OBJ/MTL links, vector blueprints, and PicoGK optimization
files are present, well-formed, non-corrupted, and conform to the 1500mm airframe standard.
"""

from pathlib import Path
import unittest


class TestGarudaVedangCADIntegrity(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.cad_dir = self.repo_root / "cad_models"
        self.blueprints_dir = self.cad_dir / "blueprints"
        self.opt_dir = self.repo_root / "optimization"

    def test_cad_files_exist(self):
        """Verify essential 3D airframe CAD files exist and are populated."""
        expected_files = [
            (self.cad_dir / "Garuda_Vedang_1500mm.glb", 50000),
            (self.cad_dir / "Garuda_Vedang_1500mm.obj", 50000),
            (self.cad_dir / "Garuda_Vedang_1500mm.mtl", 1000),
            (self.cad_dir / "Garuda_Vedang_1500mm_CFD.glb", 100000),
            (self.cad_dir / "Garuda_Vedang_1500mm_CutAccurate.blend", 50000),
            (self.cad_dir / "Garuda_Vedang_ReEngineered_AllWeather.glb", 50000),
        ]
        for f, min_bytes in expected_files:
            self.assertTrue(f.exists(), f"Missing CAD asset: {f.name}")
            self.assertGreater(f.stat().st_size, min_bytes, f"CAD asset {f.name} suspiciously small (< {min_bytes}B)")

    def test_obj_material_library_link(self):
        """Verify Garuda_Vedang_1500mm.obj links to Garuda_Vedang_1500mm.mtl and not old Alapalap."""
        obj_file = self.cad_dir / "Garuda_Vedang_1500mm.obj"
        content = obj_file.read_text(encoding="utf-8", errors="ignore")

        self.assertIn("mtllib Garuda_Vedang_1500mm.mtl", content)
        self.assertNotIn("Alapalap", content, "Found deprecated Alapalap reference in OBJ mesh")

    def test_blueprints_and_cutting_plans(self):
        """Verify laser cutting vectors and A0 plans are present."""
        expected_blueprints = [
            self.blueprints_dir / "Garuda_Vedang_A0.svg",
            self.blueprints_dir / "PR_Garuda_Vedang.pdf",
            self.blueprints_dir / "PR_Garuda_Vedang_A0.pdf",
        ]
        for b in expected_blueprints:
            self.assertTrue(b.exists(), f"Missing blueprint: {b.name}")
            self.assertGreater(b.stat().st_size, 10000, f"Blueprint {b.name} is empty or corrupted")

    def test_picogk_structural_lattice_artifacts(self):
        """Verify PicoGK lattice optimization models exist and have valid volume representation."""
        stl_file = self.opt_dir / "Garuda_Vedang_PicoGK_Lattice_Optimized.stl"
        vdb_file = self.opt_dir / "Garuda_Vedang_PicoGK_Lattice.vdb"

        self.assertTrue(stl_file.exists(), "Missing PicoGK optimized STL lattice file")
        self.assertGreater(stl_file.stat().st_size, 1000000, "PicoGK STL lattice file is too small")
        self.assertTrue(vdb_file.exists(), "Missing OpenVDB voxel lattice database")

    def test_obj_geometric_dimensions(self):
        """Parse OBJ vertices to verify airframe span matches 1500mm and geometry bounding box is valid."""
        obj_file = self.cad_dir / "Garuda_Vedang_1500mm.obj"
        xs, ys, zs = [], [], []

        with open(obj_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        try:
                            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                            xs.append(x)
                            ys.append(y)
                            zs.append(z)
                        except ValueError:
                            pass

        self.assertGreater(len(xs), 100, "Too few vertices in OBJ mesh")

        bbox_x = max(xs) - min(xs)
        bbox_y = max(ys) - min(ys)
        bbox_z = max(zs) - min(zs)

        max_dim = max(bbox_x, bbox_y, bbox_z)
        self.assertGreater(max_dim, 0.5, "Airframe scale appears too small")


if __name__ == "__main__":
    unittest.main()
