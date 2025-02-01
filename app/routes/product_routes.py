from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas import ProductCreate, ProductResponse
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

# Definir el router para los productos
router = APIRouter(prefix="/products", tags=["Products"])

# Crear un nuevo producto con validación
@router.post(
    "/",
    response_model=ProductResponse,
    summary="Crear un nuevo producto",
    description="Crea un nuevo producto en la base de datos, verificando que el SKU no esté duplicado.",
    responses={
        201: {"description": "Producto creado exitosamente"},
        400: {"description": "Faltan campos obligatorios o el SKU ya está en uso"},
        500: {"description": "Error interno del servidor"},
    }
)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        # Verificar que todos los campos están presentes
        required_fields = ["name", "category", "price", "sku"]
        missing_fields = [field for field in required_fields if getattr(product, field, None) is None]
        if missing_fields:
            raise HTTPException(status_code=400, detail=f"Faltan los siguientes campos obligatorios: {', '.join(missing_fields)}")

        # Verificar si el SKU ya existe para evitar duplicados
        existing_product = db.query(Product).filter(Product.sku == product.sku).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="El SKU ya está en uso")

        # Crear nuevo producto
        new_product = Product(**product.model_dump())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        logger.info(f"Producto creado: {new_product.id} - {new_product.name}")

        return new_product

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear producto: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail="Ocurrió un error inesperado")


# Obtener todos los productos con filtros y paginación
@router.get(
    "/",
    response_model=list[ProductResponse],
    summary="Obtener todos los productos",
    description="Lista todos los productos con opciones de filtrado y paginación.",
    responses={
        200: {"description": "Lista de productos"},
    }
)
def get_products(
    db: Session = Depends(get_db),
    category: str = Query(None, description="Filtrar por categoría"),
    min_price: float = Query(None, description="Precio mínimo"),
    max_price: float = Query(None, description="Precio máximo"),
    min_stock: int = Query(None, description="Stock mínimo"),
    max_stock: int = Query(None, description="Stock máximo"),
    limit: int = Query(10, description="Cantidad de productos por página"),
    offset: int = Query(0, description="Número de productos a saltar para paginación")
):
    from sqlalchemy.sql import func

    query = db.query(
        Product,
        func.coalesce(func.sum(Inventory.quantity), 0).label("total_stock")
    ).outerjoin(Inventory, Product.id == Inventory.product_id)

    if category:
        query = query.filter(Product.category == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    query = query.group_by(
        Product.id, Product.name, Product.description, Product.category, Product.price, Product.sku
    )

    if min_stock is not None:
        query = query.having(func.sum(Inventory.quantity) >= min_stock)
    if max_stock is not None:
        query = query.having(func.sum(Inventory.quantity) <= max_stock)

    results = query.offset(offset).limit(limit).all()

    products = []
    for product, total_stock in results:
        product_dict = product.__dict__
        product_dict["total_stock"] = total_stock
        products.append(product_dict)

    return products


# Obtener un producto por ID
@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Obtener un producto por ID",
    description="Devuelve la información de un producto dado su ID.",
    responses={
        200: {"description": "Producto encontrado"},
        404: {"description": "Producto no encontrado"},
    }
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


# Actualizar un producto
@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Actualizar un producto",
    description="Modifica la información de un producto dado su ID.",
    responses={
        200: {"description": "Producto actualizado"},
        404: {"description": "Producto no encontrado"},
        400: {"description": "Datos inválidos"},
    }
)
def update_product(product_id: int, updated_product: ProductCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if updated_product.sku and db_product.sku != updated_product.sku:
        existing_product = db.query(Product).filter(Product.sku == updated_product.sku).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="SKU already in use")

    for key, value in updated_product.model_dump().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# Eliminar un producto
@router.delete(
    "/{product_id}",
    summary="Eliminar un producto",
    description="Elimina un producto dado su ID.",
    responses={
        200: {"description": "Producto eliminado"},
        404: {"description": "Producto no encontrado"},
    }
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(product)
    db.commit()
    return {"message": "Producto eliminado"}
