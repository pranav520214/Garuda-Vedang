"""
Aerodynamic Polars & CFD Performance Tests for Garuda Vedang 1500mm Fixed-Wing UAV.
Validates lift coefficients, drag polars, stall speeds, glide ratio (L/D),
and longitudinal pitch stability margin.
"""

import math
import unittest


class TestGarudaVedangAerodynamics(unittest.TestCase):
    def setUp(self):
        # UAV Airframe Physical Parameters
        self.wingspan = 1.50          # meters
        self.root_chord = 0.21        # meters
        self.tip_chord = 0.14         # meters
        self.mac = (self.root_chord + self.tip_chord) / 2.0  # Mean Aerodynamic Chord (m)
        self.wing_area = self.wingspan * self.mac           # Wing planform area (m^2)
        self.aspect_ratio = (self.wingspan ** 2) / self.wing_area

        # Mass & Atmosphere
        self.all_up_weight_kg = 1.65  # AUW with payload (kg)
        self.rho = 1.225              # Sea-level standard air density (kg/m^3)
        self.g = 9.80665              # m/s^2
        self.weight_n = self.all_up_weight_kg * self.g

        # Airfoil Characteristics (Modified Eppler / Clark-Y variant with reflex)
        self.cl_0 = 0.28              # Zero-angle-of-attack lift coefficient
        self.cl_alpha = 0.098         # per degree (approx 5.6 per radian)
        self.cl_max = 1.25            # Maximum clean lift coefficient
        self.stall_angle_deg = 13.5   # degrees
        self.cd_0 = 0.024             # Parasitic zero-lift drag coefficient
        self.oswald_e = 0.82          # Oswald planform efficiency factor

    def test_wing_geometry(self):
        """Validate wingspan, aspect ratio, and MAC calculation."""
        self.assertAlmostEqual(self.wingspan, 1.50, places=2)
        self.assertGreater(self.aspect_ratio, 8.0, "Aspect ratio must be > 8.0 for efficient glide")
        self.assertLess(self.aspect_ratio, 10.0, "Aspect ratio capped at 10.0 for structural rigidity")

    def test_stall_speed(self):
        """Verify stall speed is below 9.0 m/s for safe belly recovery and hand launch."""
        # V_stall = sqrt((2 * W) / (rho * S * CL_max))
        v_stall = math.sqrt((2.0 * self.weight_n) / (self.rho * self.wing_area * self.cl_max))
        self.assertLess(v_stall, 9.0, f"Stall speed {v_stall:.2f} m/s must be < 9.0 m/s")
        self.assertGreater(v_stall, 6.0, f"Stall speed {v_stall:.2f} m/s realistically > 6.0 m/s")

    def test_cruise_speed_and_reynolds_number(self):
        """Verify cruise velocity (13-16 m/s) and typical operating Reynolds number."""
        v_cruise = 14.0  # m/s cruise
        nu = 1.5e-5      # Kinematic viscosity of air (m^2/s)
        reynolds = (v_cruise * self.mac) / nu

        self.assertGreater(reynolds, 150000, "Reynolds number must exceed 150k to avoid laminar separation bubbles")
        self.assertLess(reynolds, 300000, "Reynolds number realistic for sub-scale UAV")

    def test_glide_ratio_ld_max(self):
        """Verify maximum lift-to-drag ratio (L/D)_max exceeds 12.0 for extended search & rescue gliding."""
        # Induced drag k = 1 / (pi * e * AR)
        k = 1.0 / (math.pi * self.oswald_e * self.aspect_ratio)
        # Optimal CL for (L/D)_max is sqrt(CD0 / k)
        cl_opt = math.sqrt(self.cd_0 / k)
        cd_opt = 2.0 * self.cd_0
        ld_max = cl_opt / cd_opt

        self.assertGreater(ld_max, 12.0, f"Max L/D {ld_max:.2f} must exceed 12.0 for efficient endurance")
        self.assertLess(ld_max, 20.0, f"Max L/D {ld_max:.2f} should be realistic for twin-boom UAV with belly scout")

    def test_level_cruise_lift_equilibrium(self):
        """Verify required CL at 14 m/s cruise is within the linear low-drag polar bucket."""
        v_cruise = 14.0
        q = 0.5 * self.rho * (v_cruise ** 2)
        cl_req = self.weight_n / (q * self.wing_area)

        # Operating CL should be between 0.35 and 0.65
        self.assertGreater(cl_req, 0.30, f"Required CL {cl_req:.3f} too low (unrealistic)")
        self.assertLess(cl_req, 0.70, f"Required CL {cl_req:.3f} dangerously close to stall")

    def test_longitudinal_static_stability_margin(self):
        """Verify static margin is positive (between 8% and 15% MAC) for hands-off flight stability."""
        # Neutral point at ~0.42 MAC due to twin-boom horizontal stabilizer
        x_np_fraction = 0.42
        # Center of Gravity placed at 0.30 MAC
        x_cg_fraction = 0.30
        static_margin = x_np_fraction - x_cg_fraction

        self.assertGreater(static_margin, 0.05, "Static margin must be > 5% MAC for stability")
        self.assertLess(static_margin, 0.18, "Static margin must not exceed 18% MAC to avoid excessive elevator trim drag")


if __name__ == "__main__":
    unittest.main()
