---
name: ai-video-prompting
description: Write prompts for AI video models that follow instructions precisely - Seedance 2.0 / 2.5 (text, image, multi-reference with @Image/@Video/@Audio, edit, extend), Kling, Veo, MiniMax/Hailuo, Runway, Wan and Sora. Covers prompt structure, second-by-second timelines, reference maps, negative wording, length limits, when to turn off prompt enhancers, and model-specific quirks we measured. Use when writing or fixing a text-to-video or image-to-video prompt, a Seedance reference prompt, when a model ignores parts of the prompt, or when someone asks how to prompt Seedance, Kling or Veo.
license: MIT
metadata:
  author: Klakix
  homepage: https://klakix.com/ai-video-skills
  version: "1.0.0"
---

# Prompting AI video models

Modern video models follow surprisingly detailed instructions, including exact timings,
as long as the prompt is ordered, concrete and free of vague style words. Write prompts in
English even for non-English content; keep spoken lines in their original language inside
quotes.

## Prompt structure (in this order)

1. **Reference map** (only in reference mode): what each attached file is.
2. **Look**: how the footage was captured (device, light, texture). See `ai-video-realism`.
3. **Scene and subject**: place, time, who is there, what they wear.
4. **Timeline**: what happens, second by second.
5. **Dialogue**: exact lines in quotes, who says them, on or off screen.
6. **Camera**: one sentence, last, ending with "nothing fast".
7. **Exclusions**: no text, no logos, no cuts, etc.

```
@Image1 is the character (front view). @Image2 is her costume for this scene.
@Image3 is the location.

Real handheld documentary footage, ordinary soft daylight, natural true-to-life colours,
real skin texture.

A narrow stone kitchen in a medieval castle. The woman from @Image1 wears the costume from
@Image2: deep blue velvet dress, flat leather shoes with no heels.
0-1.5s: she lifts the lid of a pot and steam rises.
1.5-3s: a robot vacuum glides out from under the table; she freezes, eyebrows up.
3-4s: the cook behind her drops a ladle; the cat on the bench jumps down.
She says in Turkish, quietly: "Bu da ne?"
Camera: slow handheld push-in at eye level from medium to medium-close; nothing fast.
Single continuous shot, no cuts. No text on screen, no logos.
```

## Timelines work, even long ones

`0-5s: ... 5-10s: ...` timelines were followed almost beat for beat by Seedance 2.5 in a
25-second shot with 9 beats and a 30-second single take. Use them whenever order matters.
Give each beat a visible action, not an emotion ("she laughs and covers her mouth", not
"she is happy").

## Length limits

Some interfaces cap the prompt (Seedance reference mode: 2,000 characters in several UIs;
2 of our first 10 prompts did not fit). Cut adjectives first, then merge beats. Never cut
the camera sentence or the exclusions.

## Seedance 2.x specifics

- **Modes**: text-to-video, image-to-video (first frame, optional last frame), reference
  mode (images + videos + audio as references), edit (change an existing video), extend.
- **Reference limits** (late 2026): 2.5 accepts up to 30 images, 10 videos and 10 audio
  files with total reference video up to 30 s; 2.0 and 2.0 Mini accept up to 9 images,
  3 videos, 3 audio files and up to 15 s, and audio alone is not enough as a reference.
- **Order defines the name**: the first image is @Image1, the first video @Video1, the first
  audio @Audio1. Always describe each in the reference map.
- **@Video1 as camera path**: pass a blockout or reference video and say "copy every camera
  move of @Video1 exactly". See `3d-previs-to-ai-video`.
- **@Audio1 as dialogue timing**: pass a recorded line and the model re-voices the same
  words with similar rhythm (about 0.7 s latency, 6 to 20% tempo difference), so lips land
  close to your final recording.
- **Faces**: AI-generated faces pass, real people are rejected. See `ai-character-consistency`.
- **Speech**: Turkish and other languages are usable in short lines; in long, multi-speaker
  takes words get garbled. Re-voice with TTS (see `ai-video-dialogue-and-voice`).
- **Pricing note**: reference *videos* raise the price on most providers (billed on input
  video seconds plus output seconds); reference images and audio usually do not.

## Model quirks we measured

| Model | Strength | Watch out |
|---|---|---|
| Seedance 2.5 | best for aerial, vehicles, crowds, long timelines, references | adds car badges and brand-like logos; tends to draw famous stadiums and sponsor boards in sports scenes unless told the arena is fictional |
| Seedance 2.0 Mini | cheap drafts | vehicles drive the wrong way, crowds wander off |
| Kling 3.x / 4.0 | smoothest motion, best at holding a flat green screen for 5 s | min 720p, roughly 2.5x the cost of 480p alternatives |
| MiniMax / Hailuo H3 | great "handheld documentary" look from a good first frame | sometimes cuts to a close-up by itself: add "single continuous shot, no cuts" |
| Veo 3.x | strong native audio and dialogue | 8-second cap per generation |

## Negative wording that works

Positive models ignore "don't", but these exact phrasings held up:

- `No text on screen, no logos, no badges, no watermarks.`
- `Single continuous shot, no cuts.`
- `No whip pans, no shake, no motion blur, nothing fast.`
- `Fully enclosed, no openings; the outside is only heard, never seen.`
- `The phone screen stays a perfectly flat, evenly lit, uniform pure chroma-key green the
  entire time: no content, no reflections, no glare, it never turns off.`
- `A fictional stadium with plain unbranded boards, no real club crests or sponsors.`
- For off-screen speakers: `the mother is unseen; we only hear her voice`.

## Prompt enhancers

Platform "enhance prompt" features rewrite your text. They help with one-line ideas and
hurt precise direction: they generalise camera moves and drop timings. Turn enhancement
off when you specify camera, timing or references.

## Fix list

| Problem | Prompt fix |
|---|---|
| Ignores a beat | give it its own time range and a visible action |
| Text appears on signs | "no readable signage", put any needed text in the edit |
| Wrong era details | name materials ("tallow candles, rough wool, clay cups") |
| Character drifts | fewer, better references; "keep the look of @Image1" |
| Night scene too dark | "warm glow fills the space, every face well lit" |
| Looks CGI | remove "cinematic, epic, 8k, golden hour"; describe the capture device |
| Effect looks like a hologram | describe materials: "paint and panels crumble into fine metal flakes and dust, no wireframe or hologram grid" |
