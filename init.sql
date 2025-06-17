CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    title TEXT,
    price_usd INTEGER,
    odometer INTEGER,
    username TEXT,
    phone_number INTEGER,
    image_url TEXT,
    images_count INTEGER,
    car_number TEXT,
    car_vin TEXT UNIQUE,
    datetime_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
