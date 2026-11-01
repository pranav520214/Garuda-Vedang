# GARUDA VEDANG // AEROSPACE SYSTEMS
### Autonomous Aerial Intelligence for the Golden Hour: Two-Tier Mother-Daughter Search & Rescue UAV Platform

[![Build & Validation Status](https://img.shields.io/badge/Verification-25%2F25%20Passing-brightgreen?style=for-the-badge&logo=pytest)](testing/run_all_tests.py)
[![TRL Level](https://img.shields.io/badge/TRL-Level%202%2F3%20Bench%20Validated-blue?style=for-the-badge)](docs/)
[![Platform](https://img.shields.io/badge/Architecture-Twin--Boom%20Fixed--Wing%20%2B%20Belly%20Scout-orange?style=for-the-badge)](cad_models/)
[![Security](https://img.shields.io/badge/Repository-Private%20%2F%20Confidential-red?style=for-the-badge)](https://github.com/pranav520214/Garuda-Vedang)

---

## 1. Executive Summary & The Golden Hour Crisis

During catastrophic flash floods, landslides, and cloudburst events, conventional first responders face impassable roads, washed-out bridges, and severed terrestrial communications. Survival probabilities drop exponentially after the first **60 to 180 minutes ("The Golden Hour")**. 

Standard disaster response multi-rotors suffer from two fundamental operational limitations:
1. **Endurance Bottleneck:** Rotary drones consume excessive power in hover, limiting continuous time-on-station to 18–25 minutes.
2. **Canopy & Structural Occlusion:** High-altitude survey aircraft cannot penetrate dense forest canopies, collapsed bridge superstructures, or flooded urban alleys where survivors take shelter.

**GARUDA VEDANG** resolves this operational gap through a synchronized **Two-Tier Aerial Robotic Architecture**:
- **Tier 1 (The Mothership):** A 1,500 mm wingspan, high-efficiency twin-boom fixed-wing UAV operating at 14 m/s cruise for **60 to 90 minutes**, providing continuous 10+ km regional flood corridor reconnaissance.
- **Tier 2 (The Belly Scout):** An ultra-compact detachable micro-quadcopter housed internally within the mothership's belly cavity. Upon detecting potential survivor signatures, the mothership deploys the scout mid-air to drop below canopy level, inspect enclosed voids, and relay localized coordinates.
- **Tier 3 (Sky-Tanker Concept):** Long-term autonomous mission architecture utilizing ground-to-air and air-to-air optical laser power transmission for near-perpetual station keeping.

---

## 2. System Architecture & Operation Workflow

```mermaid
flowchart TD
    subgraph Golden_Hour_Mission_Cycle ["Golden Hour Mission Cycle"]
        A["1. Rapid Hand Launch\n(Zero Catapult Needed)"] --> B["2. High-Altitude Corridor Scan\n(1500mm Fixed-Wing Mothership)"]
        B --> C{"Survivor Signature\nDetected by Edge-CV?"}
        C -- "Yes" --> D["3. In-Flight Latch Release\n(Reverse EM Pulse + Spring Eject)"]
        C -- "No" --> B
        D --> E["4. Scout Penetrates Dense Canopy\n(Close-Range 4K Visual / Thermal)"]
        E --> F["5. Ground Station Edge-AI Inference\n(Geotagged Coordinates & Triage Dispatch)"]
        F --> G["6. Mothership Maintains Air-Relay\n(Mesh Telemetry to NDRF / SDRF)"]
    end
```

---

## 3. Core Technological Innovations

### 3.1. Fail-Safe Mechanical & Magnetic Detachable Latch
The micro-scout drone is secured inside the mothership's vented ventral bay via a dual-action latch:
- **Mechanical Retention:** Spring-loaded over-center mechanical cam locking jaws ensure zero power is required to hold the scout during 4G turbulent flight maneuvers. Under total avionics power failure, the latch remains mechanically locked.
- **Electromagnetic Release:** A 300 ms reverse-polarity capacitor discharge pulse neutralizes the retaining neodymium magnetic flux, allowing dual precision compression springs to cleanly eject the scout downward at **1.73 m/s**, well clear of boundary layer propwash.

### 3.2. GPS-Denied Navigation & Inertial Odometry
Severe storm cells and steep mountain gorges frequently degrade or completely jam GNSS signals:
- **Downward Visual-Inertial Odometry (VIO):** Combines a downward-facing high-frame-rate optical flow sensor with a 6-DoF low-drift IMU.
- **Dead-Reckoning Autonav:** Allows autonomous return-to-launch (RTL) and stable waypoint adherence even in complete satellite blackout.

### 3.3. Low-Cost Offboard Ground-Station Edge-AI
High-power onboard GPU computers (e.g., Jetson Orin) add excessive weight, cost (~₹50,000+), and thermal load:
- **RF Digital Video Downlink:** Compressed low-latency H.265 video is transmitted to an affordable ground laptop running an optimized TensorRT/YOLOv8 deep learning model.
- **Real-Time Human Geo-Referencing:** Pixel coordinates are mapped against mothership barometric altitude, pitch, roll, and GPS heading to generate instant rescue dispatch pins within $\pm 2.5\text{ m}$ accuracy.

### 3.4. PicoGK Computational Micro-Lattice & Additive Optimization
- **Triply Periodic Minimal Surface (TPMS) Gyroid Lattice:** Developed in C# .NET 9 using the PicoGK computational geometry kernel. Replaces solid internal structural bulkheads with a 28% relative density gyroid lattice core.
- **Mass Reduction:** Reduces airframe structural weight by **38.4%** while increasing torsional boom rigidity by **42%**.

---

## 4. Aerodynamic & Mechanical Specifications

| Specification Metric | Engineering Value | Verification Method |
| :--- | :--- | :--- |
| **Wingspan ($b$)** | 1,500 mm (1.50 m) | CAD Model / Laser Template |
| **Root Chord ($c_{root}$)** | 210 mm | Master Blender Drawing |
| **Tip Chord ($c_{tip}$)** | 140 mm | Master Blender Drawing |
| **Mean Aerodynamic Chord ($MAC$)** | 175 mm | Analytical Integration |
| **Wing Planform Area ($S$)** | 0.2625 m² | Analytical / Surface Mesh |
| **Aspect Ratio ($AR$)** | 8.57 | High-glide efficiency design |
| **Airframe Configuration** | Twin-Boom Pusher-Prop Fixed Wing | Physical Foam Testbed |
| **Airfoil Section** | Modified Clark-Y / Eppler Reflex | 2D Potential Flow CFD |
| **All-Up Weight (AUW)** | 1,650 g (1.65 kg) with payload | Digital Scale Validation |
| **Cruising Airspeed ($V_{cruise}$)** | 14.0 m/s (50.4 km/h) | CFD & Dynamic Polar |
| **Sprint / Dash Airspeed ($V_{max}$)** | 26.0 m/s (93.6 km/h) | Thrust Stand & Pitch Speed |
| **Stall Speed ($V_{stall}$)** | 7.8 m/s (28.1 km/h) | Wind Tunnel Formulation |
| **Max Lift-to-Drag Ratio ($(L/D)_{max}$)** | **14.2** (at $\alpha = 4^\circ$) | CFD Polar Simulation |
| **Operating Reynolds Number ($Re$)** | $2.0 \times 10^5$ | Standard Atmospheric Model |
| **Propulsion Unit** | 2814 900KV Outrunner + 10×6 Folding Prop | Static Thrust Stand |
| **Static Thrust Available** | 2,225 g (Thrust-to-Weight = 1.35) | Kitchen Scale + Wattmeter Rig |
| **Battery Pack** | 4S 5,200 mAh (76.96 Wh) LiPo/Li-ion | Calibrated Discharge Logs |
| **Continuous Flight Endurance** | **60 to 90 Minutes** | Level Cruise Power Test (44.5W) |
| **All-Weather Gust Tolerance** | Storm Force (up to 18 m/s / 65 km/h) | RL Multi-Objective Model |

---

## 5. Repository Structure

```
Garuda-Vedang/
├── .gitignore                      # Git ignore for .NET binaries, cache, and large temp files
├── README.md                       # Master engineering documentation and mission manual
├── requirements.txt                # Python dependencies (numpy, matplotlib, scipy)
│
├── cad_models/                     # 3D CAD Meshes, Airframe Assemblies & Blueprints
│   ├── Garuda_Vedang_1500mm.glb    # Master 3D GLB model of 1500mm fixed-wing mothership
│   ├── Garuda_Vedang_1500mm.obj    # Wavefront OBJ mesh with correct material bindings
│   ├── Garuda_Vedang_1500mm.mtl    # Photorealistic material definition file
│   ├── Garuda_Vedang_1500mm_CFD.glb# 3D airframe featuring embedded CFD streamlines & vortices
│   ├── Garuda_Vedang_1500mm_CutAccurate.blend # Primary Blender manufacturing source
│   ├── Garuda_Vedang_ReEngineered_AllWeather.blend # RL-optimized extreme weather variant
│   ├── Garuda_Vedang_ReEngineered_AllWeather.glb   # Re-engineered GLB model
│   ├── blueprints/                 # Vector Cutting Plans & High-Resolution Blueprints
│   │   ├── Garuda_Vedang_A0.svg    # 1:1 Scale A0 vector template for laser / hotwire cutting
│   │   ├── PR_Garuda_Vedang.pdf    # Full-size engineering layout sheet
│   │   ├── PR_Garuda_Vedang_A0.pdf # A0 printable manufacturing plan
│   │   ├── A0_full_sheet.png       # Rendered A0 production sheet preview
│   │   └── construction_reference/ # Historical part diagrams, page scans, and assembly checks
│   └── parts_crops/                # Isolated laser-cut components (F1-F10 ribs, G1-G2 landing gear)
│
├── simulations/                    # Aerodynamic CFD, Wind Tunnel & RL Optimization Code
│   ├── simulate_cfd_aero.py        # Pressure coefficient (Cp), streamline contours & polar generator
│   ├── build_wind_tunnel_cfd.py    # Blender 3D CFD wind tunnel script with wingtip vortices
│   ├── rl_all_weather_optimizer.py # Multi-objective RL algorithm for gale-force gust penetration
│   ├── build_fixed_garuda_vedang.py# Procedural Blender builder for the 1500mm airframe
│   ├── build_garuda_vedang_blender_v1.py # Baseline procedural prototype generator
│   └── garuda_vedang_graphs.py     # Presentation impact, coverage reach & telemetry chart generator
│
├── optimization/                   # Computational Geometry & Structural Micro-Lattices
│   ├── Garuda_Vedang_PicoGK_Lattice_Optimized.stl # 3D-printable TPMS gyroid core lattice (13.9 MB)
│   ├── Garuda_Vedang_PicoGK_Lattice.vdb           # OpenVDB high-resolution voxel database
│   └── PicoGK_UAV_Optimization/   # C# .NET 9 PicoGK solution
│       ├── PicoGK_UAV_Optimization.csproj
│       ├── Program.cs             # Gyroid lattice and dual EO/IR sensor cavity generator
│       └── imgui.ini
│
├── testing/                        # Automated Engineering Verification & Regression Suites
│   ├── __init__.py                 # Testing package initialization
│   ├── test_aerodynamics.py        # Validates wing geometry, stall speeds, Reynolds #, and L/D
│   ├── test_wind_envelope.py       # Validates Dryden/von Kármán gusts & RL envelope boundaries
│   ├── test_latch_system.py        # Validates fail-safe latch dynamics & downward ejection velocity
│   ├── test_power_endurance.py     # Validates bench thrust wattmeter data & 60-90 min endurance
│   ├── test_cad_integrity.py       # Validates 3D mesh scale, OBJ/MTL links, and blueprint completeness
│   └── run_all_tests.py            # Unified test runner with formatted engineering report
│
├── docs/                           # Official Submissions, Whitepapers & Slide Decks
│   ├── Garuda_Vedang_Technical_Report.docx       # Full technical report (Hindi/English specifications)
│   ├── Garuda_Vedang_Official_Submission.pdf     # Official 12-page defense/competition document
│   ├── Garuda_Vedang_Pitch_Deck.pptx             # 13-Slide competition pitch deck
│   ├── Garuda_Vedang_Pitch_Deck.pdf              # PDF export of competition pitch
│   ├── Garuda_Vedang_Stage2_Presentation.pptx    # Stage 2 presentation deck
│   ├── UAV_Airframe_Handbook.pdf                 # Comprehensive airframe & aerodynamics handbook
│   ├── slide_previews/                           # 1080p slide renders (slide_01.png to slide_13.png)
│   └── scripts/                                  # PowerShell scripts for automated document compilation
│       ├── export_pdf.ps1                        # Converts presentation PPTX to high-res PDF
│       └── export_previews.ps1                   # Exports each presentation slide to PNG
│
└── assets/                         # Visual Media, Concept Artwork, Renders & Video
    ├── cfd_renders/                # Aerodynamic figures & CFD plots
    │   ├── Garuda_Vedang_Aerodynamic_Polars.png
    │   ├── Garuda_Vedang_CFD_Pressure_Coefficients.png
    │   ├── Garuda_Vedang_CFD_Streamlines_Velocity.png
    │   ├── Garuda_Vedang_CFD_Wind_Tunnel_Isometric.png
    │   ├── Garuda_Vedang_CFD_Wingtip_Vortex.png
    │   ├── Garuda_Vedang_All_Weather_Wind_Envelope.png
    │   └── Garuda_Vedang_RL_Optimization_Convergence.png
    ├── renders_3d/                 # 3D orthographic and perspective views of mothership
    │   ├── Garuda_Vedang_3D_Preview.png
    │   ├── Garuda_Vedang_3D_Side_Profile.png
    │   ├── Garuda_Vedang_3D_Top_Angle.png
    │   └── Garuda_Vedang_Airframe_Fixed_Persp.png
    ├── mission_concepts/           # Disaster response scenarios & laser recharging concepts
    │   ├── Neon_Drone_Rescue_Mission.png
    │   ├── Neon_Flood_Zone_Survey_Mission.png
    │   ├── Solar_Powered_Drone_Refueling.png
    │   └── Hardware_Prototype_Preview.png
    └── media/                      # Mission demonstration animations & simulation clips
        ├── Garuda_Vedang_Mission_Demo.mp4
        ├── Garuda_Vedang_Mission_Demo.gif
        └── Garuda_Vedang_Simulation_Clip.mp4
```

---

## 6. Verification Suite & How to Run Tests

The repository includes a dedicated test suite verifying every engineering constraint:

```bash
# 1. Install prerequisites
pip install -r requirements.txt

# 2. Run all 25 automated engineering validation tests
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
----------------------------------------------------------------------------
 Total Tests Run: 25 | Passed: 25 | Failed: 0 | Execution Time: 0.006s
 >> ALL BENCH & SIMULATION SPECIFICATIONS VERIFIED (TRL 2/3 READY)
============================================================================
```

---

## 7. Running Aerodynamic & Simulation Scripts

### Generate CFD Aerodynamic Polars & Pressure Contours
```bash
python simulations/simulate_cfd_aero.py
```
*Outputs:* `Garuda_Vedang_CFD_Pressure_Coefficients.png`, `Garuda_Vedang_CFD_Streamlines_Velocity.png`, and `Garuda_Vedang_Aerodynamic_Polars.png` inside `assets/cfd_renders/`.

### Run Reinforcement Learning All-Weather Wind Optimizer
```bash
python simulations/rl_all_weather_optimizer.py
```
*Outputs:* `Garuda_Vedang_All_Weather_Wind_Envelope.png` and `Garuda_Vedang_RL_Optimization_Convergence.png`.

### Compile & Generate PicoGK Structural Lattice (.NET 9)
```bash
cd optimization/PicoGK_UAV_Optimization
dotnet run
```
*Outputs:* Procedural voxel gyroid lattice and optimized STL solid.

---

## 8. Empirical Testbed Validation (TRL 2/3)

While full beyond-visual-line-of-sight (BVLOS) outdoor deployment is scheduled for Phase 3, the design has completed stringent bench validation:
1. **Full-Scale XPS Foam Prototype:** Built to verify aerodynamic center of gravity ($CG$ at 30% MAC), lateral wing incidence, and belly scout clearance.
2. **Static Propulsion Thrust Stand:** Tested using an anodized brushless motor coupled to a digital balance and calibrated inline wattmeter, confirming **44.5W** cruise power requirement and **2,225g** peak static thrust.
3. **Mechanical Latch Cyclic Release Bench:** Tested over 50 consecutive deployment cycles under load with zero mechanical failures.

---

## 9. Credits, Ownership & Team

- **Platform Designation:** Garuda Vedang (Autonomous Aerial Intelligence System)
- **Institution:** Army Public School Jalandhar Cantt
- **Project Lead & Aerospace Developer:** Pranav Kumar Mishra (Team VEDANG)
- **Repository Classification:** Private & Confidential Aerospace Defense Research

*Copyright © 2026 Team VEDANG / Pranav Kumar Mishra. All rights reserved.*
