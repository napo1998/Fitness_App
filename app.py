import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import numpy as np


# Page configuration
st.set_page_config(
    page_title="Winter Arc Challenge 2025 by Arturo Boquin",
    page_icon="❄️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .gold { color: #FFD700; font-size: 2rem; }
    .silver { color: #C0C0C0; font-size: 1.8rem; }
    .bronze { color: #CD7F32; font-size: 1.6rem; }
    .penalty { color: #ff4444; font-weight: bold; }
    .bonus { color: #44ff44; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Data file path
DATA_FILE = 'fitness_competition_data.csv'
CLEANED_FILE = 'fitness_competition_data_cleaned.csv'

def initialize_data():
    """Initialize or load existing data"""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            df['Date'] = pd.to_datetime(df['Date'])
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return create_empty_dataframe()
    else:
        return create_empty_dataframe()

def create_empty_dataframe():
    """Create empty dataframe with proper structure"""
    return pd.DataFrame(columns=[
        'Date', 'User', 'Goal', 'Weight (kg)', 'Body Fat %', 
        'Muscle Mass (kg)', 'Fat Mass (kg)',
        'Waist (cm)', 'Chest (cm)', 'Arms (cm)', 'Thighs (cm)',
        'Cardio Minutes', 'Strength Training Minutes', 'Steps',
        'Calories Consumed', 'Protein (g)', 'Water (L)', 'Sleep Hours', 'Notes'
    ])

def load_user_goals():
    """Load user goals from file"""
    goals_file = 'user_goals.csv'
    if os.path.exists(goals_file):
        try:
            return pd.read_csv(goals_file)
        except Exception as e:
            st.warning(f"Error loading goals: {e}")
            return pd.DataFrame(columns=['User', 'Target Fat Mass (kg)', 'Target Muscle Mass (kg)', 
                                        'Target Body Fat %', 'Target Weight (kg)', 'Weeks'])
    return pd.DataFrame(columns=['User', 'Target Fat Mass (kg)', 'Target Muscle Mass (kg)', 
                                 'Target Body Fat %', 'Target Weight (kg)', 'Weeks'])

def save_user_goals(goals_df):
    """Save user goals to file"""
    try:
        goals_df.to_csv('user_goals.csv', index=False)
        return True
    except Exception as e:
        st.error(f"Error saving goals: {e}")
        return False

def get_user_goals(user):
    """Get goals for specific user"""
    goals_df = load_user_goals()
    if user in goals_df['User'].values:
        return goals_df[goals_df['User'] == user].iloc[0]
    return None

def save_data(df):
    """Save dataframe to CSV"""
    try:
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False
        return False

def calculate_fat_mass(weight, body_fat_pct):
    """Calculate fat mass"""
    if pd.notna(weight) and pd.notna(body_fat_pct):
        return weight * (body_fat_pct / 100)
    return None

def calculate_muscle_mass_from_data(weight, fat_mass):
    """Calculate muscle mass from weight and fat mass"""
    if pd.notna(weight) and pd.notna(fat_mass):
        return weight - fat_mass
    return None

def calculate_moving_average(series, window=3):
    """Calculate moving average (3-week default)"""
    return series.rolling(window=window, min_periods=1).mean()

def get_baseline(df_user, metric, baseline_weeks=3):
    """Get baseline (average of first 3 weeks)"""
    if len(df_user) == 0:
        return None
    
    df_sorted = df_user.sort_values('Date')
    
    # Get first baseline_weeks weeks of data
    first_date = df_sorted['Date'].min()
    baseline_cutoff = first_date + timedelta(weeks=baseline_weeks)
    baseline_data = df_sorted[df_sorted['Date'] <= baseline_cutoff]
    
    if len(baseline_data) == 0:
        return None
    
    return baseline_data[metric].mean()

def calculate_normalized_progress(current_ma, baseline, invert=False):
    """Calculate normalized progress percentage"""
    if pd.isna(current_ma) or pd.isna(baseline) or baseline == 0:
        return 0
    
    progress = ((current_ma - baseline) / baseline) * 100
    
    if invert:  # For fat loss, less is better
        progress = -progress
    
    return progress

def calculate_penalty(df_user, goal):
    """Calculate penalty for goal deviation"""
    if len(df_user) < 2:
        return 0
    
    df_sorted = df_user.sort_values('Date')
    latest = df_sorted.iloc[-1]
    baseline_bf = get_baseline(df_user, 'Body Fat %')
    baseline_muscle = get_baseline(df_user, 'Muscle Mass (kg)')
    
    penalty = 0
    
    if goal == "Clean Bulk":
        # Penalize if body fat increases too much
        if pd.notna(latest['Body Fat %']) and pd.notna(baseline_bf):
            bf_change = latest['Body Fat %'] - baseline_bf
            if bf_change > 3:  # More than 3% increase
                penalty = 30
    
    elif goal == "Fat Loss":
        # Penalize if muscle mass drops too much
        if pd.notna(latest['Muscle Mass (kg)']) and pd.notna(baseline_muscle):
            muscle_loss_pct = ((latest['Muscle Mass (kg)'] - baseline_muscle) / baseline_muscle) * 100
            if muscle_loss_pct < -5:  # More than 5% muscle loss
                penalty = 30
    
    return penalty

def calculate_user_score(df_user, goal):
    """Calculate score for a user based on their goal"""
    if len(df_user) < 2:
        return {
            'score': 0,
            'primary_progress': 0,
            'secondary_progress': 0,
            'penalty': 0,
            'weeks_tracked': 0,
            'baseline_primary': 0,
            'current_primary': 0
        }
    
    df_sorted = df_user.sort_values('Date')
    
    # Calculate moving averages
    if goal == "Fat Loss":
        primary_metric = 'Fat Mass (kg)'
        secondary_metric = 'Muscle Mass (kg)'
    elif goal == "Clean Bulk":
        primary_metric = 'Muscle Mass (kg)'
        secondary_metric = 'Body Fat %'
    else:  # Recomposition
        primary_metric = 'Muscle Mass (kg)'
        secondary_metric = 'Fat Mass (kg)'
    
    # Get latest moving average
    df_sorted['Primary_MA'] = calculate_moving_average(df_sorted[primary_metric], window=3)
    df_sorted['Secondary_MA'] = calculate_moving_average(df_sorted[secondary_metric], window=3)
    
    latest = df_sorted.iloc[-1]
    current_primary_ma = latest['Primary_MA']
    current_secondary_ma = latest['Secondary_MA']
    
    # Get baselines
    baseline_primary = get_baseline(df_user, primary_metric)
    baseline_secondary = get_baseline(df_user, secondary_metric)
    
    # Calculate progress
    if goal == "Recomposition":
        # Composite score
        muscle_progress = calculate_normalized_progress(current_primary_ma, baseline_primary, invert=False)
        fat_progress = calculate_normalized_progress(current_secondary_ma, baseline_secondary, invert=True)
        primary_progress = muscle_progress
        secondary_progress = fat_progress
        raw_score = muscle_progress + fat_progress
    else:
        # Single KPI
        invert = (goal == "Fat Loss")
        primary_progress = calculate_normalized_progress(current_primary_ma, baseline_primary, invert=invert)
        
        if goal == "Fat Loss":
            secondary_progress = calculate_normalized_progress(current_secondary_ma, baseline_secondary, invert=False)
        else:
            secondary_progress = calculate_normalized_progress(current_secondary_ma, baseline_secondary, invert=False)
        
        raw_score = primary_progress
    
    # Calculate penalty
    penalty = calculate_penalty(df_user, goal)
    
    # Final score
    final_score = raw_score * (1 - penalty / 100)
    
    weeks_tracked = len(df_sorted) / 7  # Approximate weeks
    
    return {
        'score': final_score,
        'primary_progress': primary_progress,
        'secondary_progress': secondary_progress,
        'penalty': penalty,
        'weeks_tracked': weeks_tracked,
        'baseline_primary': baseline_primary,
        'current_primary': current_primary_ma
    }

def get_rankings(df):
    """Calculate rankings for all users"""
    if df.empty:
        return pd.DataFrame()
    
    users = df['User'].unique()
    rankings = []
    
    for user in users:
        df_user = df[df['User'] == user]
        
        if len(df_user) == 0:
            continue
        
        # Get user's goal
        goal = df_user['Goal'].iloc[-1]
        
        # Calculate score
        score_data = calculate_user_score(df_user, goal)
        
        rankings.append({
            'User': user,
            'Goal': goal,
            'Score': score_data['score'],
            'Primary Progress (%)': score_data['primary_progress'],
            'Secondary Progress (%)': score_data['secondary_progress'],
            'Penalty (%)': score_data['penalty'],
            'Weeks Tracked': score_data['weeks_tracked'],
            'Entries': len(df_user)
        })
    
    rankings_df = pd.DataFrame(rankings)
    
    if not rankings_df.empty:
        rankings_df = rankings_df.sort_values('Score', ascending=False).reset_index(drop=True)
        rankings_df['Rank'] = range(1, len(rankings_df) + 1)
    
    return rankings_df

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = initialize_data()

# Main app
st.markdown('<div class="main-header">❄️ Winter Arc Challenge 2025</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("👤 User Settings")
    
    # User selection/creation
    existing_users = st.session_state.data['User'].unique().tolist() if not st.session_state.data.empty else []
    
    user_option = st.radio("Select option:", ["Existing User", "New User"])
    
    if user_option == "Existing User" and existing_users:
        current_user = st.selectbox("Select User", existing_users)
    else:
        current_user = st.text_input("Enter Username", value="")
    
    st.markdown("---")
    
    # Goal selection
    st.subheader("🎯 Your Goal")
    user_goal = st.selectbox(
        "Competition Goal",
        ["Fat Loss", "Clean Bulk", "Recomposition"],
        help="Fat Loss: Minimize fat mass | Clean Bulk: Maximize muscle | Recomposition: Both"
    )
    
    st.markdown("---")
    
    # Profile
    st.subheader("📊 Profile Info")
    user_height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
    user_age = st.number_input("Age", min_value=10, max_value=120, value=30, step=1)
    user_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    
    st.markdown("---")
    
    # Data management
    st.subheader("📊 Data Management")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.data = initialize_data()
        st.rerun()

    if st.button("🧹 Clean Data", use_container_width=True):
        try:
            cleaned = clean_dataframe(st.session_state.data)
            # Save cleaned to a separate file and update session data
            saved = save_cleaned(cleaned, CLEANED_FILE)
            st.session_state.data = cleaned
            # Overwrite original persistent file as well
            save_data(st.session_state.data)
            if saved:
                st.success(f"🧹 Data cleaned and saved to {CLEANED_FILE}")
            else:
                st.warning("🧹 Data cleaned in memory, but failed to save cleaned CSV file.")
            st.rerun()
        except Exception as e:
            st.error(f"Error cleaning data: {e}")
    
    if not st.session_state.data.empty:
        csv = st.session_state.data.to_csv(index=False)
        st.download_button(
            label="📥 Download All Data",
            data=csv,
            file_name=f"competition_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file is not None:
        try:
            new_data = pd.read_csv(uploaded_file)
            new_data['Date'] = pd.to_datetime(new_data['Date'])
            st.session_state.data = new_data
            save_data(st.session_state.data)
            st.success("✅ Data imported!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏆 Rankings", "📊 My Progress", "➕ Add Entry", "📈 Charts", "📋 Data", "🎯 My Goals"])

df = st.session_state.data

with tab1:
    st.header("❄️ Winter Arc Challenge Rankings")
    
    if not df.empty:
        rankings = get_rankings(df)
        
        if not rankings.empty:
            # Top 3 podium
            st.subheader("🥇 Top 3")
            cols = st.columns(3)
            
            medals = ["🥇", "🥈", "🥉"]
            colors = ["gold", "silver", "bronze"]
            
            for i in range(min(3, len(rankings))):
                with cols[i]:
                    user_data = rankings.iloc[i]
                    st.markdown(f"<div class='{colors[i]}'>{medals[i]} {user_data['User']}</div>", unsafe_allow_html=True)
                    st.metric("Score", f"{user_data['Score']:.2f}")
                    st.caption(f"Goal: {user_data['Goal']}")
                    if user_data['Penalty (%)'] > 0:
                        st.markdown(f"<span class='penalty'>⚠️ Penalty: {user_data['Penalty (%)']}%</span>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Full rankings table
            st.subheader("📊 Full Rankings")
            
            # Format the display
            display_df = rankings[['Rank', 'User', 'Goal', 'Score', 'Primary Progress (%)', 
                                   'Secondary Progress (%)', 'Penalty (%)', 'Weeks Tracked']].copy()
            
            # Color code scores
            def color_score(val):
                if val > 5:
                    return 'background-color: #d4edda'
                elif val > 2:
                    return 'background-color: #fff3cd'
                elif val < 0:
                    return 'background-color: #f8d7da'
                return ''
            
            styled_df = display_df.style.applymap(color_score, subset=['Score'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Weekly progress chart
            st.subheader("📈 Score Evolution")
            
            fig = go.Figure()
            
            for user in df['User'].unique():
                df_user = df[df['User'] == user].sort_values('Date')
                
                if len(df_user) < 2:
                    continue
                
                goal = df_user['Goal'].iloc[-1]
                scores = []
                dates = []
                
                for i in range(len(df_user)):
                    df_subset = df_user.iloc[:i+1]
                    score_data = calculate_user_score(df_subset, goal)
                    scores.append(score_data['score'])
                    dates.append(df_subset['Date'].iloc[-1])
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=scores,
                    name=user,
                    mode='lines+markers',
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Score",
                hovermode='x unified',
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("No rankings available yet. Add data to see rankings!")
    else:
        st.info("No data available. Start adding entries to see rankings!")

with tab2:
    st.header("📊 My Progress")
    
    if not current_user:
        st.warning("Please enter a username in the sidebar")
    else:
        df_user = df[df['User'] == current_user]
        
        if not df_user.empty:
            # Calculate current score
            score_data = calculate_user_score(df_user, user_goal)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Your Score", f"{score_data['score']:.2f}")
            
            with col2:
                st.metric("Primary Progress", f"{score_data['primary_progress']:.2f}%")
            
            with col3:
                st.metric("Secondary Progress", f"{score_data['secondary_progress']:.2f}%")
            
            with col4:
                if score_data['penalty'] > 0:
                    st.markdown(f"<span class='penalty'>⚠️ Penalty: {score_data['penalty']}%</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='bonus'>✅ No Penalty</span>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Goal-specific info
            st.subheader(f"🎯 {user_goal} Progress")
            
            if user_goal == "Fat Loss":
                col1, col2 = st.columns(2)
                with col1:
                    st.info("**Primary KPI**: Fat Mass (kg) ⬇️")
                    st.write(f"Baseline: {score_data['baseline_primary']:.2f} kg")
                    st.write(f"Current (3-week MA): {score_data['current_primary']:.2f} kg")
                with col2:
                    st.warning("**Watch**: Muscle Mass (maintain)")
                    if score_data['penalty'] > 0:
                        st.error("⚠️ Too much muscle loss detected!")
            
            elif user_goal == "Clean Bulk":
                col1, col2 = st.columns(2)
                with col1:
                    st.info("**Primary KPI**: Muscle Mass (kg) ⬆️")
                    st.write(f"Baseline: {score_data['baseline_primary']:.2f} kg")
                    st.write(f"Current (3-week MA): {score_data['current_primary']:.2f} kg")
                with col2:
                    st.warning("**Watch**: Body Fat % (controlled)")
                    if score_data['penalty'] > 0:
                        st.error("⚠️ Body fat increasing too fast!")
            
            else:  # Recomposition
                col1, col2 = st.columns(2)
                with col1:
                    st.info("**KPI 1**: Muscle Mass (kg) ⬆️")
                    st.write(f"Progress: {score_data['primary_progress']:.2f}%")
                with col2:
                    st.info("**KPI 2**: Fat Mass (kg) ⬇️")
                    st.write(f"Progress: {score_data['secondary_progress']:.2f}%")
            
            st.markdown("---")
            
            # Ranking position
            rankings = get_rankings(df)
            if not rankings.empty:
                user_rank = rankings[rankings['User'] == current_user]
                if not user_rank.empty:
                    rank = user_rank['Rank'].iloc[0]
                    total = len(rankings)
                    st.subheader(f"📍 Your Position: #{rank} of {total}")
                    
                    # Progress bar
                    percentile = ((total - rank) / total) * 100
                    st.progress(percentile / 100)
                    st.caption(f"Top {100 - percentile:.0f}%")
        else:
            st.info(f"No data for {current_user}. Add your first entry!")

with tab3:
    st.header("➕ Add New Entry")
    
    if not current_user:
        st.warning("⚠️ Please enter a username in the sidebar first!")
    else:
        with st.form("entry_form", clear_on_submit=True):
            st.info(f"Adding entry for: **{current_user}** | Goal: **{user_goal}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📅 Date & Body Composition")
                entry_date = st.date_input("Date", datetime.now())
                weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=0.0, step=0.1)
                body_fat = st.number_input("Body Fat %", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                muscle_mass = st.number_input("Muscle Mass (kg)", min_value=0.0, max_value=200.0, value=0.0, step=0.1)
                
                st.subheader("📏 Measurements")
                waist = st.number_input("Waist (cm)", min_value=0.0, max_value=300.0, value=0.0, step=0.1)
                chest = st.number_input("Chest (cm)", min_value=0.0, max_value=300.0, value=0.0, step=0.1)
                arms = st.number_input("Arms (cm)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                thighs = st.number_input("Thighs (cm)", min_value=0.0, max_value=150.0, value=0.0, step=0.1)
            
            with col2:
                st.subheader("🏃 Activity")
                cardio = st.number_input("Cardio Minutes", min_value=0, max_value=1440, value=0, step=5)
                strength = st.number_input("Strength Training Minutes", min_value=0, max_value=1440, value=0, step=5)
                steps = st.number_input("Steps", min_value=0, max_value=100000, value=0, step=100)
                
                st.subheader("🍎 Nutrition & Lifestyle")
                calories = st.number_input("Calories", min_value=0, max_value=10000, value=0, step=50)
                protein = st.number_input("Protein (g)", min_value=0, max_value=500, value=0, step=5)
                water = st.number_input("Water (L)", min_value=0.0, max_value=20.0, value=0.0, step=0.1)
                sleep = st.number_input("Sleep Hours", min_value=0.0, max_value=24.0, value=0.0, step=0.1)
                
                notes = st.text_area("Notes", placeholder="How are you feeling? Training notes, energy levels...")
            
            submitted = st.form_submit_button("💾 Save Entry", use_container_width=True)
            
            if submitted:
                # Validate that at least one metric is entered
                has_data = any([
                    weight > 0, body_fat > 0, muscle_mass > 0,
                    waist > 0, chest > 0, arms > 0, thighs > 0,
                    cardio > 0, strength > 0, steps > 0,
                    calories > 0, protein > 0, water > 0, sleep > 0,
                    notes.strip()
                ])
                
                if not has_data:
                    st.error("⚠️ Please enter at least one metric!")
                else:
                    # Calculate fat mass if we have weight and body fat
                    fat_mass = calculate_fat_mass(weight, body_fat) if weight > 0 and body_fat > 0 else None
                    
                    # If muscle mass not provided but we can calculate it
                    if muscle_mass == 0 and fat_mass and weight > 0:
                        muscle_mass = weight - fat_mass
                    
                    new_entry = pd.DataFrame([{
                        'Date': pd.to_datetime(entry_date),
                        'User': current_user,
                        'Goal': user_goal,
                        'Weight (kg)': weight if weight > 0 else None,
                        'Body Fat %': body_fat if body_fat > 0 else None,
                        'Muscle Mass (kg)': muscle_mass if muscle_mass > 0 else None,
                        'Fat Mass (kg)': fat_mass,
                        'Waist (cm)': waist if waist > 0 else None,
                        'Chest (cm)': chest if chest > 0 else None,
                        'Arms (cm)': arms if arms > 0 else None,
                        'Thighs (cm)': thighs if thighs > 0 else None,
                        'Cardio Minutes': cardio if cardio > 0 else None,
                        'Strength Training Minutes': strength if strength > 0 else None,
                        'Steps': steps if steps > 0 else None,
                        'Calories Consumed': calories if calories > 0 else None,
                        'Protein (g)': protein if protein > 0 else None,
                        'Water (L)': water if water > 0 else None,
                        'Sleep Hours': sleep if sleep > 0 else None,
                        'Notes': notes if notes else None
                    }])
                    
                    st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
                    
                    if save_data(st.session_state.data):
                        st.success("✅ Entry saved successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to save entry. Please check your input and try again.")


with tab4:
    st.header("📈 Progress Charts")
    
    if not current_user:
        st.warning("Please select a user in the sidebar")
    else:
        df_user = df[df['User'] == current_user].sort_values('Date')
        
        if not df_user.empty and len(df_user) > 1:
            # Primary KPI chart
            st.subheader(f"🎯 {user_goal} - Primary Metric")
            
            fig = go.Figure()
            
            if user_goal == "Fat Loss":
                metric = 'Fat Mass (kg)'
                color = '#ef4444'
            elif user_goal == "Clean Bulk":
                metric = 'Muscle Mass (kg)'
                color = '#10b981'
            else:
                metric = 'Muscle Mass (kg)'
                color = '#8b5cf6'
            
            # Actual values
            fig.add_trace(go.Scatter(
                x=df_user['Date'],
                y=df_user[metric],
                name='Actual',
                mode='markers',
                marker=dict(size=8, color=color, opacity=0.6)
            ))
            
            # Moving average
            ma = calculate_moving_average(df_user[metric], window=3)
            fig.add_trace(go.Scatter(
                x=df_user['Date'],
                y=ma,
                name='3-Week MA',
                mode='lines',
                line=dict(color=color, width=3)
            ))
            
            # Baseline
            baseline = get_baseline(df_user, metric)
            if baseline:
                fig.add_hline(
                    y=baseline,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=f"Baseline: {baseline:.2f}"
                )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title=metric,
                height=400,
                template='plotly_white',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Composite chart for recomposition
            if user_goal == "Recomposition":
                st.subheader("📊 Muscle vs Fat")
                
                fig2 = go.Figure()
                
                fig2.add_trace(go.Scatter(
                    x=df_user['Date'],
                    y=calculate_moving_average(df_user['Muscle Mass (kg)'], window=3),
                    name='Muscle Mass (MA)',
                    line=dict(color='#10b981', width=3)
                ))
                
                fig2.add_trace(go.Scatter(
                    x=df_user['Date'],
                    y=calculate_moving_average(df_user['Fat Mass (kg)'], window=3),
                    name='Fat Mass (MA)',
                    yaxis='y2',
                    line=dict(color='#ef4444', width=3)
                ))
                
                fig2.update_layout(
                    xaxis_title="Date",
                    yaxis=dict(title='Muscle Mass (kg)', titlefont=dict(color='#10b981')),
                    yaxis2=dict(
                        title='Fat Mass (kg)',
                        overlaying='y',
                        side='right',
                        titlefont=dict(color='#ef4444')
                    ),
                    height=400,
                    template='plotly_white',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            # Body measurements
            st.subheader("📏 Body Measurements")
            
            fig3 = go.Figure()
            
            measurements = ['Waist (cm)', 'Chest (cm)', 'Arms (cm)', 'Thighs (cm)']
            colors_meas = ['#8b5cf6', '#10b981', '#f59e0b', '#ec4899']
            
            for meas, color in zip(measurements, colors_meas):
                if meas in df_user.columns and df_user[meas].notna().any():
                    fig3.add_trace(go.Scatter(
                        x=df_user['Date'],
                        y=df_user[meas],
                        name=meas,
                        mode='lines+markers',
                        line=dict(color=color, width=2)
                    ))
            
            fig3.update_layout(
                xaxis_title="Date",
                yaxis_title="Measurement (cm)",
                height=400,
                template='plotly_white',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig3, use_container_width=True)
            
        else:
            st.info("Add more data entries to see charts (minimum 2 entries needed)")

with tab5:
    st.header("📋 Data Table")
    
    if not df.empty:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_user = st.selectbox("Filter by User", ["All"] + df['User'].unique().tolist())
        
        with col2:
            filter_goal = st.selectbox("Filter by Goal", ["All", "Fat Loss", "Clean Bulk", "Recomposition"])
        
        with col3:
            entries_show = st.selectbox("Entries to show", [25, 50, 100, "All"])
        
        # Apply filters
        df_filtered = df.copy()
        
        if filter_user != "All":
            df_filtered = df_filtered[df_filtered['User'] == filter_user]
        
        if filter_goal != "All":
            df_filtered = df_filtered[df_filtered['Goal'] == filter_goal]
        
        # Sort and limit
        df_filtered = df_filtered.sort_values('Date', ascending=False)
        
        if entries_show != "All":
            df_filtered = df_filtered.head(entries_show)
        
        # Format date
        df_display = df_filtered.copy()
        df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)

        # --- Edit existing entry UI ---
        st.markdown("---")
        st.subheader("✏️ Edit an Entry")

        if not df_filtered.empty:
            # Keep original index so we can update the master dataframe
            df_edit = df_filtered.reset_index()
            # Create readable labels for selection
            labels = df_edit.apply(lambda r: f"{r['Date'].strftime('%Y-%m-%d')} | {r['User']} | {str(r.get('Notes',''))[:30]}", axis=1).tolist()
            labels = [l if l is not None else str(i) for i, l in enumerate(labels)]

            selected = st.selectbox("Select entry to edit", ["None"] + labels)

            if selected and selected != "None":
                sel_idx = labels.index(selected)
                orig_index = int(df_edit.loc[sel_idx, 'index'])
                entry = df.loc[orig_index]

                with st.form("edit_entry_form"):
                    col1e, col2e = st.columns(2)
                    with col1e:
                        edit_date = st.date_input("Date", entry['Date'].date() if pd.notna(entry['Date']) else datetime.now())
                        edit_user = st.text_input("User", entry['User'] if pd.notna(entry['User']) else "")
                        edit_goal = st.selectbox("Goal", ["Fat Loss", "Clean Bulk", "Recomposition"], index=["Fat Loss","Clean Bulk","Recomposition"].index(entry['Goal']) if pd.notna(entry.get('Goal')) else 0)
                        edit_weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=float(entry['Weight (kg)']) if pd.notna(entry['Weight (kg)']) else 0.0, step=0.1)
                        edit_body_fat = st.number_input("Body Fat %", min_value=0.0, max_value=100.0, value=float(entry['Body Fat %']) if pd.notna(entry['Body Fat %']) else 0.0, step=0.1)
                        edit_muscle = st.number_input("Muscle Mass (kg)", min_value=0.0, max_value=200.0, value=float(entry['Muscle Mass (kg)']) if pd.notna(entry['Muscle Mass (kg)']) else 0.0, step=0.1)
                        edit_fat_mass = st.number_input("Fat Mass (kg)", min_value=0.0, max_value=200.0, value=float(entry['Fat Mass (kg)']) if pd.notna(entry['Fat Mass (kg)']) else 0.0, step=0.1)
                    with col2e:
                        edit_waist = st.number_input("Waist (cm)", min_value=0.0, max_value=300.0, value=float(entry['Waist (cm)']) if pd.notna(entry['Waist (cm)']) else 0.0, step=0.1)
                        edit_chest = st.number_input("Chest (cm)", min_value=0.0, max_value=300.0, value=float(entry['Chest (cm)']) if pd.notna(entry['Chest (cm)']) else 0.0, step=0.1)
                        edit_arms = st.number_input("Arms (cm)", min_value=0.0, max_value=100.0, value=float(entry['Arms (cm)']) if pd.notna(entry['Arms (cm)']) else 0.0, step=0.1)
                        edit_thighs = st.number_input("Thighs (cm)", min_value=0.0, max_value=150.0, value=float(entry['Thighs (cm)']) if pd.notna(entry['Thighs (cm)']) else 0.0, step=0.1)
                        edit_cardio = st.number_input("Cardio Minutes", min_value=0, max_value=1440, value=int(entry['Cardio Minutes']) if pd.notna(entry['Cardio Minutes']) else 0, step=5)
                        edit_strength = st.number_input("Strength Training Minutes", min_value=0, max_value=1440, value=int(entry['Strength Training Minutes']) if pd.notna(entry['Strength Training Minutes']) else 0, step=5)
                        edit_steps = st.number_input("Steps", min_value=0, max_value=100000, value=int(entry['Steps']) if pd.notna(entry['Steps']) else 0, step=100)
                        edit_calories = st.number_input("Calories Consumed", min_value=0, max_value=10000, value=int(entry['Calories Consumed']) if pd.notna(entry['Calories Consumed']) else 0, step=50)
                        edit_protein = st.number_input("Protein (g)", min_value=0, max_value=500, value=int(entry['Protein (g)']) if pd.notna(entry['Protein (g)']) else 0, step=5)
                        edit_water = st.number_input("Water (L)", min_value=0.0, max_value=20.0, value=float(entry['Water (L)']) if pd.notna(entry['Water (L)']) else 0.0, step=0.1)
                        edit_sleep = st.number_input("Sleep Hours", min_value=0.0, max_value=24.0, value=float(entry['Sleep Hours']) if pd.notna(entry['Sleep Hours']) else 0.0, step=0.1)
                        edit_notes = st.text_area("Notes", value=entry['Notes'] if pd.notna(entry.get('Notes')) else "")

                    save_changes = st.form_submit_button("💾 Save Changes")

                    if save_changes:
                        # Update the master dataframe
                        try:
                            df.loc[orig_index, 'Date'] = pd.to_datetime(edit_date)
                            df.loc[orig_index, 'User'] = edit_user
                            df.loc[orig_index, 'Goal'] = edit_goal
                            df.loc[orig_index, 'Weight (kg)'] = edit_weight if edit_weight > 0 else None
                            df.loc[orig_index, 'Body Fat %'] = edit_body_fat if edit_body_fat > 0 else None
                            df.loc[orig_index, 'Muscle Mass (kg)'] = edit_muscle if edit_muscle > 0 else None
                            df.loc[orig_index, 'Fat Mass (kg)'] = edit_fat_mass if edit_fat_mass > 0 else None
                            df.loc[orig_index, 'Waist (cm)'] = edit_waist if edit_waist > 0 else None
                            df.loc[orig_index, 'Chest (cm)'] = edit_chest if edit_chest > 0 else None
                            df.loc[orig_index, 'Arms (cm)'] = edit_arms if edit_arms > 0 else None
                            df.loc[orig_index, 'Thighs (cm)'] = edit_thighs if edit_thighs > 0 else None
                            df.loc[orig_index, 'Cardio Minutes'] = edit_cardio if edit_cardio > 0 else None
                            df.loc[orig_index, 'Strength Training Minutes'] = edit_strength if edit_strength > 0 else None
                            df.loc[orig_index, 'Steps'] = edit_steps if edit_steps > 0 else None
                            df.loc[orig_index, 'Calories Consumed'] = edit_calories if edit_calories > 0 else None
                            df.loc[orig_index, 'Protein (g)'] = edit_protein if edit_protein > 0 else None
                            df.loc[orig_index, 'Water (L)'] = edit_water if edit_water > 0 else None
                            df.loc[orig_index, 'Sleep Hours'] = edit_sleep if edit_sleep > 0 else None
                            df.loc[orig_index, 'Notes'] = edit_notes if edit_notes.strip() else None

                            # Persist changes
                            st.session_state.data = df
                            if save_data(st.session_state.data):
                                st.success("✅ Entry updated and saved")
                                st.rerun()
                            else:
                                st.error("❌ Failed to save updated entry")
                        except Exception as e:
                            st.error(f"Error updating entry: {e}")
        else:
            st.info("No entries match filters to edit.")

        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Entries", len(df))
        with col2:
            st.metric("Total Users", df['User'].nunique())
        with col3:
            st.metric("Showing", len(df_filtered))
    else:
        st.info("No data available")

with tab6:
    st.header("🎯 Personal Goals")
    
    if not current_user:
        st.warning("⚠️ Please enter a username in the sidebar first!")
    else:
        goals_df = load_user_goals()
        user_goals = get_user_goals(current_user)
        
        st.subheader(f"Goals for {current_user}")
        
        with st.form("goals_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Body Composition Goals**")
                target_weight = st.number_input(
                    "Target Weight (kg)", 
                    min_value=0.0, 
                    max_value=300.0,
                    value=user_goals['Target Weight (kg)'] if user_goals is not None and pd.notna(user_goals.get('Target Weight (kg)')) else 0.0,
                    step=0.1
                )
                
                target_fat_mass = st.number_input(
                    "Target Fat Mass (kg)",
                    min_value=0.0,
                    max_value=200.0,
                    value=user_goals['Target Fat Mass (kg)'] if user_goals is not None and pd.notna(user_goals.get('Target Fat Mass (kg)')) else 0.0,
                    step=0.1
                )
                
                target_muscle_mass = st.number_input(
                    "Target Muscle Mass (kg)",
                    min_value=0.0,
                    max_value=200.0,
                    value=user_goals['Target Muscle Mass (kg)'] if user_goals is not None and pd.notna(user_goals.get('Target Muscle Mass (kg)')) else 0.0,
                    step=0.1
                )
            
            with col2:
                st.write("**Additional Targets**")
                target_body_fat_pct = st.number_input(
                    "Target Body Fat %",
                    min_value=0.0,
                    max_value=100.0,
                    value=user_goals['Target Body Fat %'] if user_goals is not None and pd.notna(user_goals.get('Target Body Fat %')) else 0.0,
                    step=0.1
                )
                
                timeline = st.number_input(
                    "Timeline (weeks)",
                    min_value=1,
                    max_value=52,
                    value=int(user_goals['Weeks']) if user_goals is not None and pd.notna(user_goals.get('Weeks')) else 12,
                    step=1
                )
                
                st.info("💡 Set realistic goals with a clear timeline for better tracking!")
            
            submitted = st.form_submit_button("💾 Save Goals", use_container_width=True)
            
            if submitted:
                has_goals = any([target_weight > 0, target_fat_mass > 0, target_muscle_mass > 0, target_body_fat_pct > 0])
                
                if not has_goals:
                    st.error("⚠️ Please set at least one goal!")
                else:
                    # Update or create goals entry
                    if user_goals is not None:
                        goals_df.loc[goals_df['User'] == current_user, 'Target Weight (kg)'] = target_weight
                        goals_df.loc[goals_df['User'] == current_user, 'Target Fat Mass (kg)'] = target_fat_mass
                        goals_df.loc[goals_df['User'] == current_user, 'Target Muscle Mass (kg)'] = target_muscle_mass
                        goals_df.loc[goals_df['User'] == current_user, 'Target Body Fat %'] = target_body_fat_pct
                        goals_df.loc[goals_df['User'] == current_user, 'Weeks'] = timeline
                    else:
                        new_goal = pd.DataFrame([{
                            'User': current_user,
                            'Target Weight (kg)': target_weight,
                            'Target Fat Mass (kg)': target_fat_mass,
                            'Target Muscle Mass (kg)': target_muscle_mass,
                            'Target Body Fat %': target_body_fat_pct,
                            'Weeks': timeline
                        }])
                        goals_df = pd.concat([goals_df, new_goal], ignore_index=True)
                    
                    if save_user_goals(goals_df):
                        st.success("✅ Goals saved successfully!")
                        st.balloons()
                        st.rerun()
        
        st.markdown("---")
        
        # Display goals progress
        if user_goals is not None:
            st.subheader("📊 Goals Progress")
            
            df_user = df[df['User'] == current_user]
            
            if not df_user.empty:
                latest = df_user.sort_values('Date').iloc[-1]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if user_goals['Target Weight (kg)'] > 0:
                        current_weight = latest['Weight (kg)'] if pd.notna(latest['Weight (kg)']) else 0
                        remaining = user_goals['Target Weight (kg)'] - current_weight
                        st.metric(
                            "Weight Target",
                            f"{user_goals['Target Weight (kg)']:.1f} kg",
                            delta=f"{remaining:+.1f} kg" if current_weight > 0 else "N/A"
                        )
                    else:
                        st.metric("Weight Target", "Not set")
                
                with col2:
                    if user_goals['Target Fat Mass (kg)'] > 0:
                        current_fat = latest['Fat Mass (kg)'] if pd.notna(latest['Fat Mass (kg)']) else 0
                        remaining = user_goals['Target Fat Mass (kg)'] - current_fat
                        st.metric(
                            "Fat Mass Target",
                            f"{user_goals['Target Fat Mass (kg)']:.1f} kg",
                            delta=f"{remaining:+.1f} kg" if current_fat > 0 else "N/A"
                        )
                    else:
                        st.metric("Fat Mass Target", "Not set")
                
                with col3:
                    if user_goals['Target Muscle Mass (kg)'] > 0:
                        current_muscle = latest['Muscle Mass (kg)'] if pd.notna(latest['Muscle Mass (kg)']) else 0
                        remaining = user_goals['Target Muscle Mass (kg)'] - current_muscle
                        st.metric(
                            "Muscle Mass Target",
                            f"{user_goals['Target Muscle Mass (kg)']:.1f} kg",
                            delta=f"{remaining:+.1f} kg" if current_muscle > 0 else "N/A"
                        )
                    else:
                        st.metric("Muscle Mass Target", "Not set")
                
                with col4:
                    if user_goals['Target Body Fat %'] > 0:
                        current_bf = latest['Body Fat %'] if pd.notna(latest['Body Fat %']) else 0
                        remaining = user_goals['Target Body Fat %'] - current_bf
                        st.metric(
                            "Body Fat % Target",
                            f"{user_goals['Target Body Fat %']:.1f}%",
                            delta=f"{remaining:+.1f}%" if current_bf > 0 else "N/A"
                        )
                    else:
                        st.metric("Body Fat % Target", "Not set")
                
                st.markdown("---")
                st.info(f"📅 Timeline: {int(user_goals['Weeks'])} weeks")
                
                # Goals visualization
                if len(df_user) > 1:
                    st.subheader("📈 Progress Towards Goals")
                    
                    df_user_sorted = df_user.sort_values('Date')
                    
                    fig = go.Figure()
                    
                    # Muscle Mass goal
                    if user_goals['Target Muscle Mass (kg)'] > 0:
                        fig.add_trace(go.Scatter(
                            x=df_user_sorted['Date'],
                            y=df_user_sorted['Muscle Mass (kg)'],
                            name='Muscle Mass (Actual)',
                            mode='lines+markers',
                            line=dict(color='#10b981', width=2)
                        ))
                        
                        fig.add_hline(
                            y=user_goals['Target Muscle Mass (kg)'],
                            line_dash="dash",
                            line_color='#10b981',
                            annotation_text=f"Muscle Target: {user_goals['Target Muscle Mass (kg)']:.1f} kg"
                        )
                    
                    # Fat Mass goal
                    if user_goals['Target Fat Mass (kg)'] > 0:
                        fig.add_trace(go.Scatter(
                            x=df_user_sorted['Date'],
                            y=df_user_sorted['Fat Mass (kg)'],
                            name='Fat Mass (Actual)',
                            mode='lines+markers',
                            line=dict(color='#ef4444', width=2)
                        ))
                        
                        fig.add_hline(
                            y=user_goals['Target Fat Mass (kg)'],
                            line_dash="dash",
                            line_color='#ef4444',
                            annotation_text=f"Fat Target: {user_goals['Target Fat Mass (kg)']:.1f} kg"
                        )
                    
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Mass (kg)",
                        height=400,
                        template='plotly_white',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Add entries to track progress towards your goals!")
        else:
            st.info("No goals set yet. Set your goals above to start tracking!")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
    <small>❄️ Winter Arc Challenge 2025 |Developed by Napoleon Perez & Arturo Boquin | Transform this winter 💪</small>
    </div>
""", unsafe_allow_html=True)
