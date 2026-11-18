# Datos Sintéticos con Faker + APIs de Alto Nivel con FastAPI y Swagger Avanzado 🚀📊

> **Módulo:** Big Data Aplicado (BDA) / Sistemas de Big Data  
> **Unidad 1:** Sistemas, Microservicios y APIs  
> **Profesor:** David Granados  

---

## 1. Por qué la Generación de Datos Sintéticos es Crucial en Big Data

En la industria del Big Data y la ingeniería de datos, los desarrolladores se enfrentan continuamente al dilema del **«huevo y la gallina»**:
- Para diseñar un microservicio, un pipeline de Kafka, un modelo de Machine Learning o un dashboard en Grafana, **necesitas datos con volumen y variedad**.
- Pero **no puedes usar datos reales de producción** por normativas estrictas de privacidad (**RGPD / LOPD**), secreto comercial y seguridad.
- Escribir a mano 5 registros en un archivo JSON es aburrido, poco representativo y oculta casos límite (*edge cases* como caracteres especiales, tildes, formatos de teléfono internacionales o valores nulos).

Aquí es donde entra **Faker**: una librería de Python capaz de generar miles de registros realistas, localizados geográficamente y con relaciones lógicas en cuestión de milisegundos. 

Al combinar **Faker** con **FastAPI** y **Pydantic**, los alumnos no solo aprenden teoría: **construyen un backend vivo que simula un entorno real de producción**.

---

## 2. Dominando Faker: Generando Datos Chulos y Creíbles

### 2.1. Instalación y primeros pasos

```bash
pip install faker
```

```python
from faker import Faker

# Instancia básica (por defecto genera datos en inglés)
fake = Faker()

print(fake.name())       # e.g. "John Doe"
print(fake.email())      # e.g. "johndoe@example.com"
print(fake.address())    # e.g. "123 Elm St, Springfield"
```

### 2.2. Localización: Datos en Español (`es_ES`)

En Big Data local, queremos nombres, provincias, códigos postales y DNI/NIF con formato español:

```python
from faker import Faker

# Configuración en español de España
fake = Faker('es_ES')

print(fake.name())           # "Lucía Navarro Beltrán"
print(fake.address())        # "Calle Mayor 12, 4º B\n46001 Valencia"
print(fake.dni())            # "48291047X" (¡calcula la letra correcta!)
print(fake.phone_number())   # "+34 612 34 56 78"
print(fake.iban())           # "ES91 2100 0418 4502 0005 1332"
```

> **Consejo pro:** Puedes pasar una lista de idiomas para crear datasets internacionales:  
> `fake = Faker(['es_ES', 'en_US', 'fr_FR'])` generará una mezcla cosmopolita aleatoria.

### 2.3. i18n Extrema: Árabe, Chino y Alfabetos que rompen Webs y APIs

El error clásico en desarrollo y analítica de datos en Occidente es probar únicamente con nombres estándar como *"Juan García"* o *"John Doe"*. Cuando la aplicación entra a producción internacional, surgen errores catastróficos que Faker te permite anticipar:

1. **Árabe (`ar_SA`, `ar_AA`):** Lectura RTL (*Right to Left*). Invierte maquetaciones visuales en el frontend, desborda contenedores y rompe concatenaciones ingenuas de cadenas si no hay soporte de texto bidireccional (*bidi*).
2. **Chino (`zh_CN`, `zh_TW`):** Ideogramas multibyte UTF-8 (3 a 4 bytes por carácter). Si la base de datos o columna tiene codificación heredada (`latin1`), produce *Mojibake* (`????`) o truncamiento de texto. Además, nombres reales de 2 caracteres (ej: *"张伟"*) hacen explotar validaciones simplistas como `min_length=3`.
3. **Cirílico (`ru_RU`) y Japonés (`ja_JP`):** Caracteres especiales no ASCII que rompen cabeceras HTTP, codificación en URLs y búsquedas de texto.

```python
from faker import Faker

# Proveedores multilingües
fake_ar = Faker('ar_SA')   # Árabe (RTL)
fake_zh = Faker('zh_CN')   # Chino (Multibyte ideográfico)
fake_ja = Faker('ja_JP')   # Japonés (Kanji / Kana)
fake_ru = Faker('ru_RU')   # Ruso (Cirílico)

print("Árabe (RTL):", fake_ar.name(), "|", fake_ar.address())
# 'محمد بن سلمان' -> Comprueba si tu interfaz o API rompe la alineación

print("Chino (Multibyte):", fake_zh.name(), "|", fake_zh.city())
# '张伟' -> Comprueba si tu validador Pydantic min_length=3 lo rechaza indebidamente

# Dataset global ponderado con mezcla cosmopolita:
fake_global = Faker(['es_ES', 'ar_SA', 'zh_CN', 'en_US'])
usuarios_globales = [fake_global.name() for _ in range(10)]
```

### 2.4. Reproducibilidad con Seeds (Semillas)

En analítica y testing, a veces necesitas que los datos sean aleatorios pero **idénticos en cada ejecución** (para que las pruebas de integración pasen siempre):

```python
Faker.seed(42)
fake = Faker('es_ES')

# Esta llamada devolverá EXACTAMENTE el mismo nombre en cualquier ordenador
print(fake.name())
```

---

## 3. Generando Casos de Uso Reales de Big Data

### Caso A: Sensores IoT y Ciudades Inteligentes (Smart City)

```python
import random
from faker import Faker
from datetime import datetime

fake = Faker('es_ES')

def generar_lectura_iot(sensor_id: str = None) -> dict:
    return {
        "sensor_id": sensor_id or f"SN-{fake.bothify(text='???-####').upper()}",
        "ciudad": random.choice(["Alcoy", "Alicante", "Valencia", "Castellón"]),
        "coordenadas": {
            "lat": float(fake.latitude()),
            "lon": float(fake.longitude())
        },
        "temperatura_c": round(random.gauss(21.5, 4.0), 1),
        "humedad_pct": round(random.uniform(30.0, 95.0), 1),
        "co2_ppm": random.randint(380, 1100),
        "estado": random.choices(["OK", "WARNING", "CRITICAL"], weights=[85, 12, 3])[0],
        "timestamp": fake.date_time_between(start_date="-2h", end_date="now").isoformat()
    }
```

### Caso B: Automoción, Flotas de Vehículos Conectados y Bastidores (VIN)

En el sector de Big Data y telemática (*Connected Cars*, logística de flotas, coches de alquiler y seguros inteligentes), el volumen de eventos de streaming por segundo es colosal. Faker permite modelar vehículos con fidelidad regulatoria:

* **Número de bastidor (VIN):** 17 caracteres alfanuméricos estandarizados bajo la norma internacional ISO 3779 (`fake.vin()`).
* **Matrícula española oficial:** 4 dígitos numéricos y 3 letras consonantes (`fake.bothify('#### ???').upper()`).
* **Telemetría en ruta:** Odómetro acumulado, velocidad con distribución normal gaussiana, nivel de combustible/batería (%) y códigos de diagnosis OBD-II estándar (`P0420`, `P0300`).

```python
import random
from faker import Faker

fake = Faker('es_ES')

def generar_evento_flota_vehiculo() -> dict:
    marcas_modelos = [
        ("Tesla", "Model 3", "Eléctrico"),
        ("Seat", "León", "Combustión"),
        ("Toyota", "Corolla", "Híbrido"),
        ("Renault", "Megane E-Tech", "Eléctrico"),
        ("Volvo", "XC60", "Híbrido Enchufable")
    ]
    marca, modelo, propuls = random.choice(marcas_modelos)

    return {
        "vin": fake.vin(),                                 # Bastidor ISO 3779 (17 car.)
        "matricula": fake.bothify('#### ???').upper(),     # Matrícula oficial España (ej: '5821 LXT')
        "marca": marca,
        "modelo": modelo,
        "tipo_propulsion": propuls,
        "conductor_asignado": fake.name(),
        "odometro_km": random.randint(15000, 185000),
        "velocidad_kmh": round(max(0.0, random.gauss(95.0, 18.0)), 1),
        "nivel_bateria_combustible_pct": random.randint(10, 100),
        "codigo_obd2": random.choices(
            ["P0000_OK", "P0420_CATALYST", "P0300_MISFIRE", "P0171_LEAN_BANK"],
            weights=[80, 10, 5, 5]
        )[0],
        "gps": {"lat": float(fake.latitude()), "lon": float(fake.longitude())},
        "timestamp": fake.date_time_between(start_date="-30m", end_date="now").isoformat()
    }
```

> **Ampliación con librerías comunitarias:** Para catálogos completos de vehículos reales puedes usar `pip install faker-vehicle` o crear tus propios proveedores heredando de `faker.providers.BaseProvider`.
            "latitud": float(fake.latitude()),
            "longitud": float(fake.longitude())
        },
        "temperatura": round(random.gauss(mu=22.5, sigma=5.0), 2),  # Distribución normal
        "humedad": round(random.uniform(30.0, 95.0), 1),
        "co2_ppm": random.randint(350, 1200),
        "estado": random.choices(["OK", "WARNING", "CRITICAL"], weights=[85, 12, 3])[0],
        "timestamp": fake.date_time_between(start_date="-1d", end_date="now").isoformat()
    }

# Generar 3 lecturas de prueba
print([generar_lectura_iot() for _ in range(3)])
```

### Caso B: E-Commerce y Transacciones Financieras con Relaciones

```python
def generar_cliente_con_pedidos(num_pedidos: int = 2) -> dict:
    cliente_id = fake.uuid4()
    return {
        "cliente_id": cliente_id,
        "nombre_completo": fake.name(),
        "nif": fake.dni(),
        "email": fake.free_email(),
        "tarjeta": {
            "proveedor": fake.credit_card_provider(),
            "numero_enmascarado": fake.credit_card_number(card_type=None)[-4:],
            "caducidad": fake.credit_card_expire()
        },
        "pedidos": [
            {
                "pedido_id": fake.uuid4(),
                "fecha": fake.date_this_year().isoformat(),
                "importe": round(random.uniform(9.99, 450.0), 2),
                "estado": random.choice(["ENTREGADO", "EN_TRANSITO", "CANCELADO"]),
                "articulos": [fake.word().capitalize() for _ in range(random.randint(1, 4))]
            }
            for _ in range(num_pedidos)
        ]
    }
```

---

## 4. Integrando Faker con Pydantic y FastAPI

Pydantic valida tipos y esquemas; Faker inyecta la vida. Veamos cómo modelar los datos con validaciones estrictas:

```python
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EstadoSensor(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class LecturaSensor(BaseModel):
    sensor_id: str = Field(..., description="Identificador único del sensor (formato SN-XXX-0000)")
    ciudad: str = Field(..., description="Nombre del municipio donde opera el sensor")
    temperatura: float = Field(..., ge=-20.0, le=60.0, description="Temperatura ambiental en grados Celsius")
    humedad: float = Field(..., ge=0.0, le=100.0, description="Porcentaje de humedad relativa")
    co2_ppm: int = Field(..., ge=200, le=5000, description="Concentración de CO2 en partes por millón")
    estado: EstadoSensor = Field(default=EstadoSensor.OK, description="Estado operativo del sensor")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Marca temporal UTC de la medición")
```

---

## 5. ¡A Meterle Caña a Swagger! Documentación Profesional con OpenAPI

FastAPI genera `/docs` automáticamente, pero la diferencia entre una API amateur y una API de nivel profesional está en **cómo enriqueces el OpenAPI**.

### 5.1. Metadatos Globales de la Aplicación

No te quedes con el título por defecto: añade descripción en Markdown, versiones, términos y tags organizados:

```python
from fastapi import FastAPI

tags_metadata = [
    {
        "name": "Sensores IoT",
        "description": "Operaciones de telemetría, lectura en tiempo real y simulación de métricas ambientales.",
    },
    {
        "name": "Simulación & Big Data",
        "description": "Endpoints generadores de datasets masivos con Faker para alimentar pipelines de datos.",
    },
]

app = FastAPI(
    title="Smart City Big Data API 🏙️⚡",
    description="""
    ## API de Telemetría Urbana y Simulación de Datos Masivos
    
    Esta API permite ingerir, consultar y **simular flujos masivos de datos ambientales** para el módulo de Big Data.
    
    ### Características:
    * 📡 **Telemetría IoT en tiempo real** (Temperatura, Humedad, CO2).
    * 🎲 **Generador sintético integrado con Faker** (`es_ES`).
    * 📑 **Filtrado, ordenación y paginación** preparados para streaming.
    """,
    version="1.2.0",
    contact={
        "name": "Departamento de Big Data - CIPFP Batoi",
        "url": "https://cipfpbatoi.es",
        "email": "bigdata@cipfpbatoi.es",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata
)
```

### 5.2. Decoradores de Endpoint: Summary, Description y Status Codes

Usa los parámetros de los decoradores para que cada endpoint explique exactamente qué hace y qué errores contempla:

```python
from fastapi import status, HTTPException, Query

@app.get(
    "/api/v1/sensors",
    response_model=List[LecturaSensor],
    status_code=status.HTTP_200_OK,
    tags=["Sensores IoT"],
    summary="Listar lecturas de sensores con filtros",
    response_description="Lista paginada de mediciones telemetrizadas.",
)
async def get_sensors(
    ciudad: Optional[str] = Query(None, description="Filtrar por ciudad (ej. Valencia, Alcoy)", examples=["Alcoy"]),
    min_temp: Optional[float] = Query(None, ge=-20.0, description="Filtrar mediciones con temperatura mayor o igual", examples=[20.0]),
    limit: int = Query(20, ge=1, le=500, description="Cantidad máxima de registros a retornar", examples=[50]),
):
    """
    Retorna lecturas de la red de sensores aplicando filtros opcionales:
    - **ciudad**: coincide de forma insensible a mayúsculas.
    - **min_temp**: umbral mínimo en grados Celsius.
    - **limit**: paginación de seguridad (máximo 500 registros por llamada).
    """
    # Lógica de retorno...
```

### 5.3. La Joya de la Corona: Ejemplos Ricos en Swagger con Faker

El botón **«Try it out»** de Swagger por defecto rellena los campos con valores genéricos como `"string"` o `0`. 

Podemos inyectar ejemplos realistas generados con **Faker** directamente en el esquema de Pydantic usando `json_schema_extra`:

```python
class LecturaSensorInput(BaseModel):
    sensor_id: str = Field(..., description="Código identificativo")
    ciudad: str = Field(..., description="Ciudad de origen")
    temperatura: float = Field(..., description="Temperatura en ºC")
    humedad: float = Field(..., description="Humedad relativa en %")
    co2_ppm: int = Field(..., description="Nivel de CO2")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sensor_id": "SN-ALC-4091",
                "ciudad": "Alcoy",
                "temperatura": 18.4,
                "humedad": 62.5,
                "co2_ppm": 420
            }
        }
    }
```

¡Cuando el alumno abre Swagger UI y pulsa en el método POST, **ya tiene el JSON listo para enviar sin tener que inventar nada**!

---

## 6. Código Completo: La API Simuladora de Big Data

Aquí tenéis un servicio completo y listo para ejecutar en clase (`app.py`):

```python
# app.py
from fastapi import FastAPI, Query, status, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import random
from faker import Faker

# Inicializar Faker español
fake = Faker('es_ES')

# Metadatos OpenAPI
app = FastAPI(
    title="CityData Streamer — Simulador IoT con Faker 🌆📊",
    description="API para generación y consulta de telemetría urbana sintética.",
    version="1.0.0"
)

# Modelo Pydantic
class EstadoSensor(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class LecturaSensor(BaseModel):
    id: str = Field(..., description="UUID único de la lectura", examples=["c8b9b876-2184-4861-897b-946e38a2e123"])
    sensor_id: str = Field(..., description="ID del hardware emisor", examples=["SN-VAL-2041"])
    ciudad: str = Field(..., description="Municipio", examples=["Valencia"])
    latitud: float = Field(..., examples=[39.4699])
    longitud: float = Field(..., examples=[-0.3763])
    temperatura: float = Field(..., description="Grados Celsius", examples=[21.8])
    humedad: float = Field(..., description="Porcentaje de humedad", examples=[58.0])
    co2_ppm: int = Field(..., description="Nivel de CO2 en ppm", examples=[412])
    estado: EstadoSensor = Field(..., description="Diagnóstico del sensor", examples=["OK"])
    timestamp: datetime = Field(..., description="Fecha y hora de captura")

# Base de datos en memoria para la sesión
DATABASE: List[LecturaSensor] = []

def crear_lectura_falsa(ciudad_forzada: Optional[str] = None) -> LecturaSensor:
    ciudades = ["Alcoy", "Valencia", "Alicante", "Castellón", "Elche"]
    ciudad = ciudad_forzada or random.choice(ciudades)
    return LecturaSensor(
        id=fake.uuid4(),
        sensor_id=f"SN-{ciudad[:3].upper()}-{fake.bothify(text='####')}",
        ciudad=ciudad,
        latitud=float(fake.latitude()),
        longitud=float(fake.longitude()),
        temperatura=round(random.gauss(21.0, 4.5), 1),
        humedad=round(random.uniform(35.0, 90.0), 1),
        co2_ppm=random.randint(380, 1100),
        estado=random.choices(list(EstadoSensor), weights=[80, 15, 5])[0],
        timestamp=fake.date_time_between(start_date="-2h", end_date="now")
    )

# Sembrar 50 datos iniciales al arrancar
DATABASE.extend([crear_lectura_falsa() for _ in range(50)])

# --- ENDPOINTS ---

@app.get(
    "/api/v1/telemetry",
    response_model=List[LecturaSensor],
    tags=["Telemetría Urbana"],
    summary="Consultar telemetría con filtros",
    description="Permite extraer datos históricos recientes con paginación y filtrado por ciudad o estado de alerta."
)
async def get_telemetry(
    ciudad: Optional[str] = Query(None, description="Filtrar por ciudad", examples=["Alcoy"]),
    estado: Optional[EstadoSensor] = Query(None, description="Filtrar por estado"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros")
):
    resultado = DATABASE
    if ciudad:
        resultado = [r for r in resultado if r.ciudad.lower() == ciudad.lower()]
    if estado:
        resultado = [r for r in resultado if r.estado == estado]
    return resultado[:limit]

@app.post(
    "/api/v1/simulate/burst",
    response_model=List[LecturaSensor],
    status_code=status.HTTP_201_CREATED,
    tags=["Simulación Masiva"],
    summary="Simular una ráfaga masiva de lecturas",
    description="Genera al vuelo N registros sintéticos realistas con Faker y los inyecta en el almacén de datos."
)
async def burst_simulation(
    count: int = Query(10, ge=1, le=200, description="Número de lecturas a simular al vuelo"),
    ciudad: Optional[str] = Query(None, description="Forzar una ciudad específica")
):
    nuevas_lecturas = [crear_lectura_falsa(ciudad_forzada=ciudad) for _ in range(count)]
    DATABASE.extend(nuevas_lecturas)
    return nuevas_lecturas
```

### Cómo arrancarlo:
```bash
uvicorn app:app --reload --port 8000
```
Y abrir en el navegador:
👉 **`http://localhost:8000/docs`**

---

## 7. Retos Prácticos Propuestos para los Alumnos

1. **Reto 1 (Streaming IoT):** Añadir un endpoint que simule un sensor específico reportando cada 5 segundos y enviando una anomalía intencionada (*e.g. temperatura > 50ºC*) cuando el contador sea múltiplo de 10.
2. **Reto 2 (Fintech & Fraude):** Crear un generador de transacciones con tarjeta de crédito (`fake.credit_card_full()`) e identificar en Swagger transacciones sospechosas por importes atípicos.
3. **Reto 3 (Documentación de Errores):** Documentar un error HTTP 404 explícito con su propio modelo `ErrorResponse` en el decorador `responses={404: {"model": ErrorResponse}}` cuando se busque un `sensor_id` que no exista.

