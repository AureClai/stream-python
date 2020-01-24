# Stream - Mesoscopic event-based open-source traffic simulator

## What is **Stream** ?

Here is just a fork from an original project from CEREMA.
Read the description (FR) in the original repo : https://gitlab.cerema.fr

## Main Features

1. Scenario reading from `.npy` file
2. Shortest path affectation
3. Mesoscopic event-based Simulation
4. Managed lane regulation implementation

## Contact

aurelien.clairais@cerema.fr/Stream/stream-python

## Installation

Stream works well with [Anaconda](https://www.anaconda.com/distribution/) for Python 3.7.
With Anaconda, the use of [virtual environnments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) is recommended :

```
$ conda create --name myenv
$ conda activate myenv
```

```console
$ git clone https://github.com/AureClai/stream-python
$ cd stream-python
$ pip install .
```

## Use

For this version : **test only with the provided examples** in `example`directory.

```
$ cd path_to_example_directory/
$ python -m stream inputs.npy
```

From now, a new directory `result` has been created with the result of the simulation with date and time.
To launch the analysis of the newly acquired results :

```console
$ python analysis_example.py path_to_the_results_npy_file
```

The program create an output `.npy` simulation file.

### Use QStream for better experience (**Windows Only**)

The QGIS plugin at https://gitlab.cerema.fr/Stream/qstream (**Windows Only**) provides :

- Scenario definition
- Analysis features

## Bugs

???

## License

[Cecill-B](http://www.cecill.info/licences/Licence_CeCILL-B_V1-fr.html).

## TODO

1. Implement `bokeh`-based dashboard for result analysis
2. Variable flows at exits
3. Moddable affectation module
4. Dynamical Speed Regulation
5. On-ramp regulation
6. Other format for I/O (JSON, XML, etc...)
