CREATE TABLE IF NOT EXISTS oil_prices_monthly (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  month DATE NOT NULL,
  sido TEXT NOT NULL,
  product TEXT NOT NULL DEFAULT 'gasoline',
  avg_price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS car_sales_monthly (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  month DATE NOT NULL,
  brand TEXT NOT NULL,
  model TEXT NOT NULL,
  fuel_type TEXT NOT NULL,
  segment TEXT,
  units INTEGER NOT NULL,
  avg_fuel_efficiency REAL
);

CREATE TABLE IF NOT EXISTS transit_usage_monthly (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  month DATE NOT NULL,
  sido TEXT NOT NULL,
  transport_type TEXT NOT NULL,
  rides INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS gas_stations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  station_code TEXT,
  station_name TEXT NOT NULL,
  brand TEXT,
  sido TEXT,
  sigungu TEXT,
  address TEXT,
  latitude REAL,
  longitude REAL,
  gasoline_price REAL,
  diesel_price REAL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS community_posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  snippet TEXT,
  keyword TEXT,
  published_at DATETIME NULL,
  crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transit_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  month DATE NOT NULL UNIQUE,
  used INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS gas_sales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  month DATE NOT NULL UNIQUE,
  normal_gasoline REAL NOT NULL,
  diesel REAL NOT NULL
);
