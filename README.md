# API de Gestión de Inventario

## Descripción

Este proyecto implementa una API basada en FastAPI para la administración avanzada de inventarios, proporcionando un manejo eficiente de productos, niveles de stock y movimientos logísticos. La arquitectura del sistema está completamente containerizada mediante Docker y emplea PostgreSQL como motor de base de datos relacional, garantizando escalabilidad y consistencia transaccional.

---

## Guía de Instalación

### 1. Prerrequisitos

Para la correcta ejecución del sistema, es necesario contar con las siguientes herramientas instaladas:

- Docker y Docker Compose
- Git

### 2. Clonar el Repositorio

```sh
git clone https://github.com/AndresRGCB/Sistema-Gestion-de-Inventario
cd inventory-api
```

### 3. Desplegar la Aplicación

Ejecutar el siguiente comando para construir las imágenes y desplegar los contenedores asociados:

```sh
docker-compose up --build -d
```

### 4. Validar el Funcionamiento de la API

La documentación interactiva OpenAPI/Swagger se encuentra disponible en:

```
http://localhost:8000/docs
```

---

## Documentación de la API

### URL Base: `http://localhost:8000/api`

### 1. Recuperar Listado de Productos

**Endpoint:** `/products/`  
**Método:** `GET`

### 2. Obtener Detalle de un Producto

**Endpoint:** `/products/{id}`  
**Método:** `GET`

### 3. Crear un Nuevo Producto

**Endpoint:** `/products/`  
**Método:** `POST`

### 4. Actualizar un Producto

**Endpoint:** `/products/{id}`  
**Método:** `PUT`

### 5. Eliminar un Producto

**Endpoint:** `/products/{id}`  
**Método:** `DELETE`

### 6. Consultar Inventario de un Objeto Dentro de Todas las Tiendas

**Endpoint:** `/stores/{id}/inventory`  
**Método:** `GET`

### 7. Transferir Productos entre Tiendas

**Endpoint:** `/inventory/transfer`  
**Método:** `POST`

### 8. Listar Productos con Bajo Stock

**Endpoint:** `/inventory/alerts`  
**Método:** `GET`

---

## Decisiones Técnicas

### Tecnologías Implementadas

- **FastAPI**: Framework asíncrono para la construcción de APIs de alto rendimiento.
- **PostgreSQL**: Sistema de gestión de bases de datos relacional.
- **Docker**: Contenerización para garantizar replicabilidad y despliegue eficiente.
- **Pytest**: Marco de pruebas automatizadas para validación funcional y de integración.
- **SQLAlchemy**: ORM robusto para la abstracción de la base de datos.

### Justificación del Uso de FastAPI

- Procesamiento asíncrono para optimización del rendimiento.
- Validación estricta de datos mediante Pydantic.
- Generación automática de documentación API con OpenAPI.

### Selección de PostgreSQL como Base de Datos

- Modelo relacional con integridad referencial.
- Escalabilidad y optimización para grandes volúmenes de datos.

---

## Diagrama de Arquitectura

A continuación se presenta el diagrama de arquitectura del sistema:

```plaintext
+--------------------+            +----------------------+
| Frontend (React)  |  <---> API  | FastAPI (Docker)    |
+--------------------+            +----------------------+
                                         |
                                         v
                               +-------------------+
                               | PostgreSQL (DB)   |
                               +-------------------+
```

---

## Despliegue en Google Cloud Platform (GCP)

### 1. Crear un Proyecto en GCP

```sh
gcloud projects create inventory-api --set-as-default
```

### 2. Configurar una Base de Datos en Cloud SQL

```sh
gcloud sql instances create inventory-db --database-version=POSTGRES_13 --cpu=2 --memory=8GB --region=us-central1
```

### 3. Conectar la API con Cloud SQL

Actualizar la configuración de la aplicación para apuntar a la instancia de Cloud SQL.

### 4. Desplegar la API en Cloud Run

```sh
gcloud builds submit --tag gcr.io/inventory-api/inventory-api
```

```sh
gcloud run deploy inventory-api --image gcr.io/inventory-api/inventory-api --platform managed --region us-central1 --allow-unauthenticated
```

---

## Scripts de Despliegue

### Desplegar en Entorno de Producción

```sh
docker-compose -f docker-compose.prod.yml up --build -d
```

### Detener la Aplicación

```sh
docker-compose down
```

---

## Ejecución de Pruebas

Para ejecutar las pruebas unitarias dentro del entorno Docker:

```sh
docker exec -it inventory_api pytest -v
```

Para ejecutar exclusivamente las pruebas de carga:

```sh
docker exec -it inventory_api pytest -v load_tests/
```

---

## Colección de Postman

La colección de Postman para probar la API se encuentra disponible en la carpeta `docs/` del repositorio. Para utilizarla:

1. Abre Postman.
2. Ve a **File > Import**.
3. Selecciona el archivo `docs/Inventario API.postman_collection.json`.
4. Una vez importada, puedes probar los endpoints directamente desde Postman.

Esto facilita la validación y prueba de la API sin necesidad de escribir manualmente las peticiones.




