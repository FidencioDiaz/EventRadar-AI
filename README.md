# EventRadar AI

EventRadar AI es una aplicación web reutilizable para explorar, clasificar y
priorizar eventos tecnológicos. El MVP usa el catálogo público exportado de
México Tech Week, pero separa la carga y normalización de la lógica de negocio
para poder incorporar catálogos futuros de otras fuentes.

## Problema y objetivos

Los catálogos de eventos suelen mezclar campos opcionales, estados de
inscripción y distintas formas de expresar temas. EventRadar AI ayuda a:

- encontrar eventos mediante texto y filtros;
- agruparlos con clasificación multietiqueta explicable;
- priorizarlos con una puntuación heurística configurable;
- descubrir eventos fuera de las categorías prioritarias;
- construir una agenda temporal y detectar empalmes conocidos;
- exportar los resultados filtrados a CSV.

La aplicación no convierte estimaciones en hechos: conserva la frescura y el
estado de inscripción informados por la fuente, y muestra los datos faltantes.

## Arquitectura

```text
data/events_raw.json
        |
        v
eventradar/loader.py       carga, validación, adaptadores y normalización
        |
        +--> eventradar/classifier.py  reglas multietiqueta explicables
        |
        +--> eventradar/scoring.py     componentes y puntuación 0-100
        |
        +--> eventradar/agenda.py      intervalos y empalmes
        |
        v
app.py                     interfaz Streamlit, filtros y exportación
```

- **Carga y validación:** `loader.py` acepta una lista de eventos o
  envoltorios con `events` o `items`, valida JSON y produce errores explícitos.
- **Esquema normalizado:** se añaden columnas como `event_id`, `event_name`,
  `event_date`, `registration_status` y `freshness`, sin eliminar el objeto
  original (`original_event`).
- **Clasificación:** `classifier.py` aplica reglas configurables a nombre,
  descripción, industria, resultado, formato, categorías, audiencia,
  organización y house.
- **Puntuación:** `scoring.py` calcula seis componentes y registra datos
  faltantes y el motivo de recomendación.
- **Interfaz:** `app.py` ofrece las vistas Explorar, Recomendados, Descubrir,
  Agenda y Exportar.

## Tecnologías

- Python 3.10+
- Streamlit
- pandas
- JSON y CSV
- pytest

No se usan APIs de pago ni servicios externos para ejecutar el MVP.

## Instalación

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Ejecución local

Desde la raíz del proyecto:

```bash
streamlit run app.py
```

La aplicación inicia con `data/events_raw.json`. Para usar otro catálogo
compatible, cambia el campo **Catálogo JSON** de la barra lateral. El archivo
puede ser:

- una lista de objetos de evento;
- un objeto con una propiedad `events`;
- un objeto con una propiedad `items`.

Los objetos pueden tener campos opcionales. La aplicación no inventa fechas,
horas, precios, enlaces ni estados de inscripción.

## Estructura del proyecto

```text
.
├── app.py
├── eventradar/
│   ├── agenda.py
│   ├── classifier.py
│   ├── config.py
│   ├── loader.py
│   └── scoring.py
├── data/
│   ├── available_filters.json
│   ├── events_raw.json
│   └── extraction_report.md
├── tests/
│   └── test_core.py
├── requirements.txt
├── README.md
└── .gitignore
```

Los JSON de `data/` son datos públicos necesarios para ejecutar el MVP y no se
excluyen del repositorio. Los entornos virtuales, cachés, secretos y archivos
temporales sí quedan excluidos mediante `.gitignore`.

## Clasificación multietiqueta

Las categorías iniciales se configuran en `eventradar/config.py`:

- IA y Machine Learning
- Cloud y arquitectura de soluciones
- Ingeniería de software
- Datos y analítica
- Investigación y Deep Tech
- Robótica y hardware
- Startups y emprendimiento
- Carrera y networking
- Música y tecnología creativa
- Otras industrias tecnológicas

Las reglas buscan términos en texto normalizado construido con los campos
reales disponibles: nombre, descripción, industria, resultado principal,
formato, categorías, audiencia, organización y house. Un evento puede recibir
varias etiquetas. La interfaz conserva las palabras que activaron cada regla.

Una coincidencia léxica es una señal heurística, no una clasificación segura.
Las reglas se pueden ampliar o sustituir sin cambiar el cargador ni la UI.

## Puntuación y recomendaciones

La puntuación total está limitada a 0–100 y suma estos componentes:

| Componente | Máximo | Señales actuales |
|---|---:|---|
| Alineación con intereses | 25 | coincidencias con intereses tecnológicos configurados |
| Valor profesional | 20 | aprendizaje, desarrollo, carrera, talento o founders |
| Networking | 20 | networking, comunidad, meetup, mixer o panel |
| Aprendizaje | 15 | learning, workshop, masterclass, charla o keynote |
| Valor estratégico | 10 | inversión, fundraising, estrategia, C-level o partnerships |
| Viabilidad | 10 | inscripción `open`/`waitlist` y frescura `fresh`/`aging` |

Cada componente es una señal binaria en este MVP; por eso la puntuación es una
estimación orientativa, no una medida objetiva. Si faltan fecha, hora, coste o
inscripción, se informa en la explicación. La aplicación tampoco infiere que
un evento sea gratuito o que esté abierto cuando la fuente no lo dice.

Los estados `stale` y `aging` se mantienen visibles y no se presentan como
información en tiempo real.

## Pruebas

```bash
pytest -q
```

Las pruebas cubren carga del catálogo real, preservación del registro original,
JSON inválido, campos faltantes, clasificación explicable, límites de
puntuación y detección de empalmes.

## Despliegue

### Streamlit Community Cloud

1. Crea un repositorio público o privado en GitHub.
2. Sube `app.py`, `eventradar/`, `data/`, `tests/`, `requirements.txt`,
   `README.md` y `.gitignore`.
3. En Streamlit Community Cloud selecciona el repositorio y la rama.
4. Define `app.py` como archivo principal.
5. Despliega y comprueba la carga del catálogo y la descarga CSV.

### Otro servicio Python

1. Instala `requirements.txt`.
2. Expón el proceso con:

   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
   ```

3. Monta `data/` como parte de la imagen o del artefacto de despliegue.
4. Configura el puerto del proveedor y ejecuta `pytest -q` en CI antes de
   publicar.

No se requieren secretos para este MVP. Si una futura fuente necesita
credenciales, deben configurarse como secretos del proveedor, nunca
almacenarse en el repositorio ni en `data/`.

## Limitaciones conocidas

- La clasificación y puntuación son reglas heurísticas basadas en texto.
- El catálogo inicial tiene eventos con datos de frescura desactualizados.
- Hay eventos sin fecha u horario; no se inventan valores ni se fuerzan
  empalmes.
- La agenda persiste selecciones sólo durante la sesión actual de Streamlit.
- El catálogo de origen no informa `eventPageUrl` y algunos eventos no tienen
  `lumaUrl`, por lo que pueden no tener enlace original.
- No hay base de datos, autenticación ni persistencia multiusuario.
- Los datos son un snapshot; su actualización requiere una nueva extracción.
