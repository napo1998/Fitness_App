import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe, get_as_dataframe

# Page configuration
st.set_page_config(
    page_title="Fitness & Body Composition Tracker",
    page_icon="💪",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'sheet' not in st.session_state:
    st.session_state.sheet = None
if 'data' not in st.session_state:
    st.session_state.data = None

def connect_to_google_sheets(sheet_url, credentials_json):
    """Connect to Google Sheets using service account credentials"""
    try:
        # Define the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Create credentials from the JSON
        credentials = Credentials.from_service_account_info(
            credentials_json,
            scopes=scope
        )
        
        # Authorize the client
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet
        sheet = client.open_by_url(sheet_url).sheet1
        
        return sheet, None
    except Exception as e:
        return None, str(e)

def load_data(sheet):
    """Load data from Google Sheet"""
    try:
        df = get_as_dataframe(sheet, evaluate_formulas=True)
        # Remove empty rows
        df = df.dropna(how='all')
        # Convert date column to datetime
        if not df.empty and 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def save_data(sheet, df):
    """Save data to Google Sheet"""
    try:
        set_with_dataframe(sheet, df)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def initialize_sheet(sheet):
    """Initialize the Google Sheet with headers if empty"""
    try:
        df = load_data(sheet)
        if df.empty or len(df.columns) == 0:
            # Create initial structure
            initial_data = pd.DataFrame(columns=[
                'Date', 'Weight (kg)', 'Body Fat %', 'Muscle Mass (kg)',
                'Waist (cm)', 'Chest (cm)', 'Arms (cm)', 'Thighs (cm)',
                'Cardio Minutes', 'Strength Training Minutes', 'Steps',
                'Calories Consumed', 'Water (L)', 'Sleep Hours', 'Notes'
            ])
            save_data(sheet, initial_data)
            return initial_data
        return df
    except Exception as e:
        st.error(f"Error initializing sheet: {e}")
        return pd.DataFrame()

def calculate_bmi(weight, height):
    """Calculate BMI"""
    if weight and height:
        return weight / ((height / 100) ** 2)
    return None

def calculate_lean_mass(weight, body_fat_pct):
    """Calculate lean body mass"""
    if weight and body_fat_pct:
        return weight * (1 - body_fat_pct / 100)
    return None

# Main app
st.markdown('<div class="main-header">💪 Fitness & Body Composition Tracker</div>', unsafe_allow_html=True)

# Sidebar for Google Sheets connection
with st.sidebar:
    st.header("🔗 Google Sheets Connection")
    
    st.markdown("""
    ### Setup Instructions:
    1. Create a Google Cloud Project
    2. Enable Google Sheets API
    3. Create a Service Account
    4. Download the JSON credentials
    5. Share your Google Sheet with the service account email
    """)
    
    sheet_url = st.text_input("Google Sheet URL", 
                              placeholder="https://docs.google.com/spreadsheets/d/...")
    
    credentials_file = st.file_uploader("Upload Service Account JSON", type=['json'])
    
    if st.button("Connect to Google Sheets"):
        if sheet_url and credentials_file:
            import json
            credentials_json = json.load(credentials_file)
            sheet, error = connect_to_google_sheets(sheet_url, credentials_json)
            
            if error:
                st.error(f"Connection failed: {error}")
            else:
                st.session_state.sheet = sheet
                st.session_state.connected = True
                st.session_state.data = initialize_sheet(sheet)
                st.success("✅ Connected successfully!")
                st.rerun()
        else:
            st.warning("Please provide both Sheet URL and credentials file")
    
    if st.session_state.connected:
        st.success("✅ Connected to Google Sheets")
        if st.button("Refresh Data"):
            st.session_state.data = load_data(st.session_state.sheet)
            st.rerun()

# Main content area
if not st.session_state.connected:
    st.info("👈 Please connect to your Google Sheet using the sidebar to get started")
    
    # Show sample interface
    st.subheader("Sample Interface Preview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Weight", "- kg")
    with col2:
        st.metric("Body Fat %", "- %")
    with col3:
        st.metric("BMI", "-")
    
    st.markdown("---")
    st.info("Connect your Google Sheet to start tracking your fitness journey!")

else:
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Entry", "📈 Progress Charts", "📋 Data Table"])
    
    # Load current data
    df = st.session_state.data
    
    with tab1:
        st.header("Dashboard")
        
        if not df.empty and 'Date' in df.columns:
            # Filter out rows with NaN dates
            df_clean = df.dropna(subset=['Date'])
            
            if not df_clean.empty:
                # Get latest entry
                latest = df_clean.iloc[-1]
                
                # Display key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    weight = latest.get('Weight (kg)', 0)
                    st.metric("Current Weight", f"{weight:.1f} kg" if pd.notna(weight) else "N/A")
                
                with col2:
                    bf = latest.get('Body Fat %', 0)
                    st.metric("Body Fat %", f"{bf:.1f}%" if pd.notna(bf) else "N/A")
                
                with col3:
                    if pd.notna(weight) and pd.notna(bf):
                        lean = calculate_lean_mass(weight, bf)
                        st.metric("Lean Mass", f"{lean:.1f} kg" if lean else "N/A")
                    else:
                        st.metric("Lean Mass", "N/A")
                
                with col4:
                    muscle = latest.get('Muscle Mass (kg)', 0)
                    st.metric("Muscle Mass", f"{muscle:.1f} kg" if pd.notna(muscle) else "N/A")
                
                st.markdown("---")
                
                # Recent measurements
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Body Measurements")
                    waist = latest.get('Waist (cm)', 0)
                    chest = latest.get('Chest (cm)', 0)
                    arms = latest.get('Arms (cm)', 0)
                    thighs = latest.get('Thighs (cm)', 0)
                    
                    st.write(f"**Waist:** {waist:.1f} cm" if pd.notna(waist) else "**Waist:** N/A")
                    st.write(f"**Chest:** {chest:.1f} cm" if pd.notna(chest) else "**Chest:** N/A")
                    st.write(f"**Arms:** {arms:.1f} cm" if pd.notna(arms) else "**Arms:** N/A")
                    st.write(f"**Thighs:** {thighs:.1f} cm" if pd.notna(thighs) else "**Thighs:** N/A")
                
                with col2:
                    st.subheader("Activity & Lifestyle")
                    cardio = latest.get('Cardio Minutes', 0)
                    strength = latest.get('Strength Training Minutes', 0)
                    steps = latest.get('Steps', 0)
                    water = latest.get('Water (L)', 0)
                    sleep = latest.get('Sleep Hours', 0)
                    
                    st.write(f"**Cardio:** {cardio:.0f} min" if pd.notna(cardio) else "**Cardio:** N/A")
                    st.write(f"**Strength:** {strength:.0f} min" if pd.notna(strength) else "**Strength:** N/A")
                    st.write(f"**Steps:** {steps:.0f}" if pd.notna(steps) else "**Steps:** N/A")
                    st.write(f"**Water:** {water:.1f} L" if pd.notna(water) else "**Water:** N/A")
                    st.write(f"**Sleep:** {sleep:.1f} hrs" if pd.notna(sleep) else "**Sleep:** N/A")
            else:
                st.info("No data entries yet. Add your first entry in the 'Add Entry' tab!")
        else:
            st.info("No data available. Add your first entry in the 'Add Entry' tab!")
    
    with tab2:
        st.header("Add New Entry")
        
        with st.form("entry_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Body Composition")
                entry_date = st.date_input("Date", datetime.now())
                weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1)
                body_fat = st.number_input("Body Fat %", min_value=0.0, max_value=100.0, step=0.1)
                muscle_mass = st.number_input("Muscle Mass (kg)", min_value=0.0, max_value=200.0, step=0.1)
                
                st.subheader("Measurements")
                waist = st.number_input("Waist (cm)", min_value=0.0, max_value=300.0, step=0.1)
                chest = st.number_input("Chest (cm)", min_value=0.0, max_value=300.0, step=0.1)
                arms = st.number_input("Arms (cm)", min_value=0.0, max_value=100.0, step=0.1)
                thighs = st.number_input("Thighs (cm)", min_value=0.0, max_value=150.0, step=0.1)
            
            with col2:
                st.subheader("Activity")
                cardio = st.number_input("Cardio Minutes", min_value=0, max_value=1440, step=1)
                strength = st.number_input("Strength Training Minutes", min_value=0, max_value=1440, step=1)
                steps = st.number_input("Steps", min_value=0, max_value=100000, step=100)
                
                st.subheader("Nutrition & Lifestyle")
                calories = st.number_input("Calories Consumed", min_value=0, max_value=10000, step=50)
                water = st.number_input("Water (L)", min_value=0.0, max_value=20.0, step=0.1)
                sleep = st.number_input("Sleep Hours", min_value=0.0, max_value=24.0, step=0.1)
                
                notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("Save Entry")
            
            if submitted:
                new_entry = pd.DataFrame([{
                    'Date': entry_date,
                    'Weight (kg)': weight if weight > 0 else None,
                    'Body Fat %': body_fat if body_fat > 0 else None,
                    'Muscle Mass (kg)': muscle_mass if muscle_mass > 0 else None,
                    'Waist (cm)': waist if waist > 0 else None,
                    'Chest (cm)': chest if chest > 0 else None,
                    'Arms (cm)': arms if arms > 0 else None,
                    'Thighs (cm)': thighs if thighs > 0 else None,
                    'Cardio Minutes': cardio if cardio > 0 else None,
                    'Strength Training Minutes': strength if strength > 0 else None,
                    'Steps': steps if steps > 0 else None,
                    'Calories Consumed': calories if calories > 0 else None,
                    'Water (L)': water if water > 0 else None,
                    'Sleep Hours': sleep if sleep > 0 else None,
                    'Notes': notes if notes else None
                }])
                
                # Append to existing data
                df = pd.concat([df, new_entry], ignore_index=True)
                
                # Save to Google Sheets
                if save_data(st.session_state.sheet, df):
                    st.session_state.data = df
                    st.success("✅ Entry saved successfully!")
                    st.rerun()
    
    with tab3:
        st.header("Progress Charts")
        
        if not df.empty and 'Date' in df.columns:
            df_clean = df.dropna(subset=['Date']).copy()
            
            if len(df_clean) > 0:
                # Date range filter
                col1, col2 = st.columns(2)
                with col1:
                    days_back = st.selectbox("Time Period", 
                                            [30, 60, 90, 180, 365, "All Time"],
                                            index=2)
                
                if days_back != "All Time":
                    cutoff_date = datetime.now() - timedelta(days=days_back)
                    df_filtered = df_clean[df_clean['Date'] >= cutoff_date]
                else:
                    df_filtered = df_clean
                
                if len(df_filtered) > 0:
                    # Weight and Body Fat Chart
                    fig1 = go.Figure()
                    
                    if 'Weight (kg)' in df_filtered.columns:
                        fig1.add_trace(go.Scatter(
                            x=df_filtered['Date'],
                            y=df_filtered['Weight (kg)'],
                            name='Weight (kg)',
                            line=dict(color='blue', width=2)
                        ))
                    
                    if 'Body Fat %' in df_filtered.columns:
                        fig1.add_trace(go.Scatter(
                            x=df_filtered['Date'],
                            y=df_filtered['Body Fat %'],
                            name='Body Fat %',
                            yaxis='y2',
                            line=dict(color='red', width=2)
                        ))
                    
                    fig1.update_layout(
                        title='Weight & Body Fat Progress',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Weight (kg)', titlefont=dict(color='blue')),
                        yaxis2=dict(title='Body Fat %', overlaying='y', side='right', titlefont=dict(color='red')),
                        hovermode='x unified',
                        height=400
                    )
                    
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Body Measurements Chart
                    measurements = ['Waist (cm)', 'Chest (cm)', 'Arms (cm)', 'Thighs (cm)']
                    fig2 = go.Figure()
                    
                    for measurement in measurements:
                        if measurement in df_filtered.columns:
                            fig2.add_trace(go.Scatter(
                                x=df_filtered['Date'],
                                y=df_filtered[measurement],
                                name=measurement,
                                mode='lines+markers'
                            ))
                    
                    fig2.update_layout(
                        title='Body Measurements',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Measurement (cm)'),
                        hovermode='x unified',
                        height=400
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # Activity Chart
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'Steps' in df_filtered.columns:
                            fig3 = px.bar(df_filtered, x='Date', y='Steps', 
                                         title='Daily Steps')
                            fig3.update_layout(height=300)
                            st.plotly_chart(fig3, use_container_width=True)
                    
                    with col2:
                        if 'Water (L)' in df_filtered.columns:
                            fig4 = px.bar(df_filtered, x='Date', y='Water (L)', 
                                         title='Water Intake (L)')
                            fig4.update_layout(height=300)
                            st.plotly_chart(fig4, use_container_width=True)
                    
                    # Sleep and Calories
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'Sleep Hours' in df_filtered.columns:
                            fig5 = px.line(df_filtered, x='Date', y='Sleep Hours', 
                                          title='Sleep Hours', markers=True)
                            fig5.update_layout(height=300)
                            st.plotly_chart(fig5, use_container_width=True)
                    
                    with col2:
                        if 'Calories Consumed' in df_filtered.columns:
                            fig6 = px.bar(df_filtered, x='Date', y='Calories Consumed', 
                                         title='Daily Calories')
                            fig6.update_layout(height=300)
                            st.plotly_chart(fig6, use_container_width=True)
                else:
                    st.info("No data available for the selected time period.")
            else:
                st.info("Not enough data to display charts. Add more entries!")
        else:
            st.info("No data available. Add your first entry in the 'Add Entry' tab!")
    
    with tab4:
        st.header("Data Table")
        
        if not df.empty:
            # Display the dataframe
            st.dataframe(df, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name=f"fitness_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data available.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
    <small>Fitness & Body Composition Tracker | Track your progress consistently! 💪</small>
    </div>
""", unsafe_allow_html=True)
