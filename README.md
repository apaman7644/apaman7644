# Novel Auto Generation System (長編小説自動生成システム)

## これは何か
日本語の長編小説（目安10万字）を、**段階生成・評価・改稿・比較**のループで改善するためのCLIベース基盤です。
単発生成ではなく、run単位で成果物を保存し、再現可能・比較可能な制作プロセスを重視します。

## 先に提示する実装計画（本リポジトリ初版）
1. 設計とディレクトリ構成を定義
2. データモデル（Project / NovelSpec / Bible / Outline / ChapterPlan / ChapterDraft / EvaluationReport / RevisionInstruction / FeedbackEntry / RunArtifact）
3. TOML設定読み込み
4. 保存機構（JSON/Markdown/TXT）
5. プロンプトテンプレート分離
6. モデル呼び出し抽象化（Provider層）
7. 企画生成
8. バイブル生成
9. アウトライン生成
10. 章生成
11. 評価
12. 改稿指示生成
13. run比較
14. CLI統合
15. README + AGENTS.md
16. テスト整備

## ディレクトリ構成
```text
src/novel_auto_gen/
  core/
    models/       # ドメインモデル
    pipeline/     # 生成パイプライン
    memory/       # 長編向け記憶管理
    evaluation/   # 自動評価
    revision/     # 改稿指示 / 比較
    export/       # 出力
    providers/    # モデル抽象化
    prompts/      # テンプレート管理
    storage/      # 保存
    config.py
  cli/
configs/
prompts/
workspace_data/   # 実行成果物
tests/
docs/
AGENTS.md
```

## 最小実用版 (MVP+基盤)
- `init-project` でプロジェクト初期化
- `generate-novel` で以下を一括実行
  - 企画候補生成
  - バイブル生成
  - アウトライン生成
  - 章ドラフト生成
  - 自動評価
  - 改稿指示生成
  - 原稿エクスポート
- `compare-runs` で前回比較
- `apply-feedback` で人間FB保存

## 拡張版（将来）
- 実LLMプロバイダ（OpenAI等）接続
- ベクトル検索を使う章コンテキスト選別
- 伏線台帳の自動更新強化
- EPUB/Word出力
- Web UI

## 合理的前提（明示）
- 初版は `MockProvider` により動作確認重視（再現性優先）。
- 実際の10万字出力品質は、実LLM接続後に向上させる設計。
- 評価は初版ではヒューリスティック。将来LLM評価器に差し替え可能。

## セットアップ
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 環境変数
初版は必須なし。実プロバイダ導入時に `.env` を追加予定。

## 実行例
```bash
novelgen init-project --name "memory-city" --description "長編制作"
novelgen generate-novel --project-id project_xxx --version 1 --candidates 3 --pick 1 --upto-chapter 3
novelgen apply-feedback --run-id run_xxx --feedback "主人公をより冷徹に"
novelgen compare-runs --previous-run run_a --current-run run_b
novelgen export-manuscript --run-id run_xxx --project-name "Memory City"
```

## 推奨ワークフロー（改善ループ）
1. `generate-novel` で初稿run作成
2. `evaluation.md` と `revision_instruction.json` を確認
3. `apply-feedback` で人間要望を記録
4. 改稿runを再生成
5. `compare-runs` で差分確認
6. 目標品質まで反復

## 典型的な失敗例
- **全文を毎回渡す**: コンテキスト肥大化で崩壊
- **プロンプト直書き**: 変更追跡不能
- **評価未保存**: 改善ループ不能
- **run管理なし**: 再現性喪失

## 将来拡張案
- Provider追加 (`OpenAIProvider`, `LocalLLMProvider`)
- 評価指標の重み学習
- 人手評価と自動評価の相関分析
- エージェント型の章改稿サイクル

## CLI一覧
- init-project
- generate-concept
- build-bible
- build-outline
- generate-chapter
- generate-novel
- evaluate
- revise
- compare-runs
- apply-feedback
- export-manuscript

## テスト
```bash
pytest
```
