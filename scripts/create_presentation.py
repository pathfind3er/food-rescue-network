"""
FoodRescue Network — Exact 5-Page Stage 1 Presentation Generator
Recreates and enhances the exact 5 pages from the user's presentation slide:
Page 1: Problem Statement & Database Used
Page 2: 02 / ENTITY-RELATIONSHIP DIAGRAM (Complete ER Diagram in Chen Notation)
Page 3: 03 / DATABASE RELATIONSHIPS (How Our Entities Connect)
Page 4: 04 / TABLES & RULES (Our 6 Tables, Fields & Database Rules)
Page 5: 05 / SYSTEM FLOW (How Frontend Connects to MySQL)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Theme Colors matching the user's slide design
COLOR_BG_WHITE = RGBColor(255, 255, 255)
COLOR_TEXT_BLACK = RGBColor(20, 20, 20)
COLOR_TEXT_GRAY = RGBColor(100, 116, 139)
COLOR_BORDER_GRAY = RGBColor(226, 232, 240)

# Accent Colors
COLOR_ORANGE = RGBColor(217, 119, 6)      # Problem orange
COLOR_ORANGE_BG = RGBColor(254, 243, 199)
COLOR_GREEN = RGBColor(5, 150, 105)       # MySQL green
COLOR_GREEN_BG = RGBColor(209, 250, 229)
COLOR_BLUE_ENTITY = RGBColor(189, 220, 249) # Chen entity light blue
COLOR_BLUE_BORDER = RGBColor(30, 41, 59)
COLOR_YELLOW_ATTR = RGBColor(254, 240, 138) # Chen attribute soft yellow
COLOR_YELLOW_BORDER = RGBColor(161, 98, 7)
COLOR_GREEN_REL = RGBColor(187, 247, 208)   # Chen relationship light green
COLOR_GREEN_REL_BORDER = RGBColor(22, 101, 52)
COLOR_CARD_BORDER = RGBColor(203, 213, 225)

def set_slide_background(slide):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = COLOR_BG_WHITE
    bg_shape.line.fill.background()
    return bg_shape

def add_slide_header(slide, page_num_title, subtitle=""):
    # Category Tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = "FOODRESCUE NETWORK • STAGE 1 PRESENTATION"
    p_tag.font.size = Pt(10.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = RGBColor(148, 163, 184)

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = page_num_title
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_BLACK

    # Subtitle (if present)
    if subtitle:
        p_sub = tf_title.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(13)
        p_sub.font.bold = False
        p_sub.font.color.rgb = COLOR_TEXT_GRAY

# ==============================================================================
# PAGE 1: Problem Statement & Database Used
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
set_slide_background(slide1)
add_slide_header(slide1, "Problem Statement & Database Used")

# Left Box: The Problem
card_w = Inches(5.6)
card_h = Inches(5.4)

card_left = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), card_w, card_h)
card_left.fill.solid()
card_left.fill.fore_color.rgb = RGBColor(255, 255, 255)
card_left.line.color.rgb = RGBColor(253, 230, 138)
card_left.line.width = Pt(2)
tf_l = card_left.text_frame
tf_l.word_wrap = True

# Problem Header Badge
badge_l = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(1.8), Inches(5.0), Inches(0.75))
badge_l.fill.solid()
badge_l.fill.fore_color.rgb = COLOR_ORANGE_BG
badge_l.line.color.rgb = COLOR_ORANGE
badge_l.line.width = Pt(1.5)
tf_bl = badge_l.text_frame
p_bl = tf_bl.paragraphs[0]
p_bl.text = "⚠️  The Problem"
p_bl.font.size = Pt(18)
p_bl.font.bold = True
p_bl.font.color.rgb = COLOR_ORANGE
p_bl.alignment = PP_ALIGN.CENTER

# Problem Points
problems = [
    ("Wasted Food", "Hotels throw away good food while people go hungry."),
    ("Short Time", "Cooked food spoils within 2 to 4 hours without immediate dispatch."),
    ("Double Booking", "Two NGOs might claim the exact same food batch at the same time.")
]

for idx, (title, desc) in enumerate(problems):
    py = Inches(2.9) + idx * Inches(1.2)
    box_p = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), py, Inches(5.0), Inches(0.95))
    box_p.fill.solid()
    box_p.fill.fore_color.rgb = RGBColor(254, 252, 232)
    box_p.line.color.rgb = RGBColor(254, 240, 138)
    tf_p = box_p.text_frame
    tf_p.word_wrap = True
    
    p_t = tf_p.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(14)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TEXT_BLACK
    
    p_d = tf_p.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = COLOR_TEXT_GRAY

# Right Box: Database Used: MySQL 8.0
card_right = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.5), card_w, card_h)
card_right.fill.solid()
card_right.fill.fore_color.rgb = RGBColor(255, 255, 255)
card_right.line.color.rgb = RGBColor(167, 243, 208)
card_right.line.width = Pt(2)

# Database Header Badge
badge_r = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.8), Inches(5.0), Inches(0.75))
badge_r.fill.solid()
badge_r.fill.fore_color.rgb = COLOR_GREEN_BG
badge_r.line.color.rgb = COLOR_GREEN
badge_r.line.width = Pt(1.5)
tf_br = badge_r.text_frame
p_br = tf_br.paragraphs[0]
p_br.text = "🗄️  Database Used: MySQL 8.0"
p_br.font.size = Pt(18)
p_br.font.bold = True
p_br.font.color.rgb = COLOR_GREEN
p_br.alignment = PP_ALIGN.CENTER

# Database Solutions
solutions = [
    ("Safe Locking", "Stops two NGOs from claiming the same food using SELECT ... FOR UPDATE row locks."),
    ("Auto Updates", "Saves meal counts, releases couriers, and logs audit entries automatically using Triggers."),
    ("Clean Rules", "Checks that every data entry is valid (capacity > 0, expiry > prepared_at, rating 1 to 5).")
]

for idx, (title, desc) in enumerate(solutions):
    py = Inches(2.9) + idx * Inches(1.2)
    box_s = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), py, Inches(5.0), Inches(0.95))
    box_s.fill.solid()
    box_s.fill.fore_color.rgb = RGBColor(240, 253, 244)
    box_s.line.color.rgb = RGBColor(187, 247, 208)
    tf_s = box_s.text_frame
    tf_s.word_wrap = True
    
    s_t = tf_s.paragraphs[0]
    s_t.text = title
    s_t.font.size = Pt(14)
    s_t.font.bold = True
    s_t.font.color.rgb = COLOR_TEXT_BLACK
    
    s_d = tf_s.add_paragraph()
    s_d.text = desc
    s_d.font.size = Pt(12)
    s_d.font.color.rgb = COLOR_TEXT_GRAY

# ==============================================================================
# PAGE 2: 02 / ENTITY-RELATIONSHIP DIAGRAM (Complete ER Diagram in Chen Notation)
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
set_slide_background(slide2)
add_slide_header(slide2, "02 / ENTITY-RELATIONSHIP DIAGRAM", "Complete ER Diagram (Chen Notation) — Corrected & Fully Normalized")

# Entity Box Helper
def draw_chen_entity(slide, name, x, y, w=Inches(2.4), h=Inches(0.85)):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_BLUE_ENTITY
    shape.line.color.rgb = COLOR_BLUE_BORDER
    shape.line.width = Pt(2.5)
    tf = shape.text_frame
    p = tf.paragraphs[0]
    p.text = name
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_TEXT_BLACK
    p.alignment = PP_ALIGN.CENTER
    return shape

# Relationship Diamond Helper
def draw_chen_rel(slide, name, card_text, x, y, w=Inches(1.8), h=Inches(0.7)):
    shape = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_GREEN_REL
    shape.line.color.rgb = COLOR_GREEN_REL_BORDER
    shape.line.width = Pt(1.5)
    tf = shape.text_frame
    p = tf.paragraphs[0]
    p.text = name
    p.font.bold = True
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_GREEN_REL_BORDER
    p.alignment = PP_ALIGN.CENTER
    if card_text:
        p2 = tf.add_paragraph()
        p2.text = card_text
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = RGBColor(15, 23, 42)
        p2.alignment = PP_ALIGN.CENTER
    return shape

# Attribute Oval Helper
def draw_chen_attr(slide, name, x, y, is_pk=False, w=Inches(1.6), h=Inches(0.4)):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_YELLOW_ATTR
    shape.line.color.rgb = COLOR_YELLOW_BORDER
    shape.line.width = Pt(1)
    tf = shape.text_frame
    p = tf.paragraphs[0]
    p.text = name
    p.font.size = Pt(9)
    p.font.bold = is_pk
    p.font.underline = is_pk
    p.font.color.rgb = COLOR_TEXT_BLACK
    p.alignment = PP_ALIGN.CENTER
    return shape

# Page 2: Entities
draw_chen_entity(slide2, "USERS", Inches(2.2), Inches(2.3))
draw_chen_entity(slide2, "VOLUNTEER_PROFILES", Inches(8.8), Inches(2.3), Inches(2.7))
draw_chen_entity(slide2, "IMPACT_STATS", Inches(5.4), Inches(3.6), Inches(2.5))
draw_chen_entity(slide2, "FOOD_BATCHES", Inches(2.2), Inches(4.9))
draw_chen_entity(slide2, "CLAIMS", Inches(8.8), Inches(4.9), Inches(2.7))
draw_chen_entity(slide2, "AUDIT_LOGS", Inches(5.4), Inches(6.1), Inches(2.5))

# Page 2: Relationships (Diamonds)
draw_chen_rel(slide2, "HAS_PROFILE", "1 : 1", Inches(5.7), Inches(2.38))
draw_chen_rel(slide2, "TRACKS_IMPACT", "1 : 1", Inches(4.7), Inches(3.0))
draw_chen_rel(slide2, "DONATES", "1 : N", Inches(2.5), Inches(3.6))
draw_chen_rel(slide2, "CLAIMS_BATCH", "1 : 1 UNIQUE", Inches(5.7), Inches(4.98))
draw_chen_rel(slide2, "DELIVERS", "1 : N", Inches(9.25), Inches(3.6))
draw_chen_rel(slide2, "LOGS", "1 : N", Inches(5.7), Inches(5.0))

# Corrected Attributes (No duplicates! Proper PK underlines! Proper weight_kg!)
# USERS Attributes
draw_chen_attr(slide2, "user_id", Inches(0.4), Inches(2.0), is_pk=True)
draw_chen_attr(slide2, "name", Inches(0.4), Inches(2.5))
draw_chen_attr(slide2, "email", Inches(0.4), Inches(3.0))
draw_chen_attr(slide2, "role", Inches(2.1), Inches(1.6))
draw_chen_attr(slide2, "created_at", Inches(3.8), Inches(1.6))

# VOLUNTEER_PROFILES Attributes (Added max_capacity_kg, fixed typo!)
draw_chen_attr(slide2, "volunteer_id", Inches(8.0), Inches(1.6), is_pk=True)
draw_chen_attr(slide2, "vehicle_type", Inches(9.8), Inches(1.6))
draw_chen_attr(slide2, "max_capacity_kg", Inches(11.6), Inches(2.1))
draw_chen_attr(slide2, "availability_status", Inches(11.6), Inches(2.6))

# IMPACT_STATS Attributes
draw_chen_attr(slide2, "ngo_id", Inches(8.1), Inches(3.4), is_pk=True)
draw_chen_attr(slide2, "meals_rescued", Inches(8.1), Inches(3.9))
draw_chen_attr(slide2, "co2_saved", Inches(8.1), Inches(4.4))

# FOOD_BATCHES Attributes (Fixed weight_kg, added meals!)
draw_chen_attr(slide2, "batch_id", Inches(0.4), Inches(4.5), is_pk=True)
draw_chen_attr(slide2, "food_type", Inches(0.4), Inches(5.0))
draw_chen_attr(slide2, "weight_kg", Inches(0.4), Inches(5.5))
draw_chen_attr(slide2, "meals", Inches(2.0), Inches(6.0))
draw_chen_attr(slide2, "expiry_date", Inches(3.7), Inches(6.0))

# CLAIMS Attributes (Removed status from key, added OTPs)
draw_chen_attr(slide2, "claim_id", Inches(11.6), Inches(4.4), is_pk=True)
draw_chen_attr(slide2, "pickup_otp", Inches(11.6), Inches(4.9))
draw_chen_attr(slide2, "delivery_otp", Inches(11.6), Inches(5.4))
draw_chen_attr(slide2, "status", Inches(11.6), Inches(5.9))
draw_chen_attr(slide2, "claim_time", Inches(9.3), Inches(6.0))

# AUDIT_LOGS Attributes
draw_chen_attr(slide2, "log_id", Inches(3.6), Inches(6.3), is_pk=True)
draw_chen_attr(slide2, "action", Inches(8.1), Inches(6.1))
draw_chen_attr(slide2, "timestamp", Inches(8.1), Inches(6.6))

# ==============================================================================
# PAGE 3: 03 / DATABASE RELATIONSHIPS (How Our Entities Connect)
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
set_slide_background(slide3)
add_slide_header(slide3, "03 / DATABASE RELATIONSHIPS", "How Our Entities Connect — Structural Cardinality & Referential Integrity")

# Left Column: Overview Summary Diagram
box_diag = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.5), Inches(5.5))
box_diag.fill.solid()
box_diag.fill.fore_color.rgb = RGBColor(248, 250, 252)
box_diag.line.color.rgb = COLOR_CARD_BORDER
box_diag.line.width = Pt(1.5)

tf_bd = box_diag.text_frame
tf_bd.word_wrap = True
p_bd = tf_bd.paragraphs[0]
p_bd.text = "🔗 ENTITY RELATIONSHIP MAP"
p_bd.font.bold = True
p_bd.font.size = Pt(14)
p_bd.font.color.rgb = RGBColor(30, 41, 59)

# Mini Entity Nodes on Left
m_users = draw_chen_entity(slide3, "USERS", Inches(1.2), Inches(2.3), Inches(2.0), Inches(0.6))
m_vol = draw_chen_entity(slide3, "VOLUNTEERS", Inches(3.8), Inches(2.3), Inches(2.1), Inches(0.6))
m_imp = draw_chen_entity(slide3, "IMPACT_STATS", Inches(2.5), Inches(3.4), Inches(2.1), Inches(0.6))
m_batch = draw_chen_entity(slide3, "FOOD_BATCHES", Inches(1.2), Inches(4.5), Inches(2.0), Inches(0.6))
m_claim = draw_chen_entity(slide3, "CLAIMS", Inches(3.8), Inches(4.5), Inches(2.1), Inches(0.6))
m_log = draw_chen_entity(slide3, "AUDIT_LOGS", Inches(2.5), Inches(5.6), Inches(2.1), Inches(0.6))

# Right Column: 4 Relationship Cards matching user's slide
rel_cards = [
    ("USERS & Roles", "1 : N",
     "Stores Hotels, NGOs, and Riders using a role field.\nGeneralization entity holding common authentication and contact details."),

    ("PROFILES & IMPACT_STATS", "1 : 1",
     "Keeps rider vehicle info and NGO meal scores separate.\n1:1 Subtype Specialization eliminates sparse NULL columns."),

    ("FOOD_BATCHES & CLAIMS", "1 : 1",
     "One food batch can be claimed by only one NGO.\nEnforced physically by UNIQUE(batch_id) on claims table to stop double-booking."),

    ("AUDIT_LOGS", "1 : N",
     "Triggers auto-save a history log of every action.\nPreserved via ON DELETE SET NULL even if batch or user is deleted.")
]

for idx, (title, card_type, desc) in enumerate(rel_cards):
    cy = Inches(1.5) + idx * Inches(1.4)
    c_card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.7), cy, Inches(5.8), Inches(1.25))
    c_card.fill.solid()
    c_card.fill.fore_color.rgb = RGBColor(255, 255, 255)
    c_card.line.color.rgb = COLOR_CARD_BORDER
    c_card.line.width = Pt(1.5)
    
    tf_c = c_card.text_frame
    tf_c.word_wrap = True
    
    p_t = tf_c.paragraphs[0]
    p_t.text = f"{title}   "
    p_t.font.bold = True
    p_t.font.size = Pt(13)
    p_t.font.color.rgb = COLOR_TEXT_BLACK
    
    p_tag = tf_c.add_paragraph()
    p_tag.text = f"Cardinality: {card_type}"
    p_tag.font.bold = True
    p_tag.font.size = Pt(10.5)
    p_tag.font.color.rgb = COLOR_GREEN
    
    p_d = tf_c.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = COLOR_TEXT_GRAY

# ==============================================================================
# PAGE 4: 04 / TABLES & RULES (Our 6 Tables, Fields & Database Rules)
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
set_slide_background(slide4)
add_slide_header(slide4, "04 / TABLES & RULES", "Our 6 Tables, Fields & Database Rules — Exact Keys, Constraints & Integrities")

# Corrected Table with 4 Columns (Matching user's slide structure)
t_rows = 7
t_cols = 4
tbl_shape = slide4.shapes.add_table(t_rows, t_cols, Inches(0.8), Inches(1.5), Inches(11.73), Inches(5.5))
tbl = tbl_shape.table

tbl.columns[0].width = Inches(2.2)  # Table Name
tbl.columns[1].width = Inches(2.9)  # Main Keys
tbl.columns[2].width = Inches(3.2)  # Important Fields
tbl.columns[3].width = Inches(3.43) # Database Rules

t_headers = ["Table Name", "Main Keys", "Important Fields", "Database Rules"]
for idx, text in enumerate(t_headers):
    c = tbl.cell(0, idx)
    c.fill.solid()
    c.fill.fore_color.rgb = RGBColor(30, 41, 59)
    p = c.text_frame.paragraphs[0]
    p.text = text
    p.font.bold = True
    p.font.size = Pt(11.5)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

# Exact Corrected Data
t_data = [
    ("USERS",
     "PK: user_id",
     "name, email, role, phone, zone, created_at",
     "No duplicate email (UNIQUE), required fields NOT NULL, Composite Index (role, zone)"),

    ("VOLUNTEER_PROFILES",
     "PK: volunteer_id\nFK: user_id (ON DELETE CASCADE)",
     "vehicle_type, availability_status, max_capacity_kg, vehicle_reg_no",
     "Capacity > 0 (CHECK), auto-delete with user (CASCADE), Unique registration number"),

    ("IMPACT_STATS",
     "PK: ngo_id\nFK: user_id (ON DELETE CASCADE)",
     "ngo_reg_number, daily_meal_cap, meals_rescued, co2_saved",
     "No duplicate reg no (UNIQUE), capacity > 0 (CHECK), CO2 formula (weight * 2.50)"),

    ("FOOD_BATCHES",
     "PK: batch_id\nFK: donor_id (ON DELETE CASCADE)",
     "food_type, status, weight_kg, meals, prepared_at, expiry",
     "Meals > 0 (CHECK), expiry after prep time (CHECK best_before > prepared_at), Index (zone, status)"),

    ("CLAIMS",
     "PK: claim_id\nFK: batch_id, volunteer_id, ngo_id",
     "status, claim_time, pickup_otp, delivery_otp, rating",
     "One claim per batch (UNIQUE on batch_id), rating 1 to 5 (CHECK), CASCADE on batch delete"),

    ("AUDIT_LOGS",
     "PK: log_id\nFK: user_id, batch_id",
     "action, old_status, new_status, description, timestamp",
     "Keeps log even if batch is deleted (ON DELETE SET NULL), populated automatically by Triggers")
]

for r_idx, row_items in enumerate(t_data, start=1):
    for c_idx, cell_value in enumerate(row_items):
        cell = tbl.cell(r_idx, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if r_idx % 2 == 1 else RGBColor(248, 250, 252)
        p = cell.text_frame.paragraphs[0]
        p.text = cell_value
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_BLACK
        if c_idx == 0:
            p.font.bold = True
            p.font.color.rgb = RGBColor(2, 132, 199)

# ==============================================================================
# PAGE 5: 05 / SYSTEM FLOW (How Frontend Connects to MySQL)
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
set_slide_background(slide5)
add_slide_header(slide5, "05 / SYSTEM FLOW", "How Frontend Connects to MySQL — Clean 3-Tier Execution Pipeline")

# 3 Step Cards Horizontal
step_w = Inches(3.6)
step_h = Inches(4.5)
step_y = Inches(1.8)

steps = [
    ("1. Web Page (Frontend)",
     "💻 BROWSER CLIENT",
     RGBColor(2, 132, 199),
     RGBColor(224, 242, 254),
     "• HTML, Bootstrap 5 & JavaScript send button clicks to backend.\n\n• Displays real-time countdown timer badges from view.\n\n• Lets NGOs claim food batches with instant modal validation.\n\n• Real-time terminal displays trigger audit logs."),

    ("2. Python Flask (Backend)",
     "⚙️ APPLICATION SERVER",
     RGBColor(217, 119, 6),
     RGBColor(254, 243, 199),
     "• Uses MySQL Connector to send raw parameterized SQL commands.\n\n• Strictly No ORM: Explicit control over transactions and row locks.\n\n• Calls Stored Procedures (sp_claim_food_batch).\n\n• Catches custom SQLSTATE '45000' capacity error signals."),

    ("3. MySQL Database",
     "🗄️ DATABASE ENGINE",
     RGBColor(5, 150, 105),
     RGBColor(209, 250, 229),
     "• Runs SQL queries, saves data, and checks integrity rules.\n\n• Safe Row-Level Locking (SELECT ... FOR UPDATE) prevents double-booking.\n\n• Triggers auto-calculate CO2 offsets and update impact stats.\n\n• Enforces CHECK constraints (capacity > 0, expiry > prep).")
]

for idx, (title, badge_txt, b_color, bg_color, desc) in enumerate(steps):
    sx = Inches(0.8) + idx * (step_w + Inches(0.46))
    
    # Outer Card
    s_card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, step_y, step_w, step_h)
    s_card.fill.solid()
    s_card.fill.fore_color.rgb = RGBColor(255, 255, 255)
    s_card.line.color.rgb = b_color
    s_card.line.width = Pt(2)
    
    # Header Badge
    h_badge = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx + Inches(0.2), step_y + Inches(0.25), step_w - Inches(0.4), Inches(0.7))
    h_badge.fill.solid()
    h_badge.fill.fore_color.rgb = bg_color
    h_badge.line.color.rgb = b_color
    h_badge.line.width = Pt(1)
    tf_hb = h_badge.text_frame
    p_hb = tf_hb.paragraphs[0]
    p_hb.text = badge_txt
    p_hb.font.size = Pt(11)
    p_hb.font.bold = True
    p_hb.font.color.rgb = b_color
    p_hb.alignment = PP_ALIGN.CENTER
    
    p_hbt = tf_hb.add_paragraph()
    p_hbt.text = title
    p_hbt.font.size = Pt(13)
    p_hbt.font.bold = True
    p_hbt.font.color.rgb = COLOR_TEXT_BLACK
    p_hbt.alignment = PP_ALIGN.CENTER
    
    # Text Body
    tf_sc = s_card.text_frame
    tf_sc.word_wrap = True
    
    # Spacer
    p_sp = tf_sc.paragraphs[0]
    p_sp.text = "\n\n\n"
    
    p_desc = tf_sc.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_BLACK

# Arrows between steps
arrow1 = slide5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.55), Inches(3.8), Inches(0.32), Inches(0.4))
arrow1.fill.solid()
arrow1.fill.fore_color.rgb = COLOR_GREEN
arrow1.line.fill.background()

arrow2 = slide5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(8.6), Inches(3.8), Inches(0.32), Inches(0.4))
arrow2.fill.solid()
arrow2.fill.fore_color.rgb = COLOR_GREEN
arrow2.line.fill.background()

# Save PPTX
out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'FoodRescue_Network_Stage1_Presentation.pptx'))
prs.save(out_path)
print(f"✅ Exact 5-page presentation successfully saved to: {out_path}")
