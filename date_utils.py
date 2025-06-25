import pytz
from dateutil import parser
from datetime import datetime, timedelta
import logging

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def parse_timestamp(timestamp_str, timezone_str):
    try:
        if not timestamp_str or timestamp_str.strip().lower() in ("nan", "none"):
            return None

        # Try parsing timestamp (handle ambiguous formats like UK)
        try:
            dt = parser.parse(timestamp_str, dayfirst=True)
        except Exception:
            dt = parser.parse(timestamp_str)  # fallback if dayfirst fails

        # Handle timezone fallback if needed
        tz = None
        if not timezone_str or timezone_str.strip() == "":
            tz = pytz.UTC
        else:
            try:
                tz = pytz.timezone(timezone_str)
            except Exception:
                # Try forgiving match
                possible = [z for z in pytz.all_timezones if timezone_str.lower() in z.lower()]
                if possible:
                    tz = pytz.timezone(possible[0])
                else:
                    return None  # unresolvable

        # If timestamp is naive, localize it
        if dt.tzinfo is None:
            try:
                localized = tz.localize(dt, is_dst=True)
            except pytz.NonExistentTimeError:
                # Spring forward: shift by 1 hour
                logger.warning(f"Spring forward ambiguity: {timestamp_str} — jumping forward 1 hour")
                dt += timedelta(hours=1)
                localized = tz.localize(dt, is_dst=True)
            except pytz.AmbiguousTimeError:
                # Fall back: assume DST is still on
                logger.warning(f"Fall back ambiguity: {timestamp_str} — using first occurrence")
                localized = tz.localize(dt, is_dst=True)
        else:
            localized = dt.astimezone(tz)

        return localized.astimezone(pytz.UTC)

    except Exception as e:
        logger.warning(f"⚠️ Failed to parse timestamp '{timestamp_str}' with timezone '{timezone_str}': {e}")
        return None


def convert_utc_to_timezone(utc_dt, tz_str):
    try:
        tz = pytz.timezone(tz_str)
        local_dt = utc_dt.astimezone(tz)
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.warning(f"Timezone conversion error: {e}")
        return utc_dt.strftime("%Y-%m-%d %H:%M:%S")

def is_valid_datetime(timestamp_str):
    try:
        parser.parse(timestamp_str)
        return True
    except:
        return False

