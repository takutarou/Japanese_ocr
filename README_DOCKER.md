# Docker版セットアップガイド

会社PCなど、別の環境で全く同じOCR環境を再現するためのDocker版セットアップ手順です。

## 前提条件

- Docker環境がインストールされていること
- Dockerが起動していること

## Dockerのインストール

### 重要：ライセンスについて

- **Docker Engine（CLI）**: 完全無料、商用利用OK
- **Docker Desktop**: 大企業（従業員250人以上または年間売上$10M以上）では有料

**会社で使用する場合は、Docker Desktop以外の選択肢を推奨します。**

### オプション1: Docker Engine（CLI版）- Linux推奨

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER  # 現在のユーザーをdockerグループに追加
# ログアウト/ログインして設定を反映
```

**CentOS/RHEL:**
```bash
sudo yum install docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker  # 自動起動を有効化
sudo usermod -aG docker $USER
# ログアウト/ログインして設定を反映
```

### オプション2: Colima（CLI専用）- macOS推奨（完全無料・軽量）

**macOSでCLIのみ使いたい場合のベストチョイス**

GUIなし、軽量、完全無料でDocker CLIが使えます。

```bash
# インストール（3つのパッケージを一気にインストール）
# - colima: Docker実行環境（軽量VM）
# - docker: Dockerコマンドラインツール
# - docker-compose: 複数コンテナ管理ツール
brew install colima docker docker-compose

# 起動
colima start

# リソースを指定して起動（推奨）
# まず、Macのスペックを確認してから適切な値を設定
# CPU数確認: sysctl -n hw.ncpu
# メモリ確認: sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 "GB"}'
# 目安: CPUは総コア数の50-75%、メモリは総容量の25-50%
colima start --cpu 4 --memory 8

# 確認
docker --version
docker ps

# 使い終わったら停止（リソース節約）
colima stop

# 自動起動設定（オプション）
# brew services start colima
```

**メリット:**
- ✅ 軽量（Docker Desktopより少ないメモリ使用）
- ✅ 完全無料
- ✅ 必要な時だけ起動できる
- ✅ リソース（CPU/メモリ）を細かく指定可能

### オプション3: Rancher Desktop - macOS/Windows推奨（完全無料・GUI付き）

**macOS/WindowsでGUIが欲しい場合のベストチョイス**

Docker Desktopの無料代替。GUIもありDockerコマンドが使えます。

- [Rancher Desktop ダウンロード](https://rancherdesktop.io/)
- インストール後、設定で「**dockerd (moby)**」を選択

**メリット:**
- ✅ GUIで状態確認できる
- ✅ 完全無料（企業利用OK）
- ✅ Docker Desktopとほぼ同じ使い勝手

### オプション4: OrbStack - macOSのみ（個人利用無料）

Docker Desktopより軽量・高速。

- [OrbStack ダウンロード](https://orbstack.dev/)

⚠️ **注意:** 企業利用は有料プランが必要な場合があります。個人利用は無料。

### オプション5: Podman（完全無料）

Docker互換のコンテナツール。

```bash
# macOS
brew install podman podman-compose

# Linux
sudo apt-get install podman podman-compose
```

**注意:** Podmanを使う場合、`docker`コマンドを`podman`に、`docker-compose`を`podman-compose`に読み替えてください。

## 環境別の推奨まとめ

| 環境 | 推奨ツール | 理由 |
|------|-----------|------|
| **Linux** | Docker Engine | 公式、軽量、シンプル |
| **macOS（CLI派）** | Colima | 軽量、必要時のみ起動、無料 |
| **macOS（GUI欲しい）** | Rancher Desktop | GUI付き、完全無料 |
| **Windows** | Rancher Desktop | GUI付き、完全無料 |
| **会社PC（大企業）** | Colima or Rancher Desktop | ライセンス問題なし |

## セットアップ手順

### 1. プロジェクトディレクトリに移動

```bash
cd /path/to/japanese_ocr
```

### 2. Dockerイメージのビルド

```bash
docker-compose build
```

初回は5-10分程度かかります。

## 使用方法

### 方法1: CLIコマンドを使う（推奨）

```bash
# Markdown形式で出力
docker-compose run --rm yomitoku yomitoku /app/target_files/test1.pdf -f md -o /app/output

# JSON形式で出力
docker-compose run --rm yomitoku yomitoku /app/target_files/test1.pdf -f json -o /app/output

# HTML形式で出力
docker-compose run --rm yomitoku yomitoku /app/target_files/test1.pdf -f html -o /app/output
```

### 方法2: Pythonスクリプトを使う

```bash
# ocr_sample_simple.py を使用
docker-compose run --rm yomitoku python ocr_sample_simple.py /app/target_files/test1.pdf /app/output/result.txt

# ocr_sample.py を使用
docker-compose run --rm yomitoku python ocr_sample.py /app/target_files/test1.pdf /app/output/result.txt
```

### 方法3: インタラクティブモードで使う

コンテナ内でシェルを起動して、複数のコマンドを実行:

```bash
# コンテナに入る
docker-compose run --rm yomitoku bash

# コンテナ内で実行
yomitoku /app/target_files/test1.pdf -f md -o /app/output
python ocr_sample_simple.py /app/target_files/test1.pdf /app/output/result.txt

# 終了
exit
```

## ファイルの配置

### 入力ファイル（PDF）
`target_files/` ディレクトリに配置してください。

```
japanese_ocr/
├── target_files/      ← ここにPDFを配置
│   └── test1.pdf
```

### 出力ファイル
`output/` ディレクトリに出力されます。

```
japanese_ocr/
├── output/           ← ここに結果が出力される
│   └── result.txt
```

## 便利なコマンド

### イメージの再ビルド

依存関係を変更した場合:

```bash
docker-compose build --no-cache
```

### コンテナの削除

```bash
docker-compose down
```

### ボリュームも含めて完全削除

```bash
docker-compose down -v
```

### キャッシュされたモデルの確認

```bash
docker volume ls | grep yomitoku
```

## GPU対応（オプション）

GPUを使用する場合は、`docker-compose.yml`の以下の部分をコメント解除してください:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

**前提条件:**
- NVIDIA GPU搭載マシン
- NVIDIA Dockerサポートのインストール

## トラブルシューティング

### ビルドに失敗する

```bash
# キャッシュをクリアして再ビルド
docker-compose build --no-cache
```

### 権限エラーが出る

```bash
# outputディレクトリの権限を変更
chmod -R 777 output
```

### モデルのダウンロードに時間がかかる

初回実行時は、yomitokuのモデル（数GB）がダウンロードされます。
2回目以降は`yomitoku_cache`ボリュームに保存されているため高速です。

## Dockerキャッシュについて

Dockerは複数のレイヤーでキャッシュを活用し、ビルド・実行を高速化します。

### キャッシュの種類と保存場所

#### 1. ビルドキャッシュ（ビルド高速化）
- **場所**: Colima使用時は `~/.colima/default/docker/` 内
- **内容**: Dockerfile内の各命令（RUN, COPY等）の実行結果
- **効果**: 同じ命令なら再実行せずキャッシュを再利用 → 2回目以降のビルドが高速

#### 2. yomitokuモデルキャッシュ（ダウンロード不要）
- **場所**: Named volume `japanese_ocr_yomitoku_cache`
  - Colima VM内: `/var/lib/docker/volumes/japanese_ocr_yomitoku_cache/_data`
  - Mac実体: `~/.colima/default/docker/volumes/japanese_ocr_yomitoku_cache/_data/`
- **内容**: yomitokuの学習済みモデル（約650MB）
- **効果**: 初回のみダウンロード、2回目以降は再利用

#### 3. Dockerイメージ（完成品）
- **場所**: Dockerイメージストレージ
- **内容**: ビルド済みの完全なイメージ（約1.9GB）
- **効果**: `docker-compose build`不要で即座に実行可能

### キャッシュの確認

```bash
# 全体の使用量を確認
docker system df -v

# yomitokuモデルキャッシュの詳細
docker volume inspect japanese_ocr_yomitoku_cache
```

### キャッシュのクリア

```bash
# ビルドキャッシュのみ削除（モデルは保持）
docker builder prune

# 未使用のイメージ・コンテナ・ボリューム全て削除
docker system prune -a --volumes
```

**注意**: `docker system prune -a --volumes` を実行すると、yomitokuモデルも削除されるため、次回実行時に再ダウンロードが必要になります。

## 会社PCへの展開

以下のファイルをコピーすればOKです:

```
japanese_ocr/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
├── ocr_sample.py
├── ocr_sample_simple.py
├── README_DOCKER.md
└── target_files/
    └── (処理したいPDFファイル)
```

会社PCで:

```bash
docker-compose build
docker-compose run --rm yomitoku yomitoku /app/target_files/yourfile.pdf -f md -o /app/output
```

これだけで全く同じ環境が再現されます！
