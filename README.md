# AI Video Skills

**Agent Skills for AI video production: camera angles, character consistency, Seedance and Kling prompts, realism, lip sync, pacing and viral formats.**
Ten open-source skills that teach Claude Code, Codex, Cursor, Gemini CLI and other AI agents how to plan, prompt and edit AI-generated video, based on what actually worked (and failed) in real productions.

[![License: MIT](https://img.shields.io/badge/license-MIT-black.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-10-e11d2e.svg)](#the-skills)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-black.svg)](#install)
[![Made by Klakix](https://img.shields.io/badge/made%20by-Klakix-e11d2e.svg)](https://klakix.com/ai-video-skills)

Most AI video advice is a list of magic words. These skills are different: every rule here
comes from a shot we paid for, a reel we published, or a viewer who told us something looked
wrong. "The camera is so fast it's bad." "Everything feels frozen." "Why can the mother see
inside the Trojan horse?" Each of those became a rule, a prompt pattern or a script.

## The skills

| Skill | What your agent learns |
|---|---|
| [ai-video-shot-planning](skills/ai-video-shot-planning/SKILL.md) | Shot lists with timed action beats, the four plan checks (what moves, who sees what, period/costume, one camera move), key frames first, cheap tests and cost estimates |
| [ai-video-camera-language](skills/ai-video-camera-language/SKILL.md) | 14 tested camera moves with copy-paste prompt wording, 3 to avoid, the snap-zoom-and-hold move, and `camera_speed.py` to measure camera motion with optical flow |
| [ai-character-consistency](skills/ai-character-consistency/SKILL.md) | Character bibles, turnaround sheets that do not drift, identity markers, per-shot reference sets, period costumes, and how to avoid "real person" rejections |
| [ai-video-prompting](skills/ai-video-prompting/SKILL.md) | Prompt structure, second-by-second timelines, Seedance 2.x reference maps (@Image/@Video/@Audio), negative wording that works, model quirks for Seedance, Kling, Veo, MiniMax |
| [ai-video-realism](skills/ai-video-realism/SKILL.md) | Device-based realism (balcony phone, GoPro, broadcast telephoto), words that make output look CGI, real-photo references, natural colour |
| [ai-video-dialogue-and-voice](skills/ai-video-dialogue-and-voice/SKILL.md) | One voice per character, WSOLA lip alignment (`align_to_lips.py`), keeping the model's ambience, loudness targets (`loudness.py`), verifying lines with speech-to-text |
| [ai-video-editing-and-pacing](skills/ai-video-editing-and-pacing/SKILL.md) | Measured shot-length rules, beat grids, never speeding up generated footage, sub-pixel moves, upscale-then-grade, `shot_stats.py` for pacing analysis |
| [viral-ai-video-formats](skills/viral-ai-video-formats/SKILL.md) | "History + one modern object", delayed reveal, bystander phone POV, two-character scenes, spoken CTAs, AI labels, diagnosing low reach |
| [phone-screen-compositing](skills/phone-screen-compositing/SKILL.md) | Green-screen phones and watches in AI video, sub-pixel corner tracking with no lag (`track_screen.py`), compositing with finger occlusion (`composite_screen.py`) |
| [3d-previs-to-ai-video](skills/3d-previs-to-ai-video/SKILL.md) | Grey-box 3D blockouts as camera-path references for Seedance, transformations, in-car cameras, contact-sheet checks |

All scripts are plain Python (OpenCV, NumPy, ffmpeg). No API keys, no accounts, no lock-in.

## Install

### Claude Code (plugin marketplace)

```text
/plugin marketplace add klakix-ai/ai-video-skills
/plugin install ai-video-skills@klakix-ai-video
```

### Any agent that reads Agent Skills (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Goose…)

```bash
npx skills add klakix-ai/ai-video-skills
```

### Manual

```bash
git clone https://github.com/klakix-ai/ai-video-skills.git
# Claude Code (all projects)
cp -r ai-video-skills/skills/* ~/.claude/skills/
# Codex
cp -r ai-video-skills/skills/* ~/.codex/skills/
```

### Claude.ai and the Claude desktop app

Download a skill zip from [Releases](https://github.com/klakix-ai/ai-video-skills/releases),
then upload it in **Settings → Capabilities → Skills**.

Script dependencies: `pip install opencv-python numpy` and ffmpeg on your PATH.
`faster-whisper` is optional (word timestamps for lip alignment).

## Try it

Once installed, just describe the job. The agent loads the right skill on its own:

- "Plan a 35-second reel: ancient Rome, but everyone uses electric scooters. Shot list, key frames and cost first."
- "My Seedance clip feels too fast. Measure the camera and tell me which 3 seconds to use."
- "Write a Seedance 2.5 reference prompt for my character sheet and this costume image."
- "Make a character sheet for a recurring AI host that won't drift between shots."
- "This AI video looks fake. Rewrite the prompts so it looks like a neighbour filmed it."
- "Replace the green phone screen in this clip with this chat screenshot."
- "Analyse the pacing of this viral reel and compare it to my cut."

## What we measured

A few of the numbers behind the rules (details inside each skill):

- **Camera speed**: shots viewers liked measured 0.2 to 1.2 px/frame of median optical flow at 160 px width; shots they complained about measured 2 to 5. Target ≤ 1 average, ≤ 1.5 peak.
- **Pacing**: a cut with a 1.29 s median shot was "way too fast"; the same footage at a 3.54 s median was approved. Key reveals hold 4 to 5 s.
- **Hooks**: in "history + modern object" viral reels the absurd element appears by 1.3 s; in "is this real?" reels the strongest reveals land at 3.8 to 6.7 s.
- **Calls to action**: a CTA spoken inside the video got a 5.38% comment-to-like ratio versus 0.26 to 0.54% for caption-only CTAs (one comparison).
- **Faces and safety filters**: Seedance 2.5 accepted AI-generated faces and rejected real-person photos; references without faces passed 6 of 6, references with faces 15 of 23.
- **Screen tracking**: temporal smoothing made composited UI lag up to 27 px behind a moving phone; per-frame sub-pixel tracking removed it.
- **Dialogue**: re-voicing with one TTS voice and aligning to the lips took speech-to-bed separation from 4 dB to 18 dB and fixed garbled words.
- **Cost**: a 7-shot, 30-second landscape short at 480p with upscaling cost $4 to $5 in late 2026, including key frames.

## FAQ

**What are Agent Skills?**
Folders with a `SKILL.md` file (instructions plus optional scripts and references) that AI
agents load when a task matches the skill's description. The format started in Claude Code
and is now read by many agents. Skills cost almost no context until they are used.

**Which video models do these skills cover?**
Seedance 2.0, 2.0 Mini and 2.5 in depth (text, image, multi-reference, edit, extend), plus
Kling, Veo, MiniMax/Hailuo, Runway, Wan and Sora where we have tested behaviour. The
planning, camera, realism, voice and editing rules are model-agnostic.

**How do I keep an AI character consistent across shots?**
Lock one core portrait, generate every angle separately with that portrait as reference
(not a multi-panel sheet in one go), define asymmetric identity markers, and pass a small
per-shot reference set. See [ai-character-consistency](skills/ai-character-consistency/SKILL.md).

**What are the best camera angles for AI video?**
The ones that keep the camera calm and the world alive: one slow move per shot. Our
audience's favourite was an over-the-shoulder 50 mm shot that holds still, snap-zooms on
the punchline and holds. See [ai-video-camera-language](skills/ai-video-camera-language/SKILL.md).

**Do I need Klakix to use these?**
No. The skills work with any model or platform. We built them while making videos on
[Klakix](https://klakix.com), where you can run Seedance, Kling, Veo and more in one place,
or connect your agent through the [Klakix MCP server](https://github.com/klakix-ai/klakix-mcp).

## Contributing

Found a rule that is wrong for your model, or a technique that works better? Open an issue
or a pull request with **what you tried, what came out and how you measured it**. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## More from Klakix

- [Klakix MCP server](https://github.com/klakix-ai/klakix-mcp): generate AI video, images, voice and music from Claude, ChatGPT and Cursor.
- [Klakix Bridge for Blender](https://github.com/klakix-ai/klakix-blender): let AI agents build blockouts and scenes in Blender.
- [AI video skills guide](https://klakix.com/ai-video-skills) on klakix.com · [Türkçe rehber](https://aivideoyap.com/yapay-zeka-video-skilleri) on aivideoyap.com.

## License

[MIT](LICENSE) © Klakix. Use the skills, scripts and prompt patterns in personal and commercial work.
