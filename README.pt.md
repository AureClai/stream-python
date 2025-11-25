_[:us:](https://github.com/AureClai/stream-python/blob/master/README.md)_ _[:fr:](https://github.com/AureClai/stream-python/blob/master/README.fr.md)_ _[:es:](https://github.com/AureClai/stream-python/blob/master/README.es.md)_ _[:cn:](https://github.com/AureClai/stream-python/blob/master/README.cn.md)_
_[:jp:](https://github.com/AureClai/stream-python/blob/master/README.jp.md)_ _[:portugal:](https://github.com/AureClai/stream-python/blob/master/README.pt.md)_

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/Naereen/badges/)
[![Join the chat at https://gitter.im/FaradayRF/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/stream-python/community)

<p align="center">
  <img src="https://github.com/AureClai/stream-python/blob/master/img/logo_plus_name.png" width=256 height=256/>
</p>

<h1 align="center">Simulador de Tráfego Mesoscópico Baseado em Eventos</h1>

## O que é o Stream?

Stream é uma ferramenta de simulação de tráfego mesoscópica, ou seja, uma ferramenta cujo nível de resolução é intermediário entre os níveis microscópico e macroscópico. Ele também considera veículos em vez de fluxo, mas apenas calcula os tempos de passagem dos veículos nos nós da rede viária, em vez de calcular todas as suas posições em intervalos de tempo fixos.
As vantagens desse método de resolução são: (i) tempos de cálculo reduzidos em comparação com o método microscópico, (ii) um número reduzido de parâmetros com significado físico claro, facilitando o processo de parametrização em comparação com o método microscópico, (iii) uma ampla diversidade de casos de uso muito menos restritivos do que o macroscópico.

## Principais Recursos

- Núcleo de cálculo mesoscópico baseado em eventos
- Atribuição **estática** de fluxo de entrada e caminho mais curto
- Gerenciamento limitado* de diferentes classes de veículos
- Gerenciamento complexo de nós
- Gerenciamento de cruzamentos com semáforos
- Gerenciamento de faixas específicas (faixas reservadas e auxiliares)
- Regulação dinâmica durante a simulação

## Comparação Núcleo Legacy vs Rust

O motor de simulação foi migrado de Python para Rust para obter alto desempenho e melhor escalabilidade.

| Recurso | Núcleo Python Legacy | Novo Núcleo Rust |
| :--- | :--- | :--- |
| **Velocidade** | Referência | **75x - 235x Mais rápido** |
| **Agendamento** | $O(N_{nós})$ Varredura Linear | $O(\log N)$ Heap Binário |
| **Divergência** | Bloqueio FIFO (engarrafamentos) | **Look-Ahead** (Roteamento inteligente) |
| **Física** | Ondas Cinemáticas | Ondas Cinemáticas (Idêntico) |

Veja [BENCHMARK.md](BENCHMARK.md) para um relatório científico detalhado.

## Contato

A principal contribuição é feita pelo Departamento Leste-Central do Cerema. Se você tiver alguma dúvida, envie um e-mail para o seguinte endereço: aurelien.clairais@cerema.fr

## Instalação

O Stream funciona no [Anaconda](https://www.anaconda.com/distribution/) para Python 3.9.
Com o Anaconda, é recomendado usar [ambientes virtuais](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html):

```console
$ conda create --name myenv
$ conda activate myenv
```

A instalação é feita clonando o diretório e, em seguida, instalando o pacote com `pip`.

### 1. Clonar o Diretório

```console
$ git clone https://github.com/AureClai/stream-python
$ cd stream-python
```

### 2. _(opcional)_ Mudar de Branch (se estiver desenvolvendo em um branch diferente de _master_)

```console
$ git checkout the_branch
```

### 3. Instalar

```console
$ pip install .
```

## Uso

### Uso na Linha de Comando

```console
$ stream -i file_of_inputs.npy
```

A partir daqui, uma nova pasta `result` foi criada na pasta contendo o arquivo de entrada com os resultados da simulação associados à data e hora no formato `.npy`. Se uma pasta de resultados tiver sido especificada (consulte `stream --help` na linha de comando), os resultados serão salvos nessa pasta.

### Uso através de um Script Python

```python
from stream.main import run_simulation_from_inputs
import numpy as np

# Importar o arquivo de entrada
Inputs = np.load("path_to_the_inputs_file.npy", allow_pickle=True).item()
Simulation = run_simulation_from_inputs(Inputs)
```

Aqui, os resultados são criados na forma de um dicionário na variável `Simulation`.

### Uso através da Interface Gráfica

```console
$ stream-gui
```

## Use o QStream para Projetar Cenários

A extensão QGIS https://gitlab.cerema.fr/Stream/qstream permite:

- definição de cenários
- recursos de análise

## Bugs

Nenhum bug conhecido. Se você encontrar algum bug, abra uma ["_issue_"](https://github.com/AureClai/stream-python/issues/new).

## Licença

[Cecill-B](http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html).

## TODO

1. Implementação de ferramentas de visualização com a biblioteca `dash` do Python e Plotly
2. Gerenciamento de capacidade de saída variável
3. Vários modos de atribuição
4. Regulação dinâmica de velocidade
5. Regulação de acesso
6. Gerenciamento de outros tipos de formatos de entrada/saída
