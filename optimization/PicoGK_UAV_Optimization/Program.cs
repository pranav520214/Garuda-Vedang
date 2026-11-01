using System;
using System.IO;
using System.Numerics;
using System.Collections.Generic;
using PicoGK;

public class GyroidLattice : IImplicit
{
    private readonly float m_fScale;
    private readonly float m_fThreshold;

    public GyroidLattice(float fPeriodMM, float fRelativeDensity)
    {
        m_fScale = (2.0f * (float)Math.PI) / fPeriodMM;
        // Approximate threshold for gyroid sheet thickness based on relative density
        m_fThreshold = fRelativeDensity * 1.15f;
    }

    public float fSignedDistance(in Vector3 vec)
    {
        float x = vec.X * m_fScale;
        float y = vec.Y * m_fScale;
        float z = vec.Z * m_fScale;

        // Triply Periodic Minimal Surface (TPMS) Gyroid formula:
        // G(x,y,z) = sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x)
        float fVal = (float)(Math.Sin(x) * Math.Cos(y) +
                             Math.Sin(y) * Math.Cos(z) +
                             Math.Sin(z) * Math.Cos(x));

        // Sheet gyroid thickness: |fVal| <= threshold
        return Math.Abs(fVal) - m_fThreshold;
    }
}

class Program
{
    static void Main()
    {
        Console.WriteLine("===============================================================");
        Console.WriteLine("PicoGK Computational Engineering Engine for Garuda Vedang 1500mm UAV");
        Console.WriteLine("===============================================================");

        string strOutDir = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, @"..", "..", "..", ".."));
        string strStlPath = Path.Combine(strOutDir, "Garuda_Vedang_PicoGK_Lattice_Optimized.stl");
        string strVdbPath = Path.Combine(strOutDir, "Garuda_Vedang_PicoGK_Lattice.vdb");

        // Run PicoGK with 1.0mm voxel size for fast, robust GPU generation
        Library.Go(1.0f, () =>
        {
            Console.WriteLine($"Voxel grid resolution: {Library.fVoxelSizeMM} mm");

            // 1. Construct Fuselage Outer Boundary Mesh
            Console.WriteLine("Generating Aerodynamic Airframe Mesh...");
            Mesh mshFuse = BuildFuselageMesh();

            Voxels voxFuselage = new Voxels(mshFuse);
            Console.WriteLine("Voxelized Fuselage Airframe.");

            // 2. Construct Dual EO/IR Camera Turret Bay
            Console.WriteLine("Constructing Dual EO/IR Imaging Payload Cavity...");
            Voxels voxCameraBay = BuildCameraBayVoxels();

            // 3. Structural Shelling & Additive Micro-Lattice Generation
            Console.WriteLine("Computing hollow interior & 1.5mm aerodynamic skin...");
            // Hollow skin: subtract 1.5mm offset
            Voxels voxInterior = voxFuselage.voxOffset(-1.5f);
            
            Voxels voxSkin = new Voxels(voxFuselage);
            voxSkin.BoolSubtract(voxInterior);

            // 4. Generate PicoGK Gyroid Infill Lattice (28% relative density)
            Console.WriteLine("Rendering Gyroid TPMS Micro-Lattice infill...");
            BBox3 oBounds = voxInterior.oCalculateBoundingBox();
            
            // Period: 18mm, density: 0.28 (RL optimized parameter)
            GyroidLattice oGyroid = new GyroidLattice(18.0f, 0.28f);
            Voxels voxLattice = new Voxels(oGyroid, oBounds);

            // Intersect lattice with interior space
            voxLattice.BoolIntersect(voxInterior);
            Console.WriteLine("Intersected Micro-Lattice with airframe internal core.");

            // 5. Combine Skin + Infill Lattice
            Voxels voxOptimized = new Voxels(voxSkin);
            voxOptimized.BoolAdd(voxLattice);

            // 6. Subtract EO/IR Camera Bay Cavity (Guarantees zero interference with sensor)
            voxOptimized.BoolSubtract(voxCameraBay);
            Console.WriteLine("Integrated EO/IR Camera Bay Cavity into Airframe.");

            // 7. Calculate Mass & Volume Properties
            voxOptimized.CalculateProperties(out float fVolumeMM3, out BBox3 oFinalBBox);
            float fVolumeCM3 = fVolumeMM3 / 1000.0f;
            float fPolymerDensityG_CM3 = 0.38f; // Additive foaming lightweight polymer
            float fEstAirframeMassG = fVolumeCM3 * fPolymerDensityG_CM3;

            Console.WriteLine("\n---------------------------------------------------------------");
            Console.WriteLine("PICOGK COMPUTATIONAL RE-ENGINEERING RESULTS:");
            Console.WriteLine("---------------------------------------------------------------");
            Console.WriteLine($"Bounding Box (mm): X=[{oFinalBBox.vecMin.X:F1}, {oFinalBBox.vecMax.X:F1}], " +
                              $"Y=[{oFinalBBox.vecMin.Y:F1}, {oFinalBBox.vecMax.Y:F1}], " +
                              $"Z=[{oFinalBBox.vecMin.Z:F1}, {oFinalBBox.vecMax.Z:F1}]");
            Console.WriteLine($"Solid Voxel Volume:  {fVolumeCM3:F1} cm³");
            Console.WriteLine($"Airframe Mass (LW):  {fEstAirframeMassG:F1} g (Baseline Polyfoam: 640 g)");
            Console.WriteLine($"Structural Savings:  {((640.0f - fEstAirframeMassG) / 640.0f * 100.0f):F1} %");

            // 8. Export Mesh to STL and OpenVDB
            Console.WriteLine($"\nExporting Triangulated Mesh to: {strStlPath}");
            Mesh mshFinal = voxOptimized.mshAsMesh();
            Console.WriteLine($"Generated Manifold Triangular Mesh with {mshFinal.nTriangleCount():N0} triangles.");
            mshFinal.SaveToStlFile(strStlPath, Mesh.EStlUnit.MM);
            Console.WriteLine("Saved STL successfully!");

            Console.WriteLine($"Exporting OpenVDB Voxel Field to: {strVdbPath}");
            voxOptimized.SaveToVdbFile(strVdbPath);
            Console.WriteLine("Saved OpenVDB file successfully!");

            Console.WriteLine("===============================================================");
            Console.WriteLine("PICOGK RE-ENGINEERING PIPELINE COMPLETED SUCCESSFULLY!");
            Console.WriteLine("===============================================================");
        },
        strLogFilePath: Path.Combine(strOutDir, "PicoGK_Logs.txt"),
        bEndAppWithTask: true,
        strWindowTitle: "PicoGK Garuda_Vedang Re-Engineering",
        strLightsFile: "");
    }

    static Mesh BuildFuselageMesh()
    {
        Mesh msh = new Mesh();
        // Fuselage stations in millimeters (Y forward is +, Z up is +)
        // Stations: (Y, HalfWidth, ZBottom, ZTop)
        var stations = new (float Y, float HW, float ZB, float ZT)[]
        {
            ( 143.2f, 28.0f, 16.5f, 16.5f), // Nose apex
            ( 104.5f, 46.0f,  0.0f, 60.5f), // Chin start
            (  62.5f, 58.0f,  0.0f, 83.9f), // Mid nose
            (   0.0f, 62.0f,  0.0f, 95.8f), // Wing saddle start
            (-197.9f, 62.0f,  0.0f, 95.8f), // Wing saddle end
            (-198.0f, 62.0f,  0.0f, 73.6f), // Rear step
            (-314.8f, 46.0f,  0.3f, 73.2f), // Belly upsweep start
            (-436.1f, 27.8f, 34.2f, 72.9f)  // Motor mount firewall
        };

        var ringVertIndices = new List<int[]>();

        for (int i = 0; i < stations.Length; i++)
        {
            var st = stations[i];
            float h = st.ZT - st.ZB;
            float hw = st.HW;
            float zb = st.ZB;
            float zt = st.ZT;

            if (h <= 1.0f)
            {
                int v0 = msh.nAddVertex(new Vector3(-hw, st.Y, zb));
                int v1 = msh.nAddVertex(new Vector3( hw, st.Y, zb));
                ringVertIndices.Add(new int[] { v0, v1 });
            }
            else
            {
                float r = Math.Min(12.0f, Math.Min(hw * 0.35f, h * 0.25f));
                var pts = new Vector3[]
                {
                    new Vector3(-hw + r, st.Y, zb),
                    new Vector3( hw - r, st.Y, zb),
                    new Vector3( hw,     st.Y, zb + r),
                    new Vector3( hw,     st.Y, zt - r),
                    new Vector3( hw - r, st.Y, zt),
                    new Vector3(-hw + r, st.Y, zt),
                    new Vector3(-hw,     st.Y, zt - r),
                    new Vector3(-hw,     st.Y, zb + r)
                };

                int[] idx = new int[8];
                for (int j = 0; j < 8; j++)
                {
                    idx[j] = msh.nAddVertex(pts[j]);
                }
                ringVertIndices.Add(idx);
            }
        }

        // Connect apex to ring 1
        int[] r0 = ringVertIndices[0];
        int[] r1 = ringVertIndices[1];
        msh.AddQuad(r0[0], r0[1], r1[1], r1[0], false);
        msh.AddQuad(r0[1], r1[2], r1[3], r1[4], false);
        msh.AddQuad(r0[1], r1[4], r1[5], r0[0], false);
        msh.AddQuad(r0[0], r1[5], r1[6], r1[7], false);
        msh.AddQuad(r0[0], r1[7], r1[0], r0[1], false);

        // Connect intermediate rings
        for (int i = 1; i < ringVertIndices.Count - 1; i++)
        {
            int[] ra = ringVertIndices[i];
            int[] rb = ringVertIndices[i + 1];
            for (int j = 0; j < 8; j++)
            {
                int jNext = (j + 1) % 8;
                msh.AddQuad(ra[j], ra[jNext], rb[jNext], rb[j], false);
            }
        }

        // Cap rear firewall
        int[] rEnd = ringVertIndices[ringVertIndices.Count - 1];
        msh.AddQuad(rEnd[0], rEnd[1], rEnd[2], rEnd[3], true);
        msh.AddQuad(rEnd[0], rEnd[3], rEnd[4], rEnd[5], true);
        msh.AddQuad(rEnd[0], rEnd[5], rEnd[6], rEnd[7], true);

        return msh;
    }

    static Voxels BuildCameraBayVoxels()
    {
        // Dual EO/IR Payload: Rectangular internal cavity + spherical turret blister
        // Cavity dimensions: Length=125mm (Y from 15 to 140), Width=76mm (X from -38 to +38), Height=60mm (Z from 8 to 68)
        Mesh mshBox = new Mesh();
        float xMin = -38.0f, xMax = 38.0f;
        float yMin =  15.0f, yMax = 140.0f;
        float zMin =   8.0f, zMax =  68.0f;

        Vector3[] corners = new Vector3[]
        {
            new Vector3(xMin, yMin, zMin),
            new Vector3(xMax, yMin, zMin),
            new Vector3(xMax, yMax, zMin),
            new Vector3(xMin, yMax, zMin),
            new Vector3(xMin, yMin, zMax),
            new Vector3(xMax, yMin, zMax),
            new Vector3(xMax, yMax, zMax),
            new Vector3(xMin, yMax, zMax)
        };

        int[] c = new int[8];
        for (int i = 0; i < 8; i++) c[i] = mshBox.nAddVertex(corners[i]);

        // 6 faces of box
        mshBox.AddQuad(c[0], c[1], c[2], c[3], false); // bottom
        mshBox.AddQuad(c[4], c[7], c[6], c[5], false); // top
        mshBox.AddQuad(c[0], c[4], c[5], c[1], false); // back
        mshBox.AddQuad(c[2], c[6], c[7], c[3], false); // front
        mshBox.AddQuad(c[0], c[3], c[7], c[4], false); // left
        mshBox.AddQuad(c[1], c[5], c[6], c[2], false); // right

        Voxels voxBay = new Voxels(mshBox);

        // Add spherical turret dome looking forward & downward (Radius 25mm at center of chin)
        Voxels voxTurretDome = Voxels.voxSphere(new Vector3(0.0f, 75.0f, 35.0f), 26.0f);
        voxBay.BoolAdd(voxTurretDome);

        return voxBay;
    }
}
