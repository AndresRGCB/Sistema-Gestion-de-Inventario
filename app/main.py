from fastapi import FastAPI, Request
from app.database import engine, Base
from app.routes import product_routes, inventory_routes
from loguru import logger
import sys
import json
from datetime import datetime

# Configurar Loguru para formatear logs en JSON
logger.remove()  # Eliminar cualquier configuración previa de logs
logger.add(
    sys.stdout,
    format="{message}",  # Solo mensaje, ya que estructuramos JSON manualmente
    serialize=True  # Salida en JSON
)

# Opcional: Guardar logs en un archivo
logger.add("logs.json", format="{message}", serialize=True, rotation="10 MB")

app = FastAPI(
    title="API de Inventario",
    description="API para gestionar productos e inventario con funcionalidades de stock, transferencias y alertas.",
    version="1.0.0"
)


#Middleware para registrar todas las solicitudes en logs estructurados
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para registrar logs de cada petición HTTP en formato JSON."""
    start_time = datetime.utcnow()
    
    response = await call_next(request)
    
    log_data = {
        "timestamp": start_time.isoformat(),
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host,
        "status_code": response.status_code,
    }
    
    logger.info(json.dumps(log_data))  # Guardar log en formato JSON
    return response

#Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

#Registrar las rutas en FastAPI
app.include_router(product_routes.router, prefix="/api")
app.include_router(inventory_routes.inventory_router, prefix="/api")  # Ahora se usa el nuevo router
app.include_router(inventory_routes.stores_router, prefix="/api")  # Agregar el router para /stores/{id}/inventory

@app.get("/")
def home():
    logger.info(json.dumps({"message": "API de Inventario Activa"}))
    return {"message": "API de Inventario Activa"}

@app.get("/routes")
def get_routes():
    return [{"path": route.path, "name": route.name} for route in app.routes]
