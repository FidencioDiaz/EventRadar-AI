"""Transparent, configurable multi-label event classification."""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from .config import CLASSIFICATION_RULES


def classify_event(event: Mapping[str, object], rules: Mapping[str, tuple[str, ...]] = CLASSIFICATION_RULES) -> tuple[list[str], dict[str, list[str]]]:
    text = str(event.get("source_text") or "").lower()
    labels: list[str] = []
    activated: dict[str, list[str]] = {}
    for label, terms in rules.items():
        hits = sorted({term for term in terms if term.lower() in text})
        if hits:
            labels.append(label)
            activated[label] = hits
    if not labels:
        labels = ["Otras industrias tecnológicas"]
        activated[labels[0]] = []
    return labels, activated


def add_classifications(frame: pd.DataFrame, rules: Mapping[str, tuple[str, ...]] = CLASSIFICATION_RULES) -> pd.DataFrame:
    result = frame.copy()
    classified = result.apply(lambda row: classify_event(row, rules), axis=1)
    result["classification_labels"] = classified.map(lambda item: item[0])
    result["classification_rules"] = classified.map(lambda item: item[1])
    return result

