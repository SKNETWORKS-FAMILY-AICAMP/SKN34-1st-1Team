CREATE DATABASE IF NOT EXISTS oil_car_app
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE oil_car_app;

CREATE TABLE IF NOT EXISTS oil_prices_monthly (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  month DATE NOT NULL,
  sido VARCHAR(40) NOT NULL,
  product VARCHAR(30) NOT NULL DEFAULT 'gasoline',
  avg_price DECIMAL(10, 2) NOT NULL,
  UNIQUE KEY uq_oil_month_region_product (month, sido, product)
);

CREATE TABLE IF NOT EXISTS car_sales_monthly (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  month DATE NOT NULL,
  brand VARCHAR(60) NOT NULL,
  model VARCHAR(120) NOT NULL,
  fuel_type VARCHAR(40) NOT NULL,
  segment VARCHAR(40),
  units INT NOT NULL,
  avg_fuel_efficiency DECIMAL(6, 2),
  UNIQUE KEY uq_car_month_model_fuel (month, brand, model, fuel_type)
);

CREATE TABLE IF NOT EXISTS transit_usage_monthly (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  month DATE NOT NULL,
  sido VARCHAR(40) NOT NULL,
  transport_type VARCHAR(40) NOT NULL,
  rides BIGINT NOT NULL,
  UNIQUE KEY uq_transit_month_region_type (month, sido, transport_type)
);

CREATE TABLE IF NOT EXISTS gas_stations (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  station_code VARCHAR(40),
  station_name VARCHAR(160) NOT NULL,
  brand VARCHAR(60),
  sido VARCHAR(40),
  sigungu VARCHAR(80),
  address VARCHAR(255),
  latitude DECIMAL(12, 8),
  longitude DECIMAL(12, 8),
  gasoline_price DECIMAL(10, 2),
  diesel_price DECIMAL(10, 2),
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_station_area_price (sido, sigungu, gasoline_price),
  INDEX idx_station_geo (latitude, longitude)
);

CREATE TABLE IF NOT EXISTS community_posts (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(80) NOT NULL,
  title VARCHAR(255) NOT NULL,
  url VARCHAR(500) NOT NULL,
  snippet TEXT,
  keyword VARCHAR(120),
  published_at DATETIME NULL,
  crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_post_url (url)
);
