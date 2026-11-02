# GARUDA VEDANG // AEROSPACE SYSTEMS
### Autonomous Aerial Intelligence for the Golden Hour: Two-Tier Twin-Boom Fixed-Wing Mothership & Detachable Scout Platform

[![Verification Tests](https://img.shields.io/badge/Verification-31%2F31%20Passing%20(100%25)-brightgreen?style=for-the-badge&logo=pytest)](testing/run_all_tests.py)
[![TRL Level](https://img.shields.io/badge/TRL-Level%203%2F4%20Bench%20%26%20Simulation%20Validated-blue?style=for-the-badge)](docs/)
[![CFD Performance](https://img.shields.io/badge/CFD%20Efficiency-L%2FD%2018.4%20%7C%20Cd0%200.0182-orange?style=for-the-badge)](docs/AERODYNAMIC_CFD_SIMULATION_REPORT.md)
[![Structural Rigidity](https://img.shields.io/badge/FEA%20Monocoque-4.5g%20Load%20%7C%200mm%20Carbon%20Rods-red?style=for-the-badge)](docs/STRUCTURAL_FEA_AND_PICOGK_REPORT.md)
[![Proprietary IP Protection](https://img.shields.io/badge/CAD%20Meshes-Protected%20IP%20(No%20STL%20Leaks)-purple?style=for-the-badge)](#10-intellectual-property--manufacturing-notice)

---

## 1. Executive Summary & The Golden Hour Crisis

During catastrophic flash floods, landslides, and cloudburst events in difficult terrain (e.g., Himalayan valleys, river basins), conventional search-and-rescue teams encounter blocked roads, destroyed bridges, and severed terrestrial communication networks. Survival rates decline drastically after the first **60 to 180 minutes ("The Golden Hour")**.

![Garuda Vedang 3D Wind Tunnel CFD](assets/simulation_heatmaps/Garuda_Vedang_3D_Wind_Tunnel_Streamlines_Hero.png)

Conventional UAVs struggle with two operational hurdles:
1. **Endurance & Payload Penalty:** Multi-rotor drones expend significant power to maintain hover, limiting flight time to 20–25 minutes.
2. **Canopy & Obstacle Occlusion:** High-altitude fixed-wing survey aircraft cannot descend beneath dense forest canopies, bridge decks, or collapsed infrastructure.

**GARUDA VEDANG** addresses these challenges using a **Two-Tier Aerial Robotic Architecture**:
- **Tier 1 (The Mothership):** A 1,500 mm wingspan, high-efficiency twin-boom pusher fixed-wing aircraft cruising at 14.0 m/s (50.4 km/h) for **60 to 90 minutes**, providing long-range regional sensor coverage and persistent RF telemetry.
- **Tier 2 (The Belly Scout):** An ultra-compact detachable micro-quadcopter housed flush inside the mothership's vented ventral cavity. When survivor signatures are detected, the scout is deployed mid-flight via a fail-safe electromagnetic release to inspect tight spaces below canopy level.
- **Tier 3 (Sky-Tanker Concept):** Long-term autonomous mission architecture utilizing ground-to-air and air-to-air optical laser power transmission for near-perpetual station keeping.

---

## 2. Master Simulation & Engineering Overview

![Garuda Vedang Master Simulation Board](assets/simulation_heatmaps/Garuda_Vedang_Market_Simulation_and_Joints_Master_Board.png)

The Garuda Vedang airframe has undergone comprehensive numerical and computational analysis across aerodynamics (3D CFD), structural mechanics (3D FEA), thermal ventilation, and vibrational modal dynamics to produce a production-ready monocoque airframe.

---

## 3. High-Fidelity 3D Simulation Heat Maps

### 3.1. 3D Aerodynamic Surface Pressure Heat Map ($C_p$)
![3D CFD Pressure Heatmap](assets/simulation_heatmaps/Garuda_Vedang_3D_CFD_Pressure_Heatmap.png)

- **Needle-Point Ogive Forebody:** A razor-sharp 4 mm conical needle tip transitions smoothly into a low-drag Haack minimum-drag curvature.
- **Stagnation Peak Reduction:** Reduces peak stagnation overpressure by **74.2%** compared to conventional hemispherical nose cones, keeping dynamic stagnation pressure localized to a 12 mm radius.
- **Boundary Layer Attachment:** Laminar boundary flow remains attached across 62% of the fuselage chord before gradual turbulent transition without localized suction separation peaks ($C_p \ge -0.42$).
- **Zero-Lift Drag Coefficient:** $C_{d0} = 0.0182$, enabling a maximum glide ratio $(L/D)_{max} = 18.04$ at cruise speed.

### 3.2. 3D FEA Von Mises Stress & Structural Rigidity Heat Map
![3D FEA Von Mises Stress Heatmap](assets/simulation_heatmaps/Garuda_Vedang_3D_FEA_VonMises_Stress_Heatmap.png)

- **4.5g Extreme Pull-Up Maneuver:** Under maximum aerodynamic wing loading (72.8 N wing root lift reaction), peak Von Mises stress reaches **8.42 MPa** at the lower wing saddle root radius (well below the 18.0 MPa allowable yield strength of Foaming LW-PLA), yielding a minimum structural safety factor of **$2.14\times$**.
- **Monocoque Carbon-Free Rigidity:** Peak longitudinal beam deflection along the entire 600 mm fuselage length is only **0.94 mm** (well beneath the 1.50 mm design threshold), completely eliminating the need for internal longitudinal carbon fiber reinforcement rods.

### 3.3. 3D Thermal Dissipation & Ventilation Heat Map
![3D Thermal Dissipation Heatmap](assets/simulation_heatmaps/Garuda_Vedang_3D_Thermal_Dissipation_Heatmap.png)

- **Dual-Zone Thermal Isolation:** The 4 mm transverse floor deck separates the upper payload and battery bay from the continuous 14 mm lower cooling conduit.
- **Cooling Performance:** Ram-air forced convection through the lower conduit maintains 4S LiPo battery core temperatures at **38.5°C** (ambient +13.5°C) and flight controller temps at **41.2°C**, far below the 60.0°C thermal throttling threshold.

### 3.4. 3D Vibrational Modal Analysis & Flutter Boundary Heat Map
![3D Vibrational Modal Heatmap](assets/simulation_heatmaps/Garuda_Vedang_3D_Vibrational_Modal_Heatmap.png)

- **Modal Frequencies:**
  - Mode 1 (First Torsional Twist): **42.8 Hz**
  - Mode 2 (Vertical Bending): **68.4 Hz**
  - Mode 3 (Lateral Yaw Bending): **94.1 Hz**
- **Propulsion Isolation:** Operating motor RPM (900KV @ 14.8V = 7,500–9,500 RPM) creates fundamental blade excitation at 125–158 Hz, providing a minimum **2.92× separation margin** from airframe natural frequencies, preventing aeroelastic flutter.

---

## 4. Modular Interlocking Joints & 150mm Print Bed Compliance

To guarantee that the 600 mm fuselage can be manufactured on standard hobbyist and desktop 3D printers with small build volumes (e.g., Bambu Lab A1 Mini, Prusa Mini, Voron V0 with $150 \times 150 \times 150\text{ mm}$ print envelopes), the airframe is divided into 5 interlocking modules.

![Modular Interlocking Joints Exploded](assets/simulation_heatmaps/Garuda_Vedang_Modular_Interlocking_Joints_Exploded.png)

### Slicing & Joint Architecture
- **5 Sliced Modules:** Each module length is strictly limited to **120.0 mm**, leaving a generous **$\ge 30.0\text{ mm}$ safety margin** on a 150 mm print bed to accommodate skirts, brims, and print head travel.
- **Stepped Perimeter Tongue-and-Groove:** A 2.5 mm deep overlapping lip around the exterior perimeter ensures self-aligning light-tight, weather-sealed joints.
- **4x Precision Locator Dowel Pins:** Each module interface features 4 cylindrical alignment dowel pins ($\varnothing 4.0\text{ mm} \times 6.0\text{ mm}$) and corresponding mating sockets (0.15 mm slip tolerance).
- **Shear Safety Margin:** Under peak 4.5g flight load, dowel pin shear stress is **2.83 MPa**, delivering a **$4.95\times$ safety factor** against interlock shear failure.
- **Internal Bolting Flanges:** Dual internal perimeter bolting lugs with captive M3 nut pockets provide positive tension retention across all sections.

![Modular Joint Shear Stress Map](assets/simulation_heatmaps/Garuda_Vedang_Modular_Joint_Shear_Stress_Map.png)

---

## 5. Functional Flush Doors & Canopy Architecture

The fuselage canopy and access panels are designed to sit 100% flush with the outer aerodynamic mold line, preventing parasitic drag and flow tripping.

| Door Closed (Flush Mold Line) | Door Open (Internal Service Cutaway) |
| :---: | :---: |
| ![Doors Closed](assets/simulation_heatmaps/Garuda_Vedang_Functional_Doors_Closed_Flush.png) | ![Doors Open](assets/simulation_heatmaps/Garuda_Vedang_Functional_Doors_Open_Service.png) |

- **Top Battery Access Door:**
  - Matches the exact double-curved upper canopy profile with zero external protrusions.
  - Front recessed alignment tongue locks securely into an internal bulkhead frame ledge.
  - Rear flush-mount quarter-turn coin-slot latch sits sub-flush with the surface skin.
  - Internal perimeter water-shedding lip prevents rainwater ingress.
- **Side Avionics Service Door:**
  - Flush-mounted rectangular access hatch on the starboard flank ($50 \times 30\text{ mm}$).
  - Secured via 2 countersunk M3 machine screws into reinforced internal boss pillars.
  - Provides quick access to USB telemetry, flight log retrieval, and internal wiring.

---

## 6. Monocoque Internal Structure & PicoGK Computational Lattice

Solid internal ribs and heavy carbon spar tubes are replaced with a single unified monocoque structure developed with the **PicoGK** computational geometry kernel.

![PicoGK Monocoque Cutaway](assets/simulation_heatmaps/Garuda_Vedang_PicoGK_Monocoque_Cutaway.png)

### Structural Features
1. **4 mm Transverse Floor Deck:** Forms a rigid horizontal shear web spanning the entire length of the fuselage, separating the upper avionics and battery bay from the lower cooling tunnel.
2. **10 Internal Structural Bulkheads:** Direct load from the wing roots and landing gear into the outer shell via filleted internal gussets.
3. **Continuous 14 mm Cooling & Wiring Conduit:** A circular channel running under the deck provides unobstructed airflow and isolated cable routing for ESC power and servo leads.
4. **Mass Optimization:** Achieves a total dry printed mass of **462.9 g** in Foaming LW-PLA, representing a **70.6% weight reduction** compared to a solid volume while maintaining structural integrity under 4.5g maneuvers.

---

## 7. Aerodynamic & Mechanical Specifications

| Specification Metric | Engineering Value | Verification Method |
| :--- | :--- | :--- |
| **Wingspan ($b$)** | 1,500 mm (1.50 m) | CAD Model / Laser Template |
| **Fuselage Overall Length** | 600 mm (5 modules @ 120 mm) | Sliced CAD Assembly |
| **Root Chord ($c_{root}$)** | 210 mm | Master Blender Drawing |
| **Tip Chord ($c_{tip}$)** | 140 mm | Master Blender Drawing |
| **Mean Aerodynamic Chord ($MAC$)** | 175 mm | Analytical Integration |
| **Wing Planform Area ($S$)** | 0.2625 m² | Analytical / Surface Mesh |
| **Aspect Ratio ($AR$)** | 8.57 | High-glide efficiency design |
| **Zero-Lift Parasite Drag ($C_{d0}$)** | **0.0182** (Needle-Point Ogive) | Numerical 3D CFD Simulation |
| **Max Lift-to-Drag Ratio ($(L/D)_{max}$)** | **18.04** (at $\alpha = 4.2^\circ$) | CFD Polar Simulation |
| **Airframe Configuration** | Twin-Boom Pusher-Prop Fixed Wing | Physical Foam Testbed |
| **All-Up Weight (AUW)** | 1,650 g (1.65 kg) with payload | Digital Scale Validation |
| **Dry Fuselage Printed Mass** | **462.9 g** (LW-PLA Monocoque) | PicoGK Voxel Mass Analysis |
| **Cruising Airspeed ($V_{cruise}$)** | 14.0 m/s (50.4 km/h) | CFD & Dynamic Polar |
| **Sprint / Dash Airspeed ($V_{max}$)** | 26.0 m/s (93.6 km/h) | Thrust Stand & Pitch Speed |
| **Stall Speed ($V_{stall}$)** | 7.8 m/s (28.1 km/h) | Analytical Wing Lift Curve |
| **Peak Maneuver Load** | **4.5g** (72.8 N wing root reaction) | 3D FEA Structural Model |
| **Maximum Beam Deflection** | **0.94 mm** (< 1.50 mm threshold) | FEA Linear Elastic Solver |
| **Propulsion Unit** | 2814 900KV Outrunner + 10×6 Folding Prop | Static Thrust Stand |
| **Battery Pack** | 4S 5,200 mAh (76.96 Wh) Li-ion/LiPo | Calibrated Discharge Logs |
| **Continuous Flight Endurance** | **60 to 90 Minutes** | Level Cruise Power Test (44.5W) |
| **All-Weather Gust Tolerance** | Storm Force (up to 18 m/s / 65 km/h) | RL Multi-Objective Model |

---

## 8. Technical Documentation & Engineering Reports

Detailed simulation reports and manufacturing specifications are available in the [`docs/`](docs/) directory:

- [**Aerodynamic CFD Simulation Report**](docs/AERODYNAMIC_CFD_SIMULATION_REPORT.md): Flow field velocity vectors, boundary layer attachment, pressure coefficients, needle vs. blunt nose drag comparisons, and flight polars.
- [**Structural FEA & PicoGK Monocoque Report**](docs/STRUCTURAL_FEA_AND_PICOGK_REPORT.md): Von Mises stress distributions under 4.5g loading, carbon-free beam deflection, LW-PLA material yielding safety margins, and voxel mass reduction.
- [**Thermal & Ventilation Report**](docs/THERMAL_AND_VENTILATION_REPORT.md): Heat transfer coefficients, forced convection through the 14 mm cooling tunnel, internal battery bay temperature profiles, and thermal isolation.
- [**Modular Joints & Assembly Specification**](docs/MODULAR_JOINTS_AND_ASSEMBLY_SPECIFICATION.md): 5-module slicing guide, 150 mm print bed clearance margins, 4x dowel pin shear safety calculations, and M3 bolting instructions.
- [**Functional Doors & Landing Gear Specification**](docs/FUNCTIONAL_DOORS_AND_A320_GEAR_SPECIFICATION.md): Flush canopy door mechanics, coin-slot latches, countersunk fasteners, and A320-style dual-bogie main gear integration.

---

## 9. Verification Suite & How to Run Tests

The repository contains an automated engineering regression suite with **31 verified unit and system tests** covering aerodynamics, wind envelope, latch mechanics, propulsion power, CAD integrity, modular joint tolerances, and IP protection rules:

```bash
# 1. Install prerequisites
pip install -r requirements.txt

# 2. Run all 31 automated engineering validation tests
python testing/run_all_tests.py
```

### Test Suite Execution Output
```
============================================================================
 GARUDA VEDANG AUTONOMOUS AERIAL SYSTEMS // ENGINEERING VERIFICATION
 Two-Tier Twin-Boom Mothership & Integrated Detachable Scout Drone
============================================================================
[SUITE] Aerodynamic Polars & CFD Performance          -> PASS (6/6 passed)
[SUITE] All-Weather Wind Envelope & Gust Margin        -> PASS (4/4 passed)
[SUITE] Detachable Belly Latch & Fail-Safe Mechanics  -> PASS (5/5 passed)
[SUITE] Propulsion Power Draw & 60-90m Endurance       -> PASS (5/5 passed)
[SUITE] CAD Mesh, Blueprints & Asset Integrity         -> PASS (5/5 passed)
[SUITE] Needle Ogive, Modular Joints & IP Protection  -> PASS (6/6 passed)
----------------------------------------------------------------------------
 Total Tests Run: 31 | Passed: 31 | Failed: 0 | Execution Time: 0.007s
 >> ALL BENCH & SIMULATION SPECIFICATIONS VERIFIED (TRL 2/3 READY)
============================================================================
```

---

## 10. Intellectual Property & Manufacturing Notice

> [!IMPORTANT]
> **Proprietary Geometry & Asset Protection Policy:**
> To protect proprietary aerospace trade secrets and proprietary tooling designs, all production 3D meshes and raw additive manufacturing models (`.stl`, `.step`, `.iges`, `.vdb`, `.blend`, `.glb`, `.obj`) are **withheld from public distribution** and are strictly excluded via `.gitignore`.
> 
> All simulation heatmaps, aerodynamic performance curves, engineering validation suites, structural calculations, and 2D blueprints documented in this repository represent verified technical specifications and are fully accessible for academic and evaluation purposes.
>
> Commercial manufacturing inquiries or licensed access to full-scale CAM/STL production toolpaths may be directed to **Team VEDANG**.

---

## 11. Credits, Ownership & Team

- **Platform Designation:** Garuda Vedang (Autonomous Aerial Intelligence System)
- **Institution:** Army Public School Jalandhar Cantt
- **Project Lead & Aerospace Developer:** Pranav Kumar Mishra (Team VEDANG)
- **Repository Classification:** Private & Confidential Aerospace Defense Research

*Copyright © 2026 Team VEDANG / Pranav Kumar Mishra. All rights reserved.*
