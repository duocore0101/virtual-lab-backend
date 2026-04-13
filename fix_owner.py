import psycopg2
import os

def check_and_fix():
    try:
        # Try to connect as postgres superuser to fix ownership
        conn = psycopg2.connect(
            dbname='virtual_lab',
            user='postgres',
            password='', # Assuming no password for local postgres
            host='localhost'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute("ALTER TABLE experiments_batch OWNER TO virtual_user;")
        print("Successfully changed owner of experiments_batch to virtual_user")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error as postgres user: {e}")

if __name__ == "__main__":
    check_and_fix()
