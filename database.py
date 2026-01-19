import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use system env vars only

Base = declarative_base()

class FitnessEntry(Base):
    """SQLAlchemy model for fitness entries"""
    __tablename__ = 'fitness_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    user = Column(String(100), nullable=False)
    goal = Column(String(50))
    weight_kg = Column(Float)
    body_fat_pct = Column(Float)
    muscle_mass_kg = Column(Float)
    fat_mass_kg = Column(Float)
    waist_cm = Column(Float)
    chest_cm = Column(Float)
    arms_cm = Column(Float)
    thighs_cm = Column(Float)
    cardio_minutes = Column(Integer)
    strength_training_minutes = Column(Integer)
    steps = Column(Integer)
    calories_consumed = Column(Integer)
    protein_g = Column(Integer)
    water_l = Column(Float)
    sleep_hours = Column(Float)
    notes = Column(Text)

class UserGoal(Base):
    """SQLAlchemy model for user goals"""
    __tablename__ = 'user_goals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(100), unique=True, nullable=False)
    target_fat_mass_kg = Column(Float)
    target_muscle_mass_kg = Column(Float)
    target_body_fat_pct = Column(Float)
    target_weight_kg = Column(Float)
    weeks = Column(Integer)

class DatabaseManager:
    """Manager for PostgreSQL database operations"""

    def __init__(self, db_url=None):
        """Initialize database connection

        Args:
            db_url: PostgreSQL connection string. If None, reads from environment variable DATABASE_URL
        """
        if db_url is None:
            db_url = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/fitness_db')

        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables in the database"""
        try:
            Base.metadata.create_all(self.engine)
            return True
        except Exception as e:
            st.error(f"Error creating tables: {e}")
            return False

    def save_dataframe_to_db(self, df):
        """Save pandas DataFrame to PostgreSQL

        Args:
            df: DataFrame with fitness data

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            session = self.Session()

            # Clear existing data (you might want to change this to update/insert logic)
            session.query(FitnessEntry).delete()

            # Convert DataFrame to database records
            for _, row in df.iterrows():
                entry = FitnessEntry(
                    date=pd.to_datetime(row['Date']),
                    user=row['User'],
                    goal=row.get('Goal'),
                    weight_kg=row.get('Weight (kg)'),
                    body_fat_pct=row.get('Body Fat %'),
                    muscle_mass_kg=row.get('Muscle Mass (kg)'),
                    fat_mass_kg=row.get('Fat Mass (kg)'),
                    waist_cm=row.get('Waist (cm)'),
                    chest_cm=row.get('Chest (cm)'),
                    arms_cm=row.get('Arms (cm)'),
                    thighs_cm=row.get('Thighs (cm)'),
                    cardio_minutes=int(row['Cardio Minutes']) if pd.notna(row.get('Cardio Minutes')) else None,
                    strength_training_minutes=int(row['Strength Training Minutes']) if pd.notna(row.get('Strength Training Minutes')) else None,
                    steps=int(row['Steps']) if pd.notna(row.get('Steps')) else None,
                    calories_consumed=int(row['Calories Consumed']) if pd.notna(row.get('Calories Consumed')) else None,
                    protein_g=int(row['Protein (g)']) if pd.notna(row.get('Protein (g)')) else None,
                    water_l=row.get('Water (L)'),
                    sleep_hours=row.get('Sleep Hours'),
                    notes=row.get('Notes')
                )
                session.add(entry)

            session.commit()
            session.close()
            return True

        except Exception as e:
            st.error(f"Error saving to database: {e}")
            session.rollback()
            session.close()
            return False

    def load_dataframe_from_db(self):
        """Load all fitness data from PostgreSQL into pandas DataFrame

        Returns:
            pd.DataFrame: DataFrame with fitness data
        """
        try:
            session = self.Session()
            entries = session.query(FitnessEntry).all()
            session.close()

            if not entries:
                return self._create_empty_dataframe()

            # Convert to DataFrame
            data = []
            for entry in entries:
                data.append({
                    'Date': entry.date,
                    'User': entry.user,
                    'Goal': entry.goal,
                    'Weight (kg)': entry.weight_kg,
                    'Body Fat %': entry.body_fat_pct,
                    'Muscle Mass (kg)': entry.muscle_mass_kg,
                    'Fat Mass (kg)': entry.fat_mass_kg,
                    'Waist (cm)': entry.waist_cm,
                    'Chest (cm)': entry.chest_cm,
                    'Arms (cm)': entry.arms_cm,
                    'Thighs (cm)': entry.thighs_cm,
                    'Cardio Minutes': entry.cardio_minutes,
                    'Strength Training Minutes': entry.strength_training_minutes,
                    'Steps': entry.steps,
                    'Calories Consumed': entry.calories_consumed,
                    'Protein (g)': entry.protein_g,
                    'Water (L)': entry.water_l,
                    'Sleep Hours': entry.sleep_hours,
                    'Notes': entry.notes
                })

            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            return df

        except Exception as e:
            st.error(f"Error loading from database: {e}")
            return self._create_empty_dataframe()

    def save_user_goals_to_db(self, goals_df):
        """Save user goals DataFrame to PostgreSQL

        Args:
            goals_df: DataFrame with user goals

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            session = self.Session()

            # Update or insert each user's goals
            for _, row in goals_df.iterrows():
                existing_goal = session.query(UserGoal).filter_by(user=row['User']).first()

                if existing_goal:
                    # Update existing
                    existing_goal.target_fat_mass_kg = row.get('Target Fat Mass (kg)')
                    existing_goal.target_muscle_mass_kg = row.get('Target Muscle Mass (kg)')
                    existing_goal.target_body_fat_pct = row.get('Target Body Fat %')
                    existing_goal.target_weight_kg = row.get('Target Weight (kg)')
                    existing_goal.weeks = int(row['Weeks']) if pd.notna(row.get('Weeks')) else None
                else:
                    # Insert new
                    new_goal = UserGoal(
                        user=row['User'],
                        target_fat_mass_kg=row.get('Target Fat Mass (kg)'),
                        target_muscle_mass_kg=row.get('Target Muscle Mass (kg)'),
                        target_body_fat_pct=row.get('Target Body Fat %'),
                        target_weight_kg=row.get('Target Weight (kg)'),
                        weeks=int(row['Weeks']) if pd.notna(row.get('Weeks')) else None
                    )
                    session.add(new_goal)

            session.commit()
            session.close()
            return True

        except Exception as e:
            st.error(f"Error saving goals to database: {e}")
            session.rollback()
            session.close()
            return False

    def load_user_goals_from_db(self):
        """Load user goals from PostgreSQL into pandas DataFrame

        Returns:
            pd.DataFrame: DataFrame with user goals
        """
        try:
            session = self.Session()
            goals = session.query(UserGoal).all()
            session.close()

            if not goals:
                return pd.DataFrame(columns=['User', 'Target Fat Mass (kg)', 'Target Muscle Mass (kg)',
                                            'Target Body Fat %', 'Target Weight (kg)', 'Weeks'])

            # Convert to DataFrame
            data = []
            for goal in goals:
                data.append({
                    'User': goal.user,
                    'Target Fat Mass (kg)': goal.target_fat_mass_kg,
                    'Target Muscle Mass (kg)': goal.target_muscle_mass_kg,
                    'Target Body Fat %': goal.target_body_fat_pct,
                    'Target Weight (kg)': goal.target_weight_kg,
                    'Weeks': goal.weeks
                })

            return pd.DataFrame(data)

        except Exception as e:
            st.error(f"Error loading goals from database: {e}")
            return pd.DataFrame(columns=['User', 'Target Fat Mass (kg)', 'Target Muscle Mass (kg)',
                                        'Target Body Fat %', 'Target Weight (kg)', 'Weeks'])

    def test_connection(self):
        """Test database connection

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            session = self.Session()
            session.execute('SELECT 1')
            session.close()
            return True
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return False

    def _create_empty_dataframe(self):
        """Create empty dataframe with proper structure"""
        return pd.DataFrame(columns=[
            'Date', 'User', 'Goal', 'Weight (kg)', 'Body Fat %',
            'Muscle Mass (kg)', 'Fat Mass (kg)',
            'Waist (cm)', 'Chest (cm)', 'Arms (cm)', 'Thighs (cm)',
            'Cardio Minutes', 'Strength Training Minutes', 'Steps',
            'Calories Consumed', 'Protein (g)', 'Water (L)', 'Sleep Hours', 'Notes'
        ])

def get_db_manager():
    """Get or create database manager instance

    Returns:
        DatabaseManager: Database manager instance
    """
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    return st.session_state.db_manager
