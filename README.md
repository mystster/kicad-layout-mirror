# kicad-layout-mirror

KiCad で左右分離型キーボードを設計する際に、片方の基板レイアウト（フットプリント、シェイプ、テキストなど）を元にして、もう片方のレイアウトを左右対称に生成・コピーするツールです。

## 特徴
* **フットプリントのミラーリング**: `move_footprints.py` を用いて、基準となる X 軸を中心に部品を対称の位置へ移動させます。
* **シェイプやテキストのコピー**: `copy_mirrored_shapes.py` を用いて、外形線やテキストなどの図形要素を左右対称にコピーします。

## ファイル構成と説明
* `move_footprints.py`: 指定されたマッピングに従い、フットプリントの座標や角度を左右対称に移動させるメインスクリプトです。
* `copy_mirrored_shapes.py`: 基板の外形線やシルクの図形、テキストなどを左右対称にコピーするスクリプトです。
* `fp_mapping.py`: 左右のフットプリントの参照番号（RefDes）の対応関係（ペア）を定義するファイルです。
* `kicad_utils.py`: ポイントのミラーリング計算など、共通のユーティリティ関数をまとめたファイルです。
* `debug_utils.py`: KiCadオブジェクトのプロパティを一覧表示するなど、開発・デバッグ用のスクリプトです。
* `requirements.txt`: 実行に必要な Python パッケージ（kipyなど）のリストです。

## 前提条件・依存関係
* KiCad 8.0 以上（Python スクリプティング対応版）
* [kipy](https://github.com/dvenkatesh/kipy) (KiCad 用の Python ラッパーライブラリ)

## 使い方

### 1. 仮想環境 (venv) の構築と準備
Python の仮想環境を作成し、必要なライブラリをインストールします。
```bash
# 仮想環境の作成
python -m venv .venv

# 仮想環境の有効化 (Windows)
.venv\Scripts\activate
# 仮想環境の有効化 (Mac/Linux)
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```
その後、KiCad の PCB エディタで対象の基板（`.kicad_pcb`）を開いておきます。

### 2. フットプリントの対応付け (`fp_mapping.py` の作成)
フットプリントをミラーリングする前に、右手の部品と左手の部品の対応関係を定義する必要があります。
`fp_mapping.py` を開き、`FP_MAPPING` 辞書に `"右手側の参照番号": "左手側の参照番号"` の形式でペアを記述してください。
```python
FP_MAPPING = {
    "K_R_11": "K_L_11",  # 例: 右手のキー11 と 左手のキー11
    "U2": "U1",          # 例: 右手のマイコン と 左手のマイコン
}
```

### 3. フットプリントの移動
スクリプト (`move_footprints.py` など) 内の `MIRROR_AXIS_X_MM` 変数を、ミラーリングの基準としたい X 座標（ミリメートル単位）に変更します。
その後 `move_footprints.py` を実行して、フットプリントをミラーリングします。
（あらかじめ、もう片方の基板にあるフットプリントが現在の基板に読み込まれている必要があります）

### 4. 図形やテキストのコピー
`copy_mirrored_shapes.py` を実行して、外形やシルクのテキストなどをミラーリングコピーします。

## ライセンス
This project is open-sourced under the MIT License.
