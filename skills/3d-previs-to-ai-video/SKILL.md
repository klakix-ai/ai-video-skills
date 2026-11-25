---
name: 3d-previs-to-ai-video
description: Control AI video camera paths and choreography with a 3D blockout (previs) - build a grey-box scene in Blender, three.js or any 3D tool, animate a camera, render a reference video and pass it with character/vehicle/location reference images to Seedance 2.x reference mode (@Video1 + @Image map). Covers blockout rules, one-move-per-shot camera paths, transformations planned inside the blockout, contact-sheet checks, in-vehicle cameras and realism wording. Use for FPV flights, car transformations, complex choreography, exact camera moves, "Seedance with previsualization in Blender", or when text prompts cannot get the camera move right.
license: MIT
metadata:
  author: Klakix
  homepage: https://klakix.com/ai-video-skills
  version: "1.0.0"
---

# 3D previs to AI video

Text cannot describe an exact FPV path through a street or the moment a car falls apart
and reassembles into another car. A 3D blockout can. Reference-mode video models (Seedance
2.x) copy a reference video's camera motion and timing remarkably well, and take their
*look* from reference images. You get the control of 3D with the realism of video models.

## Pipeline

1. **Block out the scene** with simple shapes: ground, buildings as boxes, characters as
   capsules, vehicles as boxes with wheels. Neutral grey materials, plain daylight.
2. **Animate the camera** (one move per shot, see rules) and the key objects.
3. **Render a contact sheet** (3 to 6 frames) and check it before anything else.
4. **Render the reference video** at the target aspect ratio and duration (8 to 15 s;
   1280 px on the long side is enough).
5. **Make reference images**: character sheet, vehicle multi-angle sheet, location photo.
   Prefer real photographs for locations and vehicles (faces and logos removed).
6. **Generate** with the blockout as @Video1 and the images as @Image1..n, using a
   reference map prompt (template below). Draft at 480p, final at 720p if the frame will
   be shown large.
7. **Compare side by side** (blockout above, result below) to check the camera followed.

## Blockout rules

- **Neutral grey, plain daylight.** Golden-hour blockouts made results dark and orange.
  The look comes from the prompt and image references, not the blockout's lighting.
- **One camera move per ≤ 8 s shot.** Three moves (dive + follow + rise) in one 8 s shot
  produced "the camera is so fast it's terrible". Keep the camera speed modest; measure the
  render with `ai-video-camera-language/scripts/camera_speed.py`.
- **Hero elements in frame at the end** of the move; the last frame is what viewers
  remember.
- **Background at a sane distance**: auto-generated layouts put mountains right behind the
  crowd, filling the frame with giant grey cones. Keep far scenery at least 3 to 4 times
  the depth of the main action.
- **The camera must see what matters.** A distant final camera made a 60-rider formation
  invisible. Fix it in the blockout, where edits are free.
- **Transformations happen inside the blockout too.** If a car turns into another car,
  build matching part groups (doors, hood, wheels) parented to one root and have them sink
  and rise in sequence; the prompt then counts the same seconds. Do not change a part while
  the camera is right next to it.
- **In-vehicle shots**: keep the camera in front of the seat backs, facing the driver, so
  the driver never leaves the frame.

## Prompt template (reference mode)

```
IMAGE / VIDEO REFERENCE MAP
@Video1 is a grey 3D blockout: it defines ONLY the camera path, timing and the positions
of the objects. Copy every camera move of @Video1 exactly. Ignore its grey materials and
lighting.
@Image1 is the courier (character sheet). @Image2 is the scooter. @Image3 is the street
(real photo).

Real FPV footage on an actual street, true-to-life colours, realistic exposure, motion
blur only on the background, dust and grime. Not CGI.

0-3s: the camera dives from rooftop height toward the courier from @Image1 riding the
scooter from @Image2 along the street from @Image3.
3-6s: it follows low behind him, weaving between parked cars.
6-8s: it rises over the intersection and holds on him as he stops at the café.
The camera never loses the subject. No text, no logos, no badges.
```

For transformations, describe material, not effects: "paint and panels crumble into fine
metal flakes and dust, revealing a glossy surface beneath; no wireframe, no hologram grid".

## Realism notes

- "35mm film, golden hour, lens flare" pushed results toward CGI. "Real FPV footage on an
  actual street, true-to-life colours, not CGI" fixed it.
- Generated location images carry a postcard look; real photos made the street believable.
- Characters: AI-generated faces pass reference filters, real-person photos do not, and
  multi-panel realistic sheets are rejected more often than single images. If a request
  with a character sheet is rejected, retry once without the face images.

## Costs and timing (late 2026)

- Seedance 2.5 reference mode with a reference video is billed on input video seconds plus
  output seconds on most providers. One 8 s 480p shot with an 8 s blockout cost about
  $0.75 to $0.85; generation took 2.5 to 3 minutes.
- Planning with an LLM that writes the scene graph: ~30 to 60 s and $0.12 to $0.20 per
  scene in our tests.
- Do the blockout iterations for free; pay only once the contact sheet is right.

## Tools

Blender (with an MCP bridge an AI agent can build the blockout for you), three.js in the
browser, Unreal/Unity, or any DCC that can render a camera animation to MP4. The model only
needs the video.
