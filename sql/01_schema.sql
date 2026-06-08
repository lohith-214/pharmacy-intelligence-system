-- ============================================================
--  Retail Pharmacy Sales & Inventory Intelligence System
--  Database Schema
-- ============================================================

DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS branches;

CREATE TABLE branches (
    branch_id     VARCHAR(10)  PRIMARY KEY,
    branch_name   VARCHAR(100) NOT NULL,
    city          VARCHAR(50)  NOT NULL,
    manager       VARCHAR(100)
);

CREATE TABLE products (
    product_id    VARCHAR(10)   PRIMARY KEY,
    medicine_name VARCHAR(150)  NOT NULL,
    category      VARCHAR(80)   NOT NULL,
    unit_price    DECIMAL(10,2) NOT NULL,
    cost_price    DECIMAL(10,2) NOT NULL,
    supplier_name VARCHAR(120),
    demand_tier   VARCHAR(20)
);

CREATE TABLE customers (
    customer_id       VARCHAR(12) PRIMARY KEY,
    age               SMALLINT,
    gender            VARCHAR(10),
    city              VARCHAR(50),
    repeat_customer   VARCHAR(5),
    loyalty_member    VARCHAR(5),
    registration_date DATE
);

CREATE TABLE sales (
    invoice_id     VARCHAR(12)   PRIMARY KEY,
    branch_id      VARCHAR(10)   REFERENCES branches(branch_id),
    product_id     VARCHAR(10)   REFERENCES products(product_id),
    medicine_name  VARCHAR(150),
    category       VARCHAR(80),
    quantity_sold  INT           NOT NULL,
    unit_price     DECIMAL(10,2) NOT NULL,
    discount_pct   DECIMAL(5,2)  DEFAULT 0,
    total_amount   DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(30),
    sales_date     DATE          NOT NULL,
    sales_month    VARCHAR(8),
    customer_id    VARCHAR(12)   REFERENCES customers(customer_id),
    day_of_week    VARCHAR(12)
);

CREATE TABLE inventory (
    inventory_id       VARCHAR(30)   PRIMARY KEY,
    product_id         VARCHAR(10)   REFERENCES products(product_id),
    branch_id          VARCHAR(10)   REFERENCES branches(branch_id),
    stock_quantity     INT           NOT NULL,
    reorder_level      INT           NOT NULL,
    max_stock_level    INT,
    supplier_name      VARCHAR(120),
    batch_number       VARCHAR(20),
    expiry_date        DATE,
    warehouse_location VARCHAR(20),
    unit_cost          DECIMAL(10,2),
    stock_value        DECIMAL(14,2)
);

CREATE INDEX idx_sales_date     ON sales(sales_date);
CREATE INDEX idx_sales_branch   ON sales(branch_id);
CREATE INDEX idx_sales_product  ON sales(product_id);
CREATE INDEX idx_sales_category ON sales(category);
CREATE INDEX idx_inv_expiry     ON inventory(expiry_date);
