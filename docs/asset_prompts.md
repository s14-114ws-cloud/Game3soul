# SOUL TETHER 素材生成プロンプト集

各ブロックをそのままコピーして、生成AIに1回で貼り付けてください。
完成したファイルは、ファイル名をそのままにしてチャットに添付すれば組み込みます。

- 効果音：ElevenLabs Sound Effects などの効果音生成AI向け（英語の方が精度が出ます）
- BGM：Suno / Udio などの作曲AI向け
- 画像：ChatGPT（画像生成）など、今までと同じ要領

---

## 1. 効果音（20種）

共通の書き出し指定：MP3またはM4A、モノラル可、無音部分をカット、音量はそろえる（ピーク -1dB 程度）。
効果音AIは1音ずつ生成するものが多いので、1行＝1回の生成です。行頭の「ファイル名」で保存してください。

```
se_jump.mp3 — Short light jump sound for a 2D pixel-art action game, soft cloth whoosh with a tiny upward chirp, 0.25 seconds, no music, clean ending.
se_land.mp3 — Soft footstep landing on a hard floor, light thud with a little dust, 0.2 seconds, 2D game sound effect.
se_dash.mp3 — Ghostly spirit dash, fast airy whoosh with a shimmering blue magical tail, 0.4 seconds, ethereal, 2D game sound effect.
se_slash_body.mp3 — Quick katana slash cutting air, sharp metallic swish, 0.3 seconds, crisp, Japanese sword, game sound effect.
se_slash_spirit.mp3 — Spectral sword slash, glassy shimmering swish with a faint choir-like sparkle, 0.35 seconds, ethereal blue magic, game sound effect.
se_lunge.mp3 — Powerful forward sword lunge, rushing wind into a heavy piercing slash with a magical ring, 0.6 seconds, game sound effect.
se_soul_out.mp3 — Soul leaving the body, deep soft heartbeat thump then a rising ethereal whoosh and chime, 0.9 seconds, mysterious, game sound effect.
se_soul_return.mp3 — Soul snapping back into the body, reverse whoosh ending in a warm solid thump, 0.7 seconds, game sound effect.
se_tether_warn.mp3 — Tense warning tone for a stretched spiritual chain, low creaking chain plus a pulsing high-pitched hum, 1.0 second, loopable, game UI warning.
se_hurt_body.mp3 — Player takes damage, dull punchy impact with a short grunt-free crunch, 0.3 seconds, game sound effect.
se_hurt_spirit.mp3 — Spirit takes damage, glassy crack with a ghostly echo, 0.4 seconds, game sound effect.
se_enemy_down.mp3 — Ghost enemy defeated, short dissolving burst with fading whispers and sparkles, 0.6 seconds, game sound effect.
se_boss_down.mp3 — Boss defeated, huge impact boom followed by a long shimmering dissolve and a low choir swell, 2.5 seconds, dramatic, game sound effect.
se_switch.mp3 — Mechanical switch or spirit device activation, clunk plus a magical blue hum rising, 0.5 seconds, game sound effect.
se_gate.mp3 — Heavy stone and iron gate grinding open, rumble with chain rattle, 1.5 seconds, game sound effect.
se_memory.mp3 — Reading a memory fragment, soft crystal chime with a gentle reverse shimmer, 0.8 seconds, nostalgic, game sound effect.
se_checkpoint.mp3 — Checkpoint shrine lit, warm bell-like chime with soft magical sparkle, 1.0 second, comforting, game sound effect.
se_cursor.mp3 — Menu cursor move, very short soft wooden tick with a tiny chime, 0.08 seconds, elegant UI sound.
se_ok.mp3 — Menu confirm, elegant bright chime with a soft koto pluck, 0.3 seconds, Japanese fantasy UI sound.
se_cancel.mp3 — Menu cancel, soft low descending pluck, 0.2 seconds, elegant UI sound.
se_text.mp3 — Dialogue text blip, extremely short soft muted pluck, 0.04 seconds, used repeatedly while text scrolls, UI sound.
```

---

## 2. BGM（10曲）

共通の書き出し指定：MP3 128kbps、1分30秒〜2分、**最後が頭へ自然につながるループ曲**、歌なし（インスト）。

```
bgm_title.mp3 — Instrumental, melancholic Japanese dark fantasy title theme, solo piano and soft strings with a distant music box, slow 80 BPM, mysterious hospital at night, a thread of hope, seamless loop, no vocals.
```
```
bgm_stage_early.mp3 — Instrumental, eerie but gentle exploration music for haunted hospital and rainy Japanese town, soft synth pads, plucked koto, light percussion, 100 BPM, curious and lonely, seamless loop, no vocals.
```
```
bgm_stage_mid.mp3 — Instrumental, tense exploration music for abandoned factory, cemetery under eclipse and ghost subway, low strings, taiko pulses, metallic textures, 110 BPM, ominous, seamless loop, no vocals.
```
```
bgm_stage_late.mp3 — Instrumental, grand and sorrowful exploration music for a research tower and a cathedral between worlds, choir pads, organ, strings, 96 BPM, emotional and climactic, seamless loop, no vocals.
```
```
bgm_boss.mp3 — Instrumental, intense boss battle music, Japanese dark fantasy, driving taiko and string ostinato, electric guitar accents, shamisen riffs, 150 BPM, dramatic, seamless loop, no vocals.
```
```
bgm_boss_final.mp3 — Instrumental, epic final boss battle, full choir, pipe organ, orchestral strings and taiko, 160 BPM, desperate and heroic, two worlds colliding, seamless loop, no vocals.
```
```
bgm_ending.mp3 — Instrumental, quiet bittersweet ending, solo piano with soft strings, morning light in an empty hospital room, 72 BPM, gentle sadness, 2 minutes, ending fades out, no vocals.
```
```
bgm_true_end.mp3 — Instrumental, warm hopeful true ending theme, piano, strings and music box, sunrise, reunion, 84 BPM, tender and uplifting, 2 minutes, no vocals.
```
```
bgm_credits.mp3 — Instrumental, staff roll theme, reprise of a gentle piano melody growing into full strings and soft choir, 90 BPM, nostalgic and uplifting, 3 minutes, natural ending, no vocals.
```
```
bgm_tension.mp3 — Instrumental, short suspense loop for cutscenes and discoveries, low drones, heartbeat pulse, faint music box, 60 BPM, seamless loop, 1 minute, no vocals.
```

---

## 3. 画像（細かい残り）

これまでと同じく「16bitドット絵風・無地のグレー背景・右向き・状態ごとに横並び・ラベル文字なし」でお願いします。

```
2Dゲーム用のドット絵素材シート（16bit風、ダークファンタジー、和風ホラー）。無地のグレー背景、ラベル文字なし、各素材の間に十分な余白。
内容：ST2「怨念の記憶」— 雨の住宅街に漂う、街の霊の記憶の結晶。紫と赤の怨念のもやに包まれた、ひび割れたガラスの破片。
状態を横に3つ並べる：①通常（ぼんやり紫に光る）②読んでいる最中（赤紫に強く光り、もやが渦巻く）③読み終わり（破片が散って薄く消えかけ）。
```
```
2Dゲーム用のドット絵素材シート（16bit風、ダークファンタジー）。無地のグレー背景、ラベル文字なし、余白多め。
内容：周期的に燃え上がる「霊火」のトラップ。青白い鬼火の炎が床の霊印から噴き上がる。
横に4コマ：①消えている（床の霊印だけがかすかに光る）②燃え始め（小さな青い火）③最大（背の高い青白い炎の柱）④消えかけ（火の粉が散る）。
```
```
2Dアクションゲームの足場タイル（16bitドット絵風）。無地のグレー背景、ラベル文字なし。
次の9テーマそれぞれについて「足場の裏面／下側を横に繰り返せるタイル」を1枚ずつ、1行に1テーマで縦に並べる：
1病院（白い壁・配管）2雨の住宅街（濡れた石垣）3学校（木の床下・梁）4工場（錆びた鉄骨）5墓地（苔むした石積み）6幽霊地下鉄（コンクリートとケーブル）7研究塔（金属パネルと青いライン）8境界（浮いた岩と紫の結晶つらら）9大聖堂（石造りのアーチとステンドグラス）。
各タイルは左右がつながるように、高さは足場の厚みの約3倍。
```
```
2Dゲームの操作ヒント用UI素材（16bitドット絵風、和風ダークファンタジー、金の縁取りの高級感）。無地のグレー背景、ラベル文字なし。
内容：オブジェクトの頭上に出す小さな「吹き出しプレート」。中に文字を入れるので中央は無地。
横に3つ：①肉体モード用（黒地に金の縁、小さな提灯の飾り）②霊体モード用（紺地に青白い縁、三日月の飾り）③押せる状態の強調版（縁が光る）。横長、小さめ。
```

---

## 4. UI追加素材（UIの高級感アップ用）

共通：16bitドット絵風・和風ダークファンタジー・金の縁取り・無地のグレー背景・ラベル文字なし・中に文字を入れる部分は無地にする。

```
2Dゲーム用UI素材（16bitドット絵風、和風ダークファンタジー、黒地に金の縁取り、提灯と鎖の装飾）。無地のグレー背景、ラベル文字なし。
内容：画面下に出す「ボスの体力ゲージ枠」。とても横長（縦横比 1:10 くらい）。左端に赤い鬼面か髑髏のエンブレム、中央にゲージを入れる暗い溝（中は空）、右端に小さな提灯。
横に2種：①通常（金の縁）②怒り・最終形態（縁が赤く光り、黒紫の炎がまとわりつく）。
```
```
2Dゲーム用UI素材（16bitドット絵風、和風ダークファンタジー）。無地のグレー背景、ラベル文字なし。
内容：画面右上に出す小さな「状況ゲージ枠」（霊界露見度・身体の危険度などを表示）。横長（1:6）、左に小さな丸いアイコン枠（中は空）、右にゲージの溝（中は空）。
横に3色：①青白（霊界）②橙（肉体）③赤紫（危険）。
```
```
2Dゲーム用UI素材（16bitドット絵風、和風、黒地に金）。無地のグレー背景、ラベル文字なし。
内容：画面中央上に一瞬出る「お知らせの帯（リボン）」。横長（1:7）、左右の端が燕尾形に切れた黒い布の帯、金の刺繍の縁、中央は文字用に無地。
横に3種：①金（記録・ART解放）②青白（霊体関連）③赤（警告）。
```
```
2Dゲーム用のロゴ素材（16bitドット絵風、和風ダークファンタジー、金と黒、鎖と魂の糸の装飾）。無地のグレー背景。
次の英字ロゴを1つずつ横長に作る（縦に並べる）：「STAGE CLEAR」「TRUE END」「ENDING」「CHECKPOINT」「GAME OVER」。
文字は金属感のある金色、黒い縁取り、背後に青白い魂の光。読みやすい太めのセリフ体。
```
```
2Dゲーム用の小さなUIアイコン（16bitドット絵風、和風、金と紺）。無地のグレー背景、ラベル文字なし、正方形のアイコンを横一列に並べる。
内容：①早送り（文字送り速度）②再生ループ（オート）③巻物（ログ）④歯車（設定）⑤本（ヒント）⑥一時停止。各アイコンは丸い金縁のメダル型。
```
