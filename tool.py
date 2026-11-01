import argparse
import json
import math
import sys
from collections import Counter

FILLERS = {"um", "uh", "er", "ah", "like", "you know", "so", "actually", "basically"}


class TranscriptError(ValueError):
    pass


def _words(text):
    return [w.strip(".,!?;:()[]{}\"'").lower() for w in str(text).split() if w.strip()]


def _items(data):
    if isinstance(data, dict):
        if "words" in data:
            return data["words"]
        raise TranscriptError("expected a list of timestamped items or an object with a 'words' list")
    return data


def validate(data, label="transcript"):
    items = _items(data)
    if not isinstance(items, list):
        raise TranscriptError(f"{label}: transcript must be a list")
    if not items:
        raise TranscriptError(f"{label}: transcript is empty")
    out = []
    last_start = -1.0
    for i, row in enumerate(items):
        if not isinstance(row, dict):
            raise TranscriptError(f"{label}: item {i} must be an object")
        try:
            start, end, text = row["start"], row["end"], row["text"]
        except KeyError as e:
            raise TranscriptError(f"{label}: item {i} missing {e.args[0]!r}") from None
        if not isinstance(text, str) or not text.strip():
            raise TranscriptError(f"{label}: item {i} text must be a non-empty string")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise TranscriptError(f"{label}: item {i} start/end must be numbers")
        if not math.isfinite(start) or not math.isfinite(end):
            raise TranscriptError(f"{label}: item {i} start/end must be finite")
        if start < 0 or end < 0:
            raise TranscriptError(f"{label}: item {i} times cannot be negative")
        if end < start:
            raise TranscriptError(f"{label}: item {i} end precedes start")
        if start < last_start:
            raise TranscriptError(f"{label}: item {i} starts before a previous item")
        last_start = start
        out.append({"start": float(start), "end": float(end), "text": text})
    if out[-1]["end"] <= out[0]["start"]:
        raise TranscriptError(f"{label}: total duration must be greater than zero")
    return out


def analyze(data, label="transcript", pause_threshold=0.75, window=60.0):
    rows = validate(data, label)
    tokens = []
    filler = Counter()
    for row in rows:
        ws = _words(row["text"])
        tokens.extend(ws)
        phrase = " ".join(ws)
        for f in FILLERS:
            if " " in f:
                filler[f] += phrase.count(f)
        for w in ws:
            if w in FILLERS:
                filler[w] += 1
    duration = rows[-1]["end"] - rows[0]["start"]
    pauses = []
    for a, b in zip(rows, rows[1:]):
        gap = b["start"] - a["end"]
        if gap >= pause_threshold:
            pauses.append({"after": a["text"], "seconds": round(gap, 2)})
    pace = []
    t = rows[0]["start"]
    end = rows[-1]["end"]
    while t < end:
        n = sum(len(_words(r["text"])) for r in rows if r["start"] < t + window and r["end"] >= t)
        pace.append({"from": round(t, 1), "to": round(min(t + window, end), 1), "wpm": round(n * 60.0 / min(window, end - t), 1)})
        t += window
    return {
        "label": label,
        "duration_seconds": round(duration, 2),
        "word_count": len(tokens),
        "overall_wpm": round(len(tokens) * 60.0 / duration, 1),
        "filler_counts": dict(sorted((k, v) for k, v in filler.items() if v)),
        "pause_count": len(pauses),
        "longest_pauses": sorted(pauses, key=lambda p: p["seconds"], reverse=True)[:3],
        "pace_windows": pace,
    }


def compare(doc):
    if not isinstance(doc, dict) or "before" not in doc or "after" not in doc:
        return analyze(doc)
    before = analyze(doc["before"], "before")
    after = analyze(doc["after"], "after")
    return {"before": before, "after": after, "changes": {
        "wpm": round(after["overall_wpm"] - before["overall_wpm"], 1),
        "fillers": sum(after["filler_counts"].values()) - sum(before["filler_counts"].values()),
        "pauses": after["pause_count"] - before["pause_count"],
    }}


def main(argv=None):
    p = argparse.ArgumentParser(description="Analyze a local timestamped rehearsal transcript JSON file.")
    p.add_argument("path")
    args = p.parse_args(argv)
    try:
        with open(args.path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        print(json.dumps(compare(doc), indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, TranscriptError) as e:
        print(f"speakflow: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
