import sqlite3
import logging

DB_NAME = "ads.db"

def init_db():
    """Initializes the database and creates the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seen_ads (
            ad_id TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Database initialized.")

def is_ad_seen(ad_id: str) -> bool:
    """Checks if an ad ID has already been seen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT ad_id FROM seen_ads WHERE ad_id = ?', (ad_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_seen_ad(ad_id: str):
    """Adds an ad ID to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO seen_ads (ad_id) VALUES (?)', (ad_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        logging.warning(f"Ad ID {ad_id} already exists in DB.")
    finally:
        conn.close()
