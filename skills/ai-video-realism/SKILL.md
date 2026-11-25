---
name: ai-video-realism
description: Make AI images and AI video look like real footage instead of glossy "AI slop". Device-based realism (describe the phone, GoPro, broadcast camera that shot it and its flaws), what words push models toward CGI, real-photo references for locations and vehicles, key frames with photographic image models, natural colour instead of heavy film looks, and absurd-but-real comedy. Use when output looks fake, plastic, too perfect, too cinematic or like a video game, when someone asks for "hyper-realistic", "photorealistic", "looks like a real video", or when planning key frames for an AI video.
license: MIT
metadata:
  author: Klakix
  homepage: https://klakix.com/ai-video-skills
  version: "1.0.0"
---

# Realism for AI video

The word "realistic" does almost nothing. What works is describing **how the footage was
captured** and letting the imperfections of that capture do the convincing.

## 1. Describe a device, not a style

Pick who filmed the scene and with what, then list that device's flaws:

| Device | Wording | Built-in flaws to name |
|---|---|---|
| Neighbour's phone from a balcony | "filmed on a phone from a third-floor balcony, slightly tilted" | digital noise, blown-out sky, railing in the foreground, quick zoom steps |
| Fan's phone in a crowd | "shot on a phone held up in a crowd" | heads blocking the frame, auto-exposure pumping, screen glare |
| Head-mounted action camera | "GoPro on a helmet" | fisheye edges, wind noise, horizon tilt |
| Underwater action camera | "underwater action camera" | blue-green cast, particles, soft focus |
| Broadcast telephoto | "TV broadcast camera with a long telephoto lens from the stands" | compressed depth, slight heat shimmer, tight framing |
| On-camera flash DSLR | "point-and-shoot with direct flash at night" | harsh shadows, red-eye, dark background |
| Security / dashcam | "fixed CCTV camera high in a corner" / "dashcam" | wide distortion, timestamp-free, low contrast |

A dinosaur walking down a residential street became believable the moment the frames were
"filmed by a neighbour on a phone from the balcony": same street, same balcony, every shot.
Keep the device consistent across the whole video; a sudden switch to "cinema" breaks it.

## 2. Words that push toward CGI (avoid)

`cinematic, epic, 8k, ultra-detailed, masterpiece, dramatic rim light, golden hour,
lens flare, anamorphic, 35mm film, film grain, HDR, octane, unreal engine, hero shot`

These describe *other AI images*. They produce posters.

## 3. Words that push toward footage (use)

```
Real documentary footage shot on location, ordinary soft daylight, natural true-to-life
colours, realistic exposure, real skin texture with visible pores, dust and wear on
surfaces, ordinary people who are not posing, nobody looks at the camera.
The absurd thing is treated as if it really happened. No stock-photo look, no readable
signage, no text on screen, not CGI.
```

Note: the "daylight" recipe is for day scenes. For night, name the actual light sources
(sodium streetlights, phone screens, a single bulb) and run a light test.

## 4. Key frames: start from a photographic still

For each shot generate a still first, then animate it (image-to-video) or use it as a
reference. In side-by-side tests, GPT Image 2.x at its highest quality setting
(1440x1080 for 4:3) produced frames clearly more photographic than other models;
Nano Banana 2 was better at exact small details and text. Key frames double as an approval
step: people judge quality far better on a still.

For consistency across shots, generate one or two key frames from text, then create the
rest by **editing** those frames ("same street, same balcony, now the dinosaur is closer")
rather than from scratch.

## 5. Use real photos for places and products

Image models draw locations with a postcard aesthetic. For a real-looking street,
building or vehicle, use a real photograph as the reference: your own, or a freely licensed
one (Wikimedia Commons), with faces, flags and religious or political symbols cropped out.
For a branded vehicle, a real street photo plus a multi-angle reference sheet beat any
generated version. Check licences before commercial use.

## 6. Colour: natural beats "film look"

Our heavy post look (desaturated, teal-orange, lifted blacks, diffusion, glow, thick grain,
vignette) was called "suffocating". The approved pipeline:

- keep the model's natural colour;
- match clips to each other at **half strength** only;
- saturation 1.0, contrast about 1.03, gentle highlight roll-off;
- very light grain (barely visible at 1080p), very light vignette;
- always compare against the raw frame side by side; if your grade is darker or duller
  than the raw clip, undo it.

## 7. Scale, physics and logic

- State real sizes ("the cat is as tall as a three-storey building, its paw covers a car").
- Keep the same layout across shots (same street corner, same parked cars).
- Ordinary people react the way people do: phones out, stepping back, pointing; not
  posing heroically.
- Run the plan's "who sees what" check (see `ai-video-shot-planning`).

## 8. Things models add that break realism

| Artifact | Prevention |
|---|---|
| Car badges, logos, brand-like grilles | "no logos or badges on the car"; scrub frame strips, cut affected frames |
| Readable signs with garbled letters | "no readable signage"; add real text in the edit |
| Hologram/wireframe transformation effects | describe physical materials: "crumbles into fine metal flakes and dust" |
| Perfect symmetry, airbrushed skin | "real skin texture, visible pores, asymmetric, slightly messy hair" |
| Heroic posing crowds | "ordinary people who are not posing" |
| Night scenes crushed to black | name light sources; "every face well lit"; test first |
