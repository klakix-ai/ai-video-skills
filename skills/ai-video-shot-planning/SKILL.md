---
name: ai-video-shot-planning
description: Plan a multi-shot AI video (Seedance, Kling, Veo, MiniMax/Hailuo, Runway, Wan) before spending money on generation. Turns an idea into a shot list with per-shot action beats, camera move, scene logic, costume and reference images, key frames, a cheap test plan and a cost estimate. Use when someone asks to make an AI short film, reel, ad, music video, story or "viral video" with more than one shot, asks for a storyboard or shot list, or is about to generate several clips in a row.
license: MIT
metadata:
  author: Klakix
  homepage: https://klakix.com/ai-video-skills
  version: "1.0.0"
---

# AI video shot planning

Generation is the expensive step and re-shoots are where budgets die. Almost every failed
AI video we made failed in the plan, not in the model: a scene that made no sense, a frozen
shot, a costume from the wrong century, a camera that moved three times in eight seconds.
Plan on paper first, look at stills second, generate video last.

## Workflow

1. **One-line premise and the joke/payoff.** Write what the viewer should feel or laugh at,
   in one sentence. If you cannot, the video has no spine yet.
2. **Pick the format** (see `viral-ai-video-formats` if it is for social). Decide aspect
   ratio from the content, not from price: cinematic and story pieces are landscape
   (4:3 or 16:9); tutorials and talking-to-camera UGC are vertical (9:16).
3. **Write the shot list** with the template below. 6 to 10 shots for a 30 to 40 second piece.
4. **Run the four plan checks** (below) on every shot. Fix the plan, not the output.
5. **Generate key frames first** (one still per shot, cheap image model). Review them with
   the person. Stills are 10 to 50 times cheaper than video and reveal most problems.
6. **One cheap video test** of the riskiest shot (night interior, crowd, transformation,
   a face) at the lowest resolution and shortest duration the model allows.
7. **Get explicit approval with a cost estimate** before generating the full set. Approval
   of a budget is not approval of a plan: show the shot list and the price together.
8. **Generate, then review every clip as a frame strip** before moving to the next shot.
   If a logic error shows up, stop and say so instead of finishing the batch.

## Shot list template

```
Shot 3 of 8 · 4 s · 4:3 · model: Seedance 2.x reference mode
Purpose:       the reveal (the joke lands here)
Location:      cramped 1980s kitchen, morning daylight through one window
Characters:    @Image1 = character sheet (front + 3/4), @Image2 = period costume
What moves:    0-1.5 s grandmother turns from the stove
               1.5-3 s she freezes, eyes on the robot vacuum
               3-4 s steam rises, the cat bolts across the floor
Camera:        one slow push-in from medium to medium-close; nothing else
Who sees what: the grandmother cannot see the doorway; the vacuum enters from behind her
Audio:         model ambience bed; line "..." recorded separately (see voice skill)
Key frame:     kf-03.png (approved)
Cost:          4 s x $0.11/s ≈ $0.43, one retry budgeted
```

## The four plan checks

**1. What moves in these 4 seconds?** The most common failure after "camera too fast" is the
opposite: a dead, frozen shot. A calm camera is good; a calm *world* is not. Give every shot
2 to 3 action beats with time ranges, plus continuous background life (people walking,
steam, traffic, wind in fabric, a waiter passing). Put words like "calm, still, gently" on
the camera, never on the subject. A fully locked-off tripod is a choice for a specific
joke, not a default.

**2. Who can see what?** Write the internal logic of every scene. If the joke is that
someone is hiding, the hiding place must be fully closed: no arch, window or gap through
which the person they hide from could look in. Say it in the prompt: "fully enclosed, no
openings, the outside is only heard, never seen". If someone asks "how many stones are
left?", the pyramid behind them must be half built. Logic errors do not stop the comedy
from working, but viewers notice them, and fixing them later means paying again.

**3. Does everything belong to the period and place?** Characters dress for the era of the
scene. Generate the costume as its own reference image and pass it as a separate image
reference. A signature accessory (earrings, a necklace) may stay for recognisability.
Modern clothes only if "time traveller" is the explicit, chosen joke.

**4. One camera move per shot.** A 4 to 8 second clip gets one slow, motivated camera move
or none. Three moves in one shot reads as frantic. See `ai-video-camera-language`.

## Cost control that works

- **Draft at the lowest resolution, upscale the keepers.** 480p generation plus a video
  upscaler to 1080p looks better than you expect and costs a fraction of 720p/1080p
  generation. Upscale raw clips, not the finished edit.
- **Budget per shot, not per video.** Typical prices we measured in November 2026 (they
  vary by provider): Seedance 2.x at 480p about $0.10 to $0.11 per second, 720p about
  $0.23 per second; a 1080p upscale of a 5 second clip about $0.04; a key frame still
  $0.08 to $0.21. A 7-shot, 30-second landscape piece at 480p with upscaling landed at
  $4 to $5 including stills.
- **One cheap test before every expensive plan.** A 4 second 480p test (about $0.43) on
  the hardest shot. Check light and logic in the frame, not just "does it look nice".
- **Night and interior scenes need a light test.** In one test, adding "warm glow fills the
  space, every face well lit" cut crushed-black pixels from 49% to 26%.
- **Only plan clips you will actually use.** Generate the clip length you need plus about
  one second of handle; most models are billed per output second.
- **Rejections are usually free and fast** (safety filters answer in about 30 seconds). A
  rejection is information about the prompt and image pair, not a reason to retry blindly.

## Review checklist for each generated clip

- [ ] Frame strip at 0.5 s intervals: logic, costume, continuity with the previous shot
- [ ] Camera speed acceptable (`ai-video-camera-language/scripts/camera_speed.py`)
- [ ] No text, logos, badges or real brands crept in (models add car badges and signage)
- [ ] Face and identity still match the character sheet
- [ ] Note the best 2 to 3 seconds; you will rarely use the whole clip

## Hand-offs

- Camera wording and speed: `ai-video-camera-language`
- Characters that stay the same across shots: `ai-character-consistency`
- Writing the actual prompts: `ai-video-prompting`
- Making it look real instead of "AI": `ai-video-realism`
- Dialogue, voice and lip sync: `ai-video-dialogue-and-voice`
- Cutting it together: `ai-video-editing-and-pacing`
