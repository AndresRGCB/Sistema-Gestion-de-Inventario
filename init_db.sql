-- Crear la base de datos (si no existe)
CREATE DATABASE inventory_db;



-- Change `inventory_user` to your actual PostgreSQL user
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;

-- Crear la tabla de productos
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    sku VARCHAR(50) UNIQUE NOT NULL
);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_sku ON products(sku);


-- Crear la tabla de inventario
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    store_id VARCHAR(50) NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    min_stock INT DEFAULT 5
);

CREATE INDEX idx_inventory_product_id ON inventory(product_id);

-- Crear la tabla de movimientos de stock
CREATE TABLE IF NOT EXISTS movements (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    source_store_id VARCHAR(50),
    target_store_id VARCHAR(50),
    quantity INT NOT NULL CHECK (quantity > 0),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(20) CHECK (type IN ('IN', 'OUT', 'TRANSFER'))
);


-- Insertar productos
INSERT INTO products (name, description, category, price, sku) VALUES
    ('Laptop Dell XPS 15', 'Laptop potente para trabajo y gaming', 'Electrónica', 2500.00, 'LAP-DELL-XPS15'),
    ('Mouse Logitech MX Master 3', 'Mouse inalámbrico ergonómico', 'Accesorios', 99.99, 'MOUSE-LOGI-MX3'),
    ('Teclado Mecánico Keychron K6', 'Teclado mecánico inalámbrico', 'Accesorios', 129.99, 'KEYCHRON-K6'),
    ('Monitor LG UltraWide', 'Monitor de 34 pulgadas para productividad', 'Electrónica', 399.99, 'MON-LG-UW34');


-- Insertar inventario (asociado a productos y tiendas ficticias)
INSERT INTO inventory (product_id, store_id, quantity, min_stock) VALUES
    (1, 'STORE-001', 10, 2),  -- Laptop Dell en la tienda 1
    (2, 'STORE-001', 5, 1),   -- Mouse Logitech en la tienda 1
    (3, 'STORE-002', 20, 3),  -- Teclado Keychron en la tienda 2
    (4, 'STORE-002', 15, 4),  -- Monitor LG en la tienda 2
    (1, 'STORE-002', 8, 2);   -- Laptop Dell en la tienda 2

-- Insertar movimientos de stock
INSERT INTO movements (product_id, source_store_id, target_store_id, quantity, type) VALUES
    (1, 'STORE-001', 'STORE-002', 2, 'TRANSFER'), -- Transferencia de laptops Dell
    (2, NULL, 'STORE-001', 10, 'IN'),  -- Entrada de 10 mouses Logitech a la tienda 1
    (3, 'STORE-002', NULL, 5, 'OUT'),  -- Venta de 5 teclados en la tienda 2
    (4, NULL, 'STORE-002', 3, 'IN');   -- Entrada de 3 monitores a la tienda 2

