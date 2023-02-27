import sqlite3

if __name__ == "__main__":
    db_file = "data/external.db"

    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file)
    conn_cursor = conn.cursor()

    conn_cursor.execute(
        "WITH diff AS (SELECT timestamp, temperature, temperature - LAG (temperature) OVER (ORDER BY timestamp) AS difference FROM data) SELECT timestamp, temperature FROM diff WHERE difference != 0.0"
    )

    results = conn_cursor.fetchall()
    print(len(results))

    conn.commit()
    conn.close()
