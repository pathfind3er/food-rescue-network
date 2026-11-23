"""
FoodRescue Network — Cloud Database Initializer
Executes and applies database/schema.sql onto any local or cloud MySQL instance (e.g. TiDB, Aiven, Railway, Render).
"""

import os
import sys
import re
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load .env
load_dotenv()

def get_connection(include_db=False):
    db_name = os.getenv('DB_NAME', 'food_rescue_db')
    conn_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'autocommit': True
    }
    
    # Handle cloud SSL if configured
    ssl_mode = os.getenv('DB_SSL', 'false').lower()
    if ssl_mode in ('true', '1', 'required'):
        conn_params['ssl_disabled'] = False

    if include_db:
        conn_params['database'] = db_name

    return mysql.connector.connect(**conn_params)

def initialize_database():
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql'))
    if not os.path.exists(schema_path):
        print(f"❌ Schema file not found at: {schema_path}")
        sys.exit(1)

    print(f"📂 Reading schema from: {schema_path}")
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    db_name = os.getenv('DB_NAME', 'food_rescue_db')
    print(f"🔌 Connecting to MySQL server at {os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 3306)} as '{os.getenv('DB_USER', 'root')}'...")

    try:
        conn = get_connection(include_db=False)
        cursor = conn.cursor()
        print(f"📦 Ensuring database `{db_name}` exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.close()
        conn.close()

        # Connect to the database itself
        conn = get_connection(include_db=True)
        cursor = conn.cursor()

        # Parse commands respecting DELIMITER blocks
        print("⚙️ Executing DDL, Triggers, Stored Procedures, and Seed Data...")
        
        # Clean lines and split custom DELIMITER blocks
        # First remove standard SQL comments
        cleaned_sql = re.sub(r'--.*$', '', sql_content, flags=re.MULTILINE)

        # Split on DELIMITER directives
        delimiter_blocks = re.split(r'DELIMITER\s+([^\s]+)', cleaned_sql)
        current_delim = ';'
        
        i = 0
        while i < len(delimiter_blocks):
            block = delimiter_blocks[i].strip()
            if not block:
                i += 1
                continue
            
            # If this entry is a delimiter change
            if block in ('$$', '//', ';'):
                current_delim = block
                i += 1
                if i < len(delimiter_blocks):
                    block = delimiter_blocks[i]
                else:
                    break

            # Execute statements in current block split by current_delim
            statements = block.split(current_delim)
            for stmt in statements:
                stmt = stmt.strip()
                # Skip USE, DROP DATABASE, CREATE DATABASE as we handled it, or empty statements
                if not stmt or stmt.upper().startswith('USE ') or stmt.upper().startswith('DROP DATABASE') or stmt.upper().startswith('CREATE DATABASE'):
                    continue
                try:
                    cursor.execute(stmt)
                except Error as err:
                    # Ignore harmless drops
                    if "Unknown table" in str(err) or "Unknown procedure" in str(err) or "does not exist" in str(err):
                        continue
                    print(f"⚠️ Statement Notice: {err} in statement: {stmt[:60]}...")

            i += 1

        cursor.close()
        conn.close()
        print("\n✅ Database and tables successfully initialized and seeded with test data!")
        print("🎉 You are ready to start the application.")

    except Error as err:
        print(f"\n❌ Error initializing database: {err}")
        sys.exit(1)

if __name__ == '__main__':
    initialize_database()
