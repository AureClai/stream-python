[![Join the chat at https://gitter.im/FaradayRF/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/FaradayRF/Lobby?utm_source=badge&utm_medium=badge&utm_content=badge)

<p align="center">
  <img src="https://github.com/AureClai/stream-python/blob/master/img/logo_plus_name.png" width=256 height=256/>
</p>

<h1 align="center">Simulateur de trafic mésoscopique événementiel open-source</h1>

Ce dossier est basé sur un _fork_ d'un projet du [Cerema](https://cerema.fr)
https://gitlab.cerema.fr/Stream/stream-python

_Read this in other languages:_ _[Ensglish](https://github.com/AureClai/stream-python/blob/master/README.md)_, _[French](https://github.com/AureClai/stream-python/blob/master/README.fr.md)_

## Sommaire

- [Qu'est ce que Stream ?](#qu'est-ce-que-stream)
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

## Qu'est ce que Stream ?

Stream est un outil de simulation mésoscopique du trafic routier, c'est-à-dire un outil dont le niveau de résolution est intermédiaire aux niveaux microscopique et macroscopique. Il considère également des véhicules plutôt qu'un flux, mais se contente de calculer les dates de passage des véhicules aux noeuds du réseau routier, plutôt que de calculer toutes ses positions à pas de temps fixe.
Les avantages de cette méthode de résolution sont (i) les temps de calculs amoindris par rapport au microscopique, (ii) un nombre réduit de paramètres au sens physique clair facilitant la démarche de paramétrage de l'outil par rapport au microscopique, (iii) une grande diversité de cas d'usage bien moins restrictifs que le macroscopique.

## Principales fonctionnalités

1. Lecture de scénario depuis des fichiers `.npy`
2. Affectation au plus court chemin
3. Simulation méscoscopique événementielle
4. Implémentation des voies réservées

## Contact

aurelien.clairais@cerema.fr

## Installation

Stream est fonctionnel sous [Anaconda](https://www.anaconda.com/distribution/) pour Python 3.7.
Avec Anaconda, l'utilisation d'[environments virtuels](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) est recommandé :

```
$ conda create --name myenv
$ conda activate myenv
```

L'installation se fait via un clône du répertoire suivit d'une installation du package avec `pip` :

```console
$ git clone https://github.com/AureClai/stream-python
$ cd stream-python
$ pip install .
```

## Utilisation

### Utilisation en ligne de commande

Pour cette version : **tester seulement avec l'exemple** dans le dossier `example`.

```
$ cd path_to_example_directory/
$ python -m stream inputs.npy
```

A partir d'ici, un nouveau dossier `result` a été créé avec les résultats de la simulation associés à la date et l'heure au format `.npy`.

### Utilisation dans des scripts

Importer les fonctions et les utiliser (voir le code source et/ou la documentation).

TODO : Ecrire la documentation

### Utiliser QStream pour concevoir des scénarios

(**Windows Seulement**)

L'extension QGIS https://gitlab.cerema.fr/Stream/qstream (**Windows Only**) permet :

- la définiton de scénarios
- des fonctionnalités d'analyse

## Bugs

Pas de bugs connus. Si vous voyez quoique ce soit, merci d'ouvrir une "_issue_".

## License

[Cecill-B](http://www.cecill.info/licences/Licence_CeCILL-B_V1-fr.html).

## TODO

(section dev en anglais)

1. Implement `bokeh`-based dashboard for result analysis
2. Variable flows at exits
3. Moddable affectation module
4. Dynamical Speed Regulation
5. On-ramp regulation
6. Other format for in and out (JSON, XML, etc...)
