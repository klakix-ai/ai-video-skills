---
name: ai-video-editing-and-pacing
description: Edit AI-generated clips into a finished short video - shot length and pacing rules measured on real audiences, cutting to a music beat grid, why you never speed up generated footage, sub-pixel camera moves instead of ffmpeg zoompan, upscaling raw clips before grading, natural colour matching, loudness, and a script that measures shot lengths of any video. Use when assembling AI video clips with ffmpeg, Python/OpenCV, Remotion, Premiere or DaVinci Resolve, when an edit feels too fast or too slow, when analysing the pacing of a reference reel, or when upscaling and colour matching AI clips.
license: MIT
metadata:
  author: Klakix
  homepage: https://klakix.com/ai-video-skills
  version: "1.0.0"
---

# Editing and pacing AI video

AI clips are generated in 4 to 10 second pieces and only 2 to 3 seconds of each are
usually the best. The edit decides whether the video feels calm and expensive or frantic
and cheap.

## Pacing rules (measured)

- **Shots ≥ ~2.6 s** (about one bar of music at 90 to 100 BPM). A first cut with a median
  shot of 1.29 s was "way too fast, everything flew by"; the recut at a median of 3.54 s
  (shortest 2.54 s) was approved.
- **Key gags get 4 to 5 s.** Let the reveal land and breathe.
- **Total 30 to 40 s** for story/comedy pieces on social. Viral references we measured ran
  18 to 24 s with a new joke every 2.4 to 2.9 s; when copying them, keep their structure
  but not their speed if your audience prefers calm.
- **Glitch/flash transitions only at 3 to 4 key moments**, on the beat. Everywhere else,
  straight cuts.
- **Exception**: a fast edit can be tolerated when every cut sits exactly on a beat and
  each shot carries a single clear joke (one approved piece had a ~1.9 s median).

Use `scripts/shot_stats.py` to measure your cut and any reference video:

```bash
python scripts/shot_stats.py reference_reel.mp4
python scripts/shot_stats.py my_cut.mp4 --threshold 0.3 --list
```

## Never speed up generated footage

Speeding clips up 1.5x to 1.7x to "add energy" produced the worst feedback of any change
we made. Use the calmest part of each clip at normal speed (`ai-video-camera-language`
has a script that finds it). Slow-motion ramps are fine.

## Choosing the best seconds of a clip

1. Make a frame strip every 0.5 s.
2. Discard: logic errors, logo/badge frames, face drift, the model's own mid-clip cut.
3. Prefer the window with the lowest camera speed that still contains the action beat.
4. Cut on motion (a turn, a step, a hand) or on the beat; not mid-blink.

## Beat grid

- Detect BPM, then verify by fitting a grid; automatic tempo estimates are often off by a
  few BPM (one track detected 129 BPM was really 127).
- Find bar starts: the phase of the 4-beat cycle with the strongest low-frequency energy.
- Cut on bar starts or beats; join music sections at bar starts with ~12 ms crossfades.
- Put the payoff on the drop; let the music stop for one key moment (silence is a cut too).
- Use generated or licensed music. Commercial songs get muted or claimed on Instagram,
  TikTok and YouTube, and cannot be used in ads.

## Camera moves added in post

Prefer asking the model for the move (see `ai-video-camera-language`). If you must add a
push-in, punch zoom or shake-free reframing in post:

- Do it with sub-pixel warps (OpenCV `warpAffine` with cubic interpolation) and eased
  curves. **ffmpeg `zoompan` rounds position to whole pixels**, so slow zooms shimmer.
- Do it on the upscaled clip, not the 480p original.
- Moves we used: slow push/pull, push toward a tracked point (a phone screen), a punch
  zoom on the beat (1.08 to 1.10 back to 1.0 over 9 frames), a 4-frame zoom-through with
  radial blur, a 2-frame colour split.

## Upscale first, grade second

1. Upscale **raw** clips (before grain, colour, overlays) to 1080p with a video upscaler
   (Topaz-class models). It sharpens texture, eyes, skin and metal far beyond a resize.
   A 5 s clip cost about $0.04 at 1080p in late 2026.
2. Then colour-match, add grain and overlays at 1080p, so text and UI stay crisp.
3. Upload limits: if your upscaler limits uploads per hour, concatenate same-size clips
   (with 4 black frames between them) into ≤ 30 s groups, upscale once, split back by frame
   number. Verify frame counts are preserved.
4. Some upscalers return slightly different sizes (e.g. 1452x1080 for 4:3); crop to the
   delivery size in the edit.

## Colour

- Keep the model's natural colour. Match clips to each other at half strength.
- Saturation 1.0, contrast ~1.03, soft highlight shoulder, very light grain and vignette.
- No teal-orange, no lifted blacks, no diffusion/glow stacks: called "suffocating".
- Always A/B against the raw frame before committing a look.

## Audio finishing

- Final -14 LUFS integrated, true peak ≤ -1 dBTP (see `ai-video-dialogue-and-voice/scripts/loudness.py`).
- Low sub-bass hits (55 to 32 Hz) on drops and the final beat feel big on phones with
  headphones and cost nothing.
- Keep the model's native ambience under music for realism.

## Text, captions and brand

- Captions: white, bold, 1 to 3 words at a time, one accent colour. Outline them over sky.
- For **organic social reach**, things that make a video look like an ad (big branded
  intro, model/brand credit lines, a long black end card) correlated with lower reach in
  our small test (3 branded videos stayed in the first test pool while unbranded edits of
  similar footage went further). Keep branding to a small mark at the end, or none, and
  put credits in the caption.
- For landscape (4:3/16:9) deliveries, reposition captions and end cards for that frame;
  do not reuse vertical layouts.

## ffmpeg gotchas

- `xfade` needs matching time bases: add `settb=AVTB` to both inputs.
- When ffmpeg is launched from Python, pass `-nostdin` or it may hang waiting for input.
- `aecho`'s second parameter is output gain for the whole signal (0.25 = -12 dB), not just
  the echo.
- RMS matching does not match perceived loudness; use LUFS.
- Windows: write scripts with LF line endings if they will run on Linux.
