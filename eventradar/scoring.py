"""Heuristic scoring with component-level explanations and missing-data flags."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from .config import DEFAULT_INTERESTS, SCORE_WEIGHTS


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term.lower() in text for term in terms)


def score_event(event: dict[str, Any] | pd.Series, interests: Iterable[str] = DEFAULT_INTERESTS) -> tuple[int, dict[str, int], list[str]]:
    text = str(event.get("source_text") or "")
    categories = " ".join(str(x) for x in event.get("categories_list", []))
    combined = f"{text} {categories}".lower()
    missing: list[str] = []
    if not event.get("event_date") or pd.isna(event.get("event_date")):
        missing.append("fecha")
    if not event.get("start_time"):
        missing.append("hora")
    if not event.get("costModel"):
        missing.append("coste")
    if not event.get("registration_status"):
        missing.append("inscripción")

    components = {
        "Alineación con intereses": round(SCORE_WEIGHTS["Alineación con intereses"] * (
            1 if _contains_any(combined, interests) else 0
        )),
        "Valor profesional": round(SCORE_WEIGHTS["Valor profesional"] * (
            1 if _contains_any(combined, ("founder", "career", "talent", "developer", "learning", "workshop")) else 0
        )),
        "Networking": round(SCORE_WEIGHTS["Networking"] * (
            1 if _contains_any(combined, ("networking", "community", "meetup", "mixer", "panel")) else 0
        )),
        "Aprendizaje": round(SCORE_WEIGHTS["Aprendizaje"] * (
            1 if _contains_any(combined, ("learning", "workshop", "masterclass", "talk", "keynote")) else 0
        )),
        "Valor estratégico": round(SCORE_WEIGHTS["Valor estratégico"] * (
            1 if _contains_any(combined, ("investor", "fundraising", "strategy", "c-level", "partnership")) else 0
        )),
        "Viabilidad": round(SCORE_WEIGHTS["Viabilidad"] * (
            1 if event.get("registration_status") in {"open", "waitlist"} and event.get("freshness") in {"fresh", "aging"} else 0
        )),
    }
    return min(100, sum(components.values())), components, missing


def add_scores(frame: pd.DataFrame, interests: Iterable[str] = DEFAULT_INTERESTS) -> pd.DataFrame:
    result = frame.copy()
    scored = result.apply(lambda row: score_event(row, interests), axis=1)
    result["score"] = scored.map(lambda item: item[0])
    result["score_components"] = scored.map(lambda item: item[1])
    result["score_missing"] = scored.map(lambda item: item[2])
    result["recommendation_reason"] = result.apply(_reason, axis=1)
    return result


def _reason(row: pd.Series) -> str:
    top = sorted(row["score_components"].items(), key=lambda item: item[1], reverse=True)
    active = [name for name, value in top if value > 0][:2]
    reason = " y ".join(active) if active else "coincidencias limitadas"
    if row["score_missing"]:
        reason += f"; faltan datos: {', '.join(row['score_missing'])}"
    if row.get("freshness") in {"stale", "aging"}:
        reason += "; disponibilidad desactualizada"
    return reason

