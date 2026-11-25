---
name: ai-video-dialogue-and-voice
description: Dialogue, voice and lip sync for AI video characters. Replace the video model's inconsistent generated speech with one fixed TTS voice per character, time-align the recording to the lips with WSOLA using word timestamps, keep the model's own ambience and laughs as the bed, mix to loudness targets, and verify every line with speech-to-text. Includes align_to_lips.py and loudness.py. Use when an AI character talks, when generated speech is garbled, sounds fake or changes between shots, when dubbing AI video into another language, or when mixing dialogue, music and effects for a short video.
license: MIT
metadata:
  author: Klakix
  homepage: https://klakix.com/ai-video-skills
  version: "1.0.0"
---

# Dialogue and voice for AI video

Video models with native audio (Seedance, Veo, Kling) produce a different voice every
shot, and in long or multi-speaker takes they garble words (in one Turkish take "Saranda",
"imbaza" appeared out of nowhere). The fix is to keep their *picture and ambience* and
replace their *speech*.

## Pipeline

1. **Write lines short.** One breath each. On-screen lines max ~10 words for social.
2. **Record the line with the character's fixed TTS voice** before generating video.
   - Pick a professional library voice, not a designed/synthetic one. In blind-ish
     comparisons designed voices were "very fake"; professional narrators "cinematic".
     Let the person choose from 2 to 3 candidates.
   - Expressive models with tags (for example ElevenLabs v3/v4): stability ~0.5,
     similarity ~0.8. Use meaningful tags (`[whispers]`, `[calling out]`); avoid stacked
     emotion tags. `[shouting]` pushed a male voice up to a childish pitch; `[calling out]`
     kept it natural.
   - Generate 2 to 4 takes at slightly different tempos.
3. **Pass the recorded line as an audio reference** (Seedance `@Audio1`) so the model
   animates the lips to roughly the same words and rhythm.
4. **Transcribe both** (the TTS take and the generated video's audio) with word timestamps
   (Whisper/faster-whisper with `word_timestamps=True`, or ElevenLabs Scribe).
5. **Align** the TTS take to the lips: `scripts/align_to_lips.py` anchors every word start
   in the recording to the same word in the video and time-stretches between anchors with
   WSOLA (no pitch change). Pick the take that needs the least stretching (≤ ~25%).
   - **Only stretch on-screen speakers.** Off-screen or behind-camera voices are placed at
     natural speed; stretching them only adds artefacts.
6. **Build the bed from the model's own audio.** Its ambience (footsteps, wind, crowd,
   clinking cups) is perfectly in sync. Duck its *speech* deeply (-40 dB) inside a mask of
   word times ±0.12 s, and apply a **fixed** gain to the bed.
   - Echo trap: never loudness-normalise the ducked bed on its own; that pulls the residual
     speech back up 10 to 30 dB and you hear a ghost double.
7. **Keep the model's laughs.** TTS laugh tags sound fake. Cut the model's own laugh from an
   isolated stem (voice isolation tool) so it stays in sync with the face.
8. **Mix and measure** (`scripts/loudness.py`):
   - final -14 LUFS integrated for social, true peak ≤ -1 dBTP;
   - lead character about -18 LUFS, side characters -19.5, off-screen voices -20.5;
   - speech should sit **at least 12 dB, ideally 18+ dB, above the bed** (measure stems);
   - if a single spike forces loudnorm into dynamic mode, use linear gain + a limiter.
9. **Verify by transcription.** You cannot listen; a transcript can. Run STT on the final
   mix: every line must read correctly and the model's garbled words must be gone. Also tag
   audio events to catch wrong sound effects (a generated "razor" effect once came back as
   an outro jingle).

## Prompt tips for scenes with speech

- Off-screen speakers: "the mother is unseen; we only hear her voice".
- Let the scene breathe: give 0.5 to 1 s before the first word.
- Keep non-verbal sounds (shushing, a group sigh, armour clanks) from the model.

## Music and effects

- Generate music instead of using commercial tracks; commercial songs get muted or claimed
  on social platforms. Mention AI-generated music in the caption where required.
- Music must not fight dialogue: none, or -8 to -10 dB under speech, pulled back ~0.6 s
  before a punchline. A spoken call to action plays without music.
- Sound effects land just before a cut or on graphic events, not randomly.

## Scripts

`scripts/align_to_lips.py` — WSOLA alignment from two word-timestamp files.

```bash
# words JSON format: [{"word": "hello", "start": 0.42, "end": 0.71}, ...]
python align_to_lips.py --audio line_take2.mp3 --audio-words take2_words.json \
  --video-words shot3_words.json --duration 5.04 --out shot3_voice.wav

# helper: get word timestamps with faster-whisper (pip install faster-whisper)
python align_to_lips.py --transcribe shot3.mp4 --language tr > shot3_words.json
```

`scripts/loudness.py` — integrated loudness, loudness range and true peak via ffmpeg.

```bash
python loudness.py final_mix.mp4 dialogue_stem.wav bed_stem.wav
```
