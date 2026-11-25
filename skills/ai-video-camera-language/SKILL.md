---
name: ai-video-camera-language
description: Camera angles, lenses and camera movement for AI video generation (Seedance, Kling, Veo, Sora, MiniMax/Hailuo, Runway, Wan, Luma). A tested library of shot types with copy-paste prompt wording, rules for camera speed, the snap-zoom-and-hold move, what to avoid (whip pans, shake, speed ramps on generated footage), and a script that measures camera speed with optical flow so you can pick the calmest part of a clip. Use when writing camera directions in a video prompt, choosing shot types for a storyboard, when a generated clip feels too fast, shaky or lifeless, or when someone asks about camera angles, camera moves or cinematography for AI video.
license: MIT
metadata:
  author: Klakix
  homepage: https://klakix.com/ai-video-skills
  version: "1.0.0"
---

# Camera language for AI video

Viewers forgive a lot in AI video. They do not forgive a camera that will not sit still.
The single strongest complaint across our productions was "the camera is so fast it's
bad", and the second was the over-correction: "everything is frozen, lifeless".
The rule that resolves both: **the camera is calm, the world is alive.**

## Rules

1. **One camera move per shot.** A 4 to 8 second clip gets one slow, motivated move, or none.
   Put the camera sentence last in the prompt and end it with "nothing fast".
2. **Never speed up generated footage in the edit.** Speeding a clip 1.5x to 1.7x was the
   direct cause of our worst feedback. Slow-motion ramps are fine; speed-ups are not.
   If you need energy, cut on the beat or add a 2 to 4 frame flash/glitch at 3 or 4 key moments.
3. **Measure, don't guess.** Downscale to 160 px width, take the median Farneback optical
   flow between consecutive frames. Target average ≤ 1 px/frame, peak ≤ 1.5. Shots our
   audience liked measured 0.2 to 1.2; shots they complained about measured 2 to 5.
   Run `scripts/camera_speed.py clip.mp4 --window 3` to get the numbers and the calmest
   3-second window to use in the edit.
4. **Calm words go on the camera, not the subject.** "The camera is almost still" plus
   "she laughs, turns, waves at the waiter" is alive. "Everything is calm and gentle" is dead.
5. **Avoid in the prompt:** whip pans, handheld shake, motion blur on the subject, crash
   cuts inside one generation, "dynamic camera", "epic sweeping shot". Models over-deliver
   on energy words.
6. **Two consecutive shots never share an angle.** Alternate scale (wide, medium, close)
   and height (low, eye level, high) so cuts feel intentional.
7. **Effects go in the prompt, not in post.** If you want a snap zoom or a dolly zoom, ask
   the model for it. Zooming or punching in on a 480p generation in the edit softens it and
   adds jitter (and ffmpeg's `zoompan` rounds to whole pixels, so slow zooms shimmer).

## The move audiences loved: snap zoom and hold

Over-the-shoulder medium shot on a 50 mm lens, a soft out-of-focus element in the
foreground, the subject sharp. Static for 0 to 2 seconds, one fast snap zoom-in exactly
on the joke or reveal, then hold sharp and steady. No whip, no shake, no motion blur.

```
Over-the-shoulder medium shot from just behind the character's shoulder on a 50mm lens:
her collar and hair softly out of focus in the foreground, the subject sharp.
0-2s: the camera is still. At 2s a fast snap zoom-in to the key detail, then hold steady
and sharp. No whip pans, no shake, no motion blur.
```

Models do not deliver it every time (in one batch it worked on most shots and was ignored
on one). Budget one retry for the shots where the zoom is the joke.

## Shot library

Full wording for 14 tested moves plus 3 to avoid is in
[references/camera-library.md](references/camera-library.md). Quick index:

| Move | Use it for | Risk |
|---|---|---|
| Snap zoom + hold (OTS 50 mm) | the reveal, the punchline | may be ignored, retry |
| Locked-off low hero angle (24 mm) | opening hook, ground-level hero | none |
| Static top-down drone | drifts, crowds, formations, maps | none |
| Slow-motion low push-in (35 mm) | money, sparks, dust, one "flex" moment | slow-mo can drift |
| Symmetrical one-point dolly (28 mm) | banquets, ceremonies, authority | none |
| Selfie POV (24 mm, arm's length) | character talks to camera | phone may appear, say "no phone visible" |
| Static over-the-shoulder (50 mm) | screens, phones, car interiors | none |
| FPV dive + follow | one continuous flight through a scene | needs a reference video to stay controlled |
| Rising aerial reveal | openings, scale (armies, highways) | borderline speed, measure it |
| Gimbal tracking | walking or galloping subject, long takes | held up even in 30 s takes |
| Slow handheld push-in | documentary comedy, dialogue | none |
| Slow lateral dolly | lines of people, two-shots | none |
| Locked tripod wide | gag lives in the frame, not the move | can look dead, add background life |
| In-car, camera faces driver | vehicle interiors in FPV/3D flights | driver vanishes unless stated |

## When a clip comes back wrong

| Symptom | Fix |
|---|---|
| Too fast / dizzying | remove extra moves, end with "nothing fast", use the calmest window from `camera_speed.py` |
| Frozen, lifeless | add 2 to 3 timed action beats and background motion; keep the slow camera |
| Model cut to a different angle mid-clip | add "single continuous shot, no cuts" |
| Camera ignored the move | put the camera sentence last, use lens + distance words, retry once |
| Shaky | "camera on a tripod" or "smooth gimbal", plus "no shake" |
| Subject left the frame | "the camera never loses the subject", or "he never disappears from frame" |

## Scripts

- `scripts/camera_speed.py` — per-frame camera motion (px/frame at 160 px width), average,
  peak, verdict, and the calmest N-second window. Requires `opencv-python` and `numpy`.

```bash
python scripts/camera_speed.py shot.mp4 --window 3
python scripts/camera_speed.py shots/*.mp4 --csv speeds.csv
```
