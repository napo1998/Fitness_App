import pandas as pd
import numpy as np

STANDARD_COLS = {
    "date": "Date",
    "user": "User",
    "goal": "Goal",
    "weightkg": "Weight (kg)",
    "weight (kg)": "Weight (kg)",
    "bodyfat%": "Body Fat %",
    "body fat %": "Body Fat %",
    "musclemasskg": "Muscle Mass (kg)",
    "muscle mass (kg)": "Muscle Mass (kg)",
    "fatmasskg": "Fat Mass (kg)",
    "fat mass (kg)": "Fat Mass (kg)",
    "waistcm": "Waist (cm)",
    "chestcm": "Chest (cm)",
    "armscm": "Arms (cm)",
    "thighscm": "Thighs (cm)",
    "cardiominutes": "Cardio Minutes",
    "strengthtrainingminutes": "Strength Training Minutes",
    "steps": "Steps",
    "caloriesconsumed": "Calories Consumed",
    "proteing": "Protein (g)",
    "waterl": "Water (L)",
    "sleephours": "Sleep Hours",
    "notes": "Notes"
}


def _normalize_col_name(name: str) -> str:
    if not isinstance(name, str):
        return name
    s = name.strip().lower()
    s = s.replace(' ', '').replace('-', '').replace('_', '').replace('(', '').replace(')', '')
    return s


def _map_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = {}
    for c in df.columns:
        key = _normalize_col_name(c)
        if key in STANDARD_COLS:
            cols[c] = STANDARD_COLS[key]
    if cols:
        df = df.rename(columns=cols)
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Perform best-effort cleaning on the fitness dataset.

    Steps:
    - Normalize/rename common column variants
    - Parse dates
    - Strip whitespace from strings
    - Convert numeric columns to numeric, coerce errors
    - Remove impossible values (negatives, bodyfat>100)
    - Calculate Fat Mass / Muscle Mass if missing
    - Drop rows missing Date or User
    - Deduplicate by User+Date keeping the most recent
    """
    if df is None:
        return pd.DataFrame()

    df = df.copy()

    # Rename columns to canonical names
    df = _map_columns(df)

    # Ensure Date column exists and is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    else:
        df['Date'] = pd.NaT

    # Trim string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    # Required string fields
    if 'User' not in df.columns:
        df['User'] = None
    if 'Goal' not in df.columns:
        df['Goal'] = None

    # Numeric columns we expect
    numeric_cols = [
        'Weight (kg)', 'Body Fat %', 'Muscle Mass (kg)', 'Fat Mass (kg)',
        'Waist (cm)', 'Chest (cm)', 'Arms (cm)', 'Thighs (cm)',
        'Cardio Minutes', 'Strength Training Minutes', 'Steps',
        'Calories Consumed', 'Protein (g)', 'Water (L)', 'Sleep Hours'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = np.nan

    # Remove impossible values
    if 'Body Fat %' in df.columns:
        df.loc[(df['Body Fat %'] < 0) | (df['Body Fat %'] > 100), 'Body Fat %'] = np.nan

    for col in numeric_cols:
        if col in df.columns:
            df.loc[df[col] < 0, col] = np.nan

    # Calculate Fat Mass if missing
    if 'Fat Mass (kg)' in df.columns and 'Weight (kg)' in df.columns and 'Body Fat %' in df.columns:
        missing_fat_mass = df['Fat Mass (kg)'].isna() & df['Weight (kg)'].notna() & df['Body Fat %'].notna()
        df.loc[missing_fat_mass, 'Fat Mass (kg)'] = df.loc[missing_fat_mass, 'Weight (kg)'] * (df.loc[missing_fat_mass, 'Body Fat %'] / 100)

    # Calculate Muscle Mass if missing
    if 'Muscle Mass (kg)' in df.columns and 'Weight (kg)' in df.columns and 'Fat Mass (kg)' in df.columns:
        missing_muscle = df['Muscle Mass (kg)'].isna() & df['Weight (kg)'].notna() & df['Fat Mass (kg)'].notna()
        df.loc[missing_muscle, 'Muscle Mass (kg)'] = df.loc[missing_muscle, 'Weight (kg)'] - df.loc[missing_muscle, 'Fat Mass (kg)']

    # Drop rows without Date or User
    df = df[~(df['Date'].isna() | df['User'].isna() | (df['User'].astype(str).str.strip() == ''))]

    # Deduplicate: keep last occurrence
    if 'User' in df.columns and 'Date' in df.columns:
        df = df.sort_values('Date').drop_duplicates(subset=['User', 'Date'], keep='last')

    df = df.reset_index(drop=True)

    return df


def save_cleaned(df: pd.DataFrame, path: str) -> bool:
    try:
        df.to_csv(path, index=False)
        return True
    except Exception:
        return False


__all__ = ['clean_dataframe', 'save_cleaned']
