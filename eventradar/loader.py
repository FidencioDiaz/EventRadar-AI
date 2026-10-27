"""Catalog loading, validation, normalization, and source adapters."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


class CatalogError(ValueError):
    """Raised when a catalog cannot be loaded or has no usable events."""


def load_json(path: str | Path) -> Any:
    """Load JSON with an actionable error for missing or invalid files."""
    source = Path(path)
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CatalogError(f"No existe el archivo de catálogo: {source}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"JSON inválido en {source}, línea {exc.lineno}: {exc.msg}") from exc


def extract_events(payload: Any) -> list[dict[str, Any]]:
    """Adapt common catalog envelopes without coupling to one provider."""
    if isinstance(payload, dict):
        events = payload.get("events")
        if events is None:
            events = payload.get("items")
    else:
        events = payload
    if not isinstance(events, list) or not events:
        raise CatalogError("El catálogo no contiene una lista de eventos no vacía.")
    valid = [item for item in events if isinstance(item, dict)]
    if not valid:
        raise CatalogError("El catálogo no contiene objetos de evento válidos.")
    return valid


def _as_text(value: Any) -> str:
    if isinstance(value, list):
        return " | ".join(_as_text(item) for item in value)
    if isinstance(value, dict):
        return " | ".join(f"{key}: {_as_text(item)}" for key, item in value.items())
    return "" if value is None else str(value)


def _availability(event: dict[str, Any], key: str) -> Any:
    availability = event.get("availability")
    return availability.get(key) if isinstance(availability, dict) else None


def normalize_events(events: Iterable[dict[str, Any]]) -> pd.DataFrame:
    """Create stable analysis columns while retaining each provider record."""
    rows: list[dict[str, Any]] = []
    for event in events:
        categories = event.get("categories") or []
        audience = event.get("audience") or []
        source_text = " ".join(
            _as_text(event.get(field))
            for field in ("name", "description", "industry", "mainOutcome", "format",
                          "categories", "audience", "house", "org")
        ).lower()
        row = dict(event)
        row.update({
            "event_id": event.get("id") or "",
            "event_name": event.get("name") or "(sin nombre)",
            "event_date": pd.to_datetime(event.get("date"), errors="coerce"),
            "start_time": event.get("startTime"),
            "end_time": event.get("endTime"),
            "categories_list": categories if isinstance(categories, list) else [categories],
            "audience_list": audience if isinstance(audience, list) else [audience],
            "source_text": source_text,
            "registration_status": _availability(event, "registration") or event.get("status"),
            "freshness": _availability(event, "freshness") or "missing",
            "occupancy": _availability(event, "occupancy") or "unknown",
            "original_event": event,
        })
        rows.append(row)
    return pd.DataFrame(rows)


def load_catalog(path: str | Path) -> pd.DataFrame:
    return normalize_events(extract_events(load_json(path)))

