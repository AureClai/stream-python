[![Join the chat at https://gitter.im/FaradayRF/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/stream-python/community)

<p align="center">
  <img src="https://github.com/AureClai/stream-python/blob/master/img/logo_plus_name.png" width=256 height=256/>
</p>

<h1 align="center">Simulateur de trafic mésoscopique événementiel open-source</h1>

Ce dossier est basé sur un _fork_ d'un projet du [Cerema](https://cerema.fr)
https://gitlab.cerema.fr/Stream/stream-python

_Read this in other languages:_ _[English](https://github.com/AureClai/stream-python/blob/master/README.en.md)_

## Sommaire

- [Qu'est ce que Stream ?](#qu'est-ce-que-stream)
- [Principales fonctionnalités](#principales-fonctionnalites)
- [Contact](#contact)
- [Installation](#installation)
- [Utilisation](#utilisation)
  - [Utilisation en ligne de commande](#utilisation-en-ligne-de-commande)
  - [Utilisation dans des scripts](#Utilisation-dans-des-scripts)
  - [Utiliser QStream pour concevoir des scénarios](#utiliser-qstream-pour-concevoir-des-scenarios)
- [Bugs](#bugs)
- [License](#license)
- [TODO](#todo)

## Qu'est ce que Stream ?

Stream est un outil de simulation mésoscopique du trafic routier, c'est-à-dire un outil dont le niveau de résolution est intermédiaire aux niveaux microscopique et macroscopique. Il considère également des véhicules plutôt qu'un flux, mais se contente de calculer les dates de passage des véhicules aux noeuds du réseau routier, plutôt que de calculer toutes ses positions à pas de temps fixe.
Les avantages de cette méthode de résolution sont (i) les temps de calculs amoindris par rapport au microscopique, (ii) un nombre réduit de paramètres au sens physique clair facilitant la démarche de paramétrage de l'outil par rapport au microscopique, (iii) une grande diversité de cas d'usage bien moins restrictifs que le macroscopique.

## Principales fonctionnalités

- Coeur de calcul mesoscopique événementiel
- Affectation **statique** en amont et au plus cours chemin
- Gestion limitée \* de différentes classes de véhicules
- Gestion de noeuds complexes
- Gestion des carrefour à feux
- Gestion des voies spécifiques (voies réservées et auxiliaires)
- Régulation dynamique en cours de simulation

## Contact

La principale contribution est réalisée par la Direction Départemental Centre-Est du Cerema. En cas de question, veuillez envoyer un mail à l'adresse suivante :
aurelien.clairais@cerema.fr

## Installation

Stream est fonctionnel sous [Anaconda](https://www.anaconda.com/distribution/) pour Python 3.7.
Avec Anaconda, l'utilisation d'[environments virtuels](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) est recommandé :

```
$ conda create --name myenv
$ conda activate myenv
```

L'installation se fait via un clône du répertoire suivit d'une installation du package avec `pip`.

### 1. Cloner le répertoire

```console
$ git clone https://github.com/AureClai/stream-python
$ cd stream-python
```

### 2. _(facultatif)_ Changer de branche (si développement sur autre branche que _master_)

```console
$ git checkout la_branche
```

### 3. Installer

```console
$ pip install .
```

## Utilisation

### Utilisation en ligne de commande

```
$ cd path_to_input_ny/
$ python -m file_of_inputs.npy
```

A partir d'ici, un nouveau dossier `result` a été créé avec les résultats de la simulation associés à la date et l'heure au format `.npy`.

### Utilisation via un script python

```python
from stream.main import run_simulation_from_inputs
import numpy as np

# Importer le fichier d'entrées
Inputs = np.load("chemin_vers_le_fichier_inputs.npy", allow_pickle=True).item()
Simulation = run_simulation_from_inputs(Inputs)
```

Ici, les résultats sont créé sous la forme d'un dictionnaire dans la variable `Simulation`.

### Utiliser QStream pour concevoir des scénarios

L'extension QGIS https://gitlab.cerema.fr/Stream/qstream permet :

- la définiton de scénarios
- des fonctionnalités d'analyse

### Exemple

Pour lancer le fichier d'exemple dans le dossier `stream-python` via la console de commande :

```console
$ cd example
$ python -m inputs.npy
```

ou via un script Python :

```python
from stream.main import run_simulation_from_inputs
import numpy as np

# Importer le fichier d'entrées
Inputs = np.load("inputs.npy", allow_pickle=True).item()
Simulation = run_simulation_from_inputs(Inputs)
```

## Bugs

Pas de bugs connus. Si vous êtes témoins d'un bug, merci d'ouvrir une ["_issue_"](https://github.com/AureClai/stream-python/issues/new).

## License

[Cecill-B](http://www.cecill.info/licences/Licence_CeCILL-B_V1-fr.html).

## TODO

1. Implémentation d'outils de visualisation avec la librairies Python `dash` de Plotly
2. Gestion de capacité variables en sortie de réseau
3. Plusieurs modes d'affectation
4. Régulation dynamique des vitesses
5. Régulation d'accès
6. Gestion d'autres types de fomat d'entrées/sorties
