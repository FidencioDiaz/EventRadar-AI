import json

import pandas as pd
import pytest

from eventradar.agenda import find_overlaps
from eventradar.classifier import add_classifications
from eventradar.loader import CatalogError, extract_events, load_catalog, normalize_events
from eventradar.scoring import add_scores


ROOT = "data/events_raw.json"


def test_real_catalog_loads_and_preserves_count():
    frame = add_scores(add_classifications(load_catalog(ROOT)))
    assert len(frame) == 589
    assert frame["event_id"].nunique() == 589
    assert frame["original_event"].map(lambda event: isinstance(event, dict)).all()


def test_missing_date_and_links_are_not_invented():
    frame = normalize_events([{"id": "x", "name": "Sin fecha", "date": None}])
    assert pd.isna(frame.iloc[0]["event_date"])
    assert frame.iloc[0]["lumaUrl"] if "lumaUrl" in frame else True


def test_invalid_catalog_has_explicit_error(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(CatalogError):
        load_catalog(path)
    with pytest.raises(CatalogError):
        extract_events({"events": []})


def test_classification_records_activated_rules():
    frame = add_classifications(normalize_events([{
        "id": "x", "name": "AI workshop", "description": "networking",
        "categories": ["Artificial Intelligence"], "audience": [],
    }]))
    assert "IA y Machine Learning" in frame.iloc[0]["classification_labels"]
    assert frame.iloc[0]["classification_rules"]["IA y Machine Learning"]


def test_score_is_bounded_and_reports_missing_fields():
    frame = add_scores(add_classifications(normalize_events([{"id": "x", "name": "Evento"}])))
    row = frame.iloc[0]
    assert 0 <= row["score"] <= 100
    assert "fecha" in row["score_missing"]
    assert "coste" in row["score_missing"]


def test_agenda_detects_known_overlap():
    frame = normalize_events([
        {"id": "a", "name": "A", "date": "2026-10-26", "startTime": "10:00", "endTime": "11:00"},
        {"id": "b", "name": "B", "date": "2026-10-26", "startTime": "10:30", "endTime": "11:30"},
    ])
    assert find_overlaps(frame) == [("a", "b")]
