# 日本語PDF OCR環境

yomitokuを使用して、画像化された日本語PDFからテキストを抽出するための環境です。

## セットアップ

### 1. popplerのインストール（システムツール）

PDFを画像に変換するために必要なシステムツールです。

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
- [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)からダウンロード
- または`conda install -c conda-forge poppler`

### 2. 仮想環境の作成

```bash
python3 -m venv .venv
```

### 3. 仮想環境の有効化

```bash
source .venv/bin/activate
```

### 4. pipのアップグレード

```bash
pip install --upgrade pip
```

### 5. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

## 使用方法

### バッチ処理（推奨）

`input_files/` ディレクトリ内の全PDFファイルを一括でOCR処理します。

```bash
# Markdown形式で出力
python batch_ocr.py -f md

# JSON形式で出力
python batch_ocr.py -f json

# HTML形式で出力
python batch_ocr.py -f html

# CSV形式で出力（Excelで開ける形式）
python batch_ocr.py -f csv
```

#### 動作フロー

1. `input_files/` からPDFファイルを読み込み
2. OCR処理を実行（yomitoku使用）
3. 結果を `output/` に保存（元のファイル名を保持: `test1.pdf` → `test1.md`）
4. 処理完了したPDFを `processed_files/` に移動

#### オプション

```bash
python batch_ocr.py -f md -i カスタム入力Dir -o カスタム出力Dir -p カスタム処理済みDir
```

- `-f, --format`: 出力形式 (md, json, html, csv) ※デフォルト: md
- `-i, --input`: 入力ディレクトリ ※デフォルト: input_files
- `-o, --output`: 出力ディレクトリ ※デフォルト: output
- `-p, --processed`: 処理済みファイルの移動先 ※デフォルト: processed_files

#### 特徴

- 失敗時に2回自動リトライ
- CSV形式は自動的にUTF-8 BOM付きで保存（Excelで文字化けしない）
- ページごとのファイルを自動マージ
- 処理完了したPDFは自動的に `processed_files/` に移動

### 単一ファイルの処理

yomitoku CLIコマンドで1ファイルずつ処理することもできます。

```bash
# Markdown形式で出力
yomitoku <PDFファイルのパス> -f md -o <出力ディレクトリ>

# JSON形式で出力
yomitoku <PDFファイルのパス> -f json -o <出力ディレクトリ>

# HTML形式で出力
yomitoku <PDFファイルのパス> -f html -o <出力ディレクトリ>

# CSV形式で出力
yomitoku <PDFファイルのパス> -f csv -o <出力ディレクトリ>
```

#### CLIコマンドのオプション

- `-f, --format`: 出力形式 (json, csv, html, md)
- `-o, --outdir`: 出力ディレクトリ
- `-v, --vis`: 結果の可視化を有効化
- `-d, --device`: 使用デバイス (cpu または cuda)
- `--ignore_line_break`: 改行を無視
- `--figure`: 図を出力に含める

## Docker版

別環境で同じOCR環境を再現する場合は、[README_DOCKER.md](README_DOCKER.md)を参照してください。

## 注意事項

- 初回実行時は、モデルのダウンロードが行われるため時間がかかります
- デフォルトでCPUを使用します。GPUを使う場合は `-d cuda` オプションを指定してください

## 仮想環境の無効化

作業が終わったら、以下のコマンドで仮想環境を無効化できます:

```bash
deactivate
```
