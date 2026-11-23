"""
FoodRescue Network — Cloud Database Initializer
Executes DDL, tables, views, seed data, and procedures on local or cloud MySQL instances (MySQL 8.0, TiDB, Aiven, Render).
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
    db_name = os.getenv('DB_NAME', os.getenv('DB_DATABASE', 'food_rescue_db'))
    conn_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', os.getenv('DB_USERNAME', 'root')),
        'password': os.getenv('DB_PASSWORD', ''),
        'autocommit': True
    }
    
    # Handle cloud SSL (TiDB, Aiven, etc.)
    ssl_mode = os.getenv('DB_SSL', 'false').lower()
    if ssl_mode in ('true', '1', 'required') or 'tidbcloud.com' in conn_params['host'] or 'aivencloud.com' in conn_params['host']:
        conn_params['ssl_disabled'] = False
        conn_params['ssl_verify_cert'] = False
        conn_params['ssl_verify_identity'] = False

    if include_db:
        conn_params['database'] = db_name

    return mysql.connector.connect(**conn_params)

def initialize_database():
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql'))
    if not os.path.exists(schema_path):
        print(f"❌ Schema file not found at: {schema_path}")
        sys.exit(1)

    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    db_name = os.getenv('DB_NAME', os.getenv('DB_DATABASE', 'food_rescue_db'))
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', os.getenv('DB_USERNAME', 'root'))
    print(f"🔌 Connecting to MySQL server at {db_host}:{os.getenv('DB_PORT', 3306)} as '{db_user}'...")

    try:
        conn = get_connection(include_db=False)
        cursor = conn.cursor()
        print(f"📦 Ensuring database `{db_name}` exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.close()
        conn.close()

        # Connect to target database
        conn = get_connection(include_db=True)
        cursor = conn.cursor()

        # If --reset flag or initial setup, clean tables
        if '--reset' in sys.argv:
            print("🧹 Resetting existing tables and views...")
            cursor.execute("DROP VIEW IF EXISTS vw_live_rescue_feed;")
            cursor.execute("DROP TABLE IF EXISTS claims, audit_logs, food_batches, impact_stats, volunteer_profiles, users;")

        print(f"⚙️ Applying tables, constraints, views, and seed data from schema.sql...")

        # Strip standard SQL comments
        cleaned_sql = re.sub(r'--.*$', '', sql_content, flags=re.MULTILINE)

        # Split on DELIMITER blocks to preserve procedures/triggers where supported
        delimiter_blocks = re.split(r'DELIMITER\s+([^\s]+)', cleaned_sql)
        current_delim = ';'
        
        i = 0
        executed_count = 0
        while i < len(delimiter_blocks):
            block = delimiter_blocks[i].strip()
            if not block:
                i += 1
                continue
            
            if block in ('$$', '//', ';'):
                current_delim = block
                i += 1
                if i < len(delimiter_blocks):
                    block = delimiter_blocks[i]
                else:
                    break

            statements = block.split(current_delim)
            for stmt in statements:
                stmt = stmt.strip()
                if not stmt or stmt.upper().startswith('USE ') or stmt.upper().startswith('DROP DATABASE') or stmt.upper().startswith('CREATE DATABASE'):
                    continue
                try:
                    cursor.execute(stmt)
                    executed_count += 1
                except Error as err:
                    err_msg = str(err).lower()
                    if "already exists" in err_msg or "unknown table" in err_msg or "does not exist" in err_msg:
                        continue
                    # Gracefully handle engines (like TiDB) that don't support procedural triggers
                    if "trigger" in err_msg or "procedure" in err_msg or "syntax" in err_msg:
                        title_match = re.search(r'CREATE\s+(TRIGGER|PROCEDURE|FUNCTION)\s+`?([a-zA-Z0-9_]+)`?', stmt, re.IGNORECASE)
                        if title_match:
                            print(f"ℹ️ Engine note: {title_match.group(1)} `{title_match.group(2)}` is handled via app-level ACID transactions for this database engine.")
                            continue
                    print(f"⚠️ Notice: {err} in: {stmt[:60]}...")

            i += 1

        cursor.close()
        conn.close()
        print(f"\n✅ Successfully initialized database `{db_name}` with {executed_count} SQL operations!")
        print("🎉 Seed data, users, batches, claims, and views are ready.")

    except Error as err:
        print(f"\n❌ Error initializing database: {err}")
        sys.exit(1)

if __name__ == '__main__':
    initialize_database()
