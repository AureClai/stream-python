_[:us:](https://github.com/AureClai/stream-python/blob/master/README.md)_ _[:fr:](https://github.com/AureClai/stream-python/blob/master/README.fr.md)_ _[:es:](https://github.com/AureClai/stream-python/blob/master/README.es.md)_ _[:cn:](https://github.com/AureClai/stream-python/blob/master/README.cn.md)_
_[:jp:](https://github.com/AureClai/stream-python/blob/master/README.jp.md)_ _[:portugal:](https://github.com/AureClai/stream-python/blob/master/README.pt.md)_

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/Naereen/badges/)
[![Join the chat at https://gitter.im/FaradayRF/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/stream-python/community)

<p align="center">
  <img src="https://github.com/AureClai/stream-python/blob/master/img/logo_plus_name.png" width=256 height=256/>
</p>

<h1 align="center">イベントベースの中程度交通シミュレーター</h1>

## Streamとは？

Streamは中程度の交通シミュレーションツールです。つまり、その解像度はマイクロとマクロの中間レベルです。また、流れではなく車両を考慮し、道路ネットワークのノードで車両の通過時間を計算するだけで、固定時間ステップでの全ての位置を計算するのではありません。
この解像度のメリットは、(i) 微視的と比較して計算時間が短縮されること、(ii) 物理的な意味を持つパラメータの数が減少し、パラメータ化プロセスが容易になること、(iii) マクロの制約よりもはるかに多様なユースケースが可能であることです。

## 主な機能

- イベントベースの中程度計算コア
- 上流および最短経路の**静的**割り当て
- 異なる車両クラスの制限管理*
- 複雑なノード管理
- 信号機交差点の管理
- 特定の車線の管理（予約および補助車線）
- シミュレーション中の動的な規制

## 連絡先

主な貢献者はCerema東中央部です。ご質問がある場合は、次のアドレスにメールを送信してください：aurelien.clairais@cerema.fr

## インストール

StreamはPython 3.9向けの[Anaconda](https://www.anaconda.com/distribution/)で動作します。
Anacondaでは、[仮想環境](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)の使用を推奨します。

```console
$ conda create --name myenv
$ conda activate myenv
```

インストールは、ディレクトリをクローンし、`pip`でパッケージをインストールすることで行われます。

### 1. ディレクトリのクローン

```console
$ git clone https://github.com/AureClai/stream-python
$ cd stream-python
```

### 2. _(オプション)_ ブランチの切り替え（_master_以外のブランチで開発する場合）

```console
$ git checkout the_branch
```

### 3. インストール

```console
$ pip install .
```

## 使用法

### コマンドラインの使用法

```console
$ stream -i file_of_inputs.npy
```

ここから、入力ファイルを含むフォルダに新しい`result`フォルダが作成され、シミュレーション結果が日付と時間の`.npy`形式で保存されます。結果フォルダが指定されている場合（コマンドラインの`stream --help`を参照）、結果はこのフォルダに保存されます。

### Pythonスクリプトを使用した方法

```python
from stream.main import run_simulation_from_inputs
import numpy as np

# 入力ファイルのインポート
Inputs = np.load("path_to_the_inputs_file.npy", allow_pickle=True).item()
Simulation = run_simulation_from_inputs(Inputs)
```

ここでは、結果は`Simulation`変数に辞書形式で作成されます。

### グラフィックインターフェースを使用した方法

```console
$ stream-gui
```

## シナリオの設計にQStreamを使用する

QGISの拡張機能であるhttps://gitlab.cerema.fr/Stream/qstreamを使用すると、次のことが可能です。

- シナリオの定義
- 解析機能

## バグ

既知のバグはありません。バグが発生した場合は、["_issue_"](https://github.com/AureClai/stream-python/issues/new)をオープンしてください。

## ライセンス

[Cecill-B](http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html)。

## TODO

1. Pythonの`dash`ライブラリを使用した可視化ツールの実装
2. 可変出力容量の管理
3. 複数の割り当てモード
4. 動的速度制御
5. アクセス制御
6. 他の入力/出力形式の管理
