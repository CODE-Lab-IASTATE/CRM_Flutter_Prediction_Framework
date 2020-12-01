# Authors: Andrew Thelen and Brandon Crow
# Description:
# 	This python script is almost the exact same as the "aeroelasticModal_mystranFun3dSu2.py"
#	script that Andrew uploaded to CyBox in the 
#	"/CODELab/software/codes/Andrew/pyCAPS_SU2_prescribed_motion" directory. Brandon added onto
#	that in order to use AFLR4 to do the surface meshing for the AGARD wing. Another difference #	is that Brandon created the AGARD geometry and changed the Mystran parameters to match the #	values found in Andrew's PhD Thesis.


import sys,os
import numpy as np



def main(numEigenVector):
    from pyCAPS import capsProblem
    projectName = 'aeroelastic'
    workDir = 'AeroelasticModal'

    # load the geometry
    myProblem = capsProblem()

    # Import geometry
    myProblem.loadCAPS("./AGARD445_DataTransfer.csm")

    # load aims
    aflr4 = myProblem.loadAIM(aim = "aflr4AIM",
                              altName = "aflr4",
                              analysisDir = workDir + "_FUN3D")

    myProblem.loadAIM(aim = "tetgenAIM",
                      altName = "tetgen_su2",
                      analysisDir = workDir + "_SU2",
                      capsIntent = "CFD",
                      parents = aflr4.aimName)
    
    myProblem.loadAIM(aim = "tetgenAIM",
                      altName = "tetgen_fun3d",
                      analysisDir = workDir + "_FUN3D",
                      capsIntent = "CFD",
                      parents = aflr4.aimName)

    myProblem.loadAIM(aim = "mystranAIM",
                  altName = "mystran_modal",
                  analysisDir = workDir + "_MYSTRAN",
                  capsIntent = "STRUCTURE")
    myProblem.loadAIM(aim = "su2AIM",
                  altName = "su2",
                  analysisDir = workDir + "_SU2",
                  parents = ["tetgen_su2"],
                  capsIntent = "CFD")
    myProblem.loadAIM(aim = "fun3dAIM",
                  altName = "fun3d",
                  analysisDir = workDir + "_FUN3D",
                  parents = ["tetgen_fun3d"],
                  capsIntent = "CFD")

    # arbitrary aero settings
    aero = {"machNumber": 0.8,
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
    aflr4.setAnalysisVal("max_scale", 0.5)
    aflr4.setAnalysisVal("min_scale",0.2)
    aflr4.setAnalysisVal("Mesh_Sizing",[("Skin", {"edgeWeight":0.1,"scaleFactor":0.02, "bcType":"STD_UG3_GBC"}),
                                        ("SymmPlane", {"AFLR_Edge_Scale_Factor_Weight":0.4, "scaleFactor":5})])

    # Generate Surface Mesh
    aflr4.preAnalysis()
    aflr4.postAnalysis()
    
    
    # mesh settings (first parameter was 0.01)
    myProblem.analysis["tetgen_fun3d"].setAnalysisVal("Tess_Params", [.00005, 0.00001, 20.0])
    myProblem.analysis["tetgen_fun3d"].setAnalysisVal("Preserve_Surf_Mesh", True)
    myProblem.analysis["tetgen_su2"].setAnalysisVal("Tess_Params", [.00005, 0.00001, 20.0])
    myProblem.analysis["tetgen_su2"].setAnalysisVal("Preserve_Surf_Mesh", True)

    
    # prepare fun3d case
    prepFun3d(myProblem,projectName,aero,numEigenVector)

    # prepare su2 case
    prepSu2(myProblem,projectName,aero)

    # get mode shapes mapped to su2 surface grid
    getSu2modes(myProblem,projectName,numEigenVector)

    # close the problem
    myProblem.closeCAPS()

    return



def prepFun3d(myProblem,projectName,aero,numEigenVector):

    eigen = { "extractionMethod"     : "Lanczos",   
              "frequencyRange"       : [0, 200],
              "numEstEigenvalue"     : 1,
              "numDesiredEigenvalue" : numEigenVector,
              "eigenNormaliztion"    : "MASS"}

    # (see dissertation/IFASD paper for "calibrated" youngModulus, density, skin membraneThickness, etc.)
    madeupium = {"materialType" : "isotropic",
		 "shearModulus" : 8.31E7 ,
                 "youngModulus" : 5.34E8 ,
                 "poissonRatio": 0.31,
                 "density" : 147}

    skin  = {"propertyType" : "Shell",
             "membraneThickness" : 0.0165,
             "material"        : "madeupium"}

    ribSpar  = {"propertyType" : "Shell",
                "membraneThickness" : 0.00005,
                "material"        : "madeupium"}

    constraint = {"groupName" : "Rib_Root",
                  "dofConstraint" : 123456}

    inviscid = {"bcType": "Inviscid"}

    transfers = ["Skin_Top", "Skin_Bottom", "Skin_Tip"]
    #transfers = ["Skin_Bottom", "Skin_Top", "Skin_Tip"]
	
    eigenVector = []
    for i in range(numEigenVector):
        eigenVector.append("EigenVector_" + str(i+1))
    for i in transfers:
        myProblem.createDataTransfer(variableName = eigenVector,
                                     aimSrc = ["mystran_modal"]*len(eigenVector),
                                     aimDest =["fun3d"]*len(eigenVector),
                                     capsBound = i)

    # fun3d inputs
    myProblem.analysis["fun3d"].setAnalysisVal("Proj_Name", projectName)
    myProblem.analysis["fun3d"].setAnalysisVal("Mesh_ASCII_Flag", False)
    myProblem.analysis["fun3d"].setAnalysisVal("Mach", aero["machNumber"])
    myProblem.analysis["fun3d"].setAnalysisVal("Equation_Type","compressible")
    myProblem.analysis["fun3d"].setAnalysisVal("Viscous", "inviscid")
    myProblem.analysis["fun3d"].setAnalysisVal("Num_Iter",10)
    myProblem.analysis["fun3d"].setAnalysisVal("Time_Accuracy","2ndorderOPT")
    myProblem.analysis["fun3d"].setAnalysisVal("Time_Step",0.001*aero["soundSpeed"])
    myProblem.analysis["fun3d"].setAnalysisVal("Num_Subiter", 30)
    myProblem.analysis["fun3d"].setAnalysisVal("Temporal_Error",0.01)
    myProblem.analysis["fun3d"].setAnalysisVal("CFL_Schedule",[1, 5.0])
    myProblem.analysis["fun3d"].setAnalysisVal("CFL_Schedule_Iter", [1, 40])
    myProblem.analysis["fun3d"].setAnalysisVal("Overwrite_NML", True)
    myProblem.analysis["fun3d"].setAnalysisVal("Restart_Read","off")
    myProblem.analysis["fun3d"].setAnalysisVal("Boundary_Condition", [("Skin", inviscid),
                                                ("SymmPlane", "SymmetryY"),
                                                ("Farfield","farfield")])

    # mystran inputs
    myProblem.analysis["mystran_modal"].setAnalysisVal("Proj_Name", projectName)
    myProblem.analysis["mystran_modal"].setAnalysisVal("Edge_Point_Max", 25)
    myProblem.analysis["mystran_modal"].setAnalysisVal("Quad_Mesh", True)
    myProblem.analysis["mystran_modal"].setAnalysisVal("Tess_Params", [.010, .1, 15]) # old values were [.060, 0.1, 15]
    myProblem.analysis["mystran_modal"].setAnalysisVal("Analysis_Type", "Modal");
    myProblem.analysis["mystran_modal"].setAnalysisVal("Analysis", ("EigenAnalysis", eigen))
    myProblem.analysis["mystran_modal"].setAnalysisVal("Material", ("Madeupium", madeupium))
    myProblem.analysis["mystran_modal"].setAnalysisVal("Property", [("Skin", skin), ("Rib_Root", ribSpar)])
    myProblem.analysis["mystran_modal"].setAnalysisVal("Constraint", ("edgeConstraint", constraint))
    
    # Run pre/post-analysis for tetgen
    myProblem.analysis["tetgen_fun3d"].preAnalysis()
    myProblem.analysis["tetgen_fun3d"].postAnalysis()
    
    # Populate vertex sets in the bounds after the mesh generation is completed
    for j in transfers:
        myProblem.dataBound[j].fillVertexSets()
    
    # Run pre/post-analysis for mystran and execute
    myProblem.analysis["mystran_modal"].preAnalysis()
    
    # Run mystran
    print("\n\nRunning Mystran......")
    currentDirectory = os.getcwd() # Get our current working directory 
    os.chdir(myProblem.analysis["mystran_modal"].analysisDir) # Move into test directory
    os.system("mystran.exe " + projectName +  ".dat > Info.out") # Run fun3d via system call
    
    if os.path.getsize("Info.out") == 0: # 
        print("Mystran excution possibly failed\n")
        myProblem.closeCAPS()
    
    os.chdir(currentDirectory) # Move back to top directory 
    
    # Run AIM post-analysis
    myProblem.analysis["mystran_modal"].postAnalysis()
    
    # Execute the dataTransfer
    print("\nExecuting dataTransfer ......")
    for j in transfers:
        for eigenName in eigenVector:
            myProblem.dataBound[j].executeTransfer(eigenName)
            #myProblem.dataBound[j].dataSetSrc[eigenName].viewData()
            #myProblem.dataBound[j].viewData()
        #myProblem.dataBound[j].writeTecplot(myProblem.analysis[i].analysisDir + "/Data")
    
    # Retrive natural frequencies from the structural analysis
    naturalFreq = myProblem.analysis["mystran_modal"].getAnalysisOutVal("EigenRadian") # rads/s
    mass = myProblem.analysis["mystran_modal"].getAnalysisOutVal("EigenGeneralMass")
    
    modalTuple = [] # Build up Modal Aeroelastic tuple  
    for j in eigenVector:
        modeNum = int(j.strip("EigenVector_"))
        value = {"frequency" : naturalFreq[modeNum-1],
                 "damping" : 0.99,
                 "generalMass" : mass[modeNum-1],
                 "generalVelocity" : 0.1}
        modalTuple.append((j,value))
    
    # Add Eigen information in fun3d     
    myProblem.analysis["fun3d"].setAnalysisVal("Modal_Aeroelastic", modalTuple)
    myProblem.analysis["fun3d"].setAnalysisVal("Modal_Ref_Velocity", aero["velocity"])
    myProblem.analysis["fun3d"].setAnalysisVal("Modal_Ref_Dynamic_Pressure", aero["dynamicPressure"])
    myProblem.analysis["fun3d"].setAnalysisVal("Modal_Ref_Length", 1.0)
    
    # Run the preAnalysis 
    myProblem.analysis["fun3d"].preAnalysis()

    return



def prepSu2(myProblem,projectName,aero):

    # su2 inputs
    myProblem.analysis["su2"].setAnalysisVal("Proj_Name", projectName)
    myProblem.analysis["su2"].setAnalysisVal("SU2_Version", "Falcon") # "Falcon", "Raven"
    myProblem.analysis["su2"].setAnalysisVal("Mach", aero["machNumber"])
    myProblem.analysis["su2"].setAnalysisVal("Equation_Type","compressible")
    myProblem.analysis["su2"].setAnalysisVal("Num_Iter",5) # Way too few to converge the solver, but this is an example
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



def getSu2modes(myProblem,projectName,numEigenVector):
    import subprocess

    # there are cleaner ways to do this, but grep returns each line containing "i=", while "|" pipes output into sed commands
    # (the first removes i= and everything before, while the second removes everything after the first comma)
    Nnodes = int(subprocess.check_output(('grep "i=" %s/%s_body1_mode1.dat | sed "s/.*i=//g" | sed "s/,.*//g"' %
             (myProblem.analysis["fun3d"].analysisDir,projectName)),shell=True))

    # get nodal information for each mode
    for i in range(numEigenVector):
        fun3dDir = myProblem.analysis["fun3d"].analysisDir
        su2Dir = myProblem.analysis["su2"].analysisDir
        modeFile = ('%s/%s_body1_mode%.0f.dat' % (fun3dDir,projectName,i+1))
        command = ('sed -n "%.0f,%.0fp" %s > %s/mode%.0f.dat' % (4,Nnodes+3,modeFile,su2Dir,i+1))
        os.system(command)

    return



if __name__ == "__main__":
    numEigenVector = int(sys.argv[1])
    main(numEigenVector)

