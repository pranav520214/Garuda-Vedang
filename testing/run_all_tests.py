#!/usr/bin/env python3
"""
Unified Test Runner for Garuda Vedang Autonomous Aerial Systems.
Executes all regression suites (aerodynamics, wind envelope, latch mechanics, power, CAD integrity)
and prints a formatted engineering verification report.
"""

import sys
import time
import unittest
from pathlib import Path

# Add testing directory and repo root to sys.path
TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from test_aerodynamics import TestGarudaVedangAerodynamics
from test_wind_envelope import TestGarudaVedangWindEnvelope
from test_latch_system import TestGarudaVedangLatchSystem
from test_power_endurance import TestGarudaVedangPowerAndEndurance
from test_cad_integrity import TestGarudaVedangCADIntegrity
from test_needle_fuselage_and_joints import TestGarudaVedangNeedleAndJoints


def run_test_suite():
    print("=" * 76)
    print(" GARUDA VEDANG AUTONOMOUS AERIAL SYSTEMS // ENGINEERING VERIFICATION")
    print(" Two-Tier Twin-Boom Mothership & Integrated Detachable Scout Drone")
    print("=" * 76)
    print(f" Repository Base: {REPO_ROOT}")
    print(f" Timestamp:       {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 76)

    suites = [
        ("Aerodynamic Polars & CFD Performance", TestGarudaVedangAerodynamics),
        ("All-Weather Wind Envelope & Gust Margin", TestGarudaVedangWindEnvelope),
        ("Detachable Belly Latch & Fail-Safe Mechanics", TestGarudaVedangLatchSystem),
        ("Propulsion Power Draw & 60-90m Endurance", TestGarudaVedangPowerAndEndurance),
        ("CAD Mesh, Blueprints & Asset Integrity", TestGarudaVedangCADIntegrity),
        ("Needle Ogive, Modular Joints & IP Protection", TestGarudaVedangNeedleAndJoints),
    ]

    total_passed = 0
    total_failed = 0
    total_errors = 0
    start_total_time = time.time()

    for title, test_class in suites:
        print(f"\n[SUITE] {title}")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        start_t = time.time()
        result = runner.run(suite)
        elapsed = time.time() - start_t

        passed = result.testsRun - len(result.failures) - len(result.errors)
        total_passed += passed
        total_failed += len(result.failures)
        total_errors += len(result.errors)

        status_str = "PASS" if result.wasSuccessful() else "FAIL"
        print(f" -> Result: {status_str} ({passed}/{result.testsRun} passed in {elapsed:.3f}s)")

    total_time = time.time() - start_total_time
    total_tests = total_passed + total_failed + total_errors

    print("\n" + "=" * 76)
    print(" VERIFICATION SUMMARY & MISSION FLIGHT READINESS")
    print("=" * 76)
    print(f" Total Tests Run: {total_tests}")
    print(f" Tests Passed:    {total_passed}")
    print(f" Tests Failed:    {total_failed}")
    print(f" Tests Errored:   {total_errors}")
    print(f" Execution Time:  {total_time:.3f} seconds")
    print("-" * 76)

    if total_failed == 0 and total_errors == 0:
        print(" >> ALL BENCH & SIMULATION SPECIFICATIONS VERIFIED (TRL 2/3 READY)")
        print("=" * 76)
        return 0
    else:
        print(" >> VERIFICATION FAILURES DETECTED")
        print("=" * 76)
        return 1


if __name__ == "__main__":
    sys.exit(run_test_suite())
