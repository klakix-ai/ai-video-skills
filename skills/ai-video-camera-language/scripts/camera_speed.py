#!/usr/bin/env python3
"""Measure how fast the camera moves in a video clip.

Method: every frame is downscaled to 160 px width and converted to grey; dense Farneback
optical flow is computed between consecutive frames; the median flow magnitude of a frame
pair approximates global camera motion in pixels per frame (at 160 px width).

Thresholds come from audience feedback on real AI video productions:
    <= 1.0 px/frame average and <= 1.5 peak  -> calm, comfortable
    1.0 - 2.0                                 -> lively, check it in context
    > 2.0                                     -> too fast for most viewers

Usage:
    python camera_speed.py clip.mp4
    python camera_speed.py clip.mp4 --window 3          # also find the calmest 3 s window
    python camera_speed.py shots/*.mp4 --csv speeds.csv # batch, one row per clip
    python camera_speed.py clip.mp4 --per-frame         # print the per-frame curve

Requires: pip install opencv-python numpy
"""
from __future__ import annotations

import argparse
import csv
import glob
import sys

import cv2
import numpy as np

WIDTH = 160
CALM_AVG, CALM_PEAK, FAST = 1.0, 1.5, 2.0


def flow_curve(path: str) -> tuple[np.ndarray, float]:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise SystemExit(f"cannot open {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    prev = None
    values: list[float] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        h, w = frame.shape[:2]
        small = cv2.resize(frame, (WIDTH, max(1, round(h * WIDTH / w))), interpolation=cv2.INTER_AREA)
        grey = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        if prev is not None:
            flow = cv2.calcOpticalFlowFarneback(prev, grey, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            values.append(float(np.median(np.linalg.norm(flow, axis=2))))
        prev = grey
    cap.release()
    return np.array(values), float(fps)


def verdict(avg: float, peak: float) -> str:
    if avg <= CALM_AVG and peak <= CALM_PEAK:
        return "calm"
    if avg <= FAST:
        return "lively"
    return "too fast"


def calmest_window(curve: np.ndarray, fps: float, seconds: float) -> tuple[float, float, float] | None:
    n = int(round(seconds * fps))
    if n <= 0 or len(curve) < n:
        return None
    sums = np.convolve(curve, np.ones(n), mode="valid") / n
    i = int(np.argmin(sums))
    return i / fps, (i + n) / fps, float(sums[i])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--window", type=float, default=0, help="find the calmest window of N seconds")
    ap.add_argument("--csv", help="write one row per clip to this CSV file")
    ap.add_argument("--per-frame", action="store_true", help="print the per-frame curve")
    args = ap.parse_args()

    paths: list[str] = []
    for p in args.videos:
        paths.extend(sorted(glob.glob(p)) or [p])

    rows = []
    for path in paths:
        curve, fps = flow_curve(path)
        if len(curve) == 0:
            print(f"{path}: fewer than 2 frames", file=sys.stderr)
            continue
        avg, peak = float(curve.mean()), float(np.percentile(curve, 95))
        row = {"file": path, "fps": round(fps, 3), "avg_px_per_frame": round(avg, 2),
               "peak_p95": round(peak, 2), "max": round(float(curve.max()), 2), "verdict": verdict(avg, peak)}
        line = f"{path}: avg {avg:.2f} px/frame, peak(p95) {peak:.2f}, max {curve.max():.2f} -> {row['verdict']}"
        if args.window:
            win = calmest_window(curve, fps, args.window)
            if win:
                row.update(calm_start=round(win[0], 2), calm_end=round(win[1], 2), calm_avg=round(win[2], 2))
                line += f"; calmest {args.window:g}s: {win[0]:.2f}-{win[1]:.2f}s (avg {win[2]:.2f})"
        print(line)
        if args.per_frame:
            for i, v in enumerate(curve, start=1):
                print(f"  {i / fps:7.2f}s  {v:5.2f}")
        rows.append(row)

    if args.csv and rows:
        keys = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0]).index(k) if k in rows[0] else 99)
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
