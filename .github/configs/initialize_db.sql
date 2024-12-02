CREATE DATABASE IF NOT EXISTS example_database;
USE example_database;

CREATE TABLE IF NOT EXISTS example_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    caliber VARCHAR(50),
    shop VARCHAR(255),
    link VARCHAR(255),
    product_name VARCHAR(255),
    price VARCHAR(255),
    available VARCHAR(255),
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);