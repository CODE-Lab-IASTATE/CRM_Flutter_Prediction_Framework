# Authors: Andrew Thelen and Brandon Crow
# Description:
#   This file is intended to be used as to generate steady CFD simulation cases for the AGARD wing.

import sys,os
import numpy as np



def main():
    from pyCAPS import capsProblem
    projectName = 'aeroelastic'
    workDir = 'AGARD'

    # load the geometry
    myProblem = capsProblem()

    # Import geometry
    myProblem.loadCAPS("./AGARD445_DataTransfer.csm")

    # load aims
    aflr4 = myProblem.loadAIM(aim = "aflr4AIM",
                              altName = "aflr4",
                              analysisDir = workDir + "_SU2_Steady")

    myProblem.loadAIM(aim = "tetgenAIM",
                      altName = "tetgen_su2",
                      analysisDir = workDir + "_SU2_Steady",
                      capsIntent = "CFD",
                      parents = aflr4.aimName)

    myProblem.loadAIM(aim = "su2AIM",
                      altName = "su2",
                      analysisDir = workDir + "_SU2_Steady",
                      parents = ["tetgen_su2"],
                      capsIntent = "CFD")

    # arbitrary aero settings
    aero = {"machNumber": 0.8,
            "Alpha":0.0,
            "density": 1.225,           # kg/m^3
            "temperature": 30+273.15}   # Kelvin
    aero["soundSpeed"] = np.sqrt(1.4*287.15*aero["temperature"])    # m/s
    aero["velocity"] = aero["machNumber"]*aero["soundSpeed"]        # m/s
    aero["dynamicPressure"] = 0.5*aero["density"]*aero["velocity"]**2.

    # AFLR4 Surface Mesh Settings
    aflr4.setAnalysisVal("Proj_Name", "AFLR4_Mesh")
    aflr4.setAnalysisVal("Mesh_ASCII_Flag", True)
    aflr4.setAnalysisVal("Mesh_Format", "Tecplot")
    aflr4.setAnalysisVal("ff_nseg",20)
    aflr4.setAnalysisVal("max_scale", 1)
    aflr4.setAnalysisVal("min_scale",0.7)
    aflr4.setAnalysisVal("Mesh_Sizing",[("Skin", {"edgeWeight":0.1,"scaleFactor":0.02, "bcType":"STD_UG3_GBC"}),
                                        ("SymmPlane", {"AFLR_Edge_Scale_Factor_Weight":0.4, "scaleFactor":5})])

    # Generate Surface Mesh
    aflr4.preAnalysis()
    aflr4.postAnalysis()
    
    
    # mesh settings (first parameter was 0.01)
    myProblem.analysis["tetgen_su2"].setAnalysisVal("Tess_Params", [.00005, 0.00001, 20.0])
    myProblem.analysis["tetgen_su2"].setAnalysisVal("Preserve_Surf_Mesh", True)


    # prepare su2 case
    prepSu2(myProblem,projectName,aero)


    # close the problem
    myProblem.closeCAPS()

    return


def prepSu2(myProblem,projectName,aero):

    # su2 inputs
    myProblem.analysis["su2"].setAnalysisVal("Proj_Name", projectName)
    myProblem.analysis["su2"].setAnalysisVal("SU2_Version", "Falcon") # "Falcon", "Raven"
    myProblem.analysis["su2"].setAnalysisVal("Mach", aero["machNumber"])
    myProblem.analysis["su2"].setAnalysisVal("Alpha", aero["Alpha"])
    myProblem.analysis["su2"].setAnalysisVal("Equation_Type","compressible")
    myProblem.analysis["su2"].setAnalysisVal("Num_Iter",1000) # Way too few to converge the solver, but this is an example
    myProblem.analysis["su2"].setAnalysisVal("Residual_Reduction",6)
    myProblem.analysis["su2"].setAnalysisVal("Output_Format", "Tecplot")
    myProblem.analysis["su2"].setAnalysisVal("Overwrite_CFG", True)
    myProblem.analysis["su2"].setAnalysisVal("Pressure_Scale_Factor",aero["dynamicPressure"])
    myProblem.analysis["su2"].setAnalysisVal("Surface_Monitor", "Skin")

    inviscid = {"bcType" : "Inviscid"}
    myProblem.analysis["su2"].setAnalysisVal("Boundary_Condition", [("Skin", inviscid),
                                                                    ("SymmPlane", "SymmetryY"),
                                                                    ("Farfield","farfield")])

    # Run pre/post-analysis for tetgen
    myProblem.analysis["tetgen_su2"].preAnalysis()
    myProblem.analysis["tetgen_su2"].postAnalysis()

    # Run su2 pre-analysis
    myProblem.analysis["su2"].preAnalysis()

    return



if __name__ == "__main__":
    main()

