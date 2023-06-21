_[:us:](https://github.com/AureClai/stream-python/blob/master/README.md)_ _[:fr:](https://github.com/AureClai/stream-python/blob/master/README.fr.md)_ _[:es:](https://github.com/AureClai/stream-python/blob/master/README.es.md)_ _[:cn:](https://github.com/AureClai/stream-python/blob/master/README.cn.md)_
_[:jp:](https://github.com/AureClai/stream-python/blob/master/README.jp.md)_ _[:portugal:](https://github.com/AureClai/stream-python/blob/master/README.pt.md)_

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/Naereen/badges/)
[![Join the chat at https://gitter.im/FaradayRF/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/stream-python/community)

<p align="center">
  <img src="https://github.com/AureClai/stream-python/blob/master/img/logo_plus_name.png" width=256 height=256/>
</p>

<h1 align="center">Event-Based Mesoscopic Traffic Simulator</h1>

## What is Stream?

Stream is a mesoscopic traffic simulation tool, that is, a tool whose level of resolution is intermediate between microscopic and macroscopic levels. It also considers vehicles rather than a flow, but merely calculates the passing times of vehicles at the nodes of the road network, rather than calculating all its positions at fixed time steps.
The advantages of this resolution method are (i) reduced computing times compared to microscopic, (ii) a reduced number of parameters with clear physical meaning facilitating the parameterization process compared to microscopic, (iii) a wide diversity of use cases far less restrictive than the macroscopic one.

## Main Features

- Event-based mesoscopic calculation core
- Upstream and shortest path **static** assignment
- Limited management * of different vehicle classes
- Complex node management
- Traffic light intersection management
- Specific lane management (reserved and auxiliary lanes)
- Dynamic regulation during simulation

## Contact

The main contribution is made by the Cerema East-Central Department. If you have any questions, please send an email to the following address: aurelien.clairais@cerema.fr

## Installation

Stream works under [Anaconda](https://www.anaconda.com/distribution/) for Python 3.9.
With Anaconda, the use of [virtual environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) is recommended:

```console
$ conda create --name myenv
$ conda activate myenv
```

The installation is done via cloning the directory followed by installing the package with `pip`.

### 1. Clone the Directory

```console
$ git clone https://github.com/AureClai/stream-python
$ cd stream-python
```

### 2. _(optional)_ Switch Branch (if developing on a branch other than _master_)

```console
$ git checkout the_branch
```

### 3. Install

```console
$ pip install .
```

## Usage

### Command Line Usage

```console
$ stream -i file_of_inputs.npy
```

From here, a new `result` folder has been created in the folder containing the input file with the simulation results associated with the date and time in `.npy` format. If a results folder has been pointed (see `stream --help` on command line), the results will be saved in this folder.

### Usage via a Python Script

```python
from stream.main import run_simulation_from_inputs
import numpy as np

# Import the input file
Inputs = np.load("path_to_the_inputs_file.npy", allow_pickle=True).item()
Simulation = run_simulation_from_inputs(Inputs)
```

Here, the results are created in the form of a dictionary in the `Simulation` variable.

### Usage via the Graphic Interface

```console
$ stream-gui
```

## Use QStream to Design Scenarios

The QGIS extension https://gitlab.cerema.fr/Stream/qstream allows:

- scenario definition
- analysis features

## Bugs

No known bugs. If you witness a bug, please open an ["_issue_"](https://github.com/AureClai/stream-python/issues/new).

## License

[Cecill-B](http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html).

## TODO

1. Implementation of visualization tools with the Python `dash` library from Plotly
2. Management of variable output capacity
3. Several assignment modes
4. Dynamic speed regulation
5. Access regulation
6. Management of other types of input/output formats
