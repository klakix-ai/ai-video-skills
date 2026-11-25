#!/usr/bin/env python3
"""Report integrated loudness (LUFS), loudness range (LU) and true peak (dBTP) with ffmpeg's ebur128.

Usage:
    python loudness.py final.mp4 dialogue.wav bed.wav
    python loudness.py final.mp4 --target -14     # flag files more than 1 LU off target

Targets used in our productions: final mix -14 LUFS / true peak <= -1 dBTP for social video;
lead voice ~-18 LUFS, side characters ~-19.5, off-screen ~-20.5; speech >= 12 dB (ideally 18+)
above the ambience bed when measured as separate stems.

Requires: ffmpeg on PATH.
"""
from __future__ import annotations

import argparse
import re
import subprocess


def measure(path: str) -> dict:
    proc = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", path,
                           "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    summary = proc.stderr[proc.stderr.rfind("Summary:"):]
    def grab(label: str) -> float | None:
        m = re.search(label + r":\s+(-?[\d.]+|-inf)", summary)
        if not m:
            return None
        return float("-inf") if m.group(1) == "-inf" else float(m.group(1))
    return {"I": grab("I"), "LRA": grab("LRA"), "TP": grab("Peak")}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--target", type=float, help="integrated loudness target, e.g. -14")
    args = ap.parse_args()
    for f in args.files:
        m = measure(f)
        if m["I"] is None:
            print(f"{f}: no audio or ffmpeg failed")
            continue
        note = ""
        if args.target is not None and abs(m["I"] - args.target) > 1:
            note += f"  <- {m['I'] - args.target:+.1f} LU off target"
        if m["TP"] is not None and m["TP"] > -1:
            note += "  <- true peak above -1 dBTP"
        print(f"{f}: {m['I']:.1f} LUFS, LRA {m['LRA']:.1f} LU, true peak {m['TP']:.1f} dBTP{note}")


if __name__ == "__main__":
    main()
