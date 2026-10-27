"""Agenda selection and overlap detection."""

from __future__ import annotations

from datetime import datetime

import pandas as pd


def _datetime(row: pd.Series, field: str) -> datetime | None:
    date = row.get("event_date")
    value = row.get(field)
    if pd.isna(date) or not value:
        return None
    try:
        return datetime.combine(date.date(), datetime.strptime(str(value), "%H:%M").time())
    except (TypeError, ValueError):
        return None


def find_overlaps(frame: pd.DataFrame) -> list[tuple[str, str]]:
    """Return pairs with known date/time ranges that overlap."""
    intervals = []
    for _, row in frame.iterrows():
        start = _datetime(row, "start_time")
        end = _datetime(row, "end_time") or start
        if start and end:
            intervals.append((row["event_id"], row["event_name"], start, end))
    overlaps = []
    for index, left in enumerate(intervals):
        for right in intervals[index + 1:]:
            if left[2] < right[3] and right[2] < left[3]:
                overlaps.append((left[0], right[0]))
    return overlaps

