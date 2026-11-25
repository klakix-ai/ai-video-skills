---
name: phone-screen-compositing
description: Put a realistic, perfectly stuck phone, tablet or watch screen (chat, notification, order tracking, map, listing) into AI-generated video. Generate the shot with a flat chroma-key green screen, track the four screen corners with sub-pixel accuracy and no temporal lag, render the UI frame by frame, and composite it with perspective, finger occlusion and screen glow. Includes track_screen.py. Use when a video joke or ad depends on what is on a phone screen, when a composited screen slides or jitters, or when someone asks how to add a phone screen / screen replacement to AI video.
license: MIT
metadata:
  author: Klakix
  homepage: https://klakix.com/ai-video-skills
  version: "1.0.0"
---

# Phone screen compositing for AI video

Video models cannot render readable, correct UI text. Full-screen UI cards cut between
shots look like a slideshow ("disgusting" was the verdict on ours). A phone held in the
scene with the UI tracked onto it looks real, and many "history + today" jokes live on a
phone screen: a chat, a delivery tracker, a listing, a notification.

## 1. Generate a green-screen shot

Key frame (image model): the character holding the phone, screen facing camera, "the
screen is flat, evenly lit, pure chroma-key green, no content, no reflections".

Video prompt (Kling held this 5 of 5 times for 5 s; most models drift without it):

```
The phone screen stays a perfectly flat, evenly lit, uniform pure chroma-key green the
entire time: no content, no reflections, no glare, it never turns off.
```

Negative prompt (if supported): `content on the phone screen, glare, screen turning black`.

Keep hand motion moderate: fast wrist turns and armour/fabric covering the screen are the
hard cases.

## 2. Track the corners: `scripts/track_screen.py`

```bash
python scripts/track_screen.py shot.mp4 corners.json --preview preview_dir
```

How it works and why:
- Greenness = G − max(R, B); largest connected component = the screen.
- Corners: convex hull → 4-point polygon → fit straight lines to the **sub-pixel** contour
  of each edge (greenness map upscaled 4x, contour at 0.5) → intersect the lines. Rounded
  phone corners are excluded from the line fits, so you get sharp virtual corners.
- Corner order is matched to the previous frame, so the top-left corner does not jump
  when the wrist rotates.
- **No temporal smoothing.** This is the important part. Savitzky-Golay smoothing over 5 to
  9 frames made the UI lag behind the phone in fast motion (up to 27 px at 716 px width,
  2 to 3x more visible after upscaling and zooming). Only nearly-still frames (< 0.5 px/frame)
  get a tiny 1-2-1 filter; above 2 px/frame the raw measurement is used.
- Outlier frames (area off by > 12% from neighbours) are dropped and interpolated.
- Finger: non-green pixels inside the screen quad are reported as the fingertip's
  position in screen coordinates (0 to 1), so you can scroll the UI with the thumb.

Verify: the difference between the raw and the final corners should be ~0 to 0.3 px in
moving frames.

## 3. Render the UI

- Build the UI as HTML and render frame by frame (Playwright screenshots), or with
  Remotion/After Effects. A neutral iOS-like layout and font; no real app names or logos
  ("Messages", not a trademarked name).
- Animations calm and iOS-like: no overshoot/bounce, small slides (~14 px), slow pulses.
  Never add a full-frame "vibration" shake.
- For scrolling content, drive the scroll from the tracked fingertip so it follows the
  thumb. It is surprisingly convincing.

## 4. Composite: `scripts/composite_screen.py`

```bash
python scripts/composite_screen.py shot.mp4 corners.json ui.png out.mp4          # still UI
python scripts/composite_screen.py shot.mp4 corners.json ui_frames/ out.mp4      # animated UI
```

It warps the UI into the quad, keys fingers in front, turns leftover green at rounded
corners into the bezel colour, clamps green spill, and keeps the source audio.

- Perspective-warp the UI into the corner quad (`cv2.getPerspectiveTransform` +
  `warpPerspective`, cubic).
- Matte from greenness with a soft alpha, so fingers and anything in front of the screen
  stay in front.
- Realism: slight blur (σ ≈ 0.55), ~93% brightness, a faint glass reflection, and at night
  a little screen light spilling onto the face and fingers.
- If the screen is small, crop the **raw** generation (not a resized one) before upscaling.
- Upscaled clips: track on the raw clip, then scale the corners by separate x/y factors
  (e.g. 1076/716 and 1928/1284) and verify frame alignment after the upscaler.

## Occlusion

When the phone passes behind armour, a sleeve or a hand, the contour shrinks. Per-frame
"consistency" rules accumulate drift (we measured 94 px). Practical fix: keep occluded
frames out of the edit window. The script has `--occlusion` that re-estimates up to two
bad corners from the others with a similarity transform; use it only when needed.

## Moves in post

If you push in toward the phone, do it with a sub-pixel warp centred on the tracked screen,
not ffmpeg `zoompan` (whole-pixel rounding = jitter on the UI).
