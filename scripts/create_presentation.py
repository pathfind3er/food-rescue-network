"""
FoodRescue Network — Stage 1 DBMS Presentation Generator
Generates a 16:9 modern, publication-grade PowerPoint deck (FoodRescue_Network_Stage1_Presentation.pptx)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# 1. Initialize Presentation with 16:9 Widescreen dimensions
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]  # Blank slide

# Color Palette
COLOR_BG_DARK = RGBColor(15, 23, 42)       # Slate 900
COLOR_BG_LIGHT = RGBColor(248, 250, 252)   # Slate 50
COLOR_CARD_BG = RGBColor(255, 255, 255)    # Pure White
COLOR_CARD_BORDER = RGBColor(226, 232, 240)# Slate 200
COLOR_PRIMARY = RGBColor(37, 99, 235)      # Blue 600
COLOR_SECONDARY = RGBColor(16, 185, 129)   # Emerald 500
COLOR_ACCENT = RGBColor(245, 158, 11)      # Amber 500
COLOR_TEXT_DARK = RGBColor(15, 23, 42)     # Slate 900
COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
COLOR_TEXT_LIGHT = RGBColor(241, 245, 249) # Slate 100
COLOR_HEADER_BG = RGBColor(30, 41, 59)     # Slate 800

def set_slide_background(slide, color):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = color
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, tag_text, title_text, dark=False):
    # Tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_SECONDARY if dark else COLOR_PRIMARY

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.7))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_LIGHT if dark else COLOR_TEXT_DARK

# ==============================================================================
# SLIDE 1: TITLE SLIDE (Dark Executive Theme)
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
set_slide_background(slide1, COLOR_BG_DARK)

# Title Badge
badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.2), Inches(3.8), Inches(0.45))
badge.fill.solid()
badge.fill.fore_color.rgb = RGBColor(30, 58, 138)
badge.line.color.rgb = COLOR_PRIMARY
tf_badge = badge.text_frame
p_b = tf_badge.paragraphs[0]
p_b.text = "DBMS LABORATORY • STAGE 1 EVALUATION"
p_b.font.size = Pt(11)
p_b.font.bold = True
p_b.font.color.rgb = RGBColor(147, 197, 253)
p_b.alignment = PP_ALIGN.CENTER

# Main Title
title_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(1.8))
tf = title_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "FoodRescue Network"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = COLOR_TEXT_LIGHT

p2 = tf.add_paragraph()
p2.text = "Surplus Food Redistribution & Logistics System"
p2.font.size = Pt(22)
p2.font.color.rgb = COLOR_SECONDARY

# Overview text
desc_box = slide1.shapes.add_textbox(Inches(0.8), Inches(3.6), Inches(11.7), Inches(1.2))
tf_d = desc_box.text_frame
tf_d.word_wrap = True
pd = tf_d.paragraphs[0]
pd.text = "A complete 3NF relational database architecture engineered with raw parameterized MySQL 8.0, strict constraint enforcement, automated triggers, stored procedures with ACID transactions (SELECT ... FOR UPDATE), and dynamic relational views."
pd.font.size = Pt(14)
pd.font.color.rgb = COLOR_TEXT_MUTED

# Meta Feature Cards
card_w = Inches(3.64)
card_h = Inches(1.6)
card_y = Inches(5.1)

cards_data = [
    ("CORE STACK", "MySQL 8.0 Server\nPython Flask (No ORM)\nBootstrap 5 + Vanilla JS", COLOR_PRIMARY),
    ("ADVANCED DBMS FEATURES", "Stored Procedures (ACID)\nTriggers & Information Schema\nComposite Indexes & Views", COLOR_SECONDARY),
    ("PROJECT DEVELOPER", "Developed by: pathfind3er\nDeployment: Render + TiDB Cloud\nStrict Academic 3NF Model", COLOR_ACCENT)
]

for idx, (head, body, acc_col) in enumerate(cards_data):
    cx = Inches(0.8) + idx * (card_w + Inches(0.4))
    c_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, card_y, card_w, card_h)
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    c_box.line.color.rgb = acc_col
    c_box.line.width = Pt(1.5)
    tf_c = c_box.text_frame
    tf_c.word_wrap = True
    
    p_ch = tf_c.paragraphs[0]
    p_ch.text = head
    p_ch.font.size = Pt(12)
    p_ch.font.bold = True
    p_ch.font.color.rgb = acc_col
    
    p_cb = tf_c.add_paragraph()
    p_cb.text = body
    p_cb.font.size = Pt(12)
    p_cb.font.color.rgb = COLOR_TEXT_LIGHT

# ==============================================================================
# SLIDE 2: 01 / PROBLEM STATEMENT & DATABASE RATIONALE
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
set_slide_background(slide2, COLOR_BG_LIGHT)
add_header(slide2, "01 / Problem Statement & Architectural Rationale", "Real-World Surplus Food Challenges vs Database Engineering Solutions")

# Left Column: The Problem (Red/Amber Cards)
col_w = Inches(5.6)
box_l = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), col_w, Inches(5.3))
box_l.fill.solid()
box_l.fill.fore_color.rgb = COLOR_CARD_BG
box_l.line.color.rgb = RGBColor(254, 202, 202)
box_l.line.width = Pt(1.5)
tf_l = box_l.text_frame
tf_l.word_wrap = True

p_lh = tf_l.paragraphs[0]
p_lh.text = "⚠️ THE LOGISTICS CHALLENGES"
p_lh.font.size = Pt(15)
p_lh.font.bold = True
p_lh.font.color.rgb = RGBColor(220, 38, 38)

problems = [
    ("Massive Edible Waste", "Hotels, banquets, and bakeries discard tons of safe cooked food daily due to absence of an automated real-time dispatch channel."),
    ("Critical Time Expiry Window", "Cooked food degrades within 2 to 6 hours. Traditional manual scheduling causes batches to spoil prior to relief delivery."),
    ("Concurrency & Double-Booking", "Multiple NGOs race to claim the same high-quantity batch simultaneously, causing operational collision without database locking."),
    ("Vehicle Capacity Violations", "Two-wheeler couriers assigned heavy bulk orders (e.g. 50 kg) cause delivery breakdowns and spillages.")
]
for p_title, p_desc in problems:
    p_t = tf_l.add_paragraph()
    p_t.text = f"• {p_title}: "
    p_t.font.bold = True
    p_t.font.size = Pt(12)
    p_t.font.color.rgb = COLOR_TEXT_DARK
    
    p_d = tf_l.add_paragraph()
    p_d.text = f"  {p_desc}"
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = COLOR_TEXT_MUTED

# Right Column: The Solution (Green/Blue Cards)
box_r = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.6), col_w, Inches(5.3))
box_r.fill.solid()
box_r.fill.fore_color.rgb = COLOR_CARD_BG
box_r.line.color.rgb = RGBColor(167, 243, 208)
box_r.line.width = Pt(1.5)
tf_r = box_r.text_frame
tf_r.word_wrap = True

p_rh = tf_r.paragraphs[0]
p_rh.text = "🛡️ MYSQL 8.0 DATABASE SOLUTIONS"
p_rh.font.size = Pt(15)
p_rh.font.bold = True
p_rh.font.color.rgb = RGBColor(5, 150, 105)

solutions = [
    ("ACID Row-Level Locking (FOR UPDATE)", "Stored procedure locks batch rows during claim initiation, eliminating double-booking and concurrency race conditions."),
    ("Dynamic Shelf-Life Views", "Relational View 'vw_live_rescue_feed' computes real-time minutes remaining using TIMESTAMPDIFF without redundant state storage."),
    ("Physical Constraint Enforcement (SQLSTATE '45000')", "Database blocks dispatch if batch weight exceeds courier's vehicle capacity (max_capacity_kg), raising custom SQL errors."),
    ("Automated Event-Driven Triggers", "Triggers synchronize batch states to DELIVERED, compute CO2 offset formulas (weight * 2.50), and maintain immutable audit logs.")
]
for s_title, s_desc in solutions:
    s_t = tf_r.add_paragraph()
    s_t.text = f"✔ {s_title}: "
    s_t.font.bold = True
    s_t.font.size = Pt(12)
    s_t.font.color.rgb = COLOR_TEXT_DARK
    
    s_d = tf_r.add_paragraph()
    s_d.text = f"  {s_desc}"
    s_d.font.size = Pt(11)
    s_d.font.color.rgb = COLOR_TEXT_MUTED

# ==============================================================================
# SLIDE 3: 02 / CORRECTED ENTITY-RELATIONSHIP DIAGRAM (CHEN NOTATION)
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
set_slide_background(slide3, COLOR_BG_LIGHT)
add_header(slide3, "02 / Entity-Relationship Architecture", "Chen Notation Conceptual Model (Corrected with Key Attributes & Cardinalities)")

# Entities & Relationships Canvas Layout
# Top Callout Box: Chen Rules Explanation
rule_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.73), Inches(0.65))
rule_box.fill.solid()
rule_box.fill.fore_color.rgb = RGBColor(238, 242, 255)
rule_box.line.color.rgb = RGBColor(199, 210, 254)
tf_rb = rule_box.text_frame
tf_rb.word_wrap = True
p_rb = tf_rb.paragraphs[0]
p_rb.text = "💡 ACADEMIC CHEN NOTATION RULES ENFORCED:"
p_rb.font.bold = True
p_rb.font.size = Pt(11)
p_rb.font.color.rgb = COLOR_PRIMARY

p_rb2 = tf_rb.add_paragraph()
p_rb2.text = "1. Primary Keys are strictly underlined. 2. Foreign keys are NOT drawn as attribute ovals (represented via relationships). 3. Cardinalities (1:1, 1:N) clearly marked."
p_rb2.font.size = Pt(10)
p_rb2.font.color.rgb = COLOR_TEXT_DARK

# Entity Visual Representation Blocks
entities_chen = [
    ("USERS", "user_id (PK)\nfull_name, email\nrole, phone, zone\ncreated_at", Inches(0.8), Inches(2.4), Inches(2.6), Inches(2.1), COLOR_PRIMARY),
    ("VOLUNTEER_PROFILES", "volunteer_id (PK/FK)\nvehicle_type\nvehicle_reg_no\nmax_capacity_kg\navailability_status", Inches(4.7), Inches(2.4), Inches(2.7), Inches(2.1), COLOR_SECONDARY),
    ("IMPACT_STATS", "ngo_id (PK/FK)\nngo_reg_number\ndaily_meal_capacity\ntotal_meals_saved\nco2_prevented_kg", Inches(8.7), Inches(2.4), Inches(2.7), Inches(2.1), COLOR_SECONDARY),
    ("FOOD_BATCHES", "batch_id (PK)\ntitle, food_type\nquantity_meals\nweight_kg, zone\nprepared_at, best_before", Inches(0.8), Inches(4.9), Inches(2.6), Inches(2.2), COLOR_PRIMARY),
    ("CLAIMS", "claim_id (PK)\npickup_otp\ndelivery_otp\nrating, claimed_at\nstatus", Inches(4.7), Inches(4.9), Inches(2.7), Inches(2.2), COLOR_ACCENT),
    ("AUDIT_LOGS", "log_id (PK)\nevent_type\nold_status, new_status\ndescription\nlogged_at", Inches(8.7), Inches(4.9), Inches(2.7), Inches(2.2), RGBColor(100, 116, 139))
]

for name, attrs, ex, ey, ew, eh, border_col in entities_chen:
    e_shape = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, ex, ey, ew, eh)
    e_shape.fill.solid()
    e_shape.fill.fore_color.rgb = COLOR_CARD_BG
    e_shape.line.color.rgb = border_col
    e_shape.line.width = Pt(2.5)
    
    tf_e = e_shape.text_frame
    tf_e.word_wrap = True
    p_en = tf_e.paragraphs[0]
    p_en.text = name
    p_en.font.bold = True
    p_en.font.size = Pt(13)
    p_en.font.color.rgb = border_col
    
    p_at = tf_e.add_paragraph()
    p_at.text = attrs
    p_at.font.size = Pt(10)
    p_at.font.color.rgb = COLOR_TEXT_DARK

# Relationship Label Badges (Center Connectors)
rel_badges = [
    ("HAS_PROFILE (1:1)", Inches(3.5), Inches(3.1)),
    ("TRACKS_IMPACT (1:1)", Inches(7.5), Inches(3.1)),
    ("DONATES (1:N)", Inches(1.3), Inches(4.55)),
    ("CLAIMS_BATCH (1:1 UNIQUE)", Inches(3.45), Inches(5.8)),
    ("DELIVERS (1:N)", Inches(5.3), Inches(4.55)),
    ("GENERATES (1:N)", Inches(7.5), Inches(5.8))
]

for r_text, rx, ry in rel_badges:
    r_shape = slide3.shapes.add_shape(MSO_SHAPE.DIAMOND, rx, ry, Inches(1.2), Inches(0.65))
    r_shape.fill.solid()
    r_shape.fill.fore_color.rgb = RGBColor(220, 252, 231)
    r_shape.line.color.rgb = RGBColor(34, 197, 94)
    r_shape.line.width = Pt(1)
    tf_r = r_shape.text_frame
    p_rt = tf_r.paragraphs[0]
    p_rt.text = r_text
    p_rt.font.size = Pt(7.5)
    p_rt.font.bold = True
    p_rt.alignment = PP_ALIGN.CENTER
    p_rt.font.color.rgb = RGBColor(20, 83, 45)

# ==============================================================================
# SLIDE 4: 03 / DATABASE RELATIONSHIPS & 3NF NORMALIZATION
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
set_slide_background(slide4, COLOR_BG_LIGHT)
add_header(slide4, "03 / Relational Schema & 3NF Normalization", "Strict Relational Modeling: Cardinalities, Foreign Key Policies & Normal Forms")

# 4 Key Relationship Cards
rel_cards = [
    ("1. USERS & SUBTYPES (1 : 1 Specialization)",
     "• volunteer_profiles and impact_stats model 1:1 specialization hierarchy.\n• PKs (volunteer_id, ngo_id) are simultaneously Foreign Keys to users.user_id.\n• Avoids sparse tables full of NULL columns for role-specific attributes.\n• Referential Integrity: ON DELETE CASCADE."),

    ("2. DONOR TO FOOD BATCHES (1 : N Supply)",
     "• A single donor posts multiple food batches over time.\n• Foreign Key: food_batches.donor_id -> users.user_id.\n• Indexed on (zone, status) for high-speed regional geospatial filtering.\n• Referential Integrity: ON DELETE CASCADE."),

    ("3. FOOD BATCHES TO CLAIMS (1 : 1 Physical Constraint)",
     "• Anti-Double Booking: Enforced by UNIQUE(batch_id) on claims table.\n• Once a batch is claimed, no second claim record can exist for that batch.\n• Links NGO, Volunteer Courier, and Donor Batch atomically.\n• Referential Integrity: ON DELETE CASCADE."),

    ("4. AUDIT LEDGER LOGGING (1 : N Event History)",
     "• Trigger-populated table recording BATCH_CREATED and DELIVERY_COMPLETED.\n• Foreign Keys: batch_id -> food_batches.batch_id, actor_user_id -> users.user_id.\n• Critical DBMS Rule: ON DELETE SET NULL guarantees historical logs survive even if a batch or user is deleted.")
]

card_w = Inches(5.6)
card_h = Inches(2.2)

for i, (title, content) in enumerate(rel_cards):
    gx = Inches(0.8) + (i % 2) * (card_w + Inches(0.53))
    gy = Inches(1.6) + (i // 2) * (card_h + Inches(0.3))
    
    c_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, gx, gy, card_w, card_h)
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = COLOR_CARD_BG
    c_box.line.color.rgb = COLOR_PRIMARY if i % 2 == 0 else COLOR_SECONDARY
    c_box.line.width = Pt(1.5)
    
    tf_c = c_box.text_frame
    tf_c.word_wrap = True
    p_t = tf_c.paragraphs[0]
    p_t.text = title
    p_t.font.bold = True
    p_t.font.size = Pt(13)
    p_t.font.color.rgb = COLOR_PRIMARY if i % 2 == 0 else COLOR_SECONDARY
    
    p_body = tf_c.add_paragraph()
    p_body.text = content
    p_body.font.size = Pt(11)
    p_body.font.color.rgb = COLOR_TEXT_DARK

# Bottom 3NF Justification Bar
nf_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.5), Inches(11.73), Inches(0.7))
nf_box.fill.solid()
nf_box.fill.fore_color.rgb = RGBColor(241, 245, 249)
nf_box.line.color.rgb = COLOR_CARD_BORDER
tf_nf = nf_box.text_frame
p_nf = tf_nf.paragraphs[0]
p_nf.text = "🏛️ 3NF NORMALIZATION PROOF:  1NF (Atomic Attributes, No Multi-valued fields) | 2NF (Full Functional Dependency on entire PK) | 3NF (Zero Transitive Dependencies; Donor & NGO contact details reside exclusively in USERS)."
p_nf.font.size = Pt(10.5)
p_nf.font.bold = True
p_nf.font.color.rgb = COLOR_TEXT_DARK

# ==============================================================================
# SLIDE 5: 04 / TABLES, FIELDS & DATABASE CONSTRAINTS (FIXED TABLE)
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
set_slide_background(slide5, COLOR_BG_LIGHT)
add_header(slide5, "04 / Physical Database Specification", "Complete Table Definitions, Primary/Foreign Keys, and Integrity Constraints")

# Create Presentation Table
rows = 7
cols = 5
table_shape = slide5.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(11.73), Inches(5.5))
table = table_shape.table

# Set Column Widths
table.columns[0].width = Inches(1.9)  # Table Name
table.columns[1].width = Inches(1.7)  # Primary Key
table.columns[2].width = Inches(2.2)  # Foreign Keys
table.columns[3].width = Inches(2.4)  # Key Fields
table.columns[4].width = Inches(3.53) # Constraints & Business Rules

headers = ["Table Name", "Primary Key (PK)", "Foreign Keys (FK)", "Key Attributes", "Database Constraints & Rules"]
for idx, text in enumerate(headers):
    cell = table.cell(0, idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_HEADER_BG
    p = cell.text_frame.paragraphs[0]
    p.text = text
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_LIGHT
    p.alignment = PP_ALIGN.CENTER

table_data = [
    ("USERS", "user_id (Auto-Inc)", "None", "full_name, email, role, phone, zone", "• UNIQUE(email)\n• ENUM('DONOR','NGO','VOLUNTEER','ADMIN')\n• Composite Index: (role, zone)"),
    ("VOLUNTEER_PROFILES", "volunteer_id", "volunteer_id -> users.user_id\n(ON DELETE CASCADE)", "vehicle_type, vehicle_reg_no, max_capacity_kg, status", "• UNIQUE(vehicle_reg_no)\n• CHECK(max_capacity_kg > 0)\n• 1:1 Specialization Subtype"),
    ("IMPACT_STATS", "ngo_id", "ngo_id -> users.user_id\n(ON DELETE CASCADE)", "ngo_reg_number, daily_meal_cap, total_meals, co2_prevented", "• UNIQUE(ngo_reg_number)\n• CHECK(daily_meal_capacity > 0)\n• Formula: CO2 = weight_kg * 2.50"),
    ("FOOD_BATCHES", "batch_id (Auto-Inc)", "donor_id -> users.user_id\n(ON DELETE CASCADE)", "title, food_type, meals, weight_kg, prepared_at, best_before", "• CHECK(quantity_meals > 0)\n• CHECK(weight_kg > 0)\n• CHECK(best_before > prepared_at)\n• Index: (zone, status)"),
    ("CLAIMS", "claim_id (Auto-Inc)", "batch_id -> food_batches\nngo_id -> users.user_id\nvolunteer_id -> users.user_id", "pickup_otp, delivery_otp, status, rating, claimed_at", "• UNIQUE(batch_id) [Anti-Double Booking]\n• CHECK(rating BETWEEN 1 AND 5)\n• ON DELETE CASCADE (on batch)"),
    ("AUDIT_LOGS", "log_id (Auto-Inc)", "batch_id -> food_batches\nactor_user_id -> users.user_id", "event_type, old_status, new_status, description, logged_at", "• ON DELETE SET NULL [Preserves legal audit trail even if batch/user is deleted]\n• Auto-inserted by MySQL Triggers")
]

for row_idx, data in enumerate(table_data, start=1):
    for col_idx, text in enumerate(data):
        cell = table.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD_BG if row_idx % 2 == 1 else RGBColor(241, 245, 249)
        p = cell.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_DARK
        if col_idx == 0:
            p.font.bold = True
            p.font.color.rgb = COLOR_PRIMARY

# ==============================================================================
# SLIDE 6: 05 / 3-TIER SYSTEM ARCHITECTURE & SQL EXECUTION FLOW
# ==============================================================================
slide6 = prs.slides.add_slide(blank_layout)
set_slide_background(slide6, COLOR_BG_LIGHT)
add_header(slide6, "05 / System Architecture & Execution Flow", "End-to-End Pipeline: Web Frontend to Python Flask and MySQL 8.0 Engine")

# 3 Architecture Cards (Horizontal Flow)
arch_w = Inches(3.64)
arch_h = Inches(4.8)
arch_y = Inches(1.6)

layers = [
    ("TIER 1: PRESENTATION LAYER",
     "Bootstrap 5 + Vanilla JavaScript",
     RGBColor(59, 130, 246),
     [
         ("Responsive Dashboard", "Real-time impact KPI counters (Meals, Weight, CO2 prevented)"),
         ("Live Surplus Feed", "Dynamic cards with real-time countdown timer badges"),
         ("Interactive Claim Modal", "Tests vehicle capacity by selecting courier and batch"),
         ("Active Dispatches", "4-Table JOIN showing OTPs and 'Confirm Delivery' action"),
         ("SQL Terminal Console", "Live audit ledger output populated by database triggers")
     ]),

    ("TIER 2: APPLICATION CONTROLLER",
     "Python Flask (Strictly Raw SQL)",
     RGBColor(16, 185, 129),
     [
         ("No ORM (Academic Rule)", "Uses pure mysql.connector for 100% transparent SQL logic"),
         ("Explicit Transactions", "Manual conn.commit() & conn.rollback() with autocommit=False"),
         ("Parameterized Queries", "Protects against SQL Injection using %s placeholders"),
         ("Cloud SSL Integration", "Connects securely to remote cloud database (TiDB/Render)"),
         ("Procedural Invocation", "Calls sp_claim_food_batch & handles SIGNAL SQLSTATE '45000'")
     ]),

    ("TIER 3: DATABASE ENGINE",
     "MySQL 8.0 / TiDB Serverless",
     RGBColor(245, 158, 11),
     [
         ("ACID Row Locks", "SELECT ... FOR UPDATE prevents race conditions on claims"),
         ("Database Triggers", "trg_after_claim_completed auto-updates stats and logs"),
         ("Relational Views", "vw_live_rescue_feed computes TIMESTAMPDIFF dynamically"),
         ("Check Constraints", "Enforces positive weights, meals, and valid shelf-life"),
         ("Information Schema", "Exposes constraints and metadata live to the examiner")
     ])
]

for idx, (title, sub, col, items) in enumerate(layers):
    ax = Inches(0.8) + idx * (arch_w + Inches(0.4))
    a_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, ax, arch_y, arch_w, arch_h)
    a_box.fill.solid()
    a_box.fill.fore_color.rgb = COLOR_CARD_BG
    a_box.line.color.rgb = col
    a_box.line.width = Pt(2)
    
    tf_a = a_box.text_frame
    tf_a.word_wrap = True
    
    p_at = tf_a.paragraphs[0]
    p_at.text = title
    p_at.font.bold = True
    p_at.font.size = Pt(13)
    p_at.font.color.rgb = col
    
    p_as = tf_a.add_paragraph()
    p_as.text = sub
    p_as.font.size = Pt(11)
    p_as.font.italic = True
    p_as.font.color.rgb = COLOR_TEXT_MUTED
    
    for item_h, item_b in items:
        p_ih = tf_a.add_paragraph()
        p_ih.text = f"• {item_h}: "
        p_ih.font.bold = True
        p_ih.font.size = Pt(10)
        p_ih.font.color.rgb = COLOR_TEXT_DARK
        
        p_ib = tf_a.add_paragraph()
        p_ib.text = f"  {item_b}"
        p_ib.font.size = Pt(9.5)
        p_ib.font.color.rgb = COLOR_TEXT_MUTED

# Bottom Flow Indicator
flow_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.55), Inches(11.73), Inches(0.6))
flow_box.fill.solid()
flow_box.fill.fore_color.rgb = RGBColor(241, 245, 249)
flow_box.line.color.rgb = COLOR_CARD_BORDER
tf_fl = flow_box.text_frame
p_fl = tf_fl.paragraphs[0]
p_fl.text = "🔄 DATA FLOW: Browser Action (REST JSON) ➔ Flask Route Handler ➔ mysql-connector-python ➔ MySQL Engine (Locks, Constraints, Triggers) ➔ JSON Response ➔ Dynamic DOM Update"
p_fl.font.size = Pt(10)
p_fl.font.bold = True
p_fl.font.color.rgb = COLOR_PRIMARY

# ==============================================================================
# SLIDE 7: 06 / LIVE VIVA DEMONSTRATION & TEST CASES
# ==============================================================================
slide7 = prs.slides.add_slide(blank_layout)
set_slide_background(slide7, COLOR_BG_LIGHT)
add_header(slide7, "06 / Live Viva Evaluation Guide", "4 Compelling Database Demonstrations to Show Evaluators Live in the UI")

demo_cases = [
    ("TEST 1: VEHICLE CAPACITY CONSTRAINT (SQLSTATE '45000')",
     "• What to do: Click 'Claim' on Batch #2 (Weight: 48.0 kg) and assign Volunteer 'Rahul Verma' (Bike, Max Cap: 15.0 kg).\n• Database Behavior: MySQL blocks transaction and triggers SIGNAL SQLSTATE '45000'.\n• Examiner Impact: UI displays exact SQL error message: 'CAPACITY_EXCEEDED: Volunteer vehicle cannot carry batch weight'. Proves real business rule enforcement!"),

    ("TEST 2: CONCURRENCY PROTECTION & OTPs (SELECT ... FOR UPDATE)",
     "• What to do: Assign Batch #1 (12.5 kg) to Volunteer 'Rahul Verma' (15.0 kg capacity).\n• Database Behavior: Stored procedure locks the batch row, generates 4-digit pickup & delivery OTPs, sets batch status to CLAIMED, and sets courier to BUSY.\n• Examiner Impact: Demonstrates ACID isolation; prevents race conditions."),

    ("TEST 3: AUTOMATED TRIGGER 2 (CO2 CALCULATION & STATE SYNC)",
     "• What to do: Scroll to 'Active Dispatches' and click 'Confirm Delivery'.\n• Database Behavior: trg_after_claim_completed updates batch to DELIVERED, releases courier to ONLINE, updates impact_stats, computes CO2 (weight * 2.50), and logs to audit_logs.\n• Examiner Impact: Top KPI cards increment immediately without page reload!"),

    ("TEST 4: INFORMATION_SCHEMA INTROSPECTION MODAL",
     "• What to do: Click 'View Active Constraints' in the top navigation bar.\n• Database Behavior: Queries INFORMATION_SCHEMA.TABLE_CONSTRAINTS, TRIGGERS, and ROUTINES live.\n• Examiner Impact: Shows examiners all 18 physical database constraints, foreign keys, triggers, and procedures active inside the running MySQL server!")
]

card_w = Inches(5.6)
card_h = Inches(2.3)

for i, (title, content) in enumerate(demo_cases):
    gx = Inches(0.8) + (i % 2) * (card_w + Inches(0.53))
    gy = Inches(1.6) + (i // 2) * (card_h + Inches(0.3))
    
    c_box = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, gx, gy, card_w, card_h)
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = COLOR_CARD_BG
    c_box.line.color.rgb = RGBColor(16, 185, 129) if i % 2 == 1 else RGBColor(37, 99, 235)
    c_box.line.width = Pt(1.5)
    
    tf_c = c_box.text_frame
    tf_c.word_wrap = True
    p_t = tf_c.paragraphs[0]
    p_t.text = title
    p_t.font.bold = True
    p_t.font.size = Pt(12)
    p_t.font.color.rgb = RGBColor(16, 185, 129) if i % 2 == 1 else RGBColor(37, 99, 235)
    
    p_body = tf_c.add_paragraph()
    p_body.text = content
    p_body.font.size = Pt(10.5)
    p_body.font.color.rgb = COLOR_TEXT_DARK

# Save presentation to project directory and artifacts
output_path_proj = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'FoodRescue_Network_Stage1_Presentation.pptx'))
prs.save(output_path_proj)
print(f"✅ Presentation successfully saved to: {output_path_proj}")
