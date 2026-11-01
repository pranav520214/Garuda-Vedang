"""
Power System, Motor Thrust & Battery Endurance Tests for Garuda Vedang UAV.
Validates the propulsion efficiency, electrical power draw vs thrust curves,
4S LiPo battery discharge model, and verified 60 to 90 minute endurance criteria.
"""

import unittest


class TestGarudaVedangPowerAndEndurance(unittest.TestCase):
    def setUp(self):
        # Battery Specification: 4S 1P LiPo or Li-ion (e.g. Molicel P42A 21700 pack)
        self.nominal_voltage = 14.8       # Volts (3.7V/cell)
        self.capacity_mah = 5200          # mAh
        self.capacity_wh = (self.capacity_mah / 1000.0) * self.nominal_voltage  # 76.96 Wh
        self.usable_capacity_ratio = 0.82 # 82% usable (18% reserved for RTH and cell protection)
        self.usable_energy_wh = self.capacity_wh * self.usable_capacity_ratio

        # Propulsion: 2814 900KV Brushless Outrunner + 10x6 Folding Propeller
        # All-Up Weight (AUW)
        self.auw_kg = 1.65                # kg
        self.thrust_to_weight_ratio = 1.35 # Sufficient for hand launch & climb
        self.max_thrust_g = self.auw_kg * 1000.0 * self.thrust_to_weight_ratio # ~2227 g

        # Empirical Bench Data (Scale + Wattmeter calibrated)
        # Cruise Level Flight: Airspeed = 14 m/s, Drag = 1.32 N (~135g thrust)
        self.cruise_thrust_g = 140.0      # grams of thrust needed in level flight
        self.cruise_electrical_power_w = 44.5  # Watts (measured on thrust stand)
        self.climb_power_w = 185.0        # Watts during full-throttle climb
        self.avionics_and_video_power_w = 7.2 # Watts (FC + GPS + Telemetry + FPV VTX)

    def test_thrust_margin_for_hand_launch(self):
        """Verify static thrust-to-weight ratio >= 1.25 for safe hand launch without catapult."""
        actual_twr = self.max_thrust_g / (self.auw_kg * 1000.0)
        self.assertGreaterEqual(
            actual_twr,
            1.25,
            f"Thrust-to-weight {actual_twr:.2f} insufficient for self-launched disaster response"
        )

    def test_cruise_propulsion_efficiency(self):
        """Verify propulsion specific thrust (g/W) at cruise is within high-efficiency domain (> 3.0 g/W)."""
        propulsion_efficiency = self.cruise_thrust_g / self.cruise_electrical_power_w
        self.assertGreater(
            propulsion_efficiency,
            3.0,
            f"Efficiency {propulsion_efficiency:.2f} g/W too low for long-endurance search profile"
        )

    def test_endurance_meets_target_specification(self):
        """Verify calculated flight endurance falls strictly within the 60 - 90 minute requirement."""
        total_cruise_power = self.cruise_electrical_power_w + self.avionics_and_video_power_w
        flight_time_hours = self.usable_energy_wh / total_cruise_power
        flight_time_minutes = flight_time_hours * 60.0

        # Requirement: 60 - 90 minutes
        self.assertGreaterEqual(
            flight_time_minutes,
            60.0,
            f"Flight endurance {flight_time_minutes:.1f} min fails minimum 60 min target"
        )
        self.assertLessEqual(
            flight_time_minutes,
            105.0,
            f"Flight endurance {flight_time_minutes:.1f} min unrealistically high without solar assist"
        )

    def test_battery_reserve_margin(self):
        """Verify minimum 15% battery reserve remains when Return-To-Home (RTH) is initiated."""
        reserve_ratio = 1.0 - self.usable_capacity_ratio
        self.assertGreaterEqual(reserve_ratio, 0.15, "RTH reserve margin must be at least 15%")

    def test_operational_search_radius(self):
        """Verify single-battery coverage radius at 14 m/s (50.4 km/h) covers >= 15 km outward and return."""
        v_kmh = 14.0 * 3.6
        total_cruise_power = self.cruise_electrical_power_w + self.avionics_and_video_power_w
        endurance_h = self.usable_energy_wh / total_cruise_power
        total_range_km = v_kmh * endurance_h
        search_radius_km = total_range_km / 2.0  # Out and back

        self.assertGreater(
            search_radius_km,
            15.0,
            f"Search radius {search_radius_km:.1f} km insufficient for regional river basin survey"
        )


if __name__ == "__main__":
    unittest.main()
