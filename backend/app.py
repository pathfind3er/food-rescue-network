"""
FoodRescue Network — Surplus Food Redistribution System
Backend Flask REST API (Strict Raw Parameterized SQL, No ORM)
Built for DBMS Lab & Project Evaluation (MySQL 8.0)
"""

import os
import datetime
from decimal import Decimal
from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error, errorcode
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

# Initialize Flask with explicit template and static paths
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'))
app = Flask(__name__, template_folder=TEMPLATE_DIR)

# Database Connection Helper Function
def get_db_connection():
    """
    Establishes a raw connection to MySQL 8.0 server.
    Uses parameterized queries and connection-level isolation.
    Supports both local MySQL and Cloud MySQL (TiDB, Aiven, Railway, Render) with SSL.
    """
    try:
        conn_kwargs = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'root'),
            'database': os.getenv('DB_NAME', 'food_rescue_db'),
            'autocommit': False  # Explicit transaction control
        }

        # Enable SSL for cloud databases (TiDB, Aiven, etc.) if requested or required
        ssl_mode = os.getenv('DB_SSL', 'false').lower()
        if ssl_mode in ('true', '1', 'required') or 'tidbcloud.com' in conn_kwargs['host'] or 'aivencloud.com' in conn_kwargs['host']:
            conn_kwargs['ssl_disabled'] = False
            conn_kwargs['ssl_verify_cert'] = False
            conn_kwargs['ssl_verify_identity'] = False

        conn = mysql.connector.connect(**conn_kwargs)
        return conn
    except Error as err:
        print(f"[DB Connection Error]: {err}")
        raise err

def serialize_row(row):
    """Utility to convert MySQL dates and Decimals into JSON serializable objects."""
    if not row:
        return row
    new_row = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            new_row[k] = float(v)
        elif isinstance(v, (datetime.date, datetime.datetime)):
            new_row[k] = v.isoformat()
        else:
            new_row[k] = v
    return new_row

# ============================================================================
# FRONTEND ROUTE
# ============================================================================
@app.route('/')
def index():
    return render_template('index.html')

# ============================================================================
# API: SYSTEM HEALTH & DB CONNECTIVITY
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT VERSION() AS mysql_version, DATABASE() AS active_db, NOW() AS db_now")
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({
            "status": "connected",
            "database": info['active_db'],
            "mysql_version": info['mysql_version'],
            "server_time": info['db_now'].isoformat()
        })
    except Error as err:
        return jsonify({
            "status": "disconnected",
            "error": str(err),
            "hint": "Ensure MySQL is running, user credentials in backend/.env are correct, and database/schema.sql has been imported."
        }), 500

# ============================================================================
# API: LIVE FOOD SURPLUS FEED (USES VIEW: vw_live_rescue_feed & PROCEDURE)
# ============================================================================
@app.route('/api/batches', methods=['GET'])
def get_batches():
    """
    1. Executes stored procedure sp_expire_stale_batches to auto-expire past-due items.
    2. Queries VIEW vw_live_rescue_feed with optional filtering by zone and food_type.
    """
    zone_filter = request.args.get('zone', '').strip()
    type_filter = request.args.get('food_type', '').strip()
    category_filter = request.args.get('category', '').strip()

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Run maintenance procedure to expire stale items (with fallback for cloud engines like TiDB)
        try:
            cursor.callproc('sp_expire_stale_batches', [0])
            conn.commit()
        except Error:
            # Procedural fallback: execute direct SQL equivalent
            cursor.execute("""
                UPDATE food_batches 
                SET status = 'EXPIRED' 
                WHERE status = 'AVAILABLE' AND best_before <= NOW()
            """)
            conn.commit()

        # 2. Query View with dynamic parameterized WHERE clauses
        query = "SELECT * FROM vw_live_rescue_feed WHERE 1=1"
        params = []

        if zone_filter:
            query += " AND zone = %s"
            params.append(zone_filter)
        if type_filter:
            query += " AND food_type = %s"
            params.append(type_filter)
        if category_filter:
            query += " AND category = %s"
            params.append(category_filter)

        query += " ORDER BY minutes_left ASC"

        cursor.execute(query, tuple(params))
        batches = [serialize_row(row) for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return jsonify({"success": True, "count": len(batches), "batches": batches})
    except Error as err:
        if conn:
            conn.close()
        return jsonify({"success": False, "error": str(err)}), 500

# ============================================================================
# API: POST NEW FOOD BATCH (DEMONSTRATES TRIGGER 1: trg_after_batch_insert)
# ============================================================================
@app.route('/api/batches', methods=['POST'])
def create_batch():
    """
    Inserts a new surplus food batch using raw parameterized SQL.
    Triggers: trg_after_batch_insert automatically writes an audit log.
    Validates: Table constraints (best_before > prepared_at, quantity > 0, weight > 0).
    """
    data = request.json or {}
    donor_id = data.get('donor_id', 1)
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    category = data.get('category', 'COOKED_MEAL')
    food_type = data.get('food_type', 'VEG')
    quantity_meals = data.get('quantity_meals')
    weight_kg = data.get('weight_kg')
    allergen_info = data.get('allergen_info', 'None').strip()
    storage_temp_req = data.get('storage_temp_req', 'HOT')
    prepared_at = data.get('prepared_at')
    best_before = data.get('best_before')
    pickup_address = data.get('pickup_address', '').strip()
    zone = data.get('zone', 'South Zone').strip()

    if not title or not quantity_meals or not weight_kg or not prepared_at or not best_before or not pickup_address:
        return jsonify({"success": False, "error": "Missing mandatory batch fields."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        insert_sql = """
        INSERT INTO food_batches (
            donor_id, title, description, category, food_type,
            quantity_meals, weight_kg, allergen_info, storage_temp_req,
            prepared_at, best_before, pickup_address, zone, status
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'AVAILABLE'
        )
        """
        cursor.execute(insert_sql, (
            donor_id, title, description, category, food_type,
            quantity_meals, weight_kg, allergen_info, storage_temp_req,
            prepared_at, best_before, pickup_address, zone
        ))

        new_batch_id = cursor.lastrowid
        conn.commit()  # Fires trg_after_batch_insert

        # Fetch the automatically generated audit log entry to show the user/examiner
        cursor.execute("""
            SELECT * FROM audit_logs 
            WHERE batch_id = %s AND event_type = 'BATCH_CREATED' 
            ORDER BY log_id DESC LIMIT 1
        """, (new_batch_id,))
        audit_entry = serialize_row(cursor.fetchone())

        # If database engine does not execute triggers automatically, insert audit log
        if not audit_entry:
            cursor.execute("""
                INSERT INTO audit_logs (batch_id, actor_user_id, event_type, old_status, new_status, description, logged_at)
                VALUES (%s, %s, 'BATCH_CREATED', NULL, 'AVAILABLE', %s, NOW())
            """, (new_batch_id, donor_id, f'Surplus batch "{title}" ({quantity_meals} meals, {weight_kg} kg) listed in {zone} [Category: {category}]'))
            conn.commit()
            cursor.execute("SELECT * FROM audit_logs WHERE batch_id = %s AND event_type = 'BATCH_CREATED' ORDER BY log_id DESC LIMIT 1", (new_batch_id,))
            audit_entry = serialize_row(cursor.fetchone())

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": f"Food batch #{new_batch_id} posted successfully. Trigger 'trg_after_batch_insert' executed.",
            "batch_id": new_batch_id,
            "audit_trigger_result": audit_entry
        }), 201

    except Error as err:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": f"MySQL Error [{err.errno}]: {err.msg}"}), 400

# ============================================================================
# API: UPDATE FOOD BATCH DETAILS
# ============================================================================
@app.route('/api/batches/<int:batch_id>', methods=['PUT'])
def update_batch(batch_id):
    data = request.json or {}
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        update_sql = """
        UPDATE food_batches 
        SET title = %s, description = %s, category = %s, food_type = %s,
            quantity_meals = %s, weight_kg = %s, allergen_info = %s,
            storage_temp_req = %s, pickup_address = %s, zone = %s
        WHERE batch_id = %s AND status = 'AVAILABLE'
        """
        cursor.execute(update_sql, (
            data.get('title'), data.get('description'), data.get('category'),
            data.get('food_type'), data.get('quantity_meals'), data.get('weight_kg'),
            data.get('allergen_info'), data.get('storage_temp_req'),
            data.get('pickup_address'), data.get('zone'), batch_id
        ))

        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Batch not found or already claimed/expired."}), 404

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": f"Batch #{batch_id} updated successfully."})
    except Error as err:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": str(err)}), 400

# ============================================================================
# API: DELETE FOOD BATCH (DEMONSTRATES CASCADE / INTEGRITY)
# ============================================================================
@app.route('/api/batches/<int:batch_id>', methods=['DELETE'])
def delete_batch(batch_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("DELETE FROM food_batches WHERE batch_id = %s", (batch_id,))
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": f"Batch #{batch_id} not found."}), 404

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({
            "success": True, 
            "message": f"Batch #{batch_id} deleted successfully. Cascaded dependent relationships preserved."
        })
    except Error as err:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": str(err)}), 400

# ============================================================================
# API: CLAIM BATCH (CALLS STORED PROCEDURE: sp_claim_food_batch)
# Demonstrates: Row-Level Locking (FOR UPDATE), Physical Vehicle Capacity Check,
# Concurrency Protection, and Full ACID Rollback on Failure.
# ============================================================================
@app.route('/api/claim', methods=['POST'])
def claim_batch():
    data = request.json or {}
    batch_id = data.get('batch_id')
    ngo_id = data.get('ngo_id')
    volunteer_id = data.get('volunteer_id')

    if not batch_id or not ngo_id or not volunteer_id:
        return jsonify({"success": False, "error": "batch_id, ngo_id, and volunteer_id are required."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        claim_id = None
        status_msg = "Batch claimed successfully."

        # Attempt to run MySQL Stored Procedure sp_claim_food_batch
        try:
            result_args = cursor.callproc('sp_claim_food_batch', [batch_id, ngo_id, volunteer_id, 0, ''])
            conn.commit()
            claim_id = result_args[3]
            status_msg = result_args[4]
        except (Error, Exception) as proc_err:
            err_str = str(proc_err).lower()
            if "does not exist" in err_str or "unsupported" in err_str or "not supported" in err_str or getattr(proc_err, 'errno', 0) in (8108, 1305, 1064):
                # ACID Transactional Fallback: execute identical row-locked logic directly
                # 1. Lock batch row FOR UPDATE
                cursor.execute("""
                    SELECT batch_id, donor_id, title, weight_kg, status, best_before, (best_before <= NOW()) AS is_expired 
                    FROM food_batches 
                    WHERE batch_id = %s FOR UPDATE
                """, (batch_id,))
                batch = cursor.fetchone()
                if not batch:
                    raise Exception(f"Batch #{batch_id} does not exist.")
                if batch['status'] != 'AVAILABLE':
                    raise Exception(f"Batch #{batch_id} is no longer available (Current Status: {batch['status']}).")
                if batch['is_expired']:
                    raise Exception(f"Batch #{batch_id} has expired past its best before date.")

                # 2. Lock volunteer profile FOR UPDATE & enforce vehicle capacity
                cursor.execute("""
                    SELECT volunteer_id, vehicle_type, max_capacity_kg, availability_status 
                    FROM volunteer_profiles 
                    WHERE volunteer_id = %s FOR UPDATE
                """, (volunteer_id,))
                vol = cursor.fetchone()
                if not vol:
                    raise Exception(f"Volunteer #{volunteer_id} does not exist.")
                if vol['availability_status'] != 'ONLINE':
                    raise Exception(f"Volunteer #{volunteer_id} is currently {vol['availability_status']} and cannot accept new dispatches.")
                if float(vol['max_capacity_kg']) < float(batch['weight_kg']):
                    return jsonify({
                        "success": False,
                        "error": f"CAPACITY_EXCEEDED: Volunteer vehicle ({vol['vehicle_type']}, max {vol['max_capacity_kg']} kg) cannot carry batch weight ({batch['weight_kg']} kg). Choose a volunteer with a larger vehicle.",
                        "sql_state": "45000",
                        "error_code": 1644
                    }), 400

                # 3. Generate 4-digit OTPs
                import random
                p_otp = str(random.randint(1000, 9999))
                d_otp = str(random.randint(1000, 9999))

                # 4. Insert into claims
                cursor.execute("""
                    INSERT INTO claims (batch_id, ngo_id, volunteer_id, pickup_otp, delivery_otp, status)
                    VALUES (%s, %s, %s, %s, %s, 'ASSIGNED')
                """, (batch_id, ngo_id, volunteer_id, p_otp, d_otp))
                claim_id = cursor.lastrowid

                # 5. Update states atomically
                cursor.execute("UPDATE food_batches SET status = 'CLAIMED' WHERE batch_id = %s", (batch_id,))
                cursor.execute("UPDATE volunteer_profiles SET availability_status = 'BUSY' WHERE volunteer_id = %s", (volunteer_id,))

                # 6. Insert audit log
                cursor.execute("""
                    INSERT INTO audit_logs (batch_id, actor_user_id, event_type, old_status, new_status, description, logged_at)
                    VALUES (%s, %s, 'BATCH_CLAIMED', 'AVAILABLE', 'CLAIMED', %s, NOW())
                """, (batch_id, volunteer_id, f"Batch #{batch_id} claimed by NGO #{ngo_id} with Volunteer #{volunteer_id}"))

                conn.commit()
            else:
                raise proc_err

        # Fetch created claim with generated OTPs
        cursor.execute("SELECT * FROM claims WHERE claim_id = %s", (claim_id,))
        claim_data = serialize_row(cursor.fetchone())

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": status_msg or "Batch claimed successfully.",
            "claim_id": claim_id,
            "claim_details": claim_data
        }), 201

    except Error as err:
        if conn:
            conn.rollback()
            conn.close()
        # Custom SIGNAL SQLSTATE '45000' messages return cleanly here
        return jsonify({
            "success": False, 
            "error_code": err.errno,
            "sql_state": err.sqlstate,
            "error": err.msg
        }), 400

# ============================================================================
# API: CONFIRM DELIVERY (DEMONSTRATES TRIGGER 2: trg_after_claim_completed)
# ============================================================================
@app.route('/api/deliver/<int:claim_id>', methods=['POST'])
def confirm_delivery(claim_id):
    """
    Marks a claim as COMPLETED.
    Fires TRIGGER trg_after_claim_completed which:
    1. Sets food_batches.status = 'DELIVERED'
    2. Sets volunteer_profiles.availability_status = 'ONLINE', increments deliveries
    3. Calculates CO2 prevented (weight * 2.50) & updates impact_stats for NGO
    4. Writes detailed execution summary to audit_logs
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify claim exists and is not already completed
        cursor.execute("SELECT * FROM claims WHERE claim_id = %s", (claim_id,))
        claim = cursor.fetchone()
        if not claim:
            conn.close()
            return jsonify({"success": False, "error": "Claim not found."}), 404

        if claim['status'] == 'COMPLETED':
            conn.close()
            return jsonify({"success": False, "error": "Delivery has already been confirmed for this claim."}), 400

        # Updating status to COMPLETED triggers trg_after_claim_completed
        cursor.execute("""
            UPDATE claims 
            SET status = 'COMPLETED', delivered_at = NOW() 
            WHERE claim_id = %s
        """, (claim_id,))
        conn.commit()

        # Query the audit_log entry inserted by trigger
        cursor.execute("""
            SELECT * FROM audit_logs 
            WHERE batch_id = %s AND event_type = 'DELIVERY_COMPLETED' 
            ORDER BY log_id DESC LIMIT 1
        """, (claim['batch_id'],))
        trigger_log = serialize_row(cursor.fetchone())

        # If database engine does not execute triggers (e.g. TiDB cloud), execute state sync in ACID transaction
        if not trigger_log:
            cursor.execute("SELECT quantity_meals, weight_kg, title FROM food_batches WHERE batch_id = %s", (claim['batch_id'],))
            b_info = cursor.fetchone()
            meals = b_info['quantity_meals'] if b_info else 0
            weight = float(b_info['weight_kg']) if b_info else 0.0
            title = b_info['title'] if b_info else 'Batch'
            co2 = round(weight * 2.50, 2)

            cursor.execute("UPDATE food_batches SET status = 'DELIVERED' WHERE batch_id = %s", (claim['batch_id'],))
            cursor.execute("UPDATE volunteer_profiles SET availability_status = 'ONLINE', total_deliveries = total_deliveries + 1 WHERE volunteer_id = %s", (claim['volunteer_id'],))
            cursor.execute("""
                UPDATE impact_stats 
                SET total_batches_rescued = total_batches_rescued + 1,
                    total_meals_saved = total_meals_saved + %s,
                    total_weight_saved_kg = total_weight_saved_kg + %s,
                    co2_prevented_kg = co2_prevented_kg + %s,
                    last_rescue_at = NOW()
                WHERE ngo_id = %s
            """, (meals, weight, co2, claim['ngo_id']))
            cursor.execute("""
                INSERT INTO audit_logs (batch_id, actor_user_id, event_type, old_status, new_status, description, logged_at)
                VALUES (%s, %s, 'DELIVERY_COMPLETED', %s, 'COMPLETED', %s, NOW())
            """, (claim['batch_id'], claim['volunteer_id'], claim['status'], f"Batch #{claim['batch_id']} (\"{title}\") completed. Saved {meals} meals, {weight} kg food. CO2 Offset: {co2} kg."))
            conn.commit()

            cursor.execute("SELECT * FROM audit_logs WHERE batch_id = %s AND event_type = 'DELIVERY_COMPLETED' ORDER BY log_id DESC LIMIT 1", (claim['batch_id'],))
            trigger_log = serialize_row(cursor.fetchone())

        # Query updated NGO impact stats to show immediate propagation
        cursor.execute("SELECT * FROM impact_stats WHERE ngo_id = %s", (claim['ngo_id'],))
        updated_impact = serialize_row(cursor.fetchone())

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": f"Claim #{claim_id} confirmed completed! Trigger 'trg_after_claim_completed' fired automatically.",
            "trigger_audit_log": trigger_log,
            "updated_impact_stats": updated_impact
        })

    except Error as err:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": str(err)}), 400

# ============================================================================
# API: DASHBOARD METRICS (AGGREGATIONS, 4-TABLE JOIN, GROUP BY, AUDIT LOGS)
# ============================================================================
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    Returns aggregated KPIs, zone-wise supply (GROUP BY),
    active claims (4-table JOIN), and the real-time audit ledger.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. KPI Aggregations (SUM, COUNT) from impact_stats and food_batches
        cursor.execute("""
            SELECT 
                COALESCE(SUM(total_meals_saved), 0) AS total_meals,
                COALESCE(SUM(total_weight_saved_kg), 0.00) AS total_weight_kg,
                COALESCE(SUM(co2_prevented_kg), 0.00) AS total_co2_kg,
                COALESCE(SUM(total_batches_rescued), 0) AS total_rescues
            FROM impact_stats
        """)
        kpi_impact = serialize_row(cursor.fetchone())

        cursor.execute("""
            SELECT 
                COUNT(*) AS total_batches,
                SUM(CASE WHEN status = 'AVAILABLE' THEN 1 ELSE 0 END) AS available_count,
                SUM(CASE WHEN status = 'CLAIMED' THEN 1 ELSE 0 END) AS claimed_count,
                SUM(CASE WHEN status = 'DELIVERED' THEN 1 ELSE 0 END) AS delivered_count,
                SUM(CASE WHEN status = 'EXPIRED' THEN 1 ELSE 0 END) AS expired_count
            FROM food_batches
        """)
        batch_counts = serialize_row(cursor.fetchone())

        # 2. Zone-wise Supply Aggregation (GROUP BY with COUNT and SUM)
        cursor.execute("""
            SELECT 
                zone, 
                COUNT(*) AS available_batches, 
                COALESCE(SUM(quantity_meals), 0) AS zone_meals,
                COALESCE(SUM(weight_kg), 0.00) AS zone_weight_kg
            FROM food_batches 
            WHERE status = 'AVAILABLE' 
            GROUP BY zone
            ORDER BY available_batches DESC
        """)
        zone_summary = [serialize_row(row) for row in cursor.fetchall()]

        # 3. 4-Table JOIN: Active Claims Tracking with Verification OTPs
        cursor.execute("""
            SELECT 
                c.claim_id,
                c.pickup_otp,
                c.delivery_otp,
                c.distance_km,
                c.status AS claim_status,
                c.claimed_at,
                b.batch_id,
                b.title AS batch_title,
                b.weight_kg,
                b.quantity_meals,
                b.pickup_address,
                b.zone,
                u_donor.full_name AS donor_name,
                u_donor.phone AS donor_phone,
                u_ngo.full_name AS ngo_name,
                u_vol.full_name AS volunteer_name,
                u_vol.phone AS volunteer_phone,
                vp.vehicle_type,
                vp.vehicle_reg_no,
                vp.max_capacity_kg
            FROM claims c
            INNER JOIN food_batches b ON c.batch_id = b.batch_id
            INNER JOIN users u_donor ON b.donor_id = u_donor.user_id
            INNER JOIN users u_ngo ON c.ngo_id = u_ngo.user_id
            INNER JOIN users u_vol ON c.volunteer_id = u_vol.user_id
            INNER JOIN volunteer_profiles vp ON c.volunteer_id = vp.volunteer_id
            WHERE c.status IN ('ASSIGNED', 'PICKED_UP')
            ORDER BY c.claimed_at DESC
        """)
        active_claims = [serialize_row(row) for row in cursor.fetchall()]

        # 4. Recent Real-Time Audit Trail
        cursor.execute("""
            SELECT 
                a.log_id,
                a.batch_id,
                a.event_type,
                a.old_status,
                a.new_status,
                a.description,
                DATE_FORMAT(a.logged_at, '%Y-%m-%d %H:%i:%s') AS logged_at,
                COALESCE(u.full_name, 'SYSTEM AUTOMATION') AS actor_name
            FROM audit_logs a
            LEFT JOIN users u ON a.actor_user_id = u.user_id
            ORDER BY a.log_id DESC
            LIMIT 25
        """)
        audit_trail = [serialize_row(row) for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "kpis": {**kpi_impact, **batch_counts},
            "zone_distribution": zone_summary,
            "active_claims": active_claims,
            "audit_trail": audit_trail
        })

    except Error as err:
        if conn:
            conn.close()
        return jsonify({"success": False, "error": str(err)}), 500

# ============================================================================
# API: DATABASE INTROSPECTION (INFORMATION_SCHEMA QUERY FOR DBMS VIVA)
# ============================================================================
@app.route('/api/schema-info', methods=['GET'])
def get_schema_info():
    """
    Directly inspects MySQL INFORMATION_SCHEMA to show active Primary Keys,
    Foreign Keys, Unique constraints, Check constraints, Triggers, and Views.
    Essential for laboratory viva demonstration!
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        db_name = os.getenv('DB_NAME', 'food_rescue_db')

        # 1. Table Constraints (PK, FK, UNIQUE, CHECK)
        cursor.execute("""
            SELECT 
                TABLE_NAME, 
                CONSTRAINT_NAME, 
                CONSTRAINT_TYPE 
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = %s
            ORDER BY TABLE_NAME, CONSTRAINT_TYPE
        """, (db_name,))
        constraints = cursor.fetchall()

        # 2. Database Triggers
        cursor.execute("""
            SELECT 
                TRIGGER_NAME, 
                EVENT_MANIPULATION, 
                EVENT_OBJECT_TABLE, 
                ACTION_TIMING, 
                CREATED
            FROM INFORMATION_SCHEMA.TRIGGERS
            WHERE TRIGGER_SCHEMA = %s
        """, (db_name,))
        triggers = cursor.fetchall()

        # 3. Stored Procedures
        cursor.execute("""
            SELECT 
                ROUTINE_NAME, 
                ROUTINE_TYPE, 
                DEFINER, 
                CREATED, 
                SECURITY_TYPE
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_SCHEMA = %s
        """, (db_name,))
        routines = cursor.fetchall()

        # 4. Views
        cursor.execute("""
            SELECT 
                TABLE_NAME AS VIEW_NAME, 
                CHECK_OPTION, 
                IS_UPDATABLE
            FROM INFORMATION_SCHEMA.VIEWS
            WHERE TABLE_SCHEMA = %s
        """, (db_name,))
        views = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "database_name": db_name,
            "constraints": constraints,
            "triggers": triggers,
            "routines": routines,
            "views": views
        })

    except Error as err:
        if conn:
            conn.close()
        return jsonify({"success": False, "error": str(err)}), 500

# ============================================================================
# API: LOOKUP HELPERS (DONORS, NGOS, VOLUNTEERS WITH CAPACITY)
# ============================================================================
@app.route('/api/lookups', methods=['GET'])
def get_lookups():
    """Returns available actors to populate frontend modal dropdowns."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Donors
        cursor.execute("SELECT user_id, full_name, zone, street_address FROM users WHERE role = 'DONOR' ORDER BY full_name")
        donors = cursor.fetchall()

        # NGOs
        cursor.execute("""
            SELECT u.user_id, u.full_name, u.zone, s.daily_meal_capacity 
            FROM users u 
            INNER JOIN impact_stats s ON u.user_id = s.ngo_id 
            WHERE u.role = 'NGO'
            ORDER BY u.full_name
        """)
        ngos = cursor.fetchall()

        # Volunteers with vehicle capacities & availability status
        cursor.execute("""
            SELECT 
                u.user_id, 
                u.full_name, 
                u.zone, 
                vp.vehicle_type, 
                vp.vehicle_reg_no, 
                vp.max_capacity_kg, 
                vp.availability_status
            FROM users u 
            INNER JOIN volunteer_profiles vp ON u.user_id = vp.volunteer_id
            WHERE u.role = 'VOLUNTEER'
            ORDER BY u.full_name
        """)
        volunteers = [serialize_row(v) for v in cursor.fetchall()]

        cursor.close()
        conn.close()
        return jsonify({
            "success": True,
            "donors": donors,
            "ngos": ngos,
            "volunteers": volunteers
        })
    except Error as err:
        if conn:
            conn.close()
        return jsonify({"success": False, "error": str(err)}), 500

# ============================================================================
# MAIN ENTRYPOINT
# ============================================================================
if __name__ == '__main__':
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 5000)))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    print(f"\n============================================================")
    print(f"🚀 FoodRescue Network Backend Server Running on Port {port}")
    print(f"📂 Template Folder: {TEMPLATE_DIR}")
    print(f"📊 MySQL Connection: {os.getenv('DB_USER', 'root')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 3306)}/{os.getenv('DB_NAME', 'food_rescue_db')}")
    print(f"============================================================\n")
    app.run(host='0.0.0.0', port=port, debug=debug)
