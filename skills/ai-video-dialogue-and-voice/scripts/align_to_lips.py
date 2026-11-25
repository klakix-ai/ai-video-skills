#!/usr/bin/env python3
"""Time-align a TTS line to the lip timing of a generated video shot (WSOLA, no pitch change).

Both inputs are word-timestamp lists for the SAME sentence:
  --audio-words  words of your clean TTS recording
  --video-words  words the video model spoke in the shot (lips follow these)
Every word start in the recording is anchored to the same word in the video; time between
anchors is mapped piecewise-linearly and stretched with WSOLA. Output is a mono WAV on the
shot's timeline (0 = first frame), exactly --duration seconds long.

Word JSON format (a list, or {"words": [...]}):
    [{"word": "hello", "start": 0.42, "end": 0.71}, ...]
Keys "text"/"s"/"e" are accepted too. Entries with "type" other than "word" are skipped.

Usage:
    python align_to_lips.py --audio take.mp3 --audio-words take.json \
        --video-words shot.json --duration 5.04 --out shot_voice.wav
    python align_to_lips.py --place take.mp3 --at 1.20 --duration 5.04 --out offscreen.wav
    python align_to_lips.py --transcribe shot.mp4 [--language tr] > shot.json   # needs faster-whisper

Requires: numpy, ffmpeg on PATH. Optional: faster-whisper for --transcribe.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

import numpy as np

SR = 44100


def read_audio(path: str) -> np.ndarray:
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.float32).copy()


def write_wav(path: str, x: np.ndarray) -> None:
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", path],
                   input=x.astype(np.float32).tobytes(), check=True)


def load_words(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("words", [])
    out = []
    for w in data:
        if w.get("type", w.get("tip", "word")) != "word":
            continue
        out.append({"word": w.get("word", w.get("text", "")),
                    "start": float(w.get("start", w.get("s"))),
                    "end": float(w.get("end", w.get("e")))})
    return out


def make_map(video_anchors: list[float], audio_anchors: list[float]):
    """Output (video) sample -> input (recording) sample; slope 1 outside the anchors."""
    v = np.array(video_anchors) * SR
    a = np.array(audio_anchors) * SR

    def f(o: float) -> float:
        if o <= v[0]:
            return a[0] - (v[0] - o)
        if o >= v[-1]:
            return a[-1] + (o - v[-1])
        return float(np.interp(o, v, a))
    return f


def wsola(x: np.ndarray, mapping, n_out: int, N: int = 1024, tol: int = 330) -> np.ndarray:
    hop = N // 2
    window = np.hanning(N).astype(np.float32)
    y = np.zeros(n_out + N, np.float32)
    wsum = np.zeros(n_out + N, np.float32)
    pad = N + tol
    xp = np.concatenate([np.zeros(pad, np.float32), x, np.zeros(2 * N + tol, np.float32)])
    prev = None
    for k in range(0, n_out, hop):
        ideal = mapping(k + N / 2) - N / 2
        if ideal < -N or ideal > len(x):
            prev = None
            continue
        ideal_i = int(round(ideal))
        if prev is None:
            best = ideal_i
        else:
            natural = prev + hop
            template = xp[pad + natural: pad + natural + N]
            lo = ideal_i - tol
            region = xp[pad + lo: pad + lo + N + 2 * tol]
            if float(np.dot(template, template)) < 1e-8 or len(region) < N + 2 * tol:
                best = ideal_i
            else:
                best = lo + int(np.argmax(np.correlate(region, template, mode="valid")))
        y[k:k + N] += xp[pad + best: pad + best + N] * window
        wsum[k:k + N] += window
        prev = best
    return y[:n_out] / np.maximum(wsum[:n_out], 1e-3)


def fade(y: np.ndarray, ms: float = 5) -> np.ndarray:
    r = int(ms / 1000 * SR)
    if len(y) > 2 * r:
        y[:r] *= np.linspace(0, 1, r)
        y[-r:] *= np.linspace(1, 0, r)
    return y


def align(args) -> None:
    a, v = load_words(args.audio_words), load_words(args.video_words)
    if len(a) != len(v):
        sys.exit(f"word count differs: recording {len(a)} vs video {len(v)}. "
                 "Edit the JSON so both list the same words (drop extras the model added).")
    audio_anchors = [w["start"] for w in a] + [a[-1]["end"]]
    video_anchors = [w["start"] for w in v] + [v[-1]["end"]]
    x = read_audio(args.audio)
    y = fade(wsola(x, make_map(video_anchors, audio_anchors), int(args.duration * SR)))
    write_wav(args.out, y)
    ratios = [(video_anchors[i + 1] - video_anchors[i]) / max(1e-3, audio_anchors[i + 1] - audio_anchors[i])
              for i in range(len(audio_anchors) - 1)]
    worst = max(abs(1 - r) for r in ratios)
    print(f"{args.out}: {len(a)} words, stretch {min(ratios):.2f}x-{max(ratios):.2f}x"
          + ("  (over 25%: try another take)" if worst > 0.25 else ""))


def place(args) -> None:
    x = read_audio(args.place)
    y = np.zeros(int(args.duration * SR), np.float32)
    b = int(args.at * SR)
    if b < 0:
        x, b = x[-b:], 0
    n = min(len(x), len(y) - b)
    if n > 0:
        y[b:b + n] = x[:n]
    write_wav(args.out, fade(y))
    print(f"{args.out}: placed at {args.at:+.2f}s without stretching")


def transcribe(args) -> None:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("pip install faster-whisper")
    model = WhisperModel(args.model, compute_type="int8")
    segments, _ = model.transcribe(args.transcribe, language=args.language, word_timestamps=True)
    words = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
             for s in segments for w in (s.words or [])]
    json.dump(words, sys.stdout, ensure_ascii=False, indent=1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audio")
    ap.add_argument("--audio-words")
    ap.add_argument("--video-words")
    ap.add_argument("--place", help="recording to place without stretching (off-screen voices)")
    ap.add_argument("--at", type=float, default=0.0, help="start time for --place, seconds on the shot timeline")
    ap.add_argument("--duration", type=float, help="shot length in seconds")
    ap.add_argument("--out")
    ap.add_argument("--transcribe", help="media file to transcribe to word JSON (stdout)")
    ap.add_argument("--language")
    ap.add_argument("--model", default="small")
    args = ap.parse_args()
    if args.transcribe:
        transcribe(args)
    elif args.place:
        if args.duration is None or not args.out:
            ap.error("--place needs --duration and --out")
        place(args)
    else:
        if not all([args.audio, args.audio_words, args.video_words, args.duration, args.out]):
            ap.error("alignment needs --audio --audio-words --video-words --duration --out")
        align(args)


if __name__ == "__main__":
    main()
