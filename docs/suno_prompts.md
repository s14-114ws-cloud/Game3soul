# SOUL TETHER — Suno 用プロンプト

Suno の Custom モードで、各曲の **Title / Style of Music / Lyrics** をそれぞれの欄に貼ってください。
インスト曲は Instrumental をオンにする（または Lyrics 欄に `[Instrumental]` だけ入れる）。
できたら **保存名** のファイル名で送ってください（mp3 / m4a どちらでも可）。ループ再生するので、終わりが頭へ自然につながる曲が理想です。

優先度：★★★＝今すぐ効果大　★★＝あると良い　★＝余裕があれば

---

## 1. タイトル（歌あり・オープニング主題歌）★★★
保存名：`song_title.m4a`　※タイトル画面でループ

**Title**
```
魂の糸
```
**Style of Music**
```
Japanese anime opening, dark fantasy, emotional J-rock ballad, female vocal, piano intro, strings, distorted guitar in chorus, taiko accents, music box, 140 BPM, melancholic yet hopeful, cinematic
```
**Lyrics**
```
[Intro - Music Box and Piano]

[Verse 1]
目を覚ました白い部屋
動かない指先 遠い声
胸の奥から 引かれる糸
まだ帰れると 誰かが言った

[Pre-Chorus]
見えないものが 見えてしまう
怖くても 止まれない

[Chorus]
切れないで 魂の糸
離れても 帰る場所がある
夜を越えて 君を探す
この手で 未来を斬り開け

[Verse 2]
名前のない 少女の影
笑うほどに 寂しそうで
ふたりで辿る 赤い糸
終わりの朝まで 手を離さない

[Pre-Chorus]
壊れた記憶 繋ぎ直して
何度でも 立ち上がる

[Chorus]
切れないで 魂の糸
離れても 帰る場所がある
夜を越えて 君を探す
この手で 未来を斬り開け

[Outro - Piano]
帰ろう 一緒に
```

---

## 2. 通常ボス（インスト）★★★
保存名：`bgm_boss.m4a`

**Title**
```
Grudge in the Lantern Light
```
**Style of Music**
```
Instrumental, intense boss battle, Japanese dark fantasy, driving taiko drums, shamisen riffs, aggressive string ostinato, heavy electric guitar, choir stabs, 160 BPM, minor key, relentless, seamless loop
```
**Lyrics**
```
[Instrumental]
```

---

## 3. 最終ボス（コーラスあり）★★★
保存名：`bgm_boss_final.m4a`　※ST11・ST12 の最終戦

**Title**
```
Sever the Last Thread
```
**Style of Music**
```
Epic final boss battle, dark symphonic metal, latin-style choir chanting Japanese words, pipe organ, full orchestra, taiko, double bass drums, 170 BPM, desperate and heroic, cinematic climax, seamless loop
```
**Lyrics**
```
[Intro - Organ and Choir]

[Choir]
還れ 還れ 魂よ
糸を断つ者に 朝は来ない

[Instrumental Break - Strings and Guitar]

[Choir]
ひとつに縫われた 夜の聖堂
それでも 我は 我として還る

[Instrumental Break - Taiko and Organ]

[Choir - Climax]
還れ 還れ 魂よ
還れ 還れ 魂よ
```

---

## 4. ステージ曲・序盤（病院／雨の住宅街／廃校）★★
保存名：`bgm_stage_early.m4a`

**Style of Music**
```
Instrumental, eerie but gentle exploration music, Japanese horror atmosphere, soft synth pads, plucked koto, music box, light percussion, rain ambience, 100 BPM, lonely and curious, seamless loop
```
**Lyrics**
```
[Instrumental]
```

## 5. ステージ曲・中盤（兵装施設／工場／墓苑／地下鉄）★★
保存名：`bgm_stage_mid.m4a`

**Style of Music**
```
Instrumental, tense exploration music, industrial dark fantasy, low strings, taiko pulses, metallic percussion, shakuhachi, ominous synth bass, 115 BPM, mysterious and driving, seamless loop
```
**Lyrics**
```
[Instrumental]
```

## 6. ステージ曲・終盤（研究塔／境界／天守／大聖堂）★★
保存名：`bgm_stage_late.m4a`

**Style of Music**
```
Instrumental, grand sorrowful exploration music, ethereal choir pads, pipe organ, strings, celesta, distant bells, 96 BPM, emotional and climactic, sacred and haunting, seamless loop
```
**Lyrics**
```
[Instrumental]
```

---

## 7. EX 零番室（インスト）★
保存名：`bgm_stage_EX_zero_room.m4a`

**Style of Music**
```
Instrumental, dark ambient suspense, deep drones, heartbeat pulse, reversed piano, glitchy textures, faint music box melody, 70 BPM, cold laboratory, dread and discovery, seamless loop
```
**Lyrics**
```
[Instrumental]
```

## 8. 零号観測者（EX ボス・コーラスあり）★
保存名：`bgm_boss_zero_observer.m4a`

**Style of Music**
```
Epic dark boss battle, glitch orchestral, eerie children choir, distorted bells, industrial percussion, organ, 150 BPM, alien and terrifying, origin of everything, seamless loop
```
**Lyrics**
```
[Intro - Glitch and Bells]

[Choir - Whisper]
帰還ハ 恐怖
肉体ハ 檻

[Instrumental Break]

[Choir]
全テノ 魂ヲ 零ヘ
全テノ 魂ヲ 零ヘ

[Instrumental Break - Climax]
```

## 9. 緊迫シーン（大鴉の説得など）★
保存名：`bgm_tension.m4a`

**Style of Music**
```
Instrumental, emotional tension, solo cello and piano, soft taiko heartbeat, wind, slow build, 72 BPM, sorrow and hope, seamless loop
```
**Lyrics**
```
[Instrumental]
```

---

### 差し替えの仕組み
- 保存名どおりのファイルを送ってもらえれば、今の仮音源と自動で入れ替わります。
- ステージ曲を個別に作りたい場合は、`bgm_stage_01_sleeping_hospital` 〜 `bgm_stage_12_return_cathedral` の名前で送ってください（無い分は上の序盤・中盤・終盤曲を使います）。
- 歌ありの曲は会話中に少し音量を下げます。
