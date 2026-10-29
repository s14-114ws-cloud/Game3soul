# SOUL TETHER / ソウルテザー

2D横スクロールアクション（肉体と霊体を切り替えて進む）。iPhone横持ち優先。

## 2つの出力

| ファイル | 用途 |
|---|---|
| `soul_tether.html` | **1ファイル版**。画像・音・フォントをすべて内蔵。ダブルクリックでオフラインでも遊べる（64MB以内に収めるため曲は64kbps）。 |
| `dist/` | **公開用（Web / PWA）版**。素材を別ファイルに分け、2回目以降は端末に保存された分ですぐ起動・オフライン可。iPhoneは「ホーム画面に追加」で全画面アプリになる。曲は元の音質。 |

## ビルド

```bash
python3 tools/build_assets.py soul_tether.html   # assets/src の画像 → 1ファイル版に埋め込み
python3 tools/build_audio.py  soul_tether.html   # assets/src/audio の音 → 1ファイル版に埋め込み
python3 tools/build_web.py                       # 1ファイル版 → dist/（公開用）
```

必要なもの：Python 3（Pillow, numpy, scipy）、ffmpeg。

## フォルダ

- `soul_tether.html` … ゲーム本体（コード＋埋め込み素材）
- `assets/src/` … 素材の原本（ドット絵シート、スチル、背景、UI）
- `assets/src/audio/` … BGM・SE・エンディング曲（Suno）の原本
- `tools/` … 素材の切り出し・埋め込み・Web版作成スクリプト
- `docs/asset_prompts.md` … 素材生成AI用プロンプト集
- `dist/` … 公開用の出力（`build_web.py` が毎回作り直す）

## 公開・テスト

- **iPhoneで手早くテスト（無料）**：PCで `cd dist && python3 -m http.server 8000`、同じWi-Fiの iPhone の Safari で `http://<PCのIPアドレス>:8000` を開く（保存機能は https でのみ有効）。
- **自動で公開URLを更新（無料枠）**：Cloudflare Pages をこのリポジトリに接続し、「ビルドコマンド：なし」「出力ディレクトリ：`dist`」。push するたびに更新される。
- **本番（Netlify）**：Publish directory を `dist` に。`dist/_headers` でキャッシュ設定済み。

## クレジット

- フォント：DotGothic16（SIL Open Font License 1.1, Fontworks Inc.）
- エンディング曲：Suno（「届かない朝」「ふたりの朝」）
- ドット絵・イラスト：ChatGPT
