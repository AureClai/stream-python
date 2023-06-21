_[:us:](https://github.com/AureClai/stream-python/blob/master/README.md)_ _[:fr:](https://github.com/AureClai/stream-python/blob/master/README.fr.md)_ _[:es:](https://github.com/AureClai/stream-python/blob/master/README.es.md)_ _[:cn:](https://github.com/AureClai/stream-python/blob/master/README.cn.md)_
_[:jp:](https://github.com/AureClai/stream-python/blob/master/README.jp.md)_ _[:portugal:](https://github.com/AureClai/stream-python/blob/master/README.pt.md)_

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/Naereen/badges/)
[![Join the chat at https://gitter.im/FaradayRF/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/stream-python/community)

<p align="center">
  <img src="https://github.com/AureClai/stream-python/blob/master/img/logo_plus_name.png" width=256 height=256/>
</p>

<h1 align="center">Simulador de tráfico mesoscópico basado en eventos de código abierto</h1>

## ¿Qué es Stream?

Stream es una herramienta de simulación de tráfico mesoscópica, es decir, una herramienta cuyo nivel de resolución es intermedio entre los niveles microscópico y macroscópico. También considera vehículos en lugar de un flujo, pero solo calcula las fechas de paso de los vehículos por los nodos de la red de carreteras, en lugar de calcular todas sus posiciones a intervalos de tiempo fijos. Las ventajas de este método de resolución son (i) los tiempos de cálculo reducidos en comparación con el método microscópico, (ii) un número reducido de parámetros con un significado físico claro que facilita la tarea de configuración de la herramienta en comparación con el método microscópico, (iii) una gran diversidad de casos de uso que son mucho menos restrictivos que el método macroscópico.

## Funcionalidades principales

- Núcleo de cálculo mesoscópico basado en eventos
- Asignación **estática** de antemano y de la ruta más corta
- Gestión limitada* de diferentes clases de vehículos
- Gestión de nodos complejos
- Gestión de cruces con semáforos
- Gestión de carriles específicos (carriles reservados y auxiliares)
- Regulación dinámica durante la simulación

## Contacto

La principal contribución ha sido realizada por la Dirección Departamental del Centro Este de Cerema. En caso de preguntas, envíe un correo electrónico a la siguiente dirección: aurelien.clairais@cerema.fr

## Instalación

Stream funciona con [Anaconda](https://www.anaconda.com/distribution/) para Python 3.9. Con Anaconda, se recomienda el uso de [entornos virtuales](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html):

```console
$ conda create --name myenv
$ conda activate myenv
```

La instalación se realiza clonando el repositorio y luego instalando el paquete con `pip`.

### 1. Clonar el repositorio

```console
$ git clone https://github.com/AureClai/stream-python
$ cd stream-python
```

### 2. _(opcional)_ Cambiar de rama (si se desarrolla en una rama distinta a _master_)

```console
$ git checkout la_rama
```

### 3. Instalar

```console
$ pip install .
```

## Uso

### Uso desde la línea de comandos

```console
$ stream -i file_of_inputs.npy
```

A partir de aquí, se ha creado una nueva carpeta `result` en la carpeta que contiene el archivo de entrada, con los resultados de la simulación correspondientes a la fecha y hora en formato `.npy`. Si se ha especificado una carpeta de resultados (véase `stream --help` en línea de comandos), los resultados se guardarán en esa carpeta.

### Uso a través de un script de python

```python
from stream.main import run_simulation_from_inputs
import numpy as np

# Importar el archivo de entradas
Inputs = np.load("ruta_al_archivo_de_entradas.npy", allow_pickle=True).item()
Simulation = run_simulation_from_inputs(Inputs)
```

En este caso, los resultados se crean en forma de un diccionario en la variable `Simulation`.

### Uso a través de la interfaz gráfica

```console
$ stream-gui
```

## Uso de QStream para diseñar escenarios

La extensión QGIS https://gitlab.cerema.fr/Stream/qstream permite:

- la definición de escenarios
- características de análisis

## Bugs

No se conocen bugs. Si eres testigo de un bug, por favor abre una ["_issue_"](https://github.com/AureClai/stream-python/issues/new).

## Licencia

[Cecill-B](http://www.cecill.info/licences/Licence_CeCILL-B_V1-fr.html).

## Por hacer

1. Implementación de herramientas de visualización con la librería Python `dash` de Plotly
2. Gestión de capacidad variable en salida de red
3. Varios modos de asignación
4. Regulación dinámica de velocidades
5. Regulación de acceso
6. Gestión de otros tipos de formatos de entrada/salida