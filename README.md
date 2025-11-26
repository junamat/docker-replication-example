# Sistema de Detección de Anomalías en Entorno Industrial

Este proyecto implementa un sistema de monitorización de temperaturas y detección de anomalías distribuido, diseñado para ejecutarse sobre **Docker Swarm**. Utiliza una arquitectura de microservicios para la ingesta de datos, almacenamiento en series temporales, visualización y predicción mediante Inteligencia Artificial.

El sistema simula un entorno industrial donde se recogen mediciones, se almacenan y se verifica si constituyen una anomalía basándose en un modelo de Deep Learning pre-entrenado servido mediante TensorFlow Serving.

## Arquitectura del Stack

El sistema se compone de los siguientes servicios orquestados en `docker-compose-serving.yml`:

  * **Web API (Flask):** Cuenta con 5 réplicas. Recibe las peticiones HTTP, gestiona la lógica y se comunica con Redis y TensorFlow Serving.
  * **Redis:** Base de datos en memoria (usando el módulo TimeSeries) para almacenar el histórico de temperaturas.
  * **TensorFlow Serving:** Servidor dedicado para realizar inferencias sobre el modelo de detección de anomalías de forma eficiente.
  * **Grafana:** Panel de visualización para monitorizar los datos almacenados en Redis.
  * **Visualizer:** Herramienta para visualizar la distribución de los contenedores en el clúster Swarm.

## Pre-requisitos

  * Docker instalado.
  * Docker Swarm inicializado (si no lo has hecho, ejecuta `docker swarm init`).
  * Tener el modelo entrenado y su configuración en una carpeta local `./models` (necesaria para el volumen de TensorFlow Serving).

## Instalación y Despliegue

### 1\. Construir la imagen de la aplicación (opcional)

Antes de desplegar el stack, asegúrate de que la imagen de la aplicación web esté disponible o constrúyela localmente:

```bash
docker build -t apfnam/get-started:part2 .
```

*(Nota: Asegúrate de que el nombre de la imagen coincida con el definido en el `docker-compose-serving.yml` o actualiza el archivo YAML).*

### 2\. Desplegar en Docker Swarm

Para lanzar el clúster con todos los servicios, ejecuta los siguientes comando:

```bash
docker stack deploy -c docker-compose-serving.yml practica_dsc
```

### 3\. Verificar el estado

Puedes ver el estado de los servicios con:

```bash
docker service ls
```

O acceder al **Visualizer** en tu navegador: `http://localhost:8080`

### 4\. Detener el stack

Cuando desees detener el servicio y volver a un estado previo a la ejecución del servicio puedes ejecutar el siguiente comando:

```bash
docker stack rm practica_dsc
docker swarm leave --force
```

## Uso de la API

La aplicación web expone el puerto **4000** (mapeado al 80 del contenedor).

### 1\. Registrar una nueva temperatura

Guarda un dato en Redis TimeSeries.

```bash
curl "http://localhost:4000/nuevo?dato=25.4"
```

### 2\. Listar mediciones

Muestra el historial de temperaturas almacenadas.

```bash
curl "http://localhost:4000/listar"
```

### 3\. Detectar anomalía

Registra el dato y consulta al modelo (vía TensorFlow Serving) si el valor es anómalo basándose en una ventana de las últimas 10 mediciones.

```bash
curl "http://localhost:4000/detectar?dato=80.5"
```

*Respuesta:* Devolverá un HTML indicando `TRUE` (rojo) o `FALSE` (verde) dependiendo de si el error de predicción supera el umbral predefinido.

## Configuración y Variables de Entorno

Los parámetros principales están definidos en el `Dockerfile` y el `docker-compose-serving.yml`:

| Variable       | Valor por defecto | Descripción                                        |
|:---------------|:------------------|:---------------------------------------------------|
| `REDIS_HOST`   | `redis`           | Host del servicio de base de datos.                |
| `SERVING_HOST` | `serving`         | Host del servicio de TensorFlow Serving.           |
| `WINDOW_SIZE`  | `10`              | Tamaño de la ventana de tiempo para la predicción. |
| `THRESHOLD`    | `9.233`           | Umbral de error para considerar una anomalía.      |
| `MODEL_NAME`   | `modelo`          | Nombre del modelo en TF Serving.                   |

## Visualización (Grafana)

El servicio de Grafana está expuesto en el puerto **3000**.

  * **URL:** `http://localhost:3000`
  * **Configuración:** Se debe configurar el *datasource* de Redis para visualizar las series temporales almacenadas.

## Estructura del Proyecto

```text
.
├── Dockerfile                  # Definición de la imagen de la Web App
├── app.py                      # Punto de entrada de la aplicación Flask
├── analizar.py                 # Lógica de detección de anomalías y conexión con TF Serving
├── requirements.txt            # Dependencias Python
├── docker-compose-serving.yml  # Definición del Stack para Swarm
└── models/                     # (Requerido) Carpeta con el modelo guardado para TF Serving
    ├── models_config/              
    │   └── models.config           # Archivo de configuración para modelos
    └── modelo/                     # Carpeta contenedora el modelo en formato SavedModel de TF
```

-----

**Desarrollo de Software Crítico - Universidad de Málaga (2025)**