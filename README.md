# Pepper Robot と Flask サーバーの連携システム
# プロジェクト実行ガイド

## 環境セットアップ

1. このリポジトリをクローンまたはダウンロードします
2. 以下のコマンドで環境をセットアップします:
このプロジェクトは、Pepper ロボットと Flask サーバーを連携させ、音声認識と応答生成を行うシステムです。

## システム概要

このシステムは以下の機能を実現します：

1. Pepper ロボットが音声を録音
2. 録音された音声内に「pepper」という単語が検出された場合のみ、その音声を Flask サーバーに送信
3. Flask サーバーで Hugging Face の Gemma 3n モデルを使用して音声をテキストに変換し、応答を生成
4. 生成された応答テキストを Pepper ロボットに返送
5. Pepper ロボットが返送されたテキストを音声で読み上げる
6. テキストチャットによる直接対話も可能（APIエンドポイント経由）

## システム構成

```
src/
├── config/             # 設定ファイル
├── flask_server/       # Flask サーバー関連のコード
├── pepper_client/      # Pepper クライアント関連のコード
└── utils/              # 共通ユーティリティ
```

## 必要条件

- Python 3.7 以上
- Pepper ロボット（または開発用のモックモード）
- 以下のPythonパッケージ：
  - flask
  - requests
  - numpy
  - torch
  - transformers
  - SpeechRecognition
  - qi (Pepper SDK、開発環境では自動的にモック化されます)

## インストール方法

1. リポジトリをクローン：
   ```
   git clone <repository-url>
   cd pepper-flask-integration
   ```

2. 必要なパッケージをインストール：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

### Flask サーバーの起動

```
python -m src.main server [--host HOST] [--port PORT]
```

オプション：
- `--host`: サーバーのホスト（デフォルト: 0.0.0.0）
- `--port`: サーバーのポート（デフォルト: 5000）

### Pepper クライアントの起動

```
python -m src.main client [PEPPER_IP] [--port PORT] [--server-host HOST] [--server-port PORT] [--once] [--interval INTERVAL]
```

引数：
- `PEPPER_IP`: Pepper ロボットの IP アドレス（デフォルト: 127.0.0.1）

オプション：
- `--port`: Pepper ロボットのポート（デフォルト: 9559）
- `--server-host`: Flask サーバーのホスト（デフォルト: 0.0.0.0）
- `--server-port`: Flask サーバーのポート（デフォルト: 5000）
- `--once`: 一度だけ実行（デフォルトは連続実行）
- `--interval`: 処理サイクル間の時間間隔（秒、デフォルト: 1.0）

## チャット機能の使用方法

Flask サーバーは、テキストチャットによる直接対話をサポートしています。以下の方法でチャット機能を利用できます：

### チャットエンドポイント

```
POST /api/response
```

### リクエスト形式

JSON 形式で以下のデータを送信します：

```json
{
  "text": "こんにちは、Pepper"
}
```

### レスポンス形式

サーバーは以下の形式で応答します：

```json
{
  "input_text": "こんにちは、Pepper",
  "response_text": "こんにちは、ご用件は何でしょうか？"
}
```

### curlを使用した例

```bash
curl -X POST http://localhost:5000/api/response \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは、Pepper"}'
```

### Pythonを使用した例

```python
import requests
import json

url = "http://localhost:5000/api/response"
data = {"text": "こんにちは、Pepper"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(data), headers=headers)
print(response.json())
```

## 開発モード

実際の Pepper ロボットがない環境でも開発できるよう、`qi` モジュールが見つからない場合は自動的にモック実装が使用されます。これにより、Pepper ロボットなしでもコードのテストが可能です。

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。
