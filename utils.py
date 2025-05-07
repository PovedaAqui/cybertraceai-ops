import pandas as pd
from datetime import datetime
from langchain_core.tools import tool

@tool
def humanize_timestamp_tool(timestamp_ms: int, tz: str = 'UTC') -> str:
    """Converts a UNIX epoch timestamp (in milliseconds) to a human-readable datetime string.

    Args:
        timestamp_ms: The UNIX epoch timestamp in milliseconds.
        tz: The target timezone (e.g., 'America/New_York', 'Europe/London'). Defaults to 'UTC'.

    Returns:
        A string representing the human-readable datetime in the specified timezone,
        formatted as YYYY-MM-DD HH:MM:SS ZZZ.
        Returns an error message string if conversion fails.
    """
    try:
        # Convert milliseconds to seconds
        timestamp_s = int(timestamp_ms) / 1000.0
        # Create datetime object from UTC timestamp
        dt_utc = datetime.utcfromtimestamp(timestamp_s)
        # Create a pandas Timestamp, localize to UTC, then convert to the target timezone
        pd_timestamp = pd.Timestamp(dt_utc, tz='UTC')
        dt_tz = pd_timestamp.tz_convert(tz)
        return dt_tz.strftime('%Y-%m-%d %H:%M:%S %Z')
    except Exception as e:
        return f"Error converting timestamp {timestamp_ms} to timezone {tz}: {str(e)}"

# Example usage (not part of the tool, just for testing)
if __name__ == '__main__':
    print(humanize_timestamp_tool.invoke({"timestamp_ms": 1678886400000})) 
    # Expected: 2023-03-15 12:00:00 UTC
    print(humanize_timestamp_tool.invoke({"timestamp_ms": 1678886400000, "tz": "America/New_York"})) 
    # Expected: 2023-03-15 08:00:00 EDT (or EST depending on date)
    print(humanize_timestamp_tool.invoke({"timestamp_ms": "invalid_input"}))
    # Expected: Error message 