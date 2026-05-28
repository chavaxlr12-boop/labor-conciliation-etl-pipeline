
## 📌 1. Visión General del Proyecto
Este proyecto implementa una solución punta a punta de **Ingeniería de Datos** local para procesar, limpiar y modelar más de 67,000 registros públicos de conciliaciones laborales correspondientes a los periodos 2025 y 2026 en el estado de Nuevo León, México. 

A través de un pipeline modular desarrollado en **Python**, los datos crudos sufren un proceso de transformación profunda para corregir problemas de inconsistencia de texto y anomalías de formato, culminando en la carga estructurada dentro de un **Data Warehouse analítico local (SQLite)** basado en un modelo dimensional en estrella (*Star Schema*).

Esta solución está diseñada de forma independiente a infraestructuras cloud, enfocándose en la eficiencia del procesamiento en memoria y estructuras relacionales nativas.

---

## 🏗️ 2. Arquitectura del Pipeline y Flujo de Datos

El flujo de la solución sigue principios de modularidad desacoplada (ETL) para garantizar un código limpio, legible y escalable:

1. **Extract (Extracción):** Ingesta controlada desde archivos planos (`.csv`), con validación de integridad basada en el diccionario de datos oficial provisto.
2. **Transform (Transformación y Calidad de Datos):** * **Data Quality Logic:** Limpieza atómica de espacios en blanco ocultos (`.strip()`) en columnas categóricas, previniendo duplicidades sintácticas durante indexaciones (ej. `"Nuevo Leon "` vs `"Nuevo Leon"`).
   * **Safe Casting:** Formateo y tipado estricto de variables monetarias (`monto_pago`) y métricas demográficas (`total_trabajadores`, `total_hombres`, `total_mujeres`), sustituyendo valores nulos por valores por defecto (`0.0` y `0`).
   * **Surrogate Keys:** Generación de llaves subrogadas secuenciales para aislar el modelo analítico de las llaves operacionales del origen.
3. **Load (Carga):** Ingesta transaccional en el motor relacional SQLite, recreando las entidades físicas del Data Warehouse.

---

## 📐 3. Modelado Dimensional (Star Schema)

Para garantizar que las consultas analíticas de negocio se ejecuten en milisegundos, los datos planos fueron normalizados y distribuidos bajo un **Modelo en Estrella** siguiendo las metodologías de Ralph Kimball:

### 🔹 Tabla de Hechos (`fact_conciliaciones`)
Almacena las métricas cuantitativas y los punteros de relación (Llaves Foráneas - FK) hacia las dimensiones:
* `id_conciliacion` (Primary Key - PK)
* `id_ubicacion` (Foreign Key - FK)
* `id_contrato` (Foreign Key - FK)
* `id_actividad` (Foreign Key - FK)
* `mes_registro`, `periodo_registro`, `motivo_convenio`, `total_trabajadores`, `total_hombres`, `total_mujeres`, `total_no_especificado`, `monto_pago`, `estatus_expediente`.

### 🔸 Tablas de Dimensiones
* **`dim_ubicacion`:** Contiene los atributos geográficos del evento (`id_ubicacion`, `entidad_registro`, `municipio_registro`, `ubicacion_establecimiento`).
* **`dim_contrato`:** Describe los aspectos contractuales analizados (`id_contrato`, `modalidad_contrato`, `clase_contrato`).
* **`dim_actividad`:** Clasificación estandarizada del sector industrial u comercial (`id_actividad`, `actividad_economica`).

---

## 🚀 4. Instrucciones de Despliegue Local

### Prerrequisitos
* Python 3.10 o superior.
* Librería de manipulación de datos `pandas`.

### Paso 1: Clonar e instalar dependencias
```bash
git clone [https://github.com/chavaxlr12boop/labor-conciliation-etl-pipeline.git]
cd labor-conciliation-etl-pipeline
pip install pandas
