import math
import unittest

import tool


class BoundaryInputTests(unittest.TestCase):
    def test_empty_transcript_has_clear_error(self):
        with self.assertRaisesRegex(tool.TranscriptError, "empty"):
            tool.analyze([])

    def test_zero_total_duration_rejected(self):
        data = [{"start": 1.0, "end": 1.0, "text": "hello"}]
        with self.assertRaisesRegex(tool.TranscriptError, "duration"):
            tool.analyze(data)

    def test_rejects_nan_and_negative_times(self):
        with self.assertRaisesRegex(tool.TranscriptError, "finite"):
            tool.analyze([{"start": 0.0, "end": math.nan, "text": "x"}])
        with self.assertRaisesRegex(tool.TranscriptError, "negative"):
            tool.analyze([{"start": -0.1, "end": 1.0, "text": "x"}])

    def test_rejects_unsorted_and_reversed_items(self):
        with self.assertRaisesRegex(tool.TranscriptError, "precedes"):
            tool.analyze([{"start": 2, "end": 1, "text": "bad"}])
        with self.assertRaisesRegex(tool.TranscriptError, "before a previous"):
            tool.analyze([
                {"start": 1, "end": 2, "text": "first"},
                {"start": 0, "end": 3, "text": "second"},
            ])

    def test_counts_fillers_pauses_and_compare_deltas(self):
        before = [
            {"start": 0, "end": 1, "text": "Um I like tests"},
            {"start": 2, "end": 3, "text": "actually they help"},
        ]
        after = [
            {"start": 0, "end": 1, "text": "I test"},
            {"start": 1.2, "end": 2.2, "text": "they help"},
        ]
        result = tool.compare({"before": before, "after": after})
        self.assertEqual(result["before"]["filler_counts"], {"actually": 1, "like": 1, "um": 1})
        self.assertEqual(result["before"]["pause_count"], 1)
        self.assertEqual(result["changes"]["fillers"], -3)
        self.assertEqual(result["changes"]["pauses"], -1)


if __name__ == "__main__":
    unittest.main()
