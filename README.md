# Speakflow

Speakflow is a tiny offline rehearsal companion for speakers who already have local timestamped transcripts. It does **not** record audio, perform speech recognition, call networks, or infer mental health/personality traits.

## User and problem

For a speaker practicing a short talk, raw transcripts make it hard to spot simple delivery issues. Speakflow reports transparent counts for filler words, pace windows, pause patterns, and optional before/after changes.

## Run the demo

```bash
python tool.py examples/tiny_transcript.json
```

Input is a JSON list of objects with `start`, `end`, and `text`, or an object containing `before` and `after` lists.

## Metrics

- `word_count` and `overall_wpm`
- 60-second `pace_windows`
- `filler_counts` for a small visible word list
- `pause_count` and up to three longest pauses using a 0.75s threshold
- before/after deltas for WPM, fillers, and pauses

Malformed, empty, non-finite, negative, unsorted, and zero-duration transcripts return clear errors instead of misleading metrics.

## Tradeoffs and non-goals

This first version is intentionally small. It uses simple whitespace tokenization and timestamp math, so punctuation-heavy transcripts may need cleanup. It is not a coaching diagnosis, speech recognizer, meeting analyzer, or cloud service.

## AI assistance and limitations

This code and documentation were drafted with AI assistance. Review outputs before using them for high-stakes talks; metrics are descriptive practice aids, not judgments.
