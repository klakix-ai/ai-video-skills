---
name: ai-character-consistency
description: Keep the same AI character (face, body, outfit, voice) consistent across many images and video shots. Covers building a character sheet / turnaround that does not drift, identity markers, per-shot reference sets for Seedance 2.x reference mode, Kling elements, Veo and Runway references, period costumes as separate references, avoiding "real person" safety rejections, and keeping one voice per character. Use when creating an AI influencer, mascot, recurring character or series, when a face changes between shots, when a model rejects a face reference, or when someone asks about character consistency, character sheets or consistent characters in AI video.
license: MIT
metadata:
  author: Klakix
  homepage: https://klakix.com/ai-video-skills
  version: "1.0.0"
---

# AI character consistency

A recurring character is the most valuable asset in AI video and the easiest one to lose.
Consistency is not a prompt trick; it is a pipeline: one locked core portrait, a sheet
generated from it angle by angle, a fixed list of identity markers, and the right subset
of references for each shot.

## 1. Write the character bible first

```
Name:        Mira (fictional), 23
Look:        warm olive skin, light freckles across the nose, hazel-green eyes,
             curtain bangs, shoulder-length dark brown hair
Identity markers (must appear every time):
             ONE mole on the LEFT cheekbone only · freckles · hazel-green eyes ·
             curtain bangs · small gold hoop earrings
Body:        165 cm, slim, natural posture
Default outfit: sage-green knit sweater, straight jeans, white sneakers
Voice:       one fixed voice ID, stability 0.5, similarity 0.8 (see voice skill)
Never:       a second mole, a mole on the right side, heavy makeup, a different eye colour
```

Identity markers are what viewers use to recognise the character, and they are what you
check in every frame. Make them specific and asymmetric (left vs right) so drift is visible.
"Cute but unique, very much like a normal person" worked far better for realism than
"beautiful model".

## 2. Build the sheet so the face does not drift

Do **not** ask an image model for a multi-panel sheet in one generation; faces drift
between panels and the sheet looks like six cousins.

1. Generate 4 candidate portraits from the bible. Pick one: the **core portrait**.
2. Generate every angle **separately and at high resolution**, each time passing the core
   portrait as the reference: front, 3/4 left, profile, back, full body front, full body 3/4,
   plus close-ups of the identity markers.
3. Assemble the sheet locally (grey background, aligned figures, equal scale). A simple
   PIL/ImageMagick layout script is enough.
4. Add an expressions page (neutral, laugh, surprise, talking) generated the same way.

The strongest image models for this (late 2026) were GPT Image 2.x and Nano Banana 2 edit
modes; GPT Image gave the most photographic skin, Nano Banana held masks and small details
most precisely.

## 3. Choose references per shot, not per project

Reference-capable video models (Seedance 2.x reference mode accepts up to 9 images on 2.0
and up to 30 on 2.5) do best with a **small, relevant** set:

| Shot | Pass |
|---|---|
| Face visible, talking | core portrait + 3/4 angle + outfit or costume image |
| Full body action | full-body front + full-body 3/4 + costume |
| Hands, back, costume detail (no face) | **face-free crops** of the costume only |
| New location | add a location image as its own reference, described in the reference map |

Name every reference in the prompt with a reference map (`@Image1 = character, front;
@Image2 = costume`). See `ai-video-prompting`.

Prefix wording matters: "@Image1: keep the look of this character" keeps identity and
lets the scene move. "Keep exactly as in @Image1" freezes pose and composition and makes
the shot lifeless.

## 4. Costumes and eras

The character changes clothes; the face does not. For period or themed scenes:

1. Generate a costume image on its own (on the character, from the core portrait).
2. Pass it as a separate reference: `@Image3 = costume for this scene`.
3. Keep one signature accessory (earrings, necklace) for recognisability.
4. Specify footwear and practical details or the model invents them ("flat leather shoes
   with no heels", otherwise you get stilettos in a medieval castle).

Modern clothes in a historical scene look like a mistake unless "time traveller" is the
explicitly chosen joke.

## 5. Safety filters and faces

Video model providers run "real person" classifiers on image references.

- **AI-generated faces pass; photos of real people are rejected.** Seedance 2.5 accepted
  our photorealistic AI character in image-to-video, reference and reference + audio modes.
  It rejected a product photo with a real model ("input image may contain real person").
- **Multi-panel realistic sheets are rejected more often** than single portraits. Pass
  single images.
- **Face references pass less often than face-free ones**: in one production 15 of 23
  requests with face references passed; face-free references passed 6 of 6.
- **The decision depends on the prompt + image pair** and tends to repeat for the same
  pair. If a request is rejected, change the set (swap a portrait for a face-free costume
  crop, or the other way round) instead of resubmitting.
- **Rejections are usually free and arrive in about 30 seconds.** For shots where the face
  is not visible, always use face-free crops.
- Never use a real person's likeness, a celebrity, or a named historical figure. Even an
  army or era name ("Seljuk soldiers") can trip text classifiers; describe the costume
  instead.

## 6. The voice is part of the character

Video models generate a different voice every shot. Record all lines with one fixed TTS
voice and align them to the lips; see `ai-video-dialogue-and-voice`. Professional library
voices sounded far more natural than designed/synthetic voices in our tests.

## 7. Per-shot consistency checklist

- [ ] Every identity marker present and on the correct side
- [ ] No extra marks (a new freckle cluster or mole on the wrong cheek is drift)
- [ ] Hair length, parting and bangs match
- [ ] Costume matches the scene's reference; accessories present
- [ ] Skin texture is photographic, not airbrushed (re-run with "real skin texture, visible
      pores" if not)
- [ ] Voice is the character's voice, not the model's

## Pitfalls we hit

- A one-shot 3x2 character sheet drifted between panels; per-angle generation fixed it.
- "Keep exactly as in @Image1" made 7 shots feel frozen; "keep the look" fixed it.
- The model added a mole-like dot on the wrong cheek in one shot: catch it in the frame
  strip, cut around it.
- A designed voice was called "very fake"; a professional narrator voice "cinematic".
