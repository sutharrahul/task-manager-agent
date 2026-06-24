import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()


def connect_db():

    DB_URI = os.getenv("POSTGRES_DB_URL")
    connection = psycopg2.connect(DB_URI)
    cursor = connection.cursor()
    table_name = "task_manager"
    return cursor, connection, table_name


# create a schema
def create_table():
    cursor, connection, table_name = connect_db()
    cursor.execute("""
    DO $$ BEGIN
        CREATE TYPE task_status AS ENUM ('pending', 'ongoing', 'completed');
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END $$;
    """)
    cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    connection.commit()
    cursor.close()
    connection.close()
    
    print("Tables created successfully!")

create_table()
