"""
Demo de Clase: Generación de Datos Sintéticos con Faker + FastAPI con Swagger Avanzado
Curso 2026-2027 · Big Data Aplicado · CIPFP Batoi

Para ejecutar:
    pip install fastapi uvicorn faker pydantic
    uvicorn demo_faker_fastapi:app --reload --port 8000
    
Acceso a la documentación interactiva Swagger:
    http://localhost:8000/docs
"""

import random
from datetime import datetime
from enum import Enum
from typing import List, Optional

from faker import Faker
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

# 1. Configuración de Faker (Localización en español de España)
fake = Faker("es_ES")

# 2. Metadatos OpenAPI para documentar la aplicación
tags_metadata = [
    {
        "name": "Telemetría Urbana",
        "description": "Consulta y monitorización de sensores ambientales en municipios de la Comunidad Valenciana.",
    },
    {
        "name": "Simulación & Big Data",
        "description": "Inyección al vuelo de ráfagas masivas de datos sintéticos generados con Faker.",
    },
]

app = FastAPI(
    title="CityData Streamer — API IoT con Faker 🏙️📡",
    description="""
    ## API de Simulación de Telemetría Urbana para Big Data
    
    Esta API permite a los alumnos interactuar con un **sistema de ingestión de datos sintéticos**,
    aprendiendo a consultar, filtrar y simular flujos masivos de eventos IoT.
    
    * 🎲 **Generación realista con Faker**: Nombres, ubicaciones, coordenadas GPS y anomalías.
    * 📑 **OpenAPI 3.1 & Swagger enriquecido**: Ejemplos preconfigurados en el *Try it out*.
    * 🔍 **Filtros avanzados**: Consulta por municipio, umbrales de temperatura y alertas.
    """,
    version="1.0.0",
    contact={
        "name": "David Granados — Especialidad Big Data",
        "email": "d.granados@cipfpbatoi.es",
    },
    openapi_tags=tags_metadata,
)

# 3. Modelos Pydantic fuertemente tipados
class EstadoSensor(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class ErrorResponse(BaseModel):
    detalle: str = Field(..., description="Mensaje explicativo del error", examples=["Sensor no encontrado en la red"])
    codigo_error: str = Field(..., description="Código de diagnóstico interno", examples=["SENSOR_NOT_FOUND"])


class LecturaSensor(BaseModel):
    id: str = Field(
        ...,
        description="Identificador universal único (UUID)",
        examples=["4b6c31bf-192a-4db3-9871-3467f6789abc"],
    )
    sensor_id: str = Field(
        ...,
        description="Código identificativo de hardware",
        examples=["SN-ALC-8321"],
    )
    ciudad: str = Field(
        ...,
        description="Municipio donde está instalado el sensor",
        examples=["Alcoy"],
    )
    latitud: float = Field(..., description="Coordenada geográfica", examples=[38.7052])
    longitud: float = Field(..., description="Coordenada geográfica", examples=[-0.4743])
    temperatura: float = Field(..., description="Temperatura ambiente en ºC", examples=[19.4])
    humedad: float = Field(..., description="Humedad relativa en %", examples=[58.0])
    co2_ppm: int = Field(..., description="Concentración de CO2 en ppm", examples=[415])
    estado: EstadoSensor = Field(..., description="Estado operativo del sensor", examples=["OK"])
    timestamp: datetime = Field(..., description="Marca de tiempo en UTC")


# 4. Almacén de datos en memoria para la sesión
DATABASE: List[LecturaSensor] = []


def crear_lectura_falsa(ciudad_forzada: Optional[str] = None) -> LecturaSensor:
    ciudades = ["Alcoy", "Valencia", "Alicante", "Castellón", "Elche", "Gandía"]
    ciudad = ciudad_forzada or random.choice(ciudades)
    
    # Simular una pequeña probabilidad de anomalía ambiental
    estado = random.choices(
        [EstadoSensor.OK, EstadoSensor.WARNING, EstadoSensor.CRITICAL],
        weights=[82, 14, 4]
    )[0]
    
    temp_base = 21.0 if estado != EstadoSensor.CRITICAL else 48.5
    
    return LecturaSensor(
        id=fake.uuid4(),
        sensor_id=f"SN-{ciudad[:3].upper()}-{fake.bothify(text='####')}",
        ciudad=ciudad,
        latitud=float(fake.latitude()),
        longitud=float(fake.longitude()),
        temperatura=round(random.gauss(temp_base, 3.5), 1),
        humedad=round(random.uniform(30.0, 95.0), 1),
        co2_ppm=random.randint(350, 1400) if estado != EstadoSensor.CRITICAL else random.randint(1800, 4500),
        estado=estado,
        timestamp=fake.date_time_between(start_date="-3h", end_date="now"),
    )


# Sembrar 40 lecturas iniciales al iniciar
DATABASE.extend([crear_lectura_falsa() for _ in range(40)])


# 5. Endpoints documentados con Swagger enriquecido
@app.get(
    "/api/v1/telemetry",
    response_model=List[LecturaSensor],
    tags=["Telemetría Urbana"],
    summary="Consultar lecturas de la red de sensores",
    description="Permite consultar el histórico reciente de lecturas IoT con filtrado opcional por ciudad o estado de alerta.",
    response_description="Lista de lecturas que cumplen los criterios de búsqueda.",
)
async def get_telemetry(
    ciudad: Optional[str] = Query(
        None,
        description="Filtrar por municipio específico",
        examples=["Alcoy"],
    ),
    estado: Optional[EstadoSensor] = Query(
        None,
        description="Filtrar por estado operativo (OK, WARNING, CRITICAL)",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Límite máximo de registros a recuperar",
    ),
):
    resultado = DATABASE
    if ciudad:
        resultado = [r for r in resultado if r.ciudad.lower() == ciudad.lower()]
    if estado:
        resultado = [r for r in resultado if r.estado == estado]
    return resultado[:limit]


@app.get(
    "/api/v1/telemetry/{sensor_id}",
    response_model=LecturaSensor,
    tags=["Telemetría Urbana"],
    summary="Obtener la última lectura de un sensor concreto",
    responses={
        200: {"description": "Lectura encontrada exitosamente."},
        404: {"model": ErrorResponse, "description": "El sensor especificado no existe en la base de datos."},
    },
)
async def get_sensor_by_id(sensor_id: str):
    for r in DATABASE:
        if r.sensor_id.upper() == sensor_id.upper():
            return r
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se ha encontrado ninguna lectura para el sensor '{sensor_id}'",
    )


@app.post(
    "/api/v1/simulate/burst",
    response_model=List[LecturaSensor],
    status_code=status.HTTP_201_CREATED,
    tags=["Simulación & Big Data"],
    summary="Inyectar ráfaga masiva de lecturas sintéticas",
    description="Genera al vuelo N eventos de telemetría con Faker y los añade a la colección en memoria.",
    response_description="Array con las nuevas lecturas sintéticas generadas.",
)
async def burst_simulation(
    count: int = Query(10, ge=1, le=100, description="Cantidad de lecturas a generar al vuelo"),
    ciudad: Optional[str] = Query(None, description="Forzar la ciudad de las mediciones generadas"),
):
    nuevas = [crear_lectura_falsa(ciudad_forzada=ciudad) for _ in range(count)]
    DATABASE.extend(nuevas)
    return nuevas


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("demo_faker_fastapi:app", host="0.0.0.0", port=8000, reload=True)

