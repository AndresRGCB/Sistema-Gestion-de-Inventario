import uuid
from fastapi.testclient import TestClient
from app.main import app
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.inventory import Inventory
from app.models.product import Product


# Cargar variables de entorno desde .env si existe
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurar la conexión a la base de datos de pruebas
test_engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


client = TestClient(app)

def reset_test_db():
    """ Drops and recreates the database before each test. """
    Base.metadata.drop_all(bind=test_engine)  
    Base.metadata.create_all(bind=test_engine)  

client = TestClient(app)


def test_create_movement():
    """Prueba registrar un movimiento de inventario."""
    reset_test_db()
    
    db = TestingSessionLocal()
    
    product = [
        Product(id=1, name="Laptop", description="Test Laptop", category="Electronics", price=1000, sku="LAP-001"),
        Product(id=2, name="Mouse", description="Gaming Mouse", category="Accessories", price=50, sku="MOU-002"),
    ]
    db.add_all(product)
    db.commit()
    
    
    inventory = [
        Inventory(product_id=1, store_id="STORE-001", quantity=10, min_stock=2),
        Inventory(product_id=2, store_id="STORE-002", quantity=5, min_stock=1),
    ]
    db.add_all(inventory)
    db.commit()
    

    source_store_id = "STORE-001"  
    target_store_id = "STORE-002" 

    movement_data = {
        "product_id": 1,
        "source_store_id": source_store_id,
        "target_store_id": target_store_id,
        "quantity": 1
    }

    response = client.post("/api/inventory/transfer", json=movement_data)

    assert response.status_code in [200, 201], f"Error en transferencia: {response.json()}"
