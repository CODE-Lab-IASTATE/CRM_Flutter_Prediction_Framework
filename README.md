# CRM Flutter Prediction Framework

Code to generate open-source analyses of the AGARD 445.6 wing and uCRM-13.5 wing with Andrew Thelen's Flutter Analysis Framework<sup>1</sup>

## Requirements:
 - [ESP/CAPS](https://acdl.mit.edu/ESP) Rev 1.17
 - [MYSTRAN](https://www.mystran.com) Version 6.12
 - [SU2](https://su2code.github.io) Version 6.2.0 "Falcon"
 - Python 2.7
 - numpy Version 1.15.0
 - matplotlib Version 2.2.2

## Introduction:
This repository contains the files and scripts that setup and run forced harmonic simulations on the AGARD 445.6 wing <sup>3</sup> and a version of the uCRM-13.5 wing that was used by Beran et al.<sup>4</sup>. The uCRM-13.5 wing was originally published by the University of Michigan MDO Lab <sup>5,6</sup>. The ESP/CAPS scripts that perform the analyses are heavily influenced by the example "aeroelasticModal\_Fun3D\_and\_Mystran.py". The steps to perform an analysis are outlined below:

1. Use the pyCAPS script to perform the structural analysis, and prepare the SU2 mesh files. A FUN3D modal simulation is also prepared.
2. Use the "Write\_surface\_position.py" script to write the SU2 mesh motion files for the simulation.
3. Update SU2 configuration file according to the desired Mach number and reduced frequency.
4. Run SU2 in series or in parallel for each mode.

## Contents:
The files in this repository fall into a few main categories: (1) pyCAPS analysis scripts, (2) python scripts for transferring FUN3D modal information to SU2 mesh motion files, and (3) input/output files for each analysis.

## Acknowledgements:
This project/material is based upon work supported by the Iowa Space Grant Consortium under NASA Award No. NNX16AL88H.

## References
<sup>1</sup> Thelen, A. S., Leifsson, L. T., and Beran, P. S., "Aeroelastic Flutter Prediction Using Multi-fidelity Modeling of the Aerodynamic Influence Coefficients," *AIAA SciTech Forum*, San Diego, CA, January 7-11, 2019. https://doi.org/doi:10.2514/6.2019-0609. 

<sup>2</sup> Thelen, A., Leifsson, L., and Beran, P., "Multifidelity Flutter Prediction Using Local Corrections to the Generalized AIC," *International Forum on Aeroelasticity and Structural Dynamics (IFASD 2019)*, Savannah, GA, June 10-13, 2019.

<sup>3</sup> Yates, Jr., E. C., "AGARD Standard Aeroelastic Configurations for Dynamic Response I - Wing 445.6." In *AGARD Report No. 765*, 1988.

<sup>4</sup> Beran, P. S., Bryson, D., Thelen, A. S., Diez, M., and Serani, A., "Comparison of Multi-Fidelity Approaches for Military Vehicle Design," *AIAA AVIATION Forum*, Virtual Event, June 15-19, 2020. doi:10.2514/6.2020-3158, URL https://arc.aiaa.org/doi/abs/10.2514/6.2020-3158.

<sup>5</sup>Multidisciplinary Design Optimization Laboratory, "uCRM: undeflected Common Research Model", 2020. URL https://mdolab.engin.umich.edu/wiki/ucrm.html

<sup>6</sup> Brooks, T. R., Kenway, G. K. W., and Martins, J. R. R. A., "Benchmark Aerostructural Models for the Study of Transonic Aircraft Wings," *AIAA Journal,* Vol. 56, No. 7, 2018, pp. 2840-2855. https://doi.org/10.2514/1.j056603.
