"""
Database setup module.

Handles PostgreSQL connection and data insertion for scraped car listings.
"""
import os

import psycopg2

from sql_queries import INSERT_CAR_QUERY


def save_car_to_database(data: dict):
    """
    Saves a new car record into the PostgreSQL database.

    Args:
        data (dict): A dictionary containing car details with keys matching
                     the columns of the 'cars' table:
                     {
                         "url": str,
                         "title": str,
                         "price_usd": int or None,
                         "odometer": int or None,
                         "username": str,
                         "phone_number": int or None,
                         "image_url": str,
                         "images_count": int or None,
                         "car_number": str,
                         "car_vin": str
                     }
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT")
        )

        cursor = conn.cursor()
        cursor.execute(INSERT_CAR_QUERY, data)
        conn.commit()
        print("✅Successfully saved the new car to the database.")

    except Exception as e:
        print("⚠️Database error:", e)
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
