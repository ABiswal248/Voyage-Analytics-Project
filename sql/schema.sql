CREATE DATABASE IF NOT EXISTS voyage_analytics
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE voyage_analytics;

CREATE TABLE IF NOT EXISTS users (
  user_code BIGINT PRIMARY KEY,
  company VARCHAR(100),
  name VARCHAR(150),
  gender VARCHAR(30),
  age INT
);

CREATE TABLE IF NOT EXISTS flights (
  travel_code BIGINT,
  user_code BIGINT,
  from_location VARCHAR(150),
  to_location VARCHAR(150),
  flight_type VARCHAR(50),
  price DECIMAL(12,2),
  travel_time DECIMAL(10,2),
  distance DECIMAL(12,2),
  agency VARCHAR(100),
  travel_date DATE,
  INDEX idx_flight_route (from_location, to_location),
  INDEX idx_flight_user (user_code)
);

CREATE TABLE IF NOT EXISTS hotels (
  hotel_row_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  travel_code BIGINT,
  user_code BIGINT,
  hotel_name VARCHAR(150),
  place VARCHAR(150),
  days INT,
  price DECIMAL(12,2),
  total DECIMAL(12,2),
  travel_date DATE,
  INDEX idx_hotel_place (place),
  INDEX idx_hotel_user (user_code)
);

CREATE TABLE IF NOT EXISTS prediction_history (
  prediction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  from_location VARCHAR(150) NOT NULL,
  to_location VARCHAR(150) NOT NULL,
  flight_type VARCHAR(50) NOT NULL,
  agency VARCHAR(100) NOT NULL,
  travel_time DECIMAL(10,2) NOT NULL,
  distance DECIMAL(12,2) NOT NULL,
  predicted_price DECIMAL(12,2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendation_history (
  recommendation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  destination VARCHAR(150) NOT NULL,
  days INT NOT NULL,
  max_budget DECIMAL(12,2),
  result_count INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
