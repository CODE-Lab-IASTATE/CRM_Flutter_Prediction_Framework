# this script is using Python version 2.7.15
import numpy as np
import sys,os,subprocess
#import matplotlib.pyplot as plt

analysisDir = 'AeroelasticModal_SU2'


Minf = 0.85  # Mach number corresponding to cruise flight condition for the uCRM-13.5
kred = 0.1  # reduced frequency=omega*b/V (in FUN3D, the nondimensional V is equal to mach number)


gdisp_magnitude = 1.0e-4 #1.e-4
Ncycles = 2
steps_per_cycle = 20

Cref = 11 # For the uCRM-13.5 wing, let this be the approximate dimension of the root chord
b = 0.5*Cref    # reference semichord length
Vref = Minf     # (SU2 probably uses the same nondimensionalization? although it might be dimensional by default)


# what to scale the unit modal displacement by
omega = kred*Vref/b
final_time = Ncycles*2.*np.pi/omega
Nsteps = steps_per_cycle*Ncycles
time_step_size = final_time/Nsteps
time = np.linspace(time_step_size,final_time,Nsteps)
scalingFunction = gdisp_magnitude*np.sin(omega*time)

# Plots the time scaling function
if 0:
    fig = plt.figure()
    plt.plot(time,scalingFunction,'-ok')
    plt.xlabel(r'time')
    plt.ylabel(r'$\eta$')
    plt.title('Scaling function')
    plt.show()

# change mach number in the .cfg file
command = ('sed -i "/^MACH_NUMBER/c MACH_NUMBER= %f" %s/*.cfg' % (Minf,analysisDir))
os.system(command)

# get number of modes
numEigenVector = len(subprocess.check_output(('ls %s/mode*.dat' % analysisDir),shell=True).split('\n')[:-1])

# set up the harmonic simulations
for i in range(numEigenVector):

    newMode = np.loadtxt('%s/mode%.0f.dat' % (analysisDir,i+1))
    if i==0:
        nodeNumbers = newMode[:,3]-1 # fun3d starts from 1, su2 starts from 0

    print('Writing mode %.0f surface files...' % (i+1)); sys.stdout.flush()
    os.system(('mkdir -p %s/Mode%.0f' % (analysisDir,i+1)))
    for j in range(len(scalingFunction)): # write surface position for each time step
        if j<10:
        	f = open(('%s/Mode%.0f/surface_positions_0000%.0f.dat' % (analysisDir,i+1,j)),'w')
        elif j<100:
        	f = open(('%s/Mode%.0f/surface_positions_000%.0f.dat' % (analysisDir,i+1,j)),'w')
        elif j<1000:
		f = open(('%s/Mode%.0f/surface_positions_00%.0f.dat' % (analysisDir,i+1,j)),'w')

        # x-y-z coordinates for the current time step
        XYZ = newMode[:,:3] + scalingFunction[j]*newMode[:,4:]
        for k in range(XYZ.shape[0]):
            f.write('%.0f  %.8e  %.8e  %.8e\n' % (nodeNumbers[k],XYZ[k,0],XYZ[k,1],XYZ[k,2]))
        f.close()
