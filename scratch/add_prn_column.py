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
        
        # Check if prn_no column exists in accounts_user
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='accounts_user' AND column_name='prn_no';")
        if not cur.fetchone():
            print("Adding 'prn_no' column to 'accounts_user'...")
            cur.execute("ALTER TABLE accounts_user ADD COLUMN prn_no VARCHAR(50);")
            print("Successfully added 'prn_no' column to 'accounts_user'")
        else:
            print("'prn_no' column already exists")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
