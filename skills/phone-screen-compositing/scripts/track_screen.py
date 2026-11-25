#!/usr/bin/env python3
"""Track the four corners of a chroma-key green phone/tablet/watch screen in every frame.

Output JSON:
    {"frames": N, "fps": 24.0,
     "corners": [[[x,y]*4] per frame],   # TL, TR, BR, BL, sub-pixel, final
     "raw":     [[[x,y]*4] per frame],   # per-frame measurement before the still-frame filter
     "finger":  [y or null per frame]}   # top of the finger inside the screen, 0 (top) .. 1 (bottom)

Design choices (from production):
  * sub-pixel edges: greenness map upscaled 4x, contour at 0.5, straight lines fitted per edge,
    corners = line intersections (rounded phone corners do not pull the fit);
  * NO temporal smoothing in motion (it makes the UI lag behind the phone); only nearly still
    frames (< 0.5 px/frame) get a 1-2-1 filter, fading out by 2 px/frame;
  * outlier frames (area off by > 12% from neighbours) are interpolated.

Usage:
    python track_screen.py shot.mp4 corners.json [--preview dir] [--occlusion]
    [--green-min 55] [--g-min 90]

Requires: pip install opencv-python numpy
"""
from __future__ import annotations

import argparse
import json
import pathlib

import cv2
import numpy as np


def greenness(bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    f = bgr.astype(np.float32)
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    return g - np.maximum(r, b), g


def fit_line(points: np.ndarray):
    vx, vy, x0, y0 = cv2.fitLine(points.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    return np.array([x0, y0]), np.array([vx, vy])


def intersect(l1, l2):
    (p, r), (q, s) = l1, l2
    m = np.array([[r[0], -s[0]], [r[1], -s[1]]])
    if abs(np.linalg.det(m)) < 1e-6:
        return None
    t = np.linalg.solve(m, q - p)[0]
    return p + t * r


def order_tl_tr_br_bl(k: np.ndarray) -> np.ndarray:
    c = k.mean(0)
    k = k[np.argsort(np.arctan2(k[:, 1] - c[1], k[:, 0] - c[0]))]
    return np.roll(k, -int(np.argmin(k.sum(1))), axis=0)


def subpixel_contour(soft: np.ndarray, region: np.ndarray, scale: int = 4):
    x, y, w, h = cv2.boundingRect(region)
    x0, y0 = max(0, x - 8), max(0, y - 8)
    x1, y1 = min(region.shape[1], x + w + 8), min(region.shape[0], y + h + 8)
    inside = cv2.dilate(region, np.ones((9, 9), np.uint8))[y0:y1, x0:x1] > 0
    roi = (soft[y0:y1, x0:x1] * inside).astype(np.float32)
    big = cv2.resize(roi, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    contours, _ = cv2.findContours((big > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None
    k = max(contours, key=cv2.contourArea).reshape(-1, 2).astype(np.float64)
    return (k + 0.5) / scale - 0.5 + np.array([x0, y0])


def find_corners(mask: np.ndarray, soft: np.ndarray):
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if n < 2:
        return None
    biggest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    region = (labels == biggest).astype(np.uint8) * 255
    contours, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(contour)
    perimeter = cv2.arcLength(hull, True)
    quad = None
    for eps in np.linspace(0.01, 0.12, 30):
        approx = cv2.approxPolyDP(hull, eps * perimeter, True)
        if len(approx) == 4:
            quad = approx.reshape(4, 2).astype(np.float64)
            break
    if quad is None:
        quad = cv2.boxPoints(cv2.minAreaRect(hull)).astype(np.float64)
    quad = order_tl_tr_br_bl(quad)
    pts = contour.reshape(-1, 2).astype(np.float64)
    fine = subpixel_contour(soft, region)
    if fine is not None and len(fine) > 40:
        pts = fine
    lines = []
    for i in range(4):
        a, b = quad[i], quad[(i + 1) % 4]
        L = np.linalg.norm(b - a)
        u = (b - a) / L
        nrm = np.array([-u[1], u[0]])
        t = (pts - a) @ u
        d = np.abs((pts - a) @ nrm)
        sel = pts[(t > 0.18 * L) & (t < 0.82 * L) & (d < max(3.0, 0.03 * L))]
        lines.append(fit_line(sel) if len(sel) >= 6 else (a, u))
    out = []
    for i in range(4):
        p = intersect(lines[(i - 1) % 4], lines[i])
        out.append(p if p is not None and np.linalg.norm(p - quad[i]) < 40 else quad[i])
    return np.array(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--preview", help="write every 20th frame with the tracked quad drawn")
    ap.add_argument("--occlusion", action="store_true", help="re-estimate up to 2 occluded corners per frame")
    ap.add_argument("--green-min", type=float, default=55, help="min G - max(R,B) for the key")
    ap.add_argument("--g-min", type=float, default=90, help="min G channel for the key")
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    if not frames:
        raise SystemExit("no frames")

    K, prev = [], None
    for f in frames:
        gn, g = greenness(f)
        m = ((gn > args.green_min) & (g > args.g_min)).astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        k = find_corners(m, np.clip((gn - 30) / 50, 0, 1))
        if k is not None and prev is not None:
            k = min((np.roll(k, r, axis=0) for r in range(4)), key=lambda x: np.linalg.norm(x - prev))
        if k is not None:
            prev = k
        K.append(k)
    if all(k is None for k in K):
        raise SystemExit("no green screen found; lower --green-min / --g-min")
    K = np.array([k if k is not None else np.full((4, 2), np.nan) for k in K])

    area = np.array([cv2.contourArea(k.astype(np.float32)) if not np.isnan(k).any() else np.nan for k in K])
    for i in range(len(K)):
        med = np.nanmedian(area[max(0, i - 4): i + 5])
        if np.isnan(area[i]) or abs(area[i] - med) > 0.12 * med:
            K[i] = np.nan
    idx = np.arange(len(K))
    for c in range(4):
        for e in range(2):
            v = K[:, c, e]
            good = ~np.isnan(v)
            K[:, c, e] = np.interp(idx, idx[good], v[good])

    Kt = K.copy()
    if args.occlusion:
        for i in range(1, len(K)):
            a, b = Kt[i - 1].astype(np.float32), K[i].astype(np.float32)
            M, _ = cv2.estimateAffinePartial2D(a, b, method=cv2.LMEDS)
            if M is None:
                continue
            err = np.linalg.norm(a @ M[:, :2].T + M[:, 2] - b, axis=1)
            bad = err > max(4.0, 3.0 * np.median(err))
            if 1 <= bad.sum() <= 2:
                M2, _ = cv2.estimateAffinePartial2D(a[~bad], b[~bad], method=cv2.LMEDS)
                if M2 is not None:
                    Kt[i][bad] = a[bad] @ M2[:, :2].T + M2[:, 2]

    speed = np.r_[0, np.linalg.norm(np.diff(Kt.mean(1), axis=0), axis=1)]
    w = np.clip((2.0 - speed) / 1.5, 0, 1)[:, None, None]
    avg = Kt.copy()
    if len(Kt) > 2:
        avg[1:-1] = 0.25 * Kt[:-2] + 0.5 * Kt[1:-1] + 0.25 * Kt[2:]
    final = w * avg + (1 - w) * Kt

    finger = []
    for f, k in zip(frames, final):
        gn, _ = greenness(f)
        inside = np.zeros(f.shape[:2], np.uint8)
        cv2.fillConvexPoly(inside, cv2.convexHull(k.astype(np.int32)), 255)
        inside = cv2.erode(inside, np.ones((9, 9), np.uint8))
        occ = ((gn < 30) & (inside > 0)).astype(np.uint8)
        occ = cv2.morphologyEx(occ, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        if occ.sum() < 60:
            finger.append(None)
            continue
        H = cv2.getPerspectiveTransform(k.astype(np.float32), np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]))
        ys, xs = np.nonzero(occ)
        uv = cv2.perspectiveTransform(np.stack([xs, ys], 1).astype(np.float32)[None], H)[0]
        finger.append(round(float(np.percentile(uv[:, 1], 2)), 4))

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump({"frames": len(frames), "fps": fps, "corners": final.round(2).tolist(),
                   "raw": K.round(2).tolist(), "finger": finger}, fh)
    moving = speed > 2
    diff = np.abs(final - K).max(axis=(1, 2))
    print(f"{args.video}: {len(frames)} frames, interpolated {int(np.isnan(area).sum())}, "
          f"max raw-vs-final in motion {diff[moving].max() if moving.any() else 0:.2f}px")

    if args.preview:
        pathlib.Path(args.preview).mkdir(parents=True, exist_ok=True)
        for i in range(0, len(frames), 20):
            f = frames[i].copy()
            cv2.polylines(f, [final[i].astype(np.int32)], True, (0, 0, 255), 2)
            for p in final[i]:
                cv2.circle(f, tuple(int(v) for v in p), 5, (255, 0, 255), -1)
            cv2.imwrite(f"{args.preview}/{pathlib.Path(args.video).stem}-{i:03d}.jpg", f)


if __name__ == "__main__":
    main()
