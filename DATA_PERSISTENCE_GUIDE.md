# Data Persistence & Recovery System

## Overview
The Fitness App now includes a comprehensive data persistence and recovery system that automatically saves data to CSV files and maintains timestamped backups for data recovery.

## Key Features

### 1. **Automatic Data Persistence**
- **Main Data File**: `fitness_competition_data.csv` - Stores all user fitness entries
- **User Goals File**: `user_goals.csv` - Stores personal goals for each user
- All data is automatically saved to CSV whenever entries are created, edited, or deleted

### 2. **In-Memory Session State Management**
- Data is loaded into `st.session_state` when the app starts
- Session state maintains data across Streamlit reruns
- `last_save_time` tracks when data was last persisted to disk

### 3. **Automatic Backup System**
- **Backup Directory**: `.data_backups/` (hidden folder)
- **Automatic Backup**: Created every time data is saved
- **Timestamped Backups**: Format: `backup_YYYYMMDD_HHMMSS_filename.csv`
- **Cleanup Policy**: Keeps the 10 most recent backups automatically

### 4. **Data Recovery Features**
- Automatic recovery from backup if main CSV file is corrupted
- Manual backup creation from the Data Management panel
- View and restore from any available backup
- One-click restoration with confirmation

## How It Works

### Data Flow
```
User Action (Add/Edit/Delete)
    ↓
Update st.session_state.data
    ↓
save_data() function:
  1. Create timestamped backup of current file
  2. Save updated data to CSV
  3. Update last_save_time
    ↓
Data persisted to disk
```

### Recovery Process
```
App Startup
    ↓
initialize_data() checks if DATA_FILE exists
    ↓
If file corrupted/missing:
  1. Display error message
  2. Automatically attempt backup recovery
  3. Load most recent backup
  4. Display recovery confirmation
    ↓
Session state loaded with recovered data
```

## Using the System

### In the App

#### Manual Backup (📋 Data Tab → Data Management & Recovery)
1. Click **"🔄 Manual Backup Now"** button
2. System creates timestamped backup
3. Confirmation message shows backup file name

#### View Available Backups
1. Click **"📥 View Backups"** button
2. See list of recent backups (most recent first)
3. File size shown in KB

#### Restore from Backup
1. Click **"Restore"** button next to desired backup
2. Data immediately restored from backup
3. App automatically refreshes
4. Continue working with recovered data

### Last Save Time
- **Metric Display**: Shows minutes since last save
- **Auto Updates**: Refreshes after each modification
- **Helps Track**: Data safety and persistence

## File Locations

### Main Data Files
```
Fitness_App/
├── fitness_competition_data.csv       (Main data file)
├── user_goals.csv                      (User goals file)
└── .data_backups/                      (Backup directory)
    ├── backup_20250112_143022_fitness_competition_data.csv
    ├── backup_20250112_143015_fitness_competition_data.csv
    ├── backup_20250112_143008_user_goals.csv
    └── ... (up to 10 most recent backups)
```

## Error Handling

### If Main File is Corrupted
1. App detects error on startup
2. Shows error message: "Error loading main data file"
3. Displays: "Attempting to recover from backup..."
4. Automatically loads most recent backup
5. Success message: "✅ Recovered from backup: [filename]"
6. Users can continue without data loss

### If Backup Creation Fails
1. Warning message displayed
2. Main save still attempts to proceed
3. Data not persisted but users are notified
4. Can manually create backup from Data tab

### If Restore Fails
1. Error message: "Error restoring from backup"
2. System explains which backup failed
3. Users can try alternative backup or check file permissions

## Code Functions

### Core Functions

#### `create_backup(filename=DATA_FILE)`
- Creates timestamped backup copy
- Returns: Backup file path or None
- Called: Every time data is saved

#### `ensure_backup_dir()`
- Creates `.data_backups` directory if missing
- Called: Before any backup operation

#### `cleanup_old_backups(max_backups=10)`
- Removes old backups exceeding max count
- Called: After each backup creation

#### `restore_from_backup(backup_file)`
- Loads DataFrame from backup file
- Returns: Restored DataFrame or None
- Converts Date column to datetime

#### `get_available_backups()`
- Returns: List of backup files sorted by recency
- Used: For displaying backup options

#### `initialize_data()`
- Loads data with error handling
- Automatically recovers from backup if needed
- Returns: DataFrame with user data

#### `save_data_to_session(df)`
- Updates session state
- Calls save_data() for persistence
- Updates last_save_time

## Best Practices

### For Users
1. **Regular Backups**: Use "Manual Backup Now" before major data changes
2. **Check Save Time**: Verify data was saved by checking "Last Save (min ago)" metric
3. **Monitor Backups**: Periodically review available backups
4. **Test Recovery**: Familiarize yourself with restore process before emergency

### For Developers
1. **Always use save_data()**: Never write to CSV directly
2. **Call on modifications**: Ensure save_data() called after any data change
3. **Check return value**: Verify save was successful
4. **Test recovery**: Regularly test backup/restore functionality

## Configuration

### Backup Settings
Edit these constants in `app.py`:

```python
BACKUP_DIR = '.data_backups'      # Directory for backups
BACKUP_INTERVAL = 5               # Minutes between backups (future feature)
```

### Backup Retention
Edit `cleanup_old_backups()` function:

```python
def cleanup_old_backups(max_backups=10):  # Change '10' to desired count
```

## Troubleshooting

### Backups Not Being Created
1. Check if `.data_backups` directory exists and is writable
2. Verify sufficient disk space
3. Check file permissions on Fitness_App directory

### Cannot Restore from Backup
1. Verify backup file exists in `.data_backups/`
2. Check file is not corrupted (try opening in text editor)
3. Ensure Date columns are present in backup

### Data Lost After Session
1. Check for available backups in Data tab
2. Use "View Backups" to see backup options
3. Click "Restore" on most recent backup
4. Contact support if issue persists

## Future Enhancements

- [ ] Scheduled automatic backups at interval (BACKUP_INTERVAL)
- [ ] Cloud backup integration
- [ ] Backup versioning system
- [ ] Data compression for old backups
- [ ] Automated cleanup of corrupted backups
- [ ] Email notifications on data recovery
- [ ] Change log tracking

## Summary

Your fitness competition data is now **protected** with:
✅ Automatic saves to CSV  
✅ In-memory session state  
✅ Timestamped backups  
✅ Automatic recovery system  
✅ One-click manual backups  
✅ Easy restoration interface  

**No data loss on app restart or crash!**
