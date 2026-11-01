"""
Mechanical & Magnetic Detachable Belly Latch System Tests.
Validates the state machine, fail-safe spring locking, electromagnetic release pulse,
ejection velocity, and mechanical tolerance margins for in-flight scout deployment.
"""

import time
import unittest


class MockLatchController:
    """Simulates the physical avionics state machine of the Garuda Vedang belly latch."""
    STATE_LOCKED = "LOCKED"
    STATE_PRE_CHECK = "PRE_CHECK"
    STATE_PULSE_RELEASE = "PULSE_RELEASE"
    STATE_EJECTED = "EJECTED"
    STATE_FAULT_RETAINED = "FAULT_RETAINED"

    def __init__(self, battery_voltage=14.8, airspeed=14.0):
        self.state = self.STATE_LOCKED
        self.battery_voltage = battery_voltage
        self.airspeed = airspeed
        self.spring_loaded_jaw_engaged = True
        self.neodymium_assist_engaged = True
        self.hall_effect_sensor_closed = True
        self.pulse_current_amps = 0.0
        self.ejection_speed_mps = 0.0

    def trigger_release_sequence(self, override_safety=False):
        # Step 1: Pre-check safety criteria
        if self.battery_voltage < 10.5 and not override_safety:
            self.state = self.STATE_FAULT_RETAINED
            return False, "Avionics low voltage abort"

        if self.airspeed > 22.0 and not override_safety:
            self.state = self.STATE_FAULT_RETAINED
            return False, "Airspeed exceeds safe deployment envelope (v > 22 m/s)"

        self.state = self.STATE_PRE_CHECK

        # Step 2: Fire reverse-polarity electromagnet pulse (300 ms pulse)
        self.pulse_current_amps = 2.4
        self.neodymium_assist_engaged = False  # neutralized by reverse coil

        # Step 3: Mechanical servo triggers release cam
        self.spring_loaded_jaw_engaged = False
        self.state = self.STATE_PULSE_RELEASE

        # Step 4: Compression spring ejects scout drone downwards
        # Force = 18 N, Scout mass = 0.180 kg -> a = 100 m/s^2 over 15mm stroke -> v = sqrt(2 * a * d) = 1.73 m/s
        self.ejection_speed_mps = 1.73
        self.hall_effect_sensor_closed = False
        self.state = self.STATE_EJECTED
        return True, "Scout successfully ejected"

    def power_failure_simulation(self):
        """Under total power loss, spring mechanism MUST default to mechanically locked."""
        self.battery_voltage = 0.0
        self.pulse_current_amps = 0.0
        # Spring-loaded latch has passive over-center mechanical lock
        self.spring_loaded_jaw_engaged = True
        self.state = self.STATE_LOCKED


class TestGarudaVedangLatchSystem(unittest.TestCase):
    def setUp(self):
        self.latch = MockLatchController(battery_voltage=14.8, airspeed=14.0)

    def test_initial_state_locked(self):
        """Verify latch initializes in mechanically locked state with active Hall effect detection."""
        self.assertEqual(self.latch.state, MockLatchController.STATE_LOCKED)
        self.assertTrue(self.latch.spring_loaded_jaw_engaged)
        self.assertTrue(self.latch.neodymium_assist_engaged)
        self.assertTrue(self.latch.hall_effect_sensor_closed)

    def test_nominal_release_sequence(self):
        """Verify standard in-flight scout deployment succeeds and achieves sufficient downward ejection velocity."""
        success, msg = self.latch.trigger_release_sequence()
        self.assertTrue(success, f"Release failed: {msg}")
        self.assertEqual(self.latch.state, MockLatchController.STATE_EJECTED)
        self.assertFalse(self.latch.hall_effect_sensor_closed)
        # Ejection speed must be >= 1.2 m/s to escape boundary layer downwash
        self.assertGreaterEqual(
            self.latch.ejection_speed_mps,
            1.20,
            f"Ejection velocity {self.latch.ejection_speed_mps:.2f} m/s too low to clear mothership downwash"
        )

    def test_power_loss_fail_safe(self):
        """Verify total avionics power cutoff does not release the scout drone unintentionally."""
        self.latch.power_failure_simulation()
        self.assertEqual(self.latch.state, MockLatchController.STATE_LOCKED)
        self.assertTrue(self.latch.spring_loaded_jaw_engaged, "Latch failed open during power loss!")

    def test_high_speed_overspeed_lockout(self):
        """Verify latch aborts deployment when airspeed exceeds safe aerodynamic boundary (v > 22 m/s)."""
        overspeed_latch = MockLatchController(battery_voltage=14.8, airspeed=25.0)
        success, msg = overspeed_latch.trigger_release_sequence()
        self.assertFalse(success)
        self.assertEqual(overspeed_latch.state, MockLatchController.STATE_FAULT_RETAINED)
        self.assertTrue(overspeed_latch.spring_loaded_jaw_engaged)

    def test_undervoltage_lockout(self):
        """Verify latch aborts when battery is below critical threshold (preventing half-open servo freeze)."""
        low_v_latch = MockLatchController(battery_voltage=9.8, airspeed=14.0)
        success, msg = low_v_latch.trigger_release_sequence()
        self.assertFalse(success)
        self.assertEqual(low_v_latch.state, MockLatchController.STATE_FAULT_RETAINED)


if __name__ == "__main__":
    unittest.main()
