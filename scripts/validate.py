#!/usr/bin/env python3
"""Validate every skill: frontmatter, naming, size limits, and that bundled Python scripts compile."""
from __future__ import annotations

import json
import pathlib
import py_compile
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
errors: list[str] = []


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if re.match(r"^[a-z_]+:", line):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip('"')
    return out


skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
manifest = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
listed = {pathlib.PurePosixPath(s).name for p in manifest["plugins"] for s in p.get("skills", [])}

for d in skills:
    md = d / "SKILL.md"
    if not md.exists():
        errors.append(f"{d.name}: missing SKILL.md")
        continue
    text = md.read_text(encoding="utf-8")
    fm = frontmatter(text)
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != d.name:
        errors.append(f"{d.name}: name '{name}' must equal the folder name")
    if not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"{d.name}: invalid name")
    if not 50 <= len(desc) <= 1024:
        errors.append(f"{d.name}: description length {len(desc)} (50-1024)")
    if len(text.splitlines()) > 500:
        errors.append(f"{d.name}: SKILL.md over 500 lines")
    if d.name not in listed:
        errors.append(f"{d.name}: not listed in .claude-plugin/marketplace.json")
    for link in re.findall(r"\]\(((?:references|scripts)/[^)]+)\)", text):
        if not (d / link).exists():
            errors.append(f"{d.name}: broken link {link}")
    for py in d.rglob("*.py"):
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{py.relative_to(ROOT)}: {e.msg}")

for s in listed - {d.name for d in skills}:
    errors.append(f"marketplace lists missing skill {s}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"{len(skills)} skills OK")
