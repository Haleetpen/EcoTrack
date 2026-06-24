import streamlit as st
import pandas as pd
import os

# 1. Set up page configuration
st.set_page_config(
    page_title="EcoTrack Green Innovation",
    page_icon="🌱",
    layout="wide"
)

# Title & Corporate Branding Headers
st.title("🌱 EcoTrack Green Innovation Dashboard")
st.markdown("### National Species Directory & Environmental Intelligence Platform")
st.write("Monitor tree survival indices, carbon credits, and species matching across Nigeria.")

# 2. Safe Data Loading Function with Error Shields
@st.cache_data
def load_species_data():
    file_path = "species_directory.csv"
    if not os.path.exists(file_path):
        st.error(f"❌ Critical Error: '{file_path}' not found in your repository directory.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        # Clean any accidental trailing spaces from column headers
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

# Load the database globally
df = load_species_data()

# Only render the interface if data loaded successfully
if not df.empty:
    
    # 3. Sidebar Location & Operational Category Filtering
    st.sidebar.header("📍 Location Filtering")
    
    # Standard states list matching Northern and National directory allocations
    available_states = ["All States", "Katsina", "Kano", "Sokoto", "Borno", "Kebbi", "Jigawa", "Yobe", "Kaduna", "Plateau"]
    selected_state = st.sidebar.selectbox("Select Target State", available_states)
    
    # Dynamic Category Mapping Loop (Replaces row['type'] with fallback shield)
    categories = []
    for index, row in df.iterrows():
        # Looks for new header 'Category', falls back to 'type', defaults cleanly if missing
        cat = row.get('Category', row.get('type', 'Windbreakers & Shelterbelts'))
        if pd.notna(cat) and str(cat).strip() not in categories:
            categories.append(str(cat).strip())
            
    st.sidebar.header("🌲 Project Type Filters")
    selected_category = st.sidebar.selectbox("Select Operational Category", ["All Categories"] + categories)

    # 4. Core Filter Logic Application
    filtered_df = df.copy()
    
    if selected_category != "All Categories":
        if 'Category' in df.columns:
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]
        elif 'type' in df.columns:
            filtered_df = filtered_df[filtered_df['type'] == selected_category]

    if selected_state != "All States":
        if 'Suitable Nigerian States' in df.columns:
            filtered_df = filtered_df[filtered_df['Suitable Nigerian States'].str.contains(selected_state, na=False, case=False)]

    # 5. Core Performance Metrics Layout
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Species Loaded", len(df))
    with col2:
        st.metric("Filtered Species Available", len(filtered_df))
    with col3:
        st.metric("Carbon Monitoring System Status", "Active ✅")

    # 6. Primary Data Explorer Grid View
    st.subheader("📋 Explorer Directory View")
    
    # Select clean columns for primary layout grid display if they match the dataset
    display_cols = [c for c in ['EcoTrack Tree ID', 'Common Name', 'Scientific Name', 'Hausa Name', 'Category', 'Growth Rate', 'Carbon Sequestration Potential'] if c in filtered_df.columns]
    
    if display_cols:
        st.dataframe(filtered_df[display_cols], use_container_width=True)
    else:
        st.dataframe(filtered_df, use_container_width=True)

    # 7. Dynamic Individual Parameter Deep-Dive View
    st.subheader("🔍 Deep Dive Inspection View")
    if not filtered_df.empty:
        # Get unique names to protect dropdown selections
        unique_names = filtered_df['Common Name'].dropna().unique()
        selected_tree = st.selectbox("Choose a tree species to examine parameters:", unique_names)
        
        # Pull row details for selected species
        tree_details = filtered_df[filtered_df['Common Name'] == selected_tree].iloc[0]
        
        detail_col1, detail_col2 = st.columns(2)
        with detail_col1:
            st.markdown(f"**Scientific Name:** *{tree_details.get('Scientific Name', 'N/A')}*")
            st.markdown(f"**Hausa Traditional Name:** {tree_details.get('Hausa Name', 'N/A')}")
            st.markdown(f"**Mature Height:** {tree_details.get('Mature Height (m)', 'N/A')} meters")
            st.markdown(f"**Lifespan Cycle:** {tree_details.get('Average Lifespan', 'N/A')} years")
        with detail_col2:
            st.markdown(f"**Drought Resistance Profile:** {tree_details.get('Drought Tolerance', 'N/A')}")
            st.markdown(f"**Ecological Target Zones:** {tree_details.get('Ecological Zone(s)', 'N/A')}")
            st.markdown(f"**Primary Deployment Use Case:** {tree_details.get('Main Uses', 'N/A')}")
            st.success(f"Estimated Carbon Sequestration Class: {tree_details.get('Estimated CO₂ Absorption Class', 'Class B')}")
    else:
        st.info("No regional tree species currently match your selected filtering matrix criteria.")
else:
    st.warning("Waiting for species_directory.csv parameters to align and compile display windows.")

