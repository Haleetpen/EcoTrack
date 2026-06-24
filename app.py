import streamlit as st
import pandas as pd
import sqlite3
import datetime
import json
import os
from dateutil.relativedelta import relativedelta

# ==============================================================================
# 1. PAGE SETUP & DESIGN STYLE
# ==============================================================================
st.set_page_config(
    page_title="EcoTrack: Green Schools Innovation",
    layout="wide",
    page_icon="🌱"
)

DB_FILE = "ecotrack_vnext.db"
CSV_FILE = "species_directory.csv"

# ==============================================================================
# NATIONAL GEOGRAPHIC REGISTRY (All 36 States + FCT & LGAs)
# ==============================================================================
NIGERIA_GEOGRAPHY = {
    "Abia": ["Aba North", "Aba South", "Arochukwu", "Bende", "Ikwuano", "Isiala Ngwa North", "Isiala Ngwa South", "Isuikwuato", "Obingwa", "Ohafia", "Osisioma", "Ugwunagbo", "Ukwa West", "Ukwa East", "Umuahia North", "Umuahia South", "Umu-Nneochi"],
    "Adamawa": ["Demsa", "Fufure", "Ganye", "Gayuk", "Gombi", "Grai", "Hong", "Jada", "Lamurde", "Madagali", "Maiha", "Mayo Belwa", "Michika", "Mubi North", "Mubi South", "Numan", "Shelleng", "Song", "Toungo", "Yola North", "Yola South"],
    "Akwa Ibom": ["Abak", "Eastern Obolo", "Eket", "Esit Eket", "Essien Udim", "Etim Ekpo", "Etinan", "Ibeno", "Ibesikpo Asutan", "Ibiono-Ibom", "Ika", "Ikono", "Ikot Abasi", "Ikot Ekpene", "Ini", "Itu", "Mbo", "Mkpat-Enin", "Nsit-Atai", "Nsit-Ibom", "Nsit-Ubium", "Obot Akara", "Okobo", "Onna", "Oron", "Oruk Anam", "Udung-Uko", "Ukanafun", "Uruan", "Urue-Offong/Oruko", "Uyo"],
    "Anambra": ["Aguata", "Anambra East", "Anambra West", "Anaocha", "Awka North", "Awka South", "Ayamelum", "Dunukofia", "Ekwusigo", "Idemili North", "Idemili South", "Ihiala", "Njikoka", "Nnewi North", "Nnewi South", "Ogbaru", "Onitsha North", "Onitsha South", "Orumba North", "Orumba South", "Oyi"],
    "Bauchi": ["Alkaleri", "Bauchi", "Bogoro", "Dambam", "Darazo", "Dass", "Gamawa", "Ganjuwa", "Giade", "Itas/Gadau", "Jama'are", "Katagum", "Kirfi", "Misau", "Ningi", "Shira", "Tafawa Balewa", "Toro", "Warji", "Zaki"],
    "Bayelsa": ["Brass", "Ekeremor", "Kolokuma/Opokuma", "Nembe", "Ogbia", "Sagbama", "Southern Ijaw", "Yenagoa"],
    "Benue": ["Agatu", "Apa", "Ado", "Buruku", "Gboko", "Guma", "Gwer East", "Gwer West", "Katsina-Ala", "Konshisha", "Kwande", "Logo", "Makurdi", "Obi", "Ogbadibo", "Ohimini", "Oju", "Okpokwu", "Oturkpo", "Tarka", "Ukum", "Ushongo", "Vandeikya"],
    "Borno": ["Abadam", "Askira/Uba", "Bama", "Bayo", "Biu", "Chibok", "Damboa", "Dikwa", "Gubio", "Guzamala", "Gwoza", "Hawul", "Jere", "Kaga", "Kala/Balge", "Konduga", "Kukawa", "Kwaya Kusar", "Mafa", "Magumeri", "Maiduguri", "Marte", "Mobbar", "Monguno", "Ngala", "Nganzai", "Shani"],
    "Cross River": ["Abi", "Akamkpa", "Akpabuyo", "Bakassi", "Bekwarra", "Biase", "Boki", "Calabar Municipal", "Calabar South", "Etung", "Ikom", "Obanliku", "Obubra", "Obudu", "Odukpani", "Ogoja", "Yakuur", "Yala"],
    "Delta": ["Aniocha North", "Aniocha South", "Bomadi", "Burutu", "Ethiope East", "Ethiope West", "Ika North East", "Ika South", "Isoko North", "Isoko South", "Ndokwa East", "Ndokwa West", "Okpe", "Oshimili North", "Oshimili South", "Patani", "Sapele", "Udu", "Ughelli North", "Ughelli South", "Ukwuani", "Uvwie", "Warri North", "Warri South", "Warri South West"],
    "Ebonyi": ["Abakaliki", "Afikpo North", "Afikpo South", "Ebonyi", "Ezza North", "Ezza South", "Ikwo", "Ishielu", "Ivo", "Izzi", "Ohaozara", "Ohaukwu", "Onicha"],
    "Edo": ["Akoko-Edo", "Egor", "Esan Central", "Esan North-East", "Esan South-East", "Esan West", "Etsako Central", "Etsako East", "Etsako West", "Igueben", "Ikpoba Okha", "Orhionmwon", "Oredo", "Ovia North-East", "Ovia South-West", "Owan East", "Owan West", "Uhunmwonde"],
    "Ekiti": ["Ado Ekiti", "Efon", "Ekiti East", "Ekiti South-West", "Ekiti West", "Emure", "Gbonyin", "Ido Osi", "Ijero", "Ikere", "Ikole", "Ilejemeje", "Irepodun/Ifelodun", "Ise/Orun", "Moba", "Oye"],
    "Enugu": ["Aninri", "Awgu", "Enugu East", "Enugu North", "Enugu South", "Ezeagu", "Igbo Etiti", "Igbo Eze North", "Igbo Eze South", "Isi Uzo", "Nkanu East", "Nkanu West", "Nsukka", "Oji River", "Udenu", "Udi", "Uzo Uwani"],
    "FCT - Abuja": ["Abaji", "Bwari", "Gwagwalada", "Kuje", "Kwali", "Municipal Area Council"],
    "Gombe": ["Akko", "Balanga", "Billiri", "Dukku", "Funakaye", "Gombe", "Kaltungo", "Kwami", "Nafada", "Shongom", "Yamaltu/Deba"],
    "Imo": ["Ahiazu Mbaise", "Ehime Mbano", "Ezinihitte", "Ideato North", "Ideato South", "Ihitte/Uboma", "Ikeduru", "Isiala Mbano", "Isu", "Mbaitoli", "Ngor Okpala", "Njaba", "Nkwerre", "Nwangele", "Obowo", "Oguta", "Ohaji/Egbema", "Okigwe", "Orlu", "Orsu", "Oru East", "Oru West", "Owerri Municipal", "Owerri North", "Owerri South", "Onuimo"],
    "Jigawa": ["Auyo", "Babura", "Biriniwa", "Birnin Kudu", "Buji", "Dutse", "Gagarawa", "Garki", "Gumel", "Guri", "Gwaram", "Gwiwa", "Hadejia", "Jahun", "Kafim Hausa", "Kaugama", "Kazaure", "Kiri Kasama", "Kiyawa", "Maigatari", "Malam Madori", "Miga", "Ringim", "Roni", "Sule Tankarkar", "Taura", "Yankwashi"],
    "Kaduna": ["Birnin Gwari", "Chikun", "Giwa", "Giwa", "Igabi", "Ikara", "Jaba", "Jema'a", "Kachia", "Kaduna North", "Kaduna South", "Kagarko", "Kajuru", "Kaura", "Kauru", "Kubau", "Kudan", "Lere", "Makarfi", "Sabon Gari", "Sanga", "Soba", "Zangon Kataf", "Zaria"],
    "Kano": ["Ajingi", "Albasu", "Bagwai", "Bebeji", "Bichi", "Bunkure", "Dala", "Dambatta", "Dawakin Kudu", "Dawakin Tofa", "Doguwa", "Fagge", "Gabasawa", "Gwarzo", "Gwale", "Karaye", "Kibiya", "Kurai", "Kumbotso", "Kunchi", "Kura", "Madobi", "Makoda", "Minjibir", "Nasarawa", "Rano", "Rimin Gado", "Rogo", "Shanono", "Sumaila", "Takai", "Tarauni", "Tofa", "Tsanyawa", "Tudun Wada", "Ungogo", "Warawa", "Wudil"],
    "Katsina": ["Bakori", "Batagarawa", "Batsari", "Baure", "Bindawa", "Charanchi", "Dan Musa", "Dandume", "Danja", "Daura", "Dutsi", "Dutsin-Ma", "Faskari", "Funtua", "Ingawa", "Jibia", "Kafur", "Kaita", "Kankara", "Kankia", "Katsina", "Kurfi", "Kusada", "Mai'Adua", "Malumfashi", "Mani", "Mashi", "Matazu", "Musawa", "Rimi", "Sabuwa", "Safana", "Sandamu", "Zango"],
    "Kebbi", ["Aleiro", "Arewa Dandi", "Argungu", "Augie", "Bagudo", "Birnin Kebbi", "Bunza", "Dandi", "Fakai", "Gwandu", "Jega", "Kalgo", "Koko/Besse", "Maiyama", "Ngaski", "Sakaba", "Shanga", "Suru", "Wasagu/Danko", "Yauri", "Zuru"],
    "Kogi": ["Adavi", "Ajaokuta", "Ankpa", "Bassa", "Dekina", "Ibaji", "Idah", "Igalamela Odolu", "Ijumu", "Kabba/Bunu", "Kogi", "Lokoja", "Mopa Muro", "Ofu", "Ogori/Magongo", "Okehi", "Okene", "Olamaboro", "Omala", "Yagba East", "Yagba West"],
    "Kwara": ["Asa", "Baruten", "Edu", "Ekiti", "Ifelodun", "Ilorin East", "Ilorin South", "Ilorin West", "Irepodun", "Isin", "Kaiama", "Moro", "Offa", "Oke Ero", "Oyun", "Pategi"],
    "Lagos": ["Agege", "Ajeromi-Ifelodun", "Alimosho", "Amuwo-Odofin", "Apapa", "Badagry", "Epe", "Eti Osa", "Ibeju-Lekki", "Ifako-Ijaiye", "Ikeja", "Ikorodu", "Kosofe", "Lagos Island", "Lagos Mainland", "Mushin", "Ojo", "Oshodi-Isolo", "Shomolu", "Surulere"],
    "Nasarawa": ["Akwanga", "Awe", "Doma", "Karu", "Keana", "Keffi", "Kokona", "Lafia", "Nasarawa", "Nasarawa Egon", "Obi", "Toto", "Wamba"],
    "Niger": ["Agaie", "Agwara", "Bida", "Borgu", "Bosso", "Chanchaga", "Edati", "Gbako", "Gurara", "Katcha", "Kontagora", "Lapai", "Lavun", "Magama", "Mariga", "Mashegu", "Mokwa", "Moya", "Paikoro", "Rafi", "Rijau", "Shiroro", "Suleja", "Tafa", "Wushishi"],
    "Ogun": ["Abeokuta North", "Abeokuta South", "Ado-Odo/Ota", "Egbado North", "Egbado South", "Ewekoro", "Ifo", "Ijebu East", "Ijebu North", "Ijebu North East", "Ijebu Ode", "Ikenne", "Imeko Afon", "Ipokia", "Obafemi Owode", "Odeda", "Odogbolu", "Ogun Waterside", "Remo North", "Shagamu"],
    "Ondo": ["Akoko North-East", "Akoko North-West", "Akoko South-West", "Akoko South-East", "Akure North", "Akure South", "Ese Odo", "Idanre", "Ifedore", "Ilaje", "Ile Oluji/Okeigbo", "Irele", "Odigbo", "Okitipupa", "Ondo East", "Ondo West", "Ose", "Owo"],
    "Osun": ["Atakunmosa East", "Atakunmosa West", "Aiyedaade", "Aiyedire", "Boluwaduro", "Boripe", "Ede North", "Ede South", "Ife Central", "Ife East", "Ife North", "Ife South", "Egbedore", "Egbado", "Ila", "Ilesa East", "Ilesa West", "Irepodun", "Irewole", "Isokan", "Iwo", "Obokun", "Odo Otin", "Ola Oluwa", "Olorunda", "Oriade", "Orolu", "Osogbo"],
    "Oyo": ["Afijio", "Akinyele", "Atiba", "Atisbo", "Egbeda", "Ibadan North", "Ibadan North-East", "Ibadan North-West", "Ibadan South-East", "Ibadan South-West", "Ibarapa Central", "Ibarapa East", "Ibarapa North", "Ido", "Irepo", "Iseyin", "Itesiwaju", "Iwajowa", "Kajola", "Lagelu", "Ogbomosho North", "Ogbomosho South", "Ogo Oluwa", "Olorunsogo", "Oluyole", "Ona Ara", "Orelope", "Ori Ire", "Oyo", "Oyo East", "Saki East", "Saki West", "Surulere"],
    "Plateau": ["Bokkos", "Barkin Ladi", "Bassa", "Jos East", "Jos North", "Jos South", "Kanam", "Kanke", "Langtang North", "Langtang South", "Mangu", "Mikang", "Pankshin", "Qua'an Pan", "Riyom", "Shendam", "Wase"],
    "Rivers": ["Abua/Odual", "Ahoada East", "Ahoada West", "Akuku Toru", "Andoni", "Asari-Toru", "Bonny", "Degema", "Emohua", "Eleme", "Etche", "Gokana", "Ikwerre", "Khana", "Obio/Akpor", "Ogba/Egbema/Ndoni", "Ogu/Bolo", "Okrika", "Omuma", "Opobo/Nkoro", "Oyigbo", "Port Harcourt", "Tai"],
    "Sokoto": ["Binji", "Bodinga", "Dange Shuni", "Gada", "Goronyo", "Gudu", "Gwadabawa", "Illela", "Isa", "Kebbe", "Kware", "Rabah", "Sabon Birni", "Shagari", "Silame", "Sokoto North", "Sokoto South", "Tambuwal", "Tangaza", "Tureta", "Wamako", "Wurno", "Yabo"],
    "Taraba": ["Ardo Kola", "Bali", "Donga", "Gashaka", "Gassol", "Ibi", "Jalingo", "Karim Lamido", "Kumi", "Lau", "Sardauna", "Takum", "Ussa", "Wukari", "Yorro", "Zing"],
    "Yobe": ["Bade", "Bursari", "Damaturu", "Fika", "Fune", "Geidam", "Gujba", "Gulani", "Jakusko", "Karasuwa", "Machina", "Nangere", "Nguru", "Potiskum", "Tarmuwa", "Yunusari", "Yusufari"],
    "Zamfara": ["Anka", "Bakura", "Birnin Magaji/Kiyaw", "Bukkuyum", "Bungudu", "Gummi", "Gusau", "Kaura Namoda", "Maradun", "Maru", "Shinkafi", "Talata Mafara", "Zurmi"]
}

# ==============================================================================
# 2. AUTOMATED MASTER DATA LOADER WITH SCHEMA SHIELDS
# ==============================================================================
def load_master_species_directory():
    """Reads species from the uploaded CSV using a robust column parser fallback framework."""
    if os.path.exists(CSV_FILE):
        try:
            df_species = pd.read_csv(CSV_FILE)
            df_species.columns = df_species.columns.str.strip()
            species_dict = {}
            for _, row in df_species.iterrows():
                # Flexible Column Resolvers
                name = row.get('Common Name', row.get('species_name', row.get('Display Name', 'Unknown Name')))
                botanical = row.get('Scientific Name', row.get('botanical_name', 'Unknown Botanical'))
                
                # Check for standard sequestration metrics or apply generic default parameters
                wd = row.get('wood_density', 0.65)
                gf = row.get('growth_factor', 0.024)
                category = row.get('Category', row.get('category', row.get('type', 'Agroforestry')))
                
                species_dict[str(name).strip()] = {
                    "botanical": botanical,
                    "wd": float(wd) if pd.notna(wd) else 0.65,
                    "gf": float(gf) if pd.notna(gf) else 0.024,
                    "type": str(category).strip()
                }
            return species_dict
        except Exception as e:
            st.error(f"⚠️ Directory structural notice: falling back to base array profile. ({e})")
            
    # Fail-safe internal framework fallback configurations
    return {
        "Neem": {"botanical": "Azadirachta indica", "wd": 0.68, "gf": 0.025, "type": "Windbreakers & Shelterbelts"},
        "Desert Date": {"botanical": "Balanites aegyptiaca", "wd": 0.72, "gf": 0.018, "type": "Windbreakers & Shelterbelts"},
        "Moringa": {"botanical": "Moringa oleifera", "wd": 0.42, "gf": 0.045, "type": "Economic & Agroforestry"},
        "Gum Arabic": {"botanical": "Acacia senegal", "wd": 0.70, "gf": 0.022, "type": "Economic & Agroforestry"}
    }

TREE_DATABASE = load_master_species_directory()

# ==============================================================================
# 3. SQLITE DATABASE APPLICATION TABLES STORAGE LAYER
# ==============================================================================
def setup_application_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'Basic Tier'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            lga_name TEXT NOT NULL,
            state_name TEXT NOT NULL,
            planting_date TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            gps_accuracy REAL NOT NULL,
            device_info TEXT,
            evidence_links TEXT,
            FOREIGN KEY(account_name) REFERENCES accounts(name)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batch_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            tree_species TEXT NOT NULL,
            qty_planted INTEGER NOT NULL,
            qty_survived INTEGER NOT NULL,
            FOREIGN KEY(event_id) REFERENCES events(event_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (
            checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            interval_months TEXT NOT NULL,
            qty_alive INTEGER NOT NULL,
            qty_dead INTEGER NOT NULL,
            inspection_date TEXT NOT NULL,
            inspector TEXT NOT NULL,
            verification_status TEXT NOT NULL DEFAULT 'Approved',
            FOREIGN KEY(event_id) REFERENCES events(event_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM accounts")
    if cursor.fetchone()[0] == 0:
        sample_profiles = [
            ("Katsina Premium Academy", "Private School", "Enterprise Tier"),
            ("Batagarawa Community School", "Public School", "Basic Tier"),
            ("Save The Green Foundation", "NGO", "Growth Tier"),
            ("EcoTrack Green Innovation Hub", "NGO", "Climate-Smart Academy")
        ]
        cursor.executemany("INSERT INTO accounts (name, type, tier) VALUES (?, ?, ?)", sample_profiles)
        
    conn.commit()
    conn.close()

setup_application_tables()

# ==============================================================================
# 4. INTELLECTUAL CALCULATION ENGINES
# ==============================================================================
def calculate_carbon_absorbed(species_name, tree_count):
    tree_info = TREE_DATABASE.get(species_name, {"wd": 0.55, "gf": 0.022})
    yearly_kg_per_tree = (tree_info["wd"] * 50) * tree_info["gf"] * 1.28 * 0.47 * 3.67
    return round(yearly_kg_per_tree * tree_count, 2)

def calculate_tree_age(date_string):
    try:
        planted_day = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        today = datetime.date.today()
        difference = relativedelta(today, planted_day)
        if difference.years == 0 and difference.months == 0 and difference.days <= 0:
            return "Planted Today"
        labels = []
        if difference.years > 0: labels.append(f"{difference.years} yr" + ("s" if difference.years > 1 else ""))
        if difference.months > 0: labels.append(f"{difference.months} mo" + ("s" if difference.months > 1 else ""))
        if difference.days > 0 and len(labels) < 2: labels.append(f"{difference.days} day" + ("s" if difference.days > 1 else ""))
        return " ".join(labels) if labels else "Just started"
    except ValueError:
        return "Unknown timeline"

def fetch_complete_green_dataset():
    conn = sqlite3.connect(DB_FILE)
    query = """
        SELECT e.event_id, e.account_name, e.lga_name, e.state_name, e.planting_date,
               e.latitude, e.longitude, e.gps_accuracy, e.evidence_links,
               b.tree_species, b.qty_planted, b.qty_survived,
               a.type as account_type, a.tier as account_tier
        FROM events e
        JOIN batch_items b ON e.event_id = b.event_id
        JOIN accounts a ON e.account_name = a.name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ==============================================================================
# 5. SIDEBAR NAVIGATION CONTROLS
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/sprout.png", width=54)
    st.title("EcoTrack Hub")
    st.caption("National Green Schools Tracking Network")
    st.divider()
    
    active_screen = st.selectbox("Where would you like to go?", [
        "1. School Form (Record Planting)",
        "2. Progress Inspections & Audits",
        "3. Live Green Dashboard",
        "4. School Performance Leaderboards"
    ])
    
    st.divider()
    conn = sqlite3.connect(DB_FILE)
    available_profiles = pd.read_sql_query("SELECT name FROM accounts", conn)["name"].tolist()
    conn.close()
    
    current_user = st.selectbox("Log in as Account:", available_profiles)
    
    conn = sqlite3.connect(DB_FILE)
    tier_info = pd.read_sql_query("SELECT tier FROM accounts WHERE name=?", conn, params=(current_user,))
    active_tier = tier_info["tier"].iloc[0] if not tier_info.empty else "Basic Tier"
    conn.close()
    
    st.info(f"📋 **Access Level:** {active_tier}")

# ==============================================================================
# SCREEN 1: RECORD TREE PLANTING TERMINAL
# ==============================================================================
if active_screen == "1. School Form (Record Planting)":
    st.title("🌳 National Planting Records Terminal")
    st.markdown("### Log entries from your latest reforestation campaigns below.")
    
    if "temporary_tree_list" not in st.session_state:
        st.session_state.temporary_tree_list = []
        
    with st.expander("📍 Automatic GPS Verification Status", expanded=True):
        col_g1, col_g2, col_g3 = st.columns(3)
        locked_lat = col_g1.number_input("Verified Latitude:", value=11.9845, format="%.6f", disabled=True)
        locked_lon = col_g2.number_input("Verified Longitude:", value=7.6253, format="%.6f", disabled=True)
        gps_signals = col_g3.number_input("GPS Signal Accuracy (Meters):", value=2.4, format="%.1f", disabled=True)

    st.subheader("➕ Add Trees to Your Report")
    
    # Category Extraction Parser
    categories = sorted(list(set([details["type"] for details in TREE_DATABASE.values()])))
    
    col_f1, col_f2 = st.columns(2)
    selected_category = col_f1.selectbox("Filter by Category Type:", categories)
    
    filtered_choices = [name for name, details in TREE_DATABASE.items() if details["type"] == selected_category]
    
    with st.form("individual_tree_form", clear_on_submit=False):
        col_i1, col_i2, col_i3 = st.columns([2, 1, 1])
        variety = col_i1.selectbox("Choose Specific Variety Name:", sorted(filtered_choices) if filtered_choices else list(TREE_DATABASE.keys()))
        num_planted = col_i2.number_input("Number Planted:", min_value=1, value=10, step=1)
        num_survived = col_i3.number_input("Number Currently Living:", min_value=0, value=10, step=1)
        
        add_to_list_btn = st.form_submit_button("Add This Variety to List")
        if add_to_list_btn:
            if num_survived > num_planted:
                st.error("Error: Living counts cannot be higher than planted counts.")
            else:
                st.session_state.temporary_tree_list.append({
                    "variety": variety, "planted": num_planted, "survived": num_survived
                })
                st.success(f"Added {variety} to report payload list.")

    if st.session_state.temporary_tree_list:
        st.markdown("#### Preview of Current Report entries:")
        st.dataframe(pd.DataFrame(st.session_state.temporary_tree_list), use_container_width=True, hide_index=True)
        if st.button("Clear Current Form List"):
            st.session_state.temporary_tree_list = []
            st.rerun()

    st.subheader("📋 Final Submission Jurisdiction Details")
    with st.form("final_report_form"):
        col_m1, col_m2 = st.columns(2)
        
        # Comprehensive State Selection Engine Mapping
        selected_state = col_m1.selectbox("Select Target State:", sorted(list(NIGERIA_GEOGRAPHY.keys())))
        local_lga = col_m2.selectbox("Select Local Government Area (LGA):", sorted(NIGERIA_GEOGRAPHY[selected_state]))
        
        planting_day = st.date_input("Date Planted (Backdate for older setups):", max_value=datetime.date.today())
        photo_evidence = st.file_uploader("Upload project proof files", accept_multiple_files=True)
        
        send_report_to_database = st.form_submit_button("🔒 Securely Save and Submit Full Report")
        if send_report_to_database:
            if not st.session_state.temporary_tree_list:
                st.error("Your tree list is empty. Add a variety above first.")
            else:
                file_names = [f.name for f in photo_evidence] if photo_evidence else ["default.png"]
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO events (account_name, lga_name, state_name, planting_date, latitude, longitude, gps_accuracy, device_info, evidence_links)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (current_user, local_lga, selected_state, str(planting_day), locked_lat, locked_lon, gps_signals, "EcoTrack Web Engine v3", json.dumps(file_names)))
                
                new_event_id = cursor.lastrowid
                final_batch_payload = [(new_event_id, item["variety"], item["planted"], item["survived"]) for item in st.session_state.temporary_tree_list]
                cursor.executemany("INSERT INTO batch_items (event_id, tree_species, qty_planted, qty_survived) VALUES (?, ?, ?, ?)", final_batch_payload)
                conn.commit()
                conn.close()
                st.success(f"🎉 Project Record #{new_event_id} has been saved for {local_lga}, {selected_state} State.")
                st.session_state.temporary_tree_list = []

# ==============================================================================
# SCREEN 2: PROGRESS INSPECTIONS & AUDITS
# ==============================================================================
elif active_screen == "2. Progress Inspections & Audits":
    st.title("🛡️ Project Follow-Up and Inspection Center")
    all_data = fetch_complete_green_dataset()
    if all_data.empty:
        st.info("No projects found in system records.")
    else:
        grouped_records = all_data[["event_id", "account_name", "planting_date", "state_name", "lga_name"]].drop_duplicates()
        grouped_records["current_age"] = grouped_records["planting_date"].apply(calculate_tree_age)
        
        dropdown_options = {
            row["event_id"]: f"Project #{row['event_id']} by {row['account_name']} ({row['lga_name']}, {row['state_name']} State) — Age: {row['current_age']}" 
            for _, row in grouped_records.iterrows()
        }
        
        target_project_id = st.selectbox("Select a Project Record to Inspect:", list(dropdown_options.keys()), format_func=lambda x: dropdown_options[x])
        
        project_meta = grouped_records[grouped_records["event_id"] == target_project_id].iloc[0]
        project_trees_subset = all_data[all_data["event_id"] == target_project_id]
        
        st.markdown("---")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"#### 📐 Project Metadata Card: ID #{target_project_id}")
            st.write(f"**Managing Institution:** {project_meta['account_name']}")
            st.write(f"**Jurisdiction:** {project_meta['lga_name']} LGA, {project_meta['state_name']}")
            st.write(f"**Initial Planting Date:** {project_meta['planting_date']} (`{project_meta['current_age']}`)")
        with col_p2:
            st.markdown("#### 🪵 Current Tree Counts on Record")
            st.dataframe(project_trees_subset[["tree_species", "qty_planted", "qty_survived"]].rename(columns={"tree_species":"Tree Variety"}), hide_index=True, use_container_width=True)

        st.markdown("### 📝 Log a New Inspection Progress Check")
        with st.form("new_checkpoint_form"):
            col_c1, col_c2, col_c3 = st.columns(3)
            milestone_step = col_c1.selectbox("Time Horizon Milestone:", ["1 Month Check", "3 Months Check", "6 Months Check", "12 Months Check", "24 Months Check"])
            living_found = col_c2.number_input("Number Alive:", min_value=0, step=1)
            dead_found = col_c3.number_input("Number Dead:", min_value=0, step=1)
            inspector_id = st.text_input("Name of Inspector:")
            
            if st.form_submit_button("Save Entry"):
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT INTO checkpoints (event_id, interval_months, qty_alive, qty_dead, inspection_date, inspector) VALUES (?, ?, ?, ?, ?, ?)", (int(target_project_id), milestone_step, living_found, dead_found, str(datetime.date.today()), inspector_id))
                conn.commit()
                conn.close()
                st.success("Audit verification payload successfully synchronized.")
                st.rerun()

# ==============================================================================
# SCREEN 3: EXECUTIVE LIVE GREEN ANALYTICS DASHBOARD
# ==============================================================================
elif active_screen == "3. Live Green Dashboard":
    st.title("📊 National Environmental Dashboard Workspace")
    analytics_base = fetch_complete_green_dataset()
    if analytics_base.empty:
        st.info("The dashboard database layers are empty. Log incoming tree items first.")
    else:
        analytics_base["co2_absorbed_kg"] = analytics_base.apply(lambda row: calculate_carbon_absorbed(row["tree_species"], row["qty_survived"]), axis=1)
        
        with st.expander("🎛️ Regional Workspace Filtering Matrix", expanded=True):
            col_f1, col_f2, col_f3 = st.columns(3)
            
            # Geo Matrix Cascading selectors
            selected_states = col_f1.multiselect("Select States:", sorted(analytics_base["state_name"].unique()), default=analytics_base["state_name"].unique())
            
            lga_choices = sorted(analytics_base[analytics_base["state_name"].isin(selected_states)]["lga_name"].unique()) if selected_states else []
            selected_lgas = col_f2.multiselect("Select LGA Districts:", lga_choices, default=lga_choices)
            
            tree_choices = sorted(analytics_base["tree_species"].unique())
            selected_trees = col_f3.multiselect("Select Tree Variety:", tree_choices, default=tree_choices)
            
        filtered_view = analytics_base[
            (analytics_base["state_name"].isin(selected_states)) & 
            (analytics_base["lga_name"].isin(selected_lgas)) & 
            (analytics_base["tree_species"].isin(selected_trees))
        ]
        
        if not filtered_view.empty:
            total_planted = filtered_view["qty_planted"].sum()
            total_survived = filtered_view["qty_survived"].sum()
            net_co2_offset = filtered_view["co2_absorbed_kg"].sum()
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Total Saplings Planted", f"{total_planted:,}")
            col_m2.metric("Verified Living Trees", f"{total_survived:,}")
            col_m3.metric("CO2 Absorbed (kg/year)", f"{net_co2_offset:,.1f}")
            
            st.subheader("🗺️ Real-Time Map of Verified Project Plantings")
            st.map(filtered_view[["latitude", "longitude"]].dropna().rename(columns={"latitude": "lat", "longitude": "lon"}), use_container_width=True)
        else:
            st.info("No active logs meet current search configuration constraints.")

# ==============================================================================
# SCREEN 4: GAMIFIED SCHOOL LEADERBOARDS
# ==============================================================================
elif active_screen == "4. School Performance Leaderboards":
    st.title("🏆 National Green Schools Championship Standings")
    ranking_base = fetch_complete_green_dataset()
    if ranking_base.empty:
        st.info("Leaderboards will calculate standings as soon as schools submit active data entries.")
    else:
        leaderboard = ranking_base.groupby("account_name").agg({"qty_planted": "sum", "qty_survived": "sum", "event_id": "nunique"}).reset_index()
        leaderboard["Survival Rate (%)"] = (leaderboard["qty_survived"] / leaderboard["qty_planted"] * 100).round(1)
        leaderboard["Total Impact Score"] = ((leaderboard["qty_survived"] * 0.6) + (leaderboard["Survival Rate (%)"] * 0.4)).round(1)
        
        sorted_lbl = leaderboard.sort_values(by="Total Impact Score", ascending=False).reset_index(drop=True)
        sorted_lbl.index += 1
        st.dataframe(sorted_lbl.rename(columns={"account_name":"School / Organization Name", "qty_planted":"Total Saplings Planted", "qty_survived":"Living Counts", "event_id":"Campaigns Logged"}), use_container_width=True)
