import uuid
from fastapi.testclient import TestClient
from app.main import app
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base


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

def generate_unique_sku():
    """Genera un SKU único para evitar duplicados."""
    return f"SKU_TEST_{uuid.uuid4().hex[:8]}"

def test_create_product():
    """Prueba para crear un producto nuevo."""
    reset_test_db()
    sku = generate_unique_sku()

    product_data = {
        "name": "Mouse Gamer",
        "description": "Mouse con RGB",
        "category": "Electronics",
        "price": 49.99,
        "sku": sku  # SKU único
    }

    response = client.post("/api/products", json=product_data)

    assert response.status_code in [200, 201], f"Error al crear producto: {response.json()}"
    
    product = response.json()
    assert product["name"] == "Mouse Gamer"
    assert product["sku"] == sku  # Verificar SKU
    return product  # Devolver para usar en otras pruebas

def test_get_all_products():
    """Prueba para obtener la lista de productos."""
    response = client.get("/api/products")

    assert response.status_code == 200, f"Error al obtener productos: {response.json()}"
    assert isinstance(response.json(), list), "La respuesta no es una lista"

def test_get_product_by_id():
    """Prueba para obtener un producto por su ID."""
    product = test_create_product()  # Crear producto antes de consultarlo
    product_id = product["id"]

    response = client.get(f"/api/products/{product_id}")
    
    assert response.status_code == 200, f"Error al obtener producto: {response.json()}"
    assert response.json()["id"] == product_id

def test_update_product():
    """Prueba para actualizar un producto existente."""
    product = test_create_product()
    product_id = product["id"]
    new_sku = generate_unique_sku()

    updated_data = {
        "name": "Teclado RGB",
        "description": "Teclado mecánico con luces",
        "category": "Electronics",
        "price": 89.99,
        "sku": new_sku  # Cambiar SKU
    }

    response = client.put(f"/api/products/{product_id}", json=updated_data)

    assert response.status_code in [200, 204], f"Error al actualizar producto: {response.json()}"

    if response.status_code == 200:  # Si hay respuesta JSON, verificar actualización
        updated_product = response.json()
        assert updated_product["name"] == "Teclado RGB"

def test_delete_product():
    """Prueba para eliminar un producto."""
    product = test_create_product()
    product_id = product["id"]

    response = client.delete(f"/api/products/{product_id}")

    assert response.status_code in [200, 204], f"Error al eliminar producto: {response.json()}"

    # Verificar que el producto ya no existe
    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 404, "El producto debería haber sido eliminado"
