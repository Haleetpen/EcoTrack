import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import jwt
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ==============================================================================
# 🗄️ SYSTEM CONFIGURATIONS & MASTER SECURITY LAYER
# ==============================================================================
JWT_SECRET = "ecotrack_sovereign_climate_secret_2026"

# Initialize Persistent State Memory Engine
if "database" not in st.session_state:
    st.session_state.database = pd.DataFrame([
        {
            "id": 1001, "timestamp": "2026-03-12 09:15:00", "school": "Katsina Science Academy",
            "lga": "Katsina", "species": "Neem (Azadirachta indica)", "planted": 250, "survived": 230,
            "age_years": 3, "lat": 12.9894, "lon": 7.6031, "status": "Approved", "auditor": "Mal. Ibrahim",
            "photo_verified": True, "carbon_kg": 250 * 1.5 * (1 + 3 * 0.08) * 3.67
        },
        {
            "id": 1002, "timestamp": "2026-04-01 14:22:00", "school": "Daura Eco-Club High",
            "lga": "Daura", "species": "Gum Arabic (Acacia senegal)", "planted": 180, "survived": 165,
            "age_years": 2, "lat": 13.0333, "lon": 8.3167, "status": "Approved", "auditor": "Mal. Ibrahim",
            "photo_verified": True, "carbon_kg": 180 * 1.2 * (1 + 2 * 0.08) * 3.67
        },
        {
            "id": 1003, "timestamp": "2026-05-18 11:04:00", "school": "Funtua Environmental School",
            "lga": "Funtua", "species": "Baobab (Adansonia digitata)", "planted": 300, "survived": 110,
            "age_years": 1, "lat": 11.5233, "lon": 7.3094, "status": "Pending", "auditor": "Unassigned",
            "photo_verified": False, "carbon_kg": 110 * 2.0 * (1 + 1 * 0.08) * 3.67
        },
        {
            "id": 1004, "timestamp": "2026-06-02 16:45:00", "school": "Mani Forestry Secondary",
            "lga": "Mani", "species": "Eucalyptus (Eucalyptus globulus)", "planted": 400, "survived": 395,
            "age_years": 4, "lat": 12.8611, "lon": 7.8722, "status": "Flagged", "auditor": "Hajiya Amina",
            "photo_verified": True, "carbon_kg": 395 * 1.0 * (1 + 4 * 0.08) * 3.67
        }
    ])

SPECIES_REGISTRY = {
    "Neem (Azadirachta indica)": {"factor": 1.5, "zone": "Arid/Sahel", "water_req": "Low"},
    "Gum Arabic (Acacia senegal)": {"factor": 1.2, "zone": "Sahel/Savannah", "water_req": "Very Low"},
    "Baobab (Adansonia digitata)": {"factor": 2.0, "zone": "Savannah", "water_req": "Low"},
    "Eucalyptus (Eucalyptus globulus)": {"factor": 1.0, "zone": "Varied", "water_req": "High"},
    "Mahogany (Khaya senegalensis)": {"factor": 2.5, "zone": "Sub-savannah", "water_req": "Medium"}
}

ECO_CLUB_SYLLABUS = {
    "Week 1-4": "Nursery Preparation, Soil Mix Dynamics & Seed Sowing Operations.",
    "Week 5-8": "Micro-irrigation Strategies, Mulching & Arid Survival Safeguards.",
    "Week 9-12": "Biometric Logging, Height/Canopy Tracking & Carbon Audit Simulators."
}


# ==============================================================================
# 🧠 CORE PROCESSING ENGINES
# ==============================================================================

def validate_field_telemetry(planted, survived, lat, lon):
    if survived > planted:
        return False, "Validation Error: Survived tree count cannot be higher than planted tree count."
    if not (11.0 <= lat <= 13.5) or not (6.5 <= lon <= 9.0):
        return False, "Validation Error: Input GPS coordinates fall outside monitored regional boundaries."
    return True, "Telemetry verified against structural constraints."


def compute_carbon_sequestration(species, survived, age):
    factor = SPECIES_REGISTRY.get(species, {"factor": 1.0})["factor"]
    age_multiplier = 1 + (age * 0.08)
    carbon_absorbed = factor * survived * age_multiplier * 3.67
    return round(carbon_absorbed, 2)


def calculate_tradable_credits(carbon_kg):
    return round(carbon_kg / 150.0, 4)


def run_survival_prediction_ai(planted, rainfall, soil, care):
    base_probability = (0.4 * rainfall) + (0.3 * soil) + (0.3 * care)
    survival_rate = min(max(base_probability, 0.08), 0.97)
    predicted_yield = int(planted * survival_rate)
    return {"rate": round(survival_rate * 100, 2), "yield": predicted_yield}


def run_fraud_auditor_ai(planted, survived):
    if planted == 0: return "Error"
    ratio = survived / planted
    if ratio > 0.96:
        return "⚠️ ANOMALY DETECTED: Suspiciously high survival rate. Flagged for manual audit verification."
    if ratio < 0.12:
        return "⚠️ WARNING: Abnormally low survival rate. Potential drought stress or intervention required."
    return "✅ VERIFIED: Data matches standard ecological patterns."


def issue_access_jwt(username, role):
    payload = {
        "sub": username, "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def parse_access_jwt(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return None


# ==============================================================================
# 📄 AUTOMATED REPORT GENERATOR
# ==============================================================================
def compile_sovereign_pdf(metrics, dataframe):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=22,
                                 textColor=colors.HexColor('#1E4620'), spaceAfter=15)
    section_style = ParagraphStyle('SecTitle', parent=styles['Heading2'], fontSize=14,
                                   textColor=colors.HexColor('#2E6930'), spaceBefore=12, spaceAfter=8)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=6)

    story.append(Paragraph("EcoTrack Climate Impact Report", title_style))
    story.append(Paragraph(
        f"<b>Platform State:</b> Official Compliance Matrix | <b>Generated:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        body_style))
    story.append(Spacer(1, 15))

    summary_data = [
        ["Total Planted Assets", "Verified Survival Volume", "Aggregate Carbon Offset", "Minted Carbon Credits"],
        [f"{metrics['planted']}", f"{metrics['survived']}", f"{metrics['carbon']} kg", f"{metrics['credits']} VCU"]
    ]
    t_summary = Table(summary_data, colWidths=[130, 130, 130, 130])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E6930')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F4F9F4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#1E4620'))
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Project Registry Audit Log", section_style))
    table_content = [["ID", "School / Institution", "LGA", "Species", "Planted", "Survived", "Status"]]
    for _, r in dataframe.iterrows():
        table_content.append(
            [str(r['id']), r['school'], r['lga'], r['species'].split(" (")[0], str(r['planted']), str(r['survived']),
             r['status']])

    t_detail = Table(table_content, colWidths=[35, 140, 70, 95, 55, 55, 60])
    t_detail.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A5D4E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBF9')])
    ]))
    story.append(t_detail)

    doc.build(story)
    buffer.seek(0)
    return buffer


# ==============================================================================
# 💻 STREAMLIT UNIFIED USER INTERFACE
# ==============================================================================
st.set_page_config(page_title="EcoTrack Platform", layout="wide", page_icon="🌱")

if "session_token" not in st.session_state:
    st.session_state.session_token = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "role" not in st.session_state:
    st.session_state.role = "Guest"

# Sidebar Branding
st.sidebar.image(
    "https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/000000/external-ecology-ecology-flatart-icons-flat-flatarticons-2.png",
    width=70)
st.sidebar.title("EcoTrack Control Hub")
st.sidebar.caption("System Status: Active")

# Authentication Control
st.sidebar.markdown("---")
st.sidebar.subheader("🔐 Account Login")
if st.session_state.session_token is None:
    user_input = st.sidebar.text_input("Username / Identity Handle", value="katsina_officer")
    role_input = st.sidebar.selectbox("Access Level Role", ["School Administrator", "State Auditor", "NGO Verifier"])
    if st.sidebar.button("Establish Secure Session"):
        st.session_state.session_token = issue_access_jwt(user_input, role_input)
        st.session_state.current_user = user_input
        st.session_state.role = role_input
        st.rerun()
else:
    st.sidebar.success(f"User: {st.session_state.current_user}")
    st.sidebar.info(f"Role Profile: {st.session_state.role}")
    if st.sidebar.button("Log Out"):
        st.session_state.session_token = None
        st.session_state.current_user = None
        st.session_state.role = "Guest"
        st.rerun()

# User Navigation Map
navigation_node = st.sidebar.radio(
    "Platform Navigation Links",
    ["1. Central Registry Dashboard", "2. Report Tree Plantings", "3. Predictive Ecological AI",
     "4. Geospatial Map Layers", "5. Approvals & Audit Queue", "6. Carbon Valuation Ledger"]
)

# Global Telemetry Math Calculations
df_current = st.session_state.database
calc_planted = df_current["planted"].sum()
calc_survived = df_current["survived"].sum()
calc_survival_rate = round((calc_survived / calc_planted) * 100, 2) if calc_planted > 0 else 0.00
calc_carbon = round(df_current["carbon_kg"].sum(), 2)
calc_credits = calculate_tradable_credits(calc_carbon)

# ------------------------------------------------------------------------------
# LINK 1: CENTRAL DASHBOARD
# ------------------------------------------------------------------------------
if navigation_node == "1. Central Registry Dashboard":
    st.title("🌱 Central Environmental Registry Dashboard")
    st.subheader("Statewide Ecological Project Tracking Infrastructure")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Registered Planted Trees", f"{calc_planted:,} Trees")
    m2.metric("Average Tree Survival Rate", f"{calc_survival_rate}%")
    m3.metric("Carbon Sequestration Mass", f"{calc_carbon:,} kg CO2e")
    m4.metric("Minted Carbon Credits", f"🪙 {calc_credits:,} VCU")

    st.markdown("---")

    left, right = st.columns([2, 1])
    with left:
        st.subheader("📋 Active Environmental Records Ledger")
        st.dataframe(df_current, use_container_width=True)
    with right:
        st.subheader("📄 Automated Compliance Export")
        st.write("Generate a signed document breakdown matching state and NGO reporting guidelines.")

        if st.session_state.session_token:
            payload_data = {"planted": calc_planted, "survived": calc_survived, "carbon": calc_carbon,
                            "credits": calc_credits}
            pdf_stream = compile_sovereign_pdf(payload_data, df_current)
            st.download_button(
                label="📥 Download Certified PDF Report",
                data=pdf_stream,
                file_name=f"EcoTrack_Climate_Report_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning(
                "🔒 Access Restricted: Please authenticate via the sidebar login window to generate official reports.")

# ------------------------------------------------------------------------------
# LINK 2: REPORT PLANTINGS (SCHOOL UPLOAD)
# ------------------------------------------------------------------------------
elif navigation_node == "2. Report Tree Plantings":
    st.title("📥 School Tree Planting Data Log")
    st.subheader("Submit New Field Telemetry for Verification")

    if st.session_state.role not in ["School Administrator", "State Auditor"]:
        st.error(
            "🚫 Access Denied: Your account profile does not possess permissions to log raw field planting telemetry data.")
    else:
        with st.form("ingestion_form"):
            st.subheader("New Project Registration Form")
            c1, c2 = st.columns(2)
            with c1:
                sch_name = st.text_input("School / Institution Name", placeholder="e.g., Jibia Science Academy")
                lga_select = st.selectbox("LGA Jurisdiction",
                                          ["Katsina", "Daura", "Funtua", "Mani", "Jibia", "Malumfashi", "Bakori"])
                species_select = st.selectbox("Ecological Tree Species", list(SPECIES_REGISTRY.keys()))
                age_input = st.number_input("Tree Growth Duration (Years)", min_value=1, max_value=25, value=2)
            with c2:
                num_planted = st.number_input("Total Trees Planted", min_value=1, value=100, step=5)
                num_survived = st.number_input("Total Trees Survived", min_value=0, value=90, step=5)
                geo_lat = st.number_input("Location Latitude", value=12.9800, format="%.4f")
                geo_lon = st.number_input("Location Longitude", value=7.6100, format="%.4f")

            uploaded_photo = st.file_uploader("🖼️ Upload Field Photographic Evidence", type=["jpg", "png", "jpeg"])
            submit_log = st.form_submit_button("Submit Data Entry to Verification Queue")

            if submit_log:
                if not sch_name:
                    st.error("Data submission failed: Institution Name field cannot be empty.")
                else:
                    val_ok, val_msg = validate_field_telemetry(num_planted, num_survived, geo_lat, geo_lon)
                    if not val_ok:
                        st.error(val_msg)
                    else:
                        ai_fraud_verdict = run_fraud_auditor_ai(num_planted, num_survived)
                        calculated_carbon_mass = compute_carbon_sequestration(species_select, num_survived, age_input)

                        status_assignment = "Flagged" if "⚠️" in ai_fraud_verdict else "Pending"
                        photo_present = True if uploaded_photo is not None else False

                        new_record = {
                            "id": int(st.session_state.database["id"].max() + 1),
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "school": sch_name, "lga": lga_select, "species": species_select,
                            "planted": num_planted, "survived": num_survived, "age_years": age_input,
                            "lat": geo_lat, "lon": geo_lon, "status": status_assignment,
                            "auditor": "Unassigned", "photo_verified": photo_present,
                            "carbon_kg": calculated_carbon_mass
                        }

                        st.session_state.database = pd.concat([st.session_state.database, pd.DataFrame([new_record])],
                                                              ignore_index=True)
                        st.success(f"Data logged into queue successfully. Initial Automated Review: {ai_fraud_verdict}")

# ------------------------------------------------------------------------------
# LINK 3: AI ENGINE
# ------------------------------------------------------------------------------
elif navigation_node == "3. Predictive Ecological AI":
    st.title("🤖 Predictive Ecological AI Model")
    st.subheader("Machine Learning Growth Simulations & Anomaly Detection Framework")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔮 Survival Rate Yield Simulator")
        st.write("Forecast long-term reforestation success using dynamic environmental variables.")

        sim_planted = st.number_input("Planned Plantation Scale (Trees)", min_value=10, value=1000, step=50)
        sim_rain = st.slider("Environmental Variable: Rainfall Index", 0.0, 1.0, 0.65)
        sim_soil = st.slider("Soil Quality Composition Index", 0.0, 1.0, 0.70)
        sim_care = st.slider("Human Care & Irrigation Index", 0.0, 1.0, 0.85)

        if st.button("Run AI Growth Projection"):
            ai_output = run_survival_prediction_ai(sim_planted, sim_rain, sim_soil, sim_care)
            st.metric(label="Predicted Project Survival Confidence", value=f"{ai_output['rate']}%")
            st.metric(label="Projected Forest Maturation Yield", value=f"{ai_output['yield']} Active Trees")

    with col2:
        st.markdown("### 🧠 Field Record Integrity Audit Scanner")
        st.write("Run data checks against automated ecological probability models to catch discrepancies.")

        chk_planted = st.number_input("Audit Baseline: Total Planted", min_value=1, value=500)
        chk_survived = st.number_input("Audit Baseline: Reported Survived", min_value=0, value=495)

        if st.button("Execute Integrity Scan"):
            fraud_verdict = run_fraud_auditor_ai(chk_planted, chk_survived)
            if "⚠️" in fraud_verdict:
                st.error(fraud_verdict)
            else:
                st.success(fraud_verdict)

# ------------------------------------------------------------------------------
# LINK 4: GIS INTERACTIVE MAP
# ------------------------------------------------------------------------------
elif navigation_node == "4. Geospatial Map Layers":
    st.title("🛰️ Geospatial Intelligence Map Layer")
    st.subheader("High-Resolution Spatial Distribution of Tree-Planting Projects")

    map_anchor = [12.9894, 7.6031]
    gis_map = folium.Map(location=map_anchor, zoom_start=8, tiles="OpenStreetMap")

    for _, entity in st.session_state.database.iterrows():
        color_matrix = "green" if entity["status"] == "Approved" else (
            "orange" if entity["status"] == "Pending" else "red")
        popup_payload = f"""
        <strong>{entity['school']}</strong><br/>
        LGA Area: {entity['lga']}<br/>
        Asset Metrics: {entity['survived']}/{entity['planted']} Survived<br/>
        Carbon Profile: {entity['carbon_kg']} kg CO2e<br/>
        Verification Status: {entity['status']}
        """
        folium.Marker(
            location=[entity["lat"], entity["lon"]],
            popup=folium.Popup(popup_payload, max_width=300),
            icon=folium.Icon(color=color_matrix, icon="leaf")
        ).add_to(gis_map)

    st_folium(gis_map, width=1200, height=550)
    st.caption(
        "🟢 Green Pins: Verified & Approved Projects | 🟠 Orange Pins: In Verification Queue | 🔴 Red Pins: Flagged for Revision")

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# LINK 5: APPROVALS & AUDITS
# ------------------------------------------------------------------------------
elif navigation_node == "5. Approvals & Audit Queue":
    st.title("🏛️ Project Verification & Governance Queue")
    st.subheader("Official Data Validation Workflow Management Interface")

    if st.session_state.role not in ["State Auditor"]:
        st.error(
            "🚫 Access Denied: Your account profile does not possess permissions to edit or manage file audit queues.")
    else:
        st.markdown("### Active Pending Submissions Log")
        log_records = st.session_state.database

        active_tasks = 0
        for idx, row in log_records.iterrows():
            if row["status"] in ["Pending", "Flagged"]:
                active_tasks += 1
                with st.expander(f"📋 Review Task: Record ID {row['id']} — {row['school']}"):
                    st.write(f"**LGA Jurisdiction:** {row['lga']} | **Tree Species Registered:** {row['species']}")
                    st.write(
                        f"**Metrics:** Planted Base Volume = {row['planted']} | Survived Active Volume = {row['survived']}")
                    st.write(f"**Photographic Verification Attached:** {row['photo_verified']}")

                    action_col1, action_col2 = st.columns(2)
                    if action_col1.button("Approve & Certify Data", key=f"app_{row['id']}"):
                        st.session_state.database.at[idx, "status"] = "Approved"
                        st.session_state.database.at[idx, "auditor"] = st.session_state.current_user
                        st.toast(f"Record {row['id']} verified and logged to registry ledger.", icon="✅")
                        st.rerun()
                    if action_col2.button("Flag for Re-inspection", key=f"flg_{row['id']}"):
                        st.session_state.database.at[idx, "status"] = "Flagged"
                        st.session_state.database.at[idx, "auditor"] = st.session_state.current_user
                        st.toast(f"Record {row['id']} quarantined.", icon="🚨")
                        st.rerun()

        if active_tasks == 0:
            st.success("All caught up! No projects currently await audit review.")

# ------------------------------------------------------------------------------
# LINK 6: CARBON VALUATION FINTECH LEDGER
# ------------------------------------------------------------------------------
elif navigation_node == "6. Carbon Valuation Ledger":
    st.title("🪙 Carbon Asset Valuation & Credits Ledger")
    st.subheader("Financial Value Conversion Metrics for Environmental Data")

    ledger_data = st.session_state.database.copy()
    ledger_data["Carbon Weight (kg CO2e)"] = ledger_data["carbon_kg"]
    ledger_data["Tradable Credit Yield (VCU)"] = ledger_data["Carbon Weight (kg CO2e)"].apply(
        calculate_tradable_credits)

    approved_credits = ledger_data[ledger_data["status"] == "Approved"]["Tradable Credit Yield (VCU)"].sum()
    quarantined_credits = ledger_data[ledger_data["status"] == "Flagged"]["Tradable Credit Yield (VCU)"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Verified Liquid Carbon Credits", f"{round(approved_credits, 4)} VCU",
              help="Credits generated from fully certified projects.")
    c2.metric("Quarantined Credit Pool", f"{round(quarantined_credits, 4)} VCU",
              help="Speculative credits held back due to audit flags.")
    c3.metric("Projected Financial Value ($USD)", f"${round(approved_credits * 24.50, 2)}",
              help="Calculated market estimation baseline ($24.50/ton).")

    st.markdown("---")
    st.subheader("Sovereign Carbon Value Matrix Ledger")
    st.dataframe(
        ledger_data[["id", "school", "species", "status", "Carbon Weight (kg CO2e)", "Tradable Credit Yield (VCU)"]],
        use_container_width=True)

    st.markdown("---")
    st.subheader("🌱 Eco-Club Curricular Integration Framework")
    st.info("Reforestation projects log metrics corresponding directly to local institutional academic timelines:")

    cx1, cx2, cx3 = st.columns(3)
    with cx1:
        st.markdown("**Phase 1: Nursery Phase**")
        st.caption(ECO_CLUB_SYLLABUS["Week 1-4"])
    with cx2:
        st.markdown("**Phase 2: Irrigation & Care**")
        st.caption(ECO_CLUB_SYLLABUS["Week 5-8"])
    with cx3:
        st.markdown("**Phase 3: Quantification**")
        st.caption(ECO_CLUB_SYLLABUS["Week 9-12"])
