CREATE DATABASE alzheimer_app;

USE alzheimer_app;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    birth_year INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    address TEXT NOT NULL,
    password VARCHAR(255) NOT NULL,
    register_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    image_path VARCHAR(255),
    prediction_result VARCHAR(50),
    confidence FLOAT,
    prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
-- Add this to your db.sql file
ALTER TABLE predictions ADD COLUMN image_data LONGBLOB;
ALTER TABLE predictions ADD COLUMN image_hash VARCHAR(255);
ALTER TABLE predictions ADD COLUMN encryption_key VARCHAR(255);
USE alzheimer_app;



-- Update the existing image_path column to be more flexible
ALTER TABLE predictions MODIFY image_path VARCHAR(500);