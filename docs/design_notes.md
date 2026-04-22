# Design Notes

## 重要設計判断
- Providerを抽象化し、呼び出し再試行を `ProviderService` に集約。
- 長編記憶は `ContextManager` で章単位取得し、全文投入を避ける。
- 評価結果は JSON/Markdown の両方保存。
- 反復改善のため、runごとに `runs/<run_id>/` を作成。

## TODO
- 実モデル接続とJSONスキーマ制約
- 伏線台帳の章間自動マッチング
- 同表現反復検出の厳密化
- EPUB/Wordエクスポータ
