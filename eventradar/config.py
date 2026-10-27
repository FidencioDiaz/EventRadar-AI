"""Configuration for classification, scoring, and application labels."""

from __future__ import annotations

CLASSIFICATION_RULES = {
    "IA y Machine Learning": (
        "artificial intelligence", "machine learning", "deep learning", "ia", "ml",
        "agente", "llm", "generative ai", "inteligencia artificial",
    ),
    "Cloud y arquitectura de soluciones": (
        "cloud", "saaS", "arquitectura", "architecture", "infraestructura",
        "devops", "aws", "azure", "gcp", "software as a service",
    ),
    "Ingeniería de software": (
        "software", "developer", "desarrollo", "programación", "engineering",
        "qa", "testing", "dev house", "backend", "frontend", "full stack",
    ),
    "Datos y analítica": (
        "data", "datos", "analytics", "analítica", "database", "bi ",
        "intelligence", "metric", "estadística",
    ),
    "Investigación y Deep Tech": (
        "deep tech", "research", "investigación", "ciencia", "quantum",
        "biotech", "healthtech", "innovation",
    ),
    "Robótica y hardware": (
        "robot", "hardware", "iot", "embedded", "maker", "electrónica",
        "mobility",
    ),
    "Startups y emprendimiento": (
        "startup", "startups", "entrepreneur", "emprendimiento", "founder",
        "fundraising", "venture", "pitch", "investor", "capital",
    ),
    "Carrera y networking": (
        "networking", "community", "talent", "career", "hiring", "mentor",
        "conecta", "founders", "meetup",
    ),
    "Música y tecnología creativa": (
        "music", "música", "creative", "creativo", "arttech", "design",
        "comedy", "gaming", "entertainment",
    ),
    "Otras industrias tecnológicas": (
        "fintech", "legal tech", "e-commerce", "edtech", "climate",
        "foodtech", "proptech", "logistics", "contech",
    ),
}

SCORE_WEIGHTS = {
    "Alineación con intereses": 25,
    "Valor profesional": 20,
    "Networking": 20,
    "Aprendizaje": 15,
    "Valor estratégico": 10,
    "Viabilidad": 10,
}

DEFAULT_INTERESTS = (
    "artificial intelligence", "data", "software", "startup", "networking",
    "cloud", "technology",
)

