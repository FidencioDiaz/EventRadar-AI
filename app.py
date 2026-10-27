"""Streamlit UI for EventRadar AI."""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import streamlit as st

from eventradar.agenda import find_overlaps
from eventradar.classifier import add_classifications
from eventradar.loader import CatalogError, load_catalog
from eventradar.scoring import add_scores

ROOT = Path(__file__).parent
DEFAULT_CATALOG = ROOT / "data" / "events_raw.json"


@st.cache_data(show_spinner=False)
def prepare_catalog(path: str) -> pd.DataFrame:
    frame = load_catalog(path)
    return add_scores(add_classifications(frame))


def _display_columns(frame: pd.DataFrame) -> pd.DataFrame:
    columns = {
        "event_name": "Evento", "event_date": "Fecha", "start_time": "Inicio",
        "format": "Formato", "industry": "Industria", "statusLabel": "Estado",
        "freshness": "Vigencia", "score": "Puntuación", "org": "Organización",
    }
    selected = [column for column in columns if column in frame.columns]
    result = frame[selected].rename(columns=columns).copy()
    if "Fecha" in result:
        result["Fecha"] = result["Fecha"].dt.strftime("%Y-%m-%d").fillna("Sin fecha")
    return result


def _multiselect(frame: pd.DataFrame, label: str, column: str) -> list[str]:
    values = sorted({
        str(value) for item in frame[column].dropna()
        for value in (item if isinstance(item, list) else [item]) if str(value)
    })
    return st.sidebar.multiselect(label, values)


def main() -> None:
    st.set_page_config(page_title="EventRadar AI", page_icon="📡", layout="wide")
    st.title("📡 EventRadar AI")
    st.caption("Explora, clasifica y prioriza eventos con reglas transparentes. Las puntuaciones son heurísticas.")
    catalog_path = st.sidebar.text_input("Catálogo JSON", str(DEFAULT_CATALOG))
    try:
        frame = prepare_catalog(catalog_path)
    except CatalogError as exc:
        st.error(str(exc))
        st.stop()

    st.sidebar.header("Explorar")
    query = st.sidebar.text_input("Buscar texto")
    today = pd.Timestamp.now().normalize()
    exclude_past = st.sidebar.checkbox("Excluir eventos pasados", value=False)
    freshness = st.sidebar.multiselect("Vigencia", sorted(frame["freshness"].dropna().unique()))
    filters = [
        ("Categoría", "categories_list"), ("Formato", "format"), ("Idioma", "language"),
        ("Coste", "costModel"), ("Modalidad", "modality"), ("Audiencia", "audience_list"),
        ("Estado de inscripción", "registration_status"),
    ]
    selected = {column: _multiselect(frame, label, column) for label, column in filters}

    filtered = frame.copy()
    if query:
        filtered = filtered[filtered["source_text"].str.contains(query.lower(), regex=False, na=False)]
    if exclude_past:
        filtered = filtered[filtered["event_date"].isna() | (filtered["event_date"] >= today)]
    if freshness:
        filtered = filtered[filtered["freshness"].isin(freshness)]
    for column, values in selected.items():
        if values:
            filtered = filtered[filtered[column].apply(
                lambda value: any(str(item) in values for item in (value if isinstance(value, list) else [value]))
            )]
    order = st.sidebar.radio("Ordenar por", ["Puntuación", "Fecha"], horizontal=True)
    filtered = filtered.sort_values("score" if order == "Puntuación" else "event_date", ascending=False if order == "Puntuación" else True, na_position="last")

    tabs = st.tabs(["Explorar", "Recomendados", "Descubrir", "Agenda", "Exportar"])
    with tabs[0]:
        st.metric("Eventos visibles", len(filtered))
        st.dataframe(_display_columns(filtered), use_container_width=True, hide_index=True)
        _event_links(filtered)
    with tabs[1]:
        recommended = filtered.nlargest(10, "score")
        for _, row in recommended.iterrows():
            st.subheader(f"{row['event_name']} · {row['score']}/100")
            st.write(row["recommendation_reason"])
            st.caption("Categorías: " + ", ".join(row["classification_labels"]))
            _single_link(row)
    with tabs[2]:
        st.write("Estas categorías no se excluyen del catálogo; sirven para descubrir temas distintos.")
        labels = sorted({label for labels in filtered["classification_labels"] for label in labels})
        chosen = st.multiselect("Categorías", labels)
        discover = filtered if not chosen else filtered[filtered["classification_labels"].apply(lambda values: any(label in chosen for label in values))]
        st.dataframe(_display_columns(discover), use_container_width=True, hide_index=True)
    with tabs[3]:
        _agenda_tab(filtered)
    with tabs[4]:
        csv = _display_columns(filtered).to_csv(index=False).encode("utf-8-sig")
        st.download_button("Descargar resultados filtrados (CSV)", csv, "eventradar_eventos.csv", "text/csv")


def _single_link(row: pd.Series) -> None:
    url = row.get("lumaUrl") or row.get("eventPageUrl")
    if url:
        st.markdown(f"[Abrir evento original]({url})")
    else:
        st.caption("No hay enlace original informado por el catálogo.")


def _event_links(frame: pd.DataFrame) -> None:
    if not frame.empty:
        st.caption("Los enlaces se muestran sólo cuando el catálogo los informa.")
        for _, row in frame.head(20).iterrows():
            _single_link(row)


def _agenda_tab(frame: pd.DataFrame) -> None:
    options = dict(zip(frame["event_id"], frame["event_name"]))
    chosen = st.multiselect("Selecciona eventos", list(options), format_func=lambda key: options[key])
    agenda = frame[frame["event_id"].isin(chosen)].sort_values(["event_date", "start_time"], na_position="last")
    st.dataframe(_display_columns(agenda), use_container_width=True, hide_index=True)
    overlaps = find_overlaps(agenda)
    if overlaps:
        st.warning(f"Empalmes detectados con fecha y horarios completos: {len(overlaps)}")
        st.write(overlaps)
    elif chosen:
        st.info("No se detectaron empalmes con la información de horarios disponible.")
    st.caption("La selección vive en la sesión actual de Streamlit; no se persiste entre sesiones.")


if __name__ == "__main__":
    main()

