"""
Project SQL queries.
"""
INSERT_CAR_QUERY = """
INSERT INTO cars (
    url, title, price_usd, odometer, username,
    phone_number, image_url, images_count, car_number, car_vin
)
VALUES (
    %(url)s, %(title)s, %(price_usd)s, %(odometer)s, %(username)s,
    %(phone_number)s, %(image_url)s, %(images_count)s, %(car_number)s, %(car_vin)s
)
ON CONFLICT (car_vin) DO NOTHING;
"""
