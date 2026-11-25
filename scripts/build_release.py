#!/usr/bin/env python3
"""Zip each skill folder into dist/<skill>.zip (for upload in Claude.ai Settings > Capabilities > Skills)."""
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
for d in sorted((ROOT / "skills").iterdir()):
    if not (d / "SKILL.md").exists():
        continue
    out = dist / f"{d.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(d.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                z.write(f, f"{d.name}/{f.relative_to(d).as_posix()}")
    print(out.relative_to(ROOT))
