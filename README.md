# 🍲 FoodRescue Network — Surplus Food Redistribution System
### Full-Stack Relational Database Management System (DBMS) Project
**Engineered for MySQL 8.0, Python (Flask with raw `mysql-connector-python`), and Bootstrap 5 + Vanilla JavaScript.**  
*Strictly No ORM (No SQLAlchemy) — Transparent Relational Logic, Raw Parameterized SQL, Stored Procedures, Triggers, Views, and ACID Transactions.*

---

## 📋 Table of Contents
1. [Project Overview & Problem Statement](#-project-overview--problem-statement)
2. [Relational Schema & 3NF Normalization](#-relational-schema--3nf-normalization)
3. [DBMS Objects Specification](#-dbms-objects-specification)
   - [Relational View (`vw_live_rescue_feed`)](#1-relational-view-vw_live_rescue_feed)
   - [Automated Trigger 1 (`trg_after_batch_insert`)](#2-trigger-1-trg_after_batch_insert)
   - [Automated Trigger 2 (`trg_after_claim_completed`)](#3-trigger-2-trg_after_claim_completed)
   - [Stored Procedure 1 (`sp_claim_food_batch`)](#4-stored-procedure-1-sp_claim_food_batch)
   - [Stored Procedure 2 (`sp_expire_stale_batches`)](#5-stored-procedure-2-sp_expire_stale_batches)
4. [Project Structure](#-project-structure)
5. [Step-by-Step Installation & Setup](#-step-by-step-installation--setup)
6. [Laboratory Viva Evaluation & Demo Script](#-laboratory-viva-evaluation--demo-script)
7. [Examiner Viva Q&A Cheat Sheet](#-examiner-viva-qa-cheat-sheet)

---

## 🎯 Project Overview & Problem Statement

Large commercial food producers (hotels, banquets, corporate dining, bakeries) generate tons of edible surplus food daily. Concurrently, local relief NGOs struggle with fragmented logistics and lack of real-time supply visibility.

**FoodRescue Network** is an enterprise-grade surplus food logistics system that connects **Donors**, **NGOs**, and **Volunteer Couriers** with strict physical validation:
- Donors post surplus food batches with dietary classification, storage temperature requirements, and shelf-life timestamps.
- NGOs claim batches dispatched to volunteers based on **physical vehicle capacity constraints**.
- Database-level automation ensures **row-level locking (`FOR UPDATE`)**, **automated CO₂ emission offset calculations**, and **append-only audit ledgers**.

---

## 🏛️ Relational Schema & 3NF Normalization

The database `food_rescue_db` consists of **6 normalized tables** designed to Third Normal Form (3NF):

```
                        ┌────────────────────────┐
                        │         users          │ (Generalization Entity)
                        │  PK: user_id           │
                        └───────────┬────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
       1:1 │ Subtype            1:1 │ Subtype            1:N │ (Donor)
           ▼                        ▼                        ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│  volunteer_profiles  │ │     impact_stats     │ │     food_batches     │
│  PK/FK: volunteer_id │ │  PK/FK: ngo_id       │ │  PK: batch_id        │
│  max_capacity_kg     │ │  total_meals_saved   │ │  FK: donor_id        │
└──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘
           │                        │                        │
           │                        │ 1:N                    │ 1:1
           │ 1:N                    ▼                        ▼
           │             ┌──────────────────────┐            │
           └────────────►│        claims        │◄───────────┘
                         │  PK: claim_id        │ (Associative Entity)
                         │  FK: batch_id        │
                         │  FK: ngo_id          │
                         │  FK: volunteer_id    │
                         └──────────┬───────────┘
                                    │
                                    ▼ Triggers & Procedures
                         ┌──────────────────────┐
                         │      audit_logs      │
                         │  PK: log_id          │
                         │  FK: batch_id        │
                         │  FK: actor_user_id   │
                         └──────────────────────┘
```

### 3NF Justification:
1. **1NF (First Normal Form):** Every attribute contains atomic values. Multi-valued dependencies are eliminated.
2. **2NF (Second Normal Form):** Every non-key attribute is fully functionally dependent on the entire primary key. In specialization entities (`volunteer_profiles`, `impact_stats`), non-key attributes depend strictly on their 1:1 foreign primary keys (`volunteer_id`, `ngo_id`).
3. **3NF (Third Normal Form):** No transitive dependencies exist ($X \to Y$ where $Y \to Z$). Donor addresses and NGO contact numbers reside only in `users`, preventing redundant duplication across inventory batches and claims.

---

## ⚙️ DBMS Objects Specification

### 1. Relational View: `vw_live_rescue_feed`
Consolidates available batches with donor contact details and computes real-time shelf life dynamically:
```sql
SELECT 
    b.batch_id, b.title, b.quantity_meals, b.weight_kg, b.category, b.food_type,
    u.full_name AS donor_name, u.phone AS donor_phone, b.pickup_address, b.zone,
    TIMESTAMPDIFF(MINUTE, NOW(), b.best_before) AS minutes_left
FROM food_batches b
INNER JOIN users u ON b.donor_id = u.user_id
WHERE b.status = 'AVAILABLE';
```

### 2. Trigger 1: `trg_after_batch_insert`
- **Timing / Event:** `AFTER INSERT ON food_batches`
- **Purpose:** Automatically inserts an immutable record into `audit_logs` whenever a donor lists surplus food:
  - `event_type`: `'BATCH_CREATED'`
  - `actor_user_id`: `NEW.donor_id`
  - `new_status`: `'AVAILABLE'`

### 3. Trigger 2: `trg_after_claim_completed`
- **Timing / Event:** `AFTER UPDATE ON claims`
- **Trigger Condition:** `OLD.status != 'COMPLETED' AND NEW.status = 'COMPLETED'`
- **Automated Actions:**
  1. Transitions `food_batches.status` to `'DELIVERED'`.
  2. Resets volunteer: `volunteer_profiles.availability_status = 'ONLINE'` and increments `total_deliveries`.
  3. Increments NGO statistics in `impact_stats`:
     $$\Delta\text{CO}_2\text{ prevented (kg)} = \text{weight\_kg} \times 2.50$$
  4. Appends a completion summary to `audit_logs`.

### 4. Stored Procedure 1: `sp_claim_food_batch`
- **Parameters:** `(IN p_batch_id INT, IN p_ngo_id INT, IN p_volunteer_id INT, OUT p_claim_id INT, OUT p_status_msg VARCHAR)`
- **Concurrency & Integrity Enforcement:**
  - `START TRANSACTION;`
  - `SELECT ... FOR UPDATE` acquires row-level exclusive locks on `food_batches` and `volunteer_profiles`.
  - **Validation Checks:**
    - Is batch status `'AVAILABLE'`? (Prevents double claims).
    - Has batch expired (`best_before <= NOW()`)?
    - Is volunteer `'ONLINE'`?
    - **Vehicle Capacity Check:** Does `volunteer_profiles.max_capacity_kg >= food_batches.weight_kg`?  
      If false $\to$ `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Capacity Violation: Volunteer vehicle capacity is less than batch weight.';`
  - Generates random 4-digit numeric verification OTPs (`pickup_otp`, `delivery_otp`).
  - Inserts row into `claims` and updates batch and volunteer statuses.
  - Commits transaction atomically; invokes `DECLARE EXIT HANDLER FOR SQLEXCEPTION` with `ROLLBACK` on any violation.

### 5. Stored Procedure 2: `sp_expire_stale_batches`
- **Parameters:** `(OUT p_expired_count INT)`
- Automatically transitions all `AVAILABLE` batches where `best_before <= NOW()` to `'EXPIRED'` and logs maintenance events.

---

## 📁 Project Structure

```
food-rescue-network/
│
├── database/
│   └── schema.sql              # Complete DDL, 3NF tables, constraints, triggers, procedures, views & seed data
│
├── backend/
│   ├── app.py                  # Flask REST API using raw mysql.connector (Zero ORM)
│   ├── requirements.txt        # Python dependencies (Flask, mysql-connector-python, python-dotenv)
│   └── .env.example            # Environment configuration template
│
├── frontend/
│   └── templates/
│       └── index.html          # Responsive Bootstrap 5 + Vanilla JS evaluation dashboard
│
└── README.md                   # Complete architectural documentation & viva demo manual
```

---

## 🚀 Step-by-Step Installation & Setup

### 1. Prerequisites
- **MySQL Server 8.0+** running locally (port 3306).
- **Python 3.8+** installed.

---

### 2. Import the Database Schema
Open your terminal or MySQL command-line prompt:

```bash
# Clone or navigate to the project directory:
cd C:\Users\HP\.gemini\antigravity\scratch\food-rescue-network

# Import the schema into MySQL:
mysql -u root -p < database/schema.sql
```
*(Enter your MySQL root password when prompted. This creates `food_rescue_db`, all tables, constraints, procedures, triggers, and seed records).*

---

### 3. Setup Python Virtual Environment
Navigate to the `backend` directory and set up dependencies:

```bash
cd backend

# Create virtual environment:
python -m venv venv

# Activate virtual environment:
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required packages:
pip install -r requirements.txt
```

---

### 4. Configure Database Credentials
Create a `.env` file in the `backend/` folder (or copy `.env.example`):

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=food_rescue_db

FLASK_PORT=5000
FLASK_DEBUG=True
```

---

### 5. Start the Application
Run the Flask server:

```bash
python app.py
```

Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

The top navigation bar will show a green badge: **`MySQL 8.0 Connected (food_rescue_db)`**.

---

## 🧪 Laboratory Viva Evaluation & Demo Script

Follow these 5 exact test cases in front of your examiner to demonstrate complete mastery of Relational Database Concepts:

### Test Case 1: Automated Trigger 1 (`trg_after_batch_insert`)
1. In the web dashboard, click **"+ Post Surplus Batch"**.
2. Enter:
   - **Donor:** Grand Hyatt Banquets
   - **Title:** Fresh Fruit Bowls & Sandwiches
   - **Meals:** 25
   - **Weight:** 8.0 kg
   - **Category:** Cooked Meal | **Type:** VEG
   - **Best Before:** Select a time 4 hours from now.
   - **Address:** 100 Gateway Boulevard, Grand Hall
3. Click **"Post Batch & Fire Trigger"**.
4. **Examiner Takeaway:** Scroll down to the **Live SQL Execution & Trigger Ledger** terminal. Point out the immediate green `[BATCH_CREATED]` row appended automatically by MySQL's `AFTER INSERT` trigger without any application-level logging code!

---

### Test Case 2: Stored Procedure & Physical Vehicle Capacity Constraint (`SQLSTATE 45000`)
1. On the surplus feed, find **Batch #2: "Gala Dinner Feast - Dum Biryani"** (Weight: **48.00 kg**).
2. Click **"Claim Batch"**.
3. In the modal:
   - **Claiming NGO:** Robin Hood Army - South
   - **Assign Volunteer:** Select **Rahul Verma (BIKE - Max Capacity: 15.00 kg)**.
4. Click **"Execute sp_claim_food_batch"**.
5. **Result:** The system displays a red transaction rollback error:
   ```
   MySQL Error [1644] (SQLSTATE 45000): Capacity Violation: Selected volunteer vehicle capacity is less than batch weight.
   ```
6. **Examiner Takeaway:** Explain how `sp_claim_food_batch` used `SELECT ... FOR UPDATE` row-level locks, validated $15.00 < 48.00$, and safely aborted the transaction with `SIGNAL SQLSTATE '45000'`!
7. **Resolution:** Switch the volunteer to **Priya Sharma (VAN - Max Capacity: 250.00 kg)** and submit. The transaction succeeds, generating secure verification OTPs!

---

### Test Case 3: Automated Trigger 2 (`trg_after_claim_completed`) & Formulaic Propagation
1. Scroll to the **Active Rescue Dispatches (4-Table Join)** section.
2. Locate the active claim created in Test Case 2.
3. Click **"Confirm Delivery"**.
4. **What MySQL does in one atomic trigger:**
   - Marks `food_batches.status` as `'DELIVERED'`.
   - Releases the volunteer back to `'ONLINE'` and increments delivery count.
   - Calculates $\text{CO}_2\text{ offset} = 48.0\text{ kg} \times 2.50 = 120.0\text{ kg}$.
   - Updates `impact_stats` for the NGO.
   - Appends a `[DELIVERY_COMPLETED]` audit log.
5. **Examiner Takeaway:** Point to the top KPI cards updating immediately with increased meals and CO₂ offset!

---

### Test Case 4: Real-Time Relational View (`vw_live_rescue_feed`)
1. Point to the countdown timer badges on the surplus cards (*"Expiring in Xh Ym"*).
2. **Explanation:** The frontend queries view `vw_live_rescue_feed`. The view joins `food_batches` with `users` and dynamically calculates `TIMESTAMPDIFF(MINUTE, NOW(), b.best_before)` without persisting redundant time data.

---

### Test Case 5: Live Database Introspection via `INFORMATION_SCHEMA`
1. In the top navigation bar, click **"View Active Constraints"**.
2. **Tab 1 (Constraints):** Shows every Primary Key, Foreign Key, Check Constraint, and Unique Constraint directly queried from `INFORMATION_SCHEMA.TABLE_CONSTRAINTS`.
3. **Tab 2 (Triggers):** Displays `trg_after_batch_insert` and `trg_after_claim_completed`.
4. **Tab 3 (Procedures):** Displays `sp_claim_food_batch` and `sp_expire_stale_batches`.
5. **Tab 4 (Views):** Displays `vw_live_rescue_feed`.

---

## 🎓 Examiner Viva Q&A Cheat Sheet

| Question | Model Answer |
| :--- | :--- |
| **Q1: Why did you not use an ORM like SQLAlchemy or Hibernate?** | *"ORMs abstract away SQL generation, hiding table locks, trigger side-effects, and join plans. In a DBMS evaluation, using raw parameterized SQL (`mysql.connector`) guarantees explicit control over ACID transactions, connection pools, and database-level stored procedures and triggers."* |
| **Q2: What is the purpose of `SELECT ... FOR UPDATE` in your claim procedure?** | *"It acquires an exclusive row-level lock on the selected batch and volunteer profile. If two NGOs attempt to claim the exact same surplus batch simultaneously, the second transaction is forced to wait until the first commits or rolls back, preventing race conditions and double-claims."* |
| **Q3: Explain the 1:1 subtype specialization in your schema.** | *"`volunteer_profiles` and `impact_stats` share a 1:1 relationship with `users` via their primary keys (`volunteer_id` and `ngo_id`), which are also foreign keys referencing `users.user_id ON DELETE CASCADE`. This models class hierarchy/specialization in 3NF without creating sparse, NULL-heavy single tables."* |
| **Q4: Why use `ON DELETE CASCADE` on `claims` but `ON DELETE SET NULL` on `audit_logs`?** | *"If a food batch is deleted, its associated claim is no longer actionable, so cascading deletion preserves referential integrity. However, an audit ledger must remain an immutable legal record; deleting a batch or actor should never erase historical transaction logs, so foreign keys in `audit_logs` are set to `NULL`."* |
| **Q5: How does your trigger calculate CO₂ emissions offset?** | *"`trg_after_claim_completed` executes upon `UPDATE ON claims` when status becomes `'COMPLETED'`. It reads the batch weight in kg and computes $\text{CO}_2\text{ prevented} = \text{weight\_kg} \times 2.50$, updating the NGO's `impact_stats` table automatically."* |
| **Q6: What is `SIGNAL SQLSTATE '45000'`?** | *"`SQLSTATE '45000'` is the ANSI SQL standard code for an unhandled user-defined exception. In our stored procedure, when a business constraint is violated (e.g., vehicle capacity < food weight), `SIGNAL SQLSTATE '45000'` throws an explicit error that triggers our `EXIT HANDLER`, rolling back the transaction."* |

---

## 📜 License
Educational DBMS Project created for academic lab and viva evaluations. Distributed under the MIT License.
