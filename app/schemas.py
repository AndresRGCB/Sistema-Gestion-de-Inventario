from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# Esquema para crear productos
class ProductCreate(BaseModel):
    name: str = Field(..., description="Nombre del producto", min_length=3)
    description: Optional[str] = Field(None, description="Descripción opcional")
    category: str = Field(..., description="Categoría del producto")
    price: float = Field(..., gt=0, description="Precio debe ser mayor a 0")
    sku: str = Field(..., description="Código SKU único", min_length=3)

# Esquema para respuestas de productos (incluye total_stock)
class ProductResponse(ProductCreate):
    id: int
    total_stock: int = 0 

    model_config = ConfigDict(from_attributes=True)

# Esquema para crear inventario
class InventoryCreate(BaseModel):
    product_id: int
    store_id: str
    quantity: int
    min_stock: int

# Esquema para respuesta de inventario
class InventoryResponse(BaseModel):
    id: int
    product_id: int
    store_id: str
    quantity: int
    min_stock: int

    model_config = ConfigDict(from_attributes=True)

# Esquema para transferencia de productos
class MovementCreate(BaseModel):
    product_id: int
    source_store_id: str
    target_store_id: str
    quantity: int
