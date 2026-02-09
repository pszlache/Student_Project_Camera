def init_db():

    # MAKE DIR FOR DB IF NEEDED
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = _get_connection()
    try:
        cursor = conn.cursor()

        # Presence events table 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presence_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                snapshot_path TEXT
            )
        """)

        # Users table (for notifications & roles) -----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL DEFAULT 'user',
                notifications_enabled INTEGER NOT NULL DEFAULT 1,
                camera_id INTEGER NULL
            )
        """)

        conn.commit()

    finally:
        conn.close()
