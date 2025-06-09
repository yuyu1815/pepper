# Pepper Robot と Flask サーバー連携システム テスト

このディレクトリには、Pepper Robot と Flask サーバー連携システムのテストコードが含まれています。

## テストの概要

以下のコンポーネントに対するテストが実装されています：

1. **Flask サーバー** (`test_flask_server.py`)
   - ヘルスチェックエンドポイント
   - 音声処理エンドポイント
   - エラーハンドリング

2. **Pepper クライアント** (`test_pepper_client.py`)
   - Pepper ロボットへの接続
   - 音声録音機能
   - テキスト読み上げ機能
   - 音声処理と応答サイクル

3. **音声ユーティリティ** (`test_audio_utils.py`)
   - 音声フォーマット変換
   - キーワード検出
   - 音声ファイル操作

4. **HTTP ユーティリティ** (`test_http_utils.py`)
   - サーバー URL 構築
   - サーバーヘルスチェック
   - 音声データ送信

5. **モデルユーティリティ** (`test_model_utils.py`)
   - モデル初期化
   - 音声からテキストへの変換
   - テキスト応答生成

## テストの実行方法

### すべてのテストを実行

以下のコマンドで、すべてのテストを一度に実行できます：

```bash
python -m test.run_tests
```

### 特定のテストを実行

特定のテストモジュールのみを実行するには、モジュール名を指定します：

```bash
python -m test.run_tests test_flask_server
python -m test.run_tests test_pepper_client
python -m test.run_tests test_audio_utils
python -m test.run_tests test_http_utils
python -m test.run_tests test_model_utils
```

### Python の unittest を直接使用

Python の unittest モジュールを直接使用することもできます：

```bash
python -m unittest test.test_flask_server
python -m unittest test.test_pepper_client
python -m unittest test.test_audio_utils
python -m unittest test.test_http_utils
python -m unittest test.test_model_utils
```

## テスト環境

テストは実際の Pepper ロボットがなくても実行できるように設計されています。必要なコンポーネントはすべてモック化されています。

## 注意事項

1. テストを実行する前に、必要なパッケージがすべてインストールされていることを確認してください。
2. テストは実際のモデルをロードせず、モックオブジェクトを使用します。
3. 実際の Pepper ロボットは必要ありません。すべての Pepper 関連の機能はモック化されています。