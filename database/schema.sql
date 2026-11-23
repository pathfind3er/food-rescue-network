-- ============================================================================
-- FoodRescue Network — Surplus Food Redistribution System
-- Complete 3NF Normalized Database Schema for MySQL 8.0
-- Demonstrates: DDL, Constraints (PK, FK, UNIQUE, CHECK), Composite Indexes,
-- Stored Procedures with ACID Transactions & Row-Level Locking (FOR UPDATE),
-- Triggers, Views, and Information Schema Introspection.
-- ============================================================================

DROP DATABASE IF EXISTS food_rescue_db;
CREATE DATABASE food_rescue_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE food_rescue_db;

-- ============================================================================
-- TABLE 1: users
-- Core entity storing all system actors (Donors, NGOs, Volunteers, Admins)
-- ============================================================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role ENUM('DONOR', 'NGO', 'VOLUNTEER', 'ADMIN') NOT NULL,
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL DEFAULT 'Metropolis',
    zone VARCHAR(50) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    latitude DECIMAL(9, 6) NULL,
    longitude DECIMAL(9, 6) NULL,
    is_verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_email UNIQUE (email),
    INDEX idx_users_role_zone (role, zone)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE 2: volunteer_profiles
-- Specialization subtype (1:1 with users WHERE role='VOLUNTEER')
-- Tracks vehicle capacity constraints used for physical validation during claims
-- ============================================================================
CREATE TABLE volunteer_profiles (
    volunteer_id INT PRIMARY KEY,
    vehicle_type ENUM('BICYCLE', 'BIKE', 'CAR', 'VAN') NOT NULL,
    vehicle_reg_no VARCHAR(50) NOT NULL,
    max_capacity_kg DECIMAL(8, 2) NOT NULL,
    availability_status ENUM('ONLINE', 'BUSY', 'OFFLINE') DEFAULT 'ONLINE',
    total_deliveries INT DEFAULT 0,
    avg_rating DECIMAL(3, 2) DEFAULT 5.00,
    CONSTRAINT fk_vol_user FOREIGN KEY (volunteer_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT uq_vol_vehicle UNIQUE (vehicle_reg_no),
    CONSTRAINT chk_vol_capacity CHECK (max_capacity_kg > 0),
    CONSTRAINT chk_vol_rating CHECK (avg_rating >= 1.00 AND avg_rating <= 5.00)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE 3: impact_stats
-- Specialization subtype (1:1 with users WHERE role='NGO')
-- Tracks aggregated real-time metrics updated automatically via database triggers
-- ============================================================================
CREATE TABLE impact_stats (
    ngo_id INT PRIMARY KEY,
    ngo_reg_number VARCHAR(50) NOT NULL,
    daily_meal_capacity INT NOT NULL,
    total_batches_rescued INT DEFAULT 0,
    total_meals_saved INT DEFAULT 0,
    total_weight_saved_kg DECIMAL(10, 2) DEFAULT 0.00,
    co2_prevented_kg DECIMAL(10, 2) DEFAULT 0.00,
    last_rescue_at DATETIME NULL,
    CONSTRAINT fk_impact_ngo FOREIGN KEY (ngo_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT uq_ngo_reg UNIQUE (ngo_reg_number),
    CONSTRAINT chk_ngo_capacity CHECK (daily_meal_capacity > 0)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE 4: food_batches
-- Core inventory of surplus food posted by donors
-- Includes strict time constraints: best_before > prepared_at
-- ============================================================================
CREATE TABLE food_batches (
    batch_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    category ENUM('COOKED_MEAL', 'BAKERY', 'PRODUCE', 'DAIRY', 'PACKAGED') NOT NULL,
    food_type ENUM('VEG', 'NON_VEG', 'VEGAN') NOT NULL,
    quantity_meals INT NOT NULL,
    weight_kg DECIMAL(8, 2) NOT NULL,
    allergen_info VARCHAR(255) DEFAULT 'None',
    storage_temp_req ENUM('HOT', 'AMBIENT', 'REFRIGERATED') NOT NULL DEFAULT 'AMBIENT',
    prepared_at DATETIME NOT NULL,
    best_before DATETIME NOT NULL,
    pickup_address VARCHAR(255) NOT NULL,
    zone VARCHAR(50) NOT NULL,
    status ENUM('AVAILABLE', 'CLAIMED', 'IN_TRANSIT', 'DELIVERED', 'EXPIRED') DEFAULT 'AVAILABLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_batch_donor FOREIGN KEY (donor_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT chk_batch_meals CHECK (quantity_meals > 0),
    CONSTRAINT chk_batch_weight CHECK (weight_kg > 0),
    CONSTRAINT chk_batch_shelf_life CHECK (best_before > prepared_at),
    INDEX idx_batches_zone_status (zone, status)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE 5: claims
-- Associative entity binding Food Batch, NGO, and Volunteer
-- Manages delivery OTPs and physical distribution lifecycle
-- ============================================================================
CREATE TABLE claims (
    claim_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    ngo_id INT NOT NULL,
    volunteer_id INT NOT NULL,
    pickup_otp VARCHAR(6) NOT NULL,
    delivery_otp VARCHAR(6) NOT NULL,
    distance_km DECIMAL(6, 2) DEFAULT 3.50,
    claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    picked_up_at DATETIME NULL,
    delivered_at DATETIME NULL,
    rating INT NULL,
    feedback_notes TEXT,
    status ENUM('ASSIGNED', 'PICKED_UP', 'COMPLETED', 'CANCELLED') DEFAULT 'ASSIGNED',
    CONSTRAINT uq_claim_batch UNIQUE (batch_id),
    CONSTRAINT fk_claim_batch FOREIGN KEY (batch_id) 
        REFERENCES food_batches(batch_id) ON DELETE CASCADE,
    CONSTRAINT fk_claim_ngo FOREIGN KEY (ngo_id) 
        REFERENCES users(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_claim_vol FOREIGN KEY (volunteer_id) 
        REFERENCES users(user_id) ON DELETE RESTRICT,
    CONSTRAINT chk_claim_rating CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5))
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE 6: audit_logs
-- Append-only ledger maintaining historical transaction trail
-- Populated automatically via database triggers and stored procedures
-- ============================================================================
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NULL,
    actor_user_id INT NULL,
    event_type VARCHAR(50) NOT NULL,
    old_status VARCHAR(50) NULL,
    new_status VARCHAR(50) NULL,
    description TEXT NOT NULL,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_batch FOREIGN KEY (batch_id) 
        REFERENCES food_batches(batch_id) ON DELETE SET NULL,
    CONSTRAINT fk_audit_user FOREIGN KEY (actor_user_id) 
        REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================================
-- VIEW: vw_live_rescue_feed
-- Consolidates active surplus food batches with donor details and real-time
-- remaining shelf life in minutes.
-- ============================================================================
CREATE OR REPLACE VIEW vw_live_rescue_feed AS
SELECT 
    b.batch_id,
    b.donor_id,
    u.full_name AS donor_name,
    u.phone AS donor_phone,
    b.title,
    b.description,
    b.category,
    b.food_type,
    b.quantity_meals,
    b.weight_kg,
    b.allergen_info,
    b.storage_temp_req,
    b.prepared_at,
    b.best_before,
    TIMESTAMPDIFF(MINUTE, NOW(), b.best_before) AS minutes_left,
    b.pickup_address,
    b.zone,
    b.status,
    b.created_at
FROM food_batches b
INNER JOIN users u ON b.donor_id = u.user_id
WHERE b.status = 'AVAILABLE';

-- ============================================================================
-- TRIGGER 1: trg_after_batch_insert
-- Automated auditing when a new surplus batch is posted
-- ============================================================================
DELIMITER $$
CREATE TRIGGER trg_after_batch_insert
AFTER INSERT ON food_batches
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        batch_id, 
        actor_user_id, 
        event_type, 
        old_status, 
        new_status, 
        description, 
        logged_at
    )
    VALUES (
        NEW.batch_id,
        NEW.donor_id,
        'BATCH_CREATED',
        NULL,
        NEW.status,
        CONCAT('Surplus batch "', NEW.title, '" (', NEW.quantity_meals, ' meals, ', NEW.weight_kg, ' kg) listed in ', NEW.zone, ' [Category: ', NEW.category, ']'),
        NOW()
    );
END$$
DELIMITER ;

-- ============================================================================
-- TRIGGER 2: trg_after_claim_completed
-- Automated state synchronization and metrics calculation upon delivery:
-- 1. Updates batch status to DELIVERED
-- 2. Releases volunteer back to ONLINE and increments delivery count
-- 3. Updates NGO cumulative impact stats and calculates CO2 offset
-- 4. Logs historical completion event in audit_logs
-- ============================================================================
DELIMITER $$
CREATE TRIGGER trg_after_claim_completed
AFTER UPDATE ON claims
FOR EACH ROW
BEGIN
    DECLARE v_meals INT DEFAULT 0;
    DECLARE v_weight DECIMAL(8,2) DEFAULT 0.00;
    DECLARE v_batch_title VARCHAR(150);
    DECLARE v_co2 DECIMAL(10,2) DEFAULT 0.00;

    -- Fire only when claim transitions to COMPLETED
    IF (OLD.status != 'COMPLETED' AND NEW.status = 'COMPLETED') THEN
        -- Retrieve batch quantitative figures
        SELECT quantity_meals, weight_kg, title
        INTO v_meals, v_weight, v_batch_title
        FROM food_batches
        WHERE batch_id = NEW.batch_id;

        -- 1. Transition batch to DELIVERED
        UPDATE food_batches
        SET status = 'DELIVERED'
        WHERE batch_id = NEW.batch_id;

        -- 2. Release volunteer
        UPDATE volunteer_profiles
        SET availability_status = 'ONLINE',
            total_deliveries = total_deliveries + 1
        WHERE volunteer_id = NEW.volunteer_id;

        -- 3. Calculate CO2 prevented (2.5 kg CO2 per kg food saved)
        SET v_co2 = v_weight * 2.50;

        -- 4. Update NGO impact records
        UPDATE impact_stats
        SET total_batches_rescued = total_batches_rescued + 1,
            total_meals_saved = total_meals_saved + v_meals,
            total_weight_saved_kg = total_weight_saved_kg + v_weight,
            co2_prevented_kg = co2_prevented_kg + v_co2,
            last_rescue_at = NOW()
        WHERE ngo_id = NEW.ngo_id;

        -- 5. Audit log
        INSERT INTO audit_logs (
            batch_id, 
            actor_user_id, 
            event_type, 
            old_status, 
            new_status, 
            description, 
            logged_at
        )
        VALUES (
            NEW.batch_id,
            NEW.volunteer_id,
            'DELIVERY_COMPLETED',
            OLD.status,
            'COMPLETED',
            CONCAT('Batch #', NEW.batch_id, ' ("', v_batch_title, '") completed. Saved ', v_meals, ' meals, ', v_weight, ' kg food. CO2 Offset: ', v_co2, ' kg.'),
            NOW()
        );
    END IF;
END$$
DELIMITER ;

-- ============================================================================
-- STORED PROCEDURE 1: sp_claim_food_batch
-- Executes ACID transactional claim operation with row-level locks (FOR UPDATE):
-- - Validates batch existence, availability, and expiration
-- - Locks volunteer profile and verifies vehicle capacity >= batch weight
-- - Generates secure 4-digit pickup and delivery OTPs
-- - Atomically commits state change and writes audit trail
-- ============================================================================
DELIMITER $$
CREATE PROCEDURE sp_claim_food_batch(
    IN p_batch_id INT,
    IN p_ngo_id INT,
    IN p_volunteer_id INT,
    OUT p_claim_id INT,
    OUT p_status_msg VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_batch_status VARCHAR(20);
    DECLARE v_best_before DATETIME;
    DECLARE v_batch_weight DECIMAL(8,2);
    DECLARE v_batch_title VARCHAR(150);
    DECLARE v_vol_status VARCHAR(20);
    DECLARE v_vol_cap DECIMAL(8,2);
    DECLARE v_pickup_otp VARCHAR(6);
    DECLARE v_delivery_otp VARCHAR(6);

    -- Exception handler to ensure full ACID rollback on any failure
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Step 1: Acquire row-level lock on food batch to prevent race condition
    SELECT status, best_before, weight_kg, title
    INTO v_batch_status, v_best_before, v_batch_weight, v_batch_title
    FROM food_batches
    WHERE batch_id = p_batch_id
    FOR UPDATE;

    -- Validation 1: Batch exists
    IF v_batch_status IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Error: Food batch does not exist.';
    END IF;

    -- Validation 2: Batch availability
    IF v_batch_status != 'AVAILABLE' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Concurrency Conflict: Batch has already been claimed by another organization or is not available.';
    END IF;

    -- Validation 3: Shelf-life expiration
    IF v_best_before <= NOW() THEN
        UPDATE food_batches SET status = 'EXPIRED' WHERE batch_id = p_batch_id;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Expiry Error: This batch has passed its best-before timestamp and cannot be claimed.';
    END IF;

    -- Step 2: Acquire row-level lock on volunteer profile
    SELECT availability_status, max_capacity_kg
    INTO v_vol_status, v_vol_cap
    FROM volunteer_profiles
    WHERE volunteer_id = p_volunteer_id
    FOR UPDATE;

    -- Validation 4: Volunteer exists
    IF v_vol_status IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Error: Volunteer profile does not exist.';
    END IF;

    -- Validation 5: Volunteer availability
    IF v_vol_status != 'ONLINE' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Dispatch Error: Volunteer is currently BUSY on another delivery or OFFLINE.';
    END IF;

    -- Validation 6: Physical Vehicle Capacity Check
    IF v_vol_cap < v_batch_weight THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Capacity Violation: Selected volunteer vehicle capacity is less than batch weight. Choose a volunteer with larger vehicle.';
    END IF;

    -- Step 3: Generate secure 4-digit numeric verification OTPs
    SET v_pickup_otp = LPAD(FLOOR(RAND() * 9000 + 1000), 4, '0');
    SET v_delivery_otp = LPAD(FLOOR(RAND() * 9000 + 1000), 4, '0');

    -- Step 4: Insert claim record
    INSERT INTO claims (
        batch_id, 
        ngo_id, 
        volunteer_id, 
        pickup_otp, 
        delivery_otp, 
        distance_km, 
        status
    )
    VALUES (
        p_batch_id, 
        p_ngo_id, 
        p_volunteer_id, 
        v_pickup_otp, 
        v_delivery_otp, 
        ROUND(2.0 + (RAND() * 6.0), 2), 
        'ASSIGNED'
    );

    SET p_claim_id = LAST_INSERT_ID();

    -- Step 5: Update batch status
    UPDATE food_batches
    SET status = 'CLAIMED'
    WHERE batch_id = p_batch_id;

    -- Step 6: Mark volunteer busy
    UPDATE volunteer_profiles
    SET availability_status = 'BUSY'
    WHERE volunteer_id = p_volunteer_id;

    -- Step 7: Record audit event
    INSERT INTO audit_logs (
        batch_id, 
        actor_user_id, 
        event_type, 
        old_status, 
        new_status, 
        description
    )
    VALUES (
        p_batch_id, 
        p_ngo_id, 
        'BATCH_CLAIMED', 
        'AVAILABLE', 
        'CLAIMED', 
        CONCAT('Batch #', p_batch_id, ' ("', v_batch_title, '") claimed by NGO ID ', p_ngo_id, '. Volunteer ID ', p_volunteer_id, ' assigned. Pickup OTP: ', v_pickup_otp)
    );

    COMMIT;
    SET p_status_msg = CONCAT('Success: Batch #', p_batch_id, ' claimed. Claim ID #', p_claim_id, ' created.');
END$$
DELIMITER ;

-- ============================================================================
-- STORED PROCEDURE 2: sp_expire_stale_batches
-- Maintenance job marking past-due batches as EXPIRED
-- ============================================================================
DELIMITER $$
CREATE PROCEDURE sp_expire_stale_batches(
    OUT p_expired_count INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    UPDATE food_batches
    SET status = 'EXPIRED'
    WHERE status = 'AVAILABLE' AND best_before <= NOW();

    SET p_expired_count = ROW_COUNT();

    IF p_expired_count > 0 THEN
        INSERT INTO audit_logs (event_type, old_status, new_status, description)
        VALUES (
            'AUTO_EXPIRED_JOB', 
            'AVAILABLE', 
            'EXPIRED', 
            CONCAT(p_expired_count, ' stale batches automatically transitioned to EXPIRED.')
        );
    END IF;

    COMMIT;
END$$
DELIMITER ;

-- ============================================================================
-- REALISTIC SEED DATA
-- Insert 2 Donors, 2 NGOs, 2 Volunteers (different capacities), 1 Admin,
-- and 3 Food Batches (varying weights to test vehicle constraints)
-- ============================================================================

-- 1. Insert Users
INSERT INTO users (user_id, full_name, email, password_hash, phone, role, street_address, city, zone, pincode, is_verified) VALUES
-- Donors
(1, 'Grand Hyatt Banquets', 'banquets@grandhyatt.example.com', 'scrypt:32768:8:1$salt$hash1', '+91-98200-11223', 'DONOR', '100 Gateway Boulevard, Grand Hall', 'Metropolis', 'South Zone', '400051', TRUE),
(2, 'Artisan Bakehouse & Cafe', 'contact@artisanbake.example.com', 'scrypt:32768:8:1$salt$hash2', '+91-98200-44556', 'DONOR', '14 Connaught Circle, Market Square', 'Metropolis', 'North Zone', '400001', TRUE),

-- NGOs
(3, 'Robin Hood Army - South', 'south@robinhood.example.org', 'scrypt:32768:8:1$salt$hash3', '+91-98700-12345', 'NGO', '45 Community Center Lane', 'Metropolis', 'South Zone', '400055', TRUE),
(4, 'Feeding Hope Foundation', 'care@feedinghope.example.org', 'scrypt:32768:8:1$salt$hash4', '+91-98700-67890', 'NGO', '88 Goodwill Avenue, Sector 4', 'Metropolis', 'Downtown', '400020', TRUE),

-- Volunteers
(5, 'Rahul Verma (Two-Wheeler Dispatch)', 'rahul.v@rescue.example.net', 'scrypt:32768:8:1$salt$hash5', '+91-99670-55443', 'VOLUNTEER', 'B-12 Railway Colony', 'Metropolis', 'South Zone', '400052', TRUE),
(6, 'Priya Sharma (Van Cargo Courier)', 'priya.s@rescue.example.net', 'scrypt:32768:8:1$salt$hash6', '+91-99670-88776', 'VOLUNTEER', 'Plot 9, Transport Hub', 'Metropolis', 'Downtown', '400018', TRUE),

-- Admin
(7, 'FoodRescue Control Room', 'control@foodrescue.internal', 'scrypt:32768:8:1$salt$hash7', '+91-98000-00000', 'ADMIN', 'Municipal Civic Center, 5th Floor', 'Metropolis', 'Downtown', '400001', TRUE);

-- 2. Insert Volunteer Profiles (Note capacity difference: 15.00 kg vs 250.00 kg)
INSERT INTO volunteer_profiles (volunteer_id, vehicle_type, vehicle_reg_no, max_capacity_kg, availability_status, total_deliveries, avg_rating) VALUES
(5, 'BIKE', 'MH-02-CW-9122', 15.00, 'ONLINE', 18, 4.85),
(6, 'VAN',  'MH-04-TR-4401', 250.00, 'ONLINE', 42, 4.95);

-- 3. Insert NGO Impact Stats
INSERT INTO impact_stats (ngo_id, ngo_reg_number, daily_meal_capacity, total_batches_rescued, total_meals_saved, total_weight_saved_kg, co2_prevented_kg, last_rescue_at) VALUES
(3, 'NGO-IND-2021-8841', 600,  24, 780,  312.50, 781.25,  DATE_SUB(NOW(), INTERVAL 1 DAY)),
(4, 'NGO-IND-2019-4102', 1200, 52, 1940, 776.00, 1940.00, DATE_SUB(NOW(), INTERVAL 4 HOUR));

-- 4. Insert Food Batches with diverse attributes
-- Batch 1: 12.5 kg (Small: Fits both Rahul's bike and Priya's van)
-- Batch 2: 48.0 kg (Large: EXCEEDS Rahul's 15kg bike -> Tests capacity constraint violation!)
-- Batch 3: 18.0 kg (Medium: Fits Priya's van, exceeds Rahul's bike)
INSERT INTO food_batches (
    batch_id, donor_id, title, description, category, food_type, 
    quantity_meals, weight_kg, allergen_info, storage_temp_req, 
    prepared_at, best_before, pickup_address, zone, status
) VALUES
(
    1, 1, 
    'Paneer Makhani & Jeera Pulao Trays', 
    'Freshly cooked premium lunch banquet surplus. Sealed in thermal insulated containers.', 
    'COOKED_MEAL', 'VEG', 
    35, 12.50, 'Dairy, Cashews', 'HOT', 
    DATE_SUB(NOW(), INTERVAL 1 HOUR), 
    DATE_ADD(NOW(), INTERVAL 5 HOUR), 
    '100 Gateway Boulevard, Grand Hyatt Service Gate 3', 'South Zone', 'AVAILABLE'
),
(
    2, 1, 
    'Gala Dinner Feast - Dum Biryani & Chicken Tikka Masala', 
    'Large catering surplus from evening corporate event. Chilled for rapid transport.', 
    'COOKED_MEAL', 'NON_VEG', 
    120, 48.00, 'Dairy, Poultry', 'REFRIGERATED', 
    DATE_SUB(NOW(), INTERVAL 2 HOUR), 
    DATE_ADD(NOW(), INTERVAL 6 HOUR), 
    '100 Gateway Boulevard, Loading Dock 2', 'South Zone', 'AVAILABLE'
),
(
    3, 2, 
    'Fresh Sourdough Loaves, Croissants & Multigrain Breads', 
    'End-of-day artisanal oven fresh baked goods packed in bakery paper bags.', 
    'BAKERY', 'VEGAN', 
    60, 18.00, 'Gluten, Wheat', 'AMBIENT', 
    DATE_SUB(NOW(), INTERVAL 3 HOUR), 
    DATE_ADD(NOW(), INTERVAL 9 HOUR), 
    '14 Connaught Circle, Artisan Bakehouse Rear Kitchen', 'North Zone', 'AVAILABLE'
);
