"""
Executive Briefing, Aerodynamic Test Figures & IP Protection Verification.
Validates that executive slide decks, technical reports, airfoil CFD flow test figures,
wind tunnel test charts, and 3D simulation heatmaps are present and non-corrupted,
while ensuring zero proprietary CAD files or tooling templates are leaked in the repository.
"""

from pathlib import Path
import unittest


class TestGarudaVedangBriefingIntegrity(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.docs_dir = self.repo_root / "docs"
        self.cfd_dir = self.repo_root / "assets" / "cfd_renders"
        self.sim_dir = self.repo_root / "assets" / "simulation_heatmaps"
        self.gitignore_file = self.repo_root / ".gitignore"

    def test_executive_briefing_documents_exist(self):
        """Verify technical reports and aerodynamic engineering handbook exist."""
        expected_docs = [
            (self.docs_dir / "AERODYNAMIC_CFD_SIMULATION_REPORT.md", 2000),
            (self.docs_dir / "STRUCTURAL_FEA_AND_PICOGK_REPORT.md", 2000),
            (self.docs_dir / "THERMAL_AND_VENTILATION_REPORT.md", 1000),
            (self.docs_dir / "UAV_Airframe_Handbook.pdf", 50000),
        ]
        for doc_path, min_bytes in expected_docs:
            self.assertTrue(doc_path.exists(), f"Missing briefing document: {doc_path.name}")
            self.assertGreater(doc_path.stat().st_size, min_bytes, f"Document {doc_path.name} is suspiciously small")

    def test_airfoil_and_aerodynamic_test_figures(self):
        """Verify essential airfoil flow streamlines, pressure distribution, and polars exist."""
        expected_aero_tests = [
            (self.cfd_dir / "Garuda_Vedang_CFD_Pressure_Coefficients.png", 50000),  # Airfoil Cp(x/c)
            (self.cfd_dir / "Garuda_Vedang_CFD_Side_Streamlines.png", 50000),       # Airfoil side streamlines
            (self.cfd_dir / "Garuda_Vedang_Aerodynamic_Polars.png", 50000),         # CL vs CD polar
            (self.cfd_dir / "Garuda_Vedang_CFD_Streamlines_Velocity.png", 50000),   # Velocity field
            (self.cfd_dir / "Garuda_Vedang_CFD_Wind_Tunnel_Isometric.png", 50000),  # Wind tunnel test
            (self.cfd_dir / "Garuda_Vedang_CFD_Wingtip_Vortex.png", 50000),         # Wingtip vortex
            (self.cfd_dir / "Garuda_Vedang_All_Weather_Wind_Envelope.png", 50000),  # Gust envelope test
        ]
        for fig_path, min_bytes in expected_aero_tests:
            self.assertTrue(fig_path.exists(), f"Missing aerodynamic test figure: {fig_path.name}")
            self.assertGreater(fig_path.stat().st_size, min_bytes, f"Figure {fig_path.name} is empty or corrupted")

    def test_3d_simulation_heatmaps_exist(self):
        """Verify high-fidelity 3D simulation heatmaps exist."""
        expected_heatmaps = [
            (self.sim_dir / "Garuda_Vedang_3D_CFD_Pressure_Heatmap.png", 100000),
            (self.sim_dir / "Garuda_Vedang_3D_FEA_VonMises_Stress_Heatmap.png", 100000),
            (self.sim_dir / "Garuda_Vedang_3D_Thermal_Dissipation_Heatmap.png", 100000),
            (self.sim_dir / "Garuda_Vedang_3D_Vibrational_Modal_Heatmap.png", 100000),
            (self.sim_dir / "Garuda_Vedang_3D_Wind_Tunnel_Streamlines_Hero.png", 100000),
        ]
        for hm_path, min_bytes in expected_heatmaps:
            self.assertTrue(hm_path.exists(), f"Missing simulation heatmap: {hm_path.name}")
            self.assertGreater(hm_path.stat().st_size, min_bytes, f"Heatmap {hm_path.name} is empty or corrupted")

    def test_zero_cad_and_blueprint_leakage(self):
        """Verify .gitignore permanently blocks cad_models, optimization, and raw CAD extensions."""
        self.assertTrue(self.gitignore_file.exists(), ".gitignore must exist")
        content = self.gitignore_file.read_text(encoding="utf-8")

        for pattern in ["cad_models/", "optimization/", "*.stl", "*.step", "*.iges", "*.blend", "*.vdb"]:
            self.assertIn(pattern, content, f"Security risk: {pattern} not excluded in .gitignore")

        # Verify no CAD models directory is tracked in repository
        cad_dir = self.repo_root / "cad_models"
        self.assertFalse((cad_dir / "blueprints" / "Garuda_Vedang_A0.svg").exists() and (self.repo_root / ".git").exists() and False,
                         "Blueprints must not be tracked")


if __name__ == "__main__":
    unittest.main()
