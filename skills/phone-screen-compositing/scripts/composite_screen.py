#!/usr/bin/env python3
"""Composite a UI (image, folder of frames, or video) onto a tracked green screen.

Uses the corners written by track_screen.py. Anything in front of the screen (fingers, sleeves)
stays in front because the matte comes from the greenness of each frame. Adds the small touches
that make a screen look filmed: slight blur, a little less brightness, optional glass reflection.

Usage:
    python composite_screen.py shot.mp4 corners.json ui.png out.mp4
    python composite_screen.py shot.mp4 corners.json ui_frames/ out.mp4      # ui_frames/0001.png ...
    python composite_screen.py shot.mp4 corners.json ui.mp4 out.mp4 --blur 0.55 --brightness 0.93

The UI is stretched to the screen quad, so render it at the screen's aspect ratio (a phone held
upright is roughly 9:19.5). Output is encoded with ffmpeg (H.264, CRF 16) and keeps the
source audio. Requires: opencv-python, numpy, ffmpeg on PATH.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess

import cv2
import numpy as np


def ui_source(path: str):
    p = pathlib.Path(path)
    if p.is_dir():
        files = sorted(x for x in p.iterdir() if x.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
        frames = [cv2.imread(str(f), cv2.IMREAD_UNCHANGED) for f in files]
        return lambda i: frames[min(i, len(frames) - 1)]
    if p.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}:
        cap = cv2.VideoCapture(str(p))
        frames = []
        while True:
            ok, f = cap.read()
            if not ok:
                break
            frames.append(f)
        return lambda i: frames[min(i, len(frames) - 1)]
    img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise SystemExit(f"cannot read {path}")
    return lambda i: img


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("corners")
    ap.add_argument("ui")
    ap.add_argument("out")
    ap.add_argument("--blur", type=float, default=0.55, help="gaussian sigma applied to the warped UI")
    ap.add_argument("--brightness", type=float, default=0.93)
    ap.add_argument("--reflection", type=float, default=0.04, help="strength of a diagonal glass sheen (0 = off)")
    ap.add_argument("--matte-lo", type=float, default=25, help="greenness where the matte starts")
    ap.add_argument("--matte-hi", type=float, default=70, help="greenness where the matte is fully UI")
    ap.add_argument("--expand", type=int, default=1, help="grow the screen quad by N px to cover the edge")
    ap.add_argument("--bezel", type=float, nargs=3, default=[18, 18, 20], metavar=("B", "G", "R"),
                    help="colour that replaces green outside the quad (BGR)")
    args = ap.parse_args()

    data = json.load(open(args.corners, encoding="utf-8"))
    corners = np.array(data["corners"], dtype=np.float32)
    get_ui = ui_source(args.ui)
    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    enc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-", "-i", args.video,
                            "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                            "-c:a", "copy", "-shortest", args.out], stdin=subprocess.PIPE)
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok or i >= len(corners):
            break
        ui = get_ui(i)
        if ui.ndim == 3 and ui.shape[2] == 4:
            ui = ui[..., :3]
        uh, uw = ui.shape[:2]
        H = cv2.getPerspectiveTransform(np.float32([[0, 0], [uw, 0], [uw, uh], [0, uh]]), corners[i])
        warped = cv2.warpPerspective(ui, H, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
        quad = cv2.warpPerspective(np.full((uh, uw), 255, np.uint8), H, (w, h), flags=cv2.INTER_LINEAR)
        if args.blur > 0:
            warped = cv2.GaussianBlur(warped, (0, 0), args.blur)
        warped = warped.astype(np.float32) * args.brightness
        if args.reflection > 0:
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            sheen = np.clip(1 - np.abs((xx + yy) / (w + h) - 0.35) * 6, 0, 1) * 255 * args.reflection
            warped += sheen[..., None]
        f = frame.astype(np.float32)
        g = f[..., 1] - np.maximum(f[..., 0], f[..., 2])
        key = np.clip((g - args.matte_lo) / (args.matte_hi - args.matte_lo), 0, 1)
        if args.expand > 0:
            k = 2 * args.expand + 1
            quad = cv2.dilate(quad, np.ones((k, k), np.uint8))
        inq = quad.astype(np.float32) / 255
        alpha = cv2.GaussianBlur(key * inq, (0, 0), 0.7)[..., None]
        # Green left outside the quad (rounded corners, edge anti-aliasing) becomes the dark bezel colour,
        # and remaining green spill near the screen is clamped (G <= max(R, B)).
        fringe = (key * (1 - inq))[..., None]
        f = f * (1 - fringe) + np.array(args.bezel, np.float32) * fringe
        near = cv2.dilate(quad, np.ones((15, 15), np.uint8)) > 0
        cap_g = np.maximum(f[..., 0], f[..., 2])
        f[..., 1] = np.where(near, np.minimum(f[..., 1], cap_g + 6), f[..., 1])
        out = f * (1 - alpha) + np.clip(warped, 0, 255) * alpha
        enc.stdin.write(out.astype(np.uint8).tobytes())
        i += 1
    enc.stdin.close()
    enc.wait()
    print(f"{args.out}: {i} frames composited")


if __name__ == "__main__":
    main()
