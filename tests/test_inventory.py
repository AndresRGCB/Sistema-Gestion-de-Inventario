from fastapi.testclient import TestClient
from app.main import app
import pytest
from dotenv import load_dotenv
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
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

def test_get_inventory_by_store():
    # Insertar inventario de prueba
    
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
        Inventory(product_id=2, store_id="STORE-001", quantity=5, min_stock=1),
    ]
    db.add_all(inventory)
    db.commit()
    
    
    """Prueba listar el inventario por tienda"""
    id = 1  # Ajusta el ID según los datos reales
    response = client.get(f"api/stores/{id}/inventory")
    assert response.status_code == 200, f"Error: {response.json()}"
    assert isinstance(response.json(), list), "La respuesta no es una lista"

def test_get_low_stock_alerts():
    """Prueba listar productos con bajo stock"""
    reset_test_db()
    response = client.get("api/inventory/alerts")
    assert response.status_code == 200, f"Error: {response.json()}"
    assert isinstance(response.json(), list), "La respuesta no es una lista"
