# CTSP_d

Code and instances to reproduce the experiments presented in the paper 
[*Formulations for the clustered traveling salesman problem with d-relaxed priority rule*](https://doi.org/10.1016/j.cor.2023.106402), by Teixeira and de Araujo (2024). 

**Note:** This is not the original version of the code, but a refactored one, 
easier to use and with no known bugs (except erros/bad behaviours caused by 
bad input values - at this moment we are not validating them).

# Requirements

The initial version of the code was developed using:

* Linux Ubuntu 20.04;
* Python 3.10;
* Gurobipy 9.5.

The present code, which is almost the same as the original one, was tested with
the following setup:

* Microsoft Windows 11;
* Python 3.12.10;
* Gurobipy 12.0.1.

The code is still not tested on a Mac OS, but since there is no OS specific
parts in the code, it should work fine in this case too.

Different versions of Python 3 and Gurobipy superior to Python 3.10 and
Gurobipy 9.5 are supposed to work with no problems. 

**Important:** Make sure to have a valid Gurobi license before trying to run 
the code.

# Usage

## The main script

Users can run the tests by calling the file `main.py`, where the whole loop of reading the data, build the models, call the solver and export the solution is ready to use.

To set up data and parameters, users should input data in the `UserInputs.py` file, which is described in details below.

## The UserInputs script

The data and parameters to be considered just need to be set in the file `UserInputs.py`. In summary, the parameters can be defined as below:

1. `GUROBI_PARAMETERS` (`dict`): Are passed direct to Gurobi to set some common parameters needed to control the solving process. 
   * `MAX_RUNTIME` (`float`): Maximum runtime parameter passed to Gurobi, set in seconds. Values must be greater then zero.
   *  `PRINT_LOG` (`bool`): Used to turn on/off the solver log printing functionality.

2. `EXPORT_SOLUTION_PARAMETERS` (`dict`): Used to control if solutions will be exported after being obtained.
    * `EXPORT_SOLUTION` (`bool`): Control if solutions will or won't be exported.
    * `DATETIME_ON_FILENAME` (`bool`): Allow to include a date-based information in the exported file name. Useful to not overwrite already existing solution files.

3. `USE_SOLVED_INSTANCES_LIST` (`bool`): Allow users to save the name of the solved instances in a text file as the solving process occurs. Useful to avoid losses in case of computer crashes. The list is then used to continue the solving process ignoring the already solved instances when the user run the script again.

4. `SOLUTION LOG LEVEL` (`int`): Control how much information about the solution process will be displayed on the terminal. This is not the Gurobi log, but short descriptions about the steps being executed in the solution process. Values must be between 0 and 4, where 0 means no information being printed, and 4 means to print informations about each step took.

5. `MODELS_LIST` (`list`[`str`]): List of models that will be used in the experiments, represented by the aliases proposed in the paper (MTZ1, MTZ2, GP1, etc).

6. `INSTANCES_LIST` (`list`[`str`]): List of instances that must be solved after calling the `main.py` file. Instances can be hardcoded one by one, or using the auxiliary functions in `InstancesUtils.py`.

# About the data

First, it is important to highlight: **I'm not the owner of the data**. The original data files are in a general text file format and can be found at [ORLab Site](https://orlab.com.vn/materials/).

In this repository, we are working with a **.json** version of them, which can be directly imported and so do not demand any extra tools to process the data. The scripts used to convert the instances were not included in the repository.

# Future Improvements

The main goal of this project is to allow researchers and students to reproduce the experiments in the paper "*Formulations for the clustered traveling salesman problem with d-relaxed priority rule*", as described above, and this goal is already being accomplished.

Some improvements are planned for the future, including code refactoring and the addition of some features to allow to reproduce the data tables and figures on the paper.

If you want to collaborate with these developments, there are a few standards to be observed on new code:

* Avoid using unnecessary external modules. For instance, if you need to manage **.csv** files, prefer using the native `csv` module instead of importing `pandas` or something similar;
* New models and experiments are a promising and interesting research field. But here we are focused in offer the tools to reproduce a paper and not in developing new ideas. So, new models and solution approaches should be developed in a new repository.

# Contact

Critics or suggestions can be sent directly to the e-mail [eduardo281.dev@gmail.com](mailto:eduardo281.dev@gmail.com).

Ideas on how to improve the code or the documentation are also welcome!
