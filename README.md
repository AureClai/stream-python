[![Join the chat at https://gitter.im/FaradayRF/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/stream-python/community)
<p align="center">
  <img src="https://github.com/AureClai/stream-python/blob/master/img/logo_plus_name.png" width=256 height=256/>
</p>

<h1 align="center">Mesoscopic event-based open-source traffic simulator</h1>

This repository is based on a fork from a project from the [Cerema](https://cerema.fr).
https://gitlab.cerema.fr/Stream/stream-python

_Read this in other languages:_ _[English](https://github.com/AureClai/stream-python/blob/master/README.md)_, _[French](https://github.com/AureClai/stream-python/blob/master/README.fr.md)_

## Table of Contents

- [What is Stream ?](#what-is-stream)
- [Main features](#main-features)
- [Contact](#contact)
- [Installation](#installation)
- [Use](#use)
  - [Use in command line](#use-in-command-line)
  - [Use in scripts](#use-in-scripts)
  - [Use QStream for scenario design](#use-qstream-for-scenario-design)
- [Bugs](#bugs)
- [License](#license)
- [TODO](#todo)

## What is Stream ?

Stream is mesoscopic road traffic simulation tool, that is that the scale of resolution is an intermediary to the microscopic and macroscopic scales. It processes vehicles instead of flows. It only calculates the passing times of the vehicles at the nodes of the network instead of calculating every position with a fixed time step. The pros of this method of resolution are that (i) the calculatation times are less than with a microscopic resolution, (ii) a smaller number of parameters with a clear physical sens easing the calibration of the model compared to the microscopic, (iii) a great diversity of applications with less restrictions than the macroscopic resolution.

## Main Features

1. Scenario reading from `.npy` file
2. Shortest path affectation
3. Mesoscopic event-based Simulation
4. Managed lane regulation implementation

## Contact

aurelien.clairais@cerema.fr

## Installation

Stream works well with [Anaconda](https://www.anaconda.com/distribution/) for Python 3.7.
With Anaconda, the use of [virtual environnments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) is recommended :

```
$ conda create --name myenv
$ conda activate myenv
```

The installation is made via clonning the directory followed by an installation with `pip` :

```console
$ git clone https://github.com/AureClai/stream-python
$ cd stream-python
$ pip install .
```

## Use

### Use in command line

For this version : **test only with the provided examples** in `example`directory.

```
$ cd path_to_example_directory/
$ python -m stream inputs.npy
```

From now, a new directory `result` has been created with the result of the simulation with date and time with the `.npy` extension.

### Use in scripts

Import the functions and use it (see source code and/or documentation).

TODO : write the documentation for use in scripts

### Use QStream for scenario design

(**Windows Only**)

The QGIS plugin at https://gitlab.cerema.fr/Stream/qstream (**Windows Only**) provides :

- Scenario definition
- Analysis features

## Bugs

No known bugs. Please write an issue if you see anything.

## License

[Cecill-B](http://www.cecill.info/licences/Licence_CeCILL-B_V1-fr.html).

## TODO

1. Implement `bokeh`-based dashboard for result analysis
2. Variable flows at exits
3. Moddable affectation module
4. Dynamical Speed Regulation
5. On-ramp regulation
6. Other format for in and out (JSON, XML, etc...)
