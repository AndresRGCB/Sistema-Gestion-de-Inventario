from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.inventory import Inventory
from app.models.movement import Movement
from app.models.product import Product
from app.schemas import InventoryResponse, MovementCreate
from sqlalchemy.exc import SQLAlchemyError
from typing import List

# Router para las rutas de inventario
inventory_router = APIRouter(prefix="/inventory", tags=["Inventory"])
stores_router = APIRouter(tags=["Stores"])  # Sin prefix

# /stores/{id}/inventory → Listar inventario por tienda
@stores_router.get(
    "/stores/{product_id}/inventory",
    response_model=List[InventoryResponse],
    summary="Obtener inventario por producto",
    description="Devuelve una lista con la cantidad de inventario disponible de un producto en distintas tiendas.",
    responses={
        200: {"description": "Lista de inventarios por tienda"},
        404: {"description": "No hay inventario disponible para este producto"},
    },
)
def get_inventory_by_product(product_id: str, db: Session = Depends(get_db)):
    inventories = db.query(Inventory).filter(Inventory.product_id == product_id).all()

    if not inventories:
        raise HTTPException(
            status_code=404, 
            detail="No hay inventario para este producto en ninguna tienda"
        )
    
    return inventories


# /inventory/transfer → Transferir productos entre tiendas con manejo de transacción
@inventory_router.post(
    "/transfer",
    summary="Transferir productos entre tiendas",
    description="Transfiere un producto de una tienda a otra, verificando disponibilidad y registrando el movimiento.",
    responses={
        200: {"description": "Transferencia realizada con éxito"},
        400: {"description": "Stock insuficiente para la transferencia"},
        404: {"description": "El producto no existe"},
        500: {"description": "Error en la transferencia"}
    }
)
def transfer_inventory(transfer_data: MovementCreate, db: Session = Depends(get_db)):
    try:
        # Verificar si el producto existe
        product = db.query(Product).filter(Product.id == transfer_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="El producto no existe")
        
        # Verificar si hay suficiente stock en la tienda de origen
        source_inventory = db.query(Inventory).filter(
            Inventory.product_id == transfer_data.product_id,
            Inventory.store_id == transfer_data.source_store_id
        ).first()

        if not source_inventory or source_inventory.quantity < transfer_data.quantity:
            raise HTTPException(status_code=400, detail="Stock insuficiente para la transferencia")

        # Restar stock de la tienda de origen
        source_inventory.quantity -= transfer_data.quantity

        # Buscar el inventario en la tienda destino o crearlo si no existe
        target_inventory = db.query(Inventory).filter(
            Inventory.product_id == transfer_data.product_id,
            Inventory.store_id == transfer_data.target_store_id
        ).first()

        if target_inventory:
            target_inventory.quantity += transfer_data.quantity
        else:
            target_inventory = Inventory(
                product_id=transfer_data.product_id,
                store_id=transfer_data.target_store_id,
                quantity=transfer_data.quantity,
                min_stock=5
            )
            db.add(target_inventory)

        # Registrar el movimiento en la tabla `movements`
        movement = Movement(
            product_id=transfer_data.product_id,
            source_store_id=transfer_data.source_store_id,
            target_store_id=transfer_data.target_store_id,
            quantity=transfer_data.quantity,
            type="TRANSFER"
        )
        db.add(movement)

        # Confirmar cambios en la base de datos
        db.commit()
        return {"message": "Transferencia realizada con éxito"}

    except SQLAlchemyError as e:
        db.rollback()  
        raise HTTPException(status_code=500, detail=f"Error en la transferencia: {str(e)}")


# /inventory/alerts → Listar productos con stock bajo
@inventory_router.get(
    "/alerts",
    response_model=list[InventoryResponse],
    summary="Listar productos con stock bajo",
    description="Devuelve una lista de productos cuyo stock es menor al mínimo definido.",
    responses={
        200: {"description": "Lista de productos con stock bajo"},
        204: {"description": "No hay productos con stock bajo"},
    }
)
def get_low_stock_alerts(db: Session = Depends(get_db)):
    low_stock_items = db.query(Inventory).filter(Inventory.quantity < Inventory.min_stock).all()

    if not low_stock_items:
        return []  # Devuelve una lista vacía para evitar errores de validación

    return low_stock_items
