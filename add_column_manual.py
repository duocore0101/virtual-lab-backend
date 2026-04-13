import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def add_column():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if year column exists
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='experiments_batch' AND column_name='year';")
        if not cur.fetchone():
            cur.execute("ALTER TABLE experiments_batch ADD COLUMN year VARCHAR(50);")
            print("Successfully added 'year' column to 'experiments_batch'")
        else:
            print("'year' column already exists")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_column()
