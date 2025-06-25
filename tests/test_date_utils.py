import unittest
from date_utils import parse_timestamp
import pytz

class TestParseTimestamp(unittest.TestCase):

    def test_iso_standard(self):
        ts = "2024-01-15 14:30:00"
        self.assertIsNotNone(parse_timestamp(ts, "UTC"))

    def test_us_format(self):
        ts = "01/15/24 2:30 PM"
        self.assertIsNotNone(parse_timestamp(ts, "America/New_York"))

    def test_uk_format(self):
        ts = "15-Jan-2024 14:30"
        self.assertIsNotNone(parse_timestamp(ts, "Europe/London"))

    def test_iso_with_utc(self):
        ts = "2024-01-15T14:30:00Z"
        self.assertIsNotNone(parse_timestamp(ts, None))

    def test_iso_without_timezone(self):
        ts = "2024-01-15T14:30:00"
        self.assertIsNotNone(parse_timestamp(ts, "America/New_York"))

    def test_microseconds(self):
        ts = "2024-01-15 14:30:00.123456"
        self.assertIsNotNone(parse_timestamp(ts, "UTC"))

    def test_date_only(self):
        ts = "2024-01-15"
        self.assertIsNotNone(parse_timestamp(ts, "UTC"))

    def test_missing_timezone(self):
        ts = "2024-01-15 12:00:00"
        self.assertIsNotNone(parse_timestamp(ts, ""))  # should assume UTC

    def test_invalid_timezone(self):
        ts = "2024-01-15 12:00:00"
        result = parse_timestamp(ts, "Mars/SpaceTime")
        self.assertIsNone(result)  # unresolvable zone

if __name__ == "__main__":
    unittest.main()
