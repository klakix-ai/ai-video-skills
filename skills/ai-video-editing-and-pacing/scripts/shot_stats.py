#!/usr/bin/env python3
"""Measure the pacing of a finished video: cut points, shot lengths, median and shortest shot.

Cuts are detected with a colour-histogram difference between consecutive frames (downscaled),
which is robust to camera motion. Use it on your own edit and on reference reels you want to
learn from.

Usage:
    python shot_stats.py video.mp4
    python shot_stats.py video.mp4 --threshold 0.35 --list
    python shot_stats.py reels/*.mp4 --csv pacing.csv

Reading the result (our audience data): median shot >= ~2.6 s felt calm and premium; 1.3 s felt
"too fast"; key reveals held 4-5 s. Whip pans can be detected as cuts - check them with --list.

Requires: pip install opencv-python numpy
"""
from __future__ import annotations

import argparse
import csv
import glob

import cv2
import numpy as np


def cuts(path: str, threshold: float, min_gap: float) -> tuple[list[float], float, int]:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise SystemExit(f"cannot open {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    prev = None
    found: list[float] = []
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (96, 54), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1, 2], None, [16, 8, 8], [0, 180, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        if prev is not None:
            d = cv2.compareHist(prev, hist, cv2.HISTCMP_BHATTACHARYYA)
            t = i / fps
            if d > threshold and (not found or t - found[-1] >= min_gap):
                found.append(t)
        prev = hist
        i += 1
    cap.release()
    return found, i / fps, i


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--threshold", type=float, default=0.35, help="histogram distance for a cut (0-1)")
    ap.add_argument("--min-gap", type=float, default=0.25, help="ignore cuts closer than this (s)")
    ap.add_argument("--list", action="store_true", help="print every shot")
    ap.add_argument("--csv")
    args = ap.parse_args()

    rows = []
    paths = [p for g in args.videos for p in (sorted(glob.glob(g)) or [g])]
    for path in paths:
        c, duration, frames = cuts(path, args.threshold, args.min_gap)
        bounds = [0.0] + c + [duration]
        shots = np.diff(bounds)
        row = {"file": path, "duration": round(duration, 2), "shots": len(shots),
               "median_shot": round(float(np.median(shots)), 2), "shortest": round(float(shots.min()), 2),
               "longest": round(float(shots.max()), 2), "cuts_per_10s": round(len(c) / max(duration, 1e-6) * 10, 2)}
        print(f"{path}: {duration:.1f}s, {len(shots)} shots, median {row['median_shot']}s, "
              f"shortest {row['shortest']}s, longest {row['longest']}s, {row['cuts_per_10s']} cuts/10s")
        if args.list:
            for n, (a, b) in enumerate(zip(bounds[:-1], bounds[1:]), start=1):
                print(f"  shot {n:2d}: {a:6.2f} - {b:6.2f}  ({b - a:4.2f}s)")
        rows.append(row)
    if args.csv and rows:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
