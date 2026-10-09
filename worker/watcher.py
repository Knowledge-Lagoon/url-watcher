import os
import time
import requests
import psycopg2

URLS = [
    "https://www.google.com",
    "https://www.github.com",
    "https://www.microsoft.com"
]

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS checks (
    id SERIAL PRIMARY KEY,
    url TEXT,
    status TEXT,
    response_ms INTEGER,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

while True:
    for url in URLS:
        try:
            start = time.time()

            response = requests.get(url, timeout=5)

            response_ms = int((time.time() - start) * 1000)

            status = "UP" if response.status_code < 400 else "DOWN"

            cur.execute(
                """
                INSERT INTO checks(url,status,response_ms)
                VALUES(%s,%s,%s)
                """,
                (url, status, response_ms)
            )

            conn.commit()

            print(f"{url} {status} {response_ms}ms")

        except Exception:
            cur.execute(
                """
                INSERT INTO checks(url,status,response_ms)
                VALUES(%s,%s,%s)
                """,
                (url, "DOWN", 0)
            )

            conn.commit()

    time.sleep(30)