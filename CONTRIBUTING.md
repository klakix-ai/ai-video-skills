# Contributing

Thanks for helping make AI video skills better. This repo values evidence over opinions.

## What makes a good contribution

- **A rule that changed a result.** Say what you tried, what came out, and how you know it
  was better (viewer feedback, a measurement, a side-by-side).
- **Model-specific behaviour** for Seedance, Kling, Veo, MiniMax/Hailuo, Runway, Wan, Sora or
  others: limits, quirks, prompt wording that works, with the date you tested (models change).
- **Scripts** that measure or fix something, in plain Python with OpenCV/NumPy/ffmpeg and a
  `--help` that explains the method.

## Style

- Skills follow the [Agent Skills](https://agentskills.io) format: `skills/<name>/SKILL.md` with
  `name` and `description` frontmatter; long material goes into `references/`, code into `scripts/`.
- Write instructions an agent can act on: imperative, concrete, with numbers where you have them.
- No real people, celebrities, brands or logos in examples.
- Keep each `SKILL.md` under ~300 lines.

## Checks

```bash
python scripts/validate.py
```
