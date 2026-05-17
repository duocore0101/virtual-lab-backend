import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_ownership():
    try:
        conn = psycopg2.connect(
            dbname='virtual_lab',
            user='postgres',
            password='',
            host='localhost'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute("SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public';")
        tables = cur.fetchall()
        for table, owner in tables:
            print(f"Table: {table}, Owner: {owner}")
            if owner != 'virtual_user':
                print(f"Changing owner of {table} to virtual_user...")
                cur.execute(f"ALTER TABLE \"{table}\" OWNER TO virtual_user;")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_ownership()
