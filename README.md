
# Winter Arc Challenge 2025 - Fitness Tracking App

## Overview
A comprehensive fitness tracking application built with Streamlit for the Winter Arc Challenge 2025. Track body composition, workouts, nutrition, and compete with friends towards your fitness goals. Data is stored locally in JSON and CSV formats for easy backup and analysis.

## Features
- 📊 Interactive dashboard with key metrics
- ➕ Easy data entry form
- 📈 Progress visualization with multiple charts
- 📋 Data table view with export functionality
- ☁️ Cloud storage with Google Sheets integration
- 📱 Mobile-friendly interface

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Sheets API

#### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Give it a name like "Fitness Tracker"

#### Step 2: Enable Google Sheets API
1. In your project, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"
4. Also enable "Google Drive API"

#### Step 3: Create Service Account Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: fitness-tracker
   - Description: Service account for fitness tracker app
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"
6. Click on the newly created service account
7. Go to the "Keys" tab
8. Click "Add Key" > "Create New Key"
9. Select "JSON" format
10. Click "Create" - this will download a JSON file
11. **Save this JSON file securely** - you'll need it to connect the app

#### Step 4: Create Your Google Sheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it (e.g., "My Fitness Data")
4. **IMPORTANT**: Share the sheet with the service account email
   - The email looks like: `fitness-tracker@your-project.iam.gserviceaccount.com`
   - You can find this email in the JSON file you downloaded (look for "client_email")
   - Click "Share" button in your Google Sheet
   - Paste the service account email
   - Give it "Editor" permissions
5. Copy the spreadsheet URL from your browser

### 3. Run the Application

```bash
streamlit run fitness_tracker.py
```

### 4. Connect to Your Google Sheet

1. The app will open in your browser
2. In the sidebar:
   - Paste your Google Sheet URL
   - Upload the JSON credentials file you downloaded
   - Click "Connect to Google Sheets"
3. Once connected, you're ready to start tracking!

## How to Use

### Dashboard Tab
- View your latest measurements and metrics
- See current body composition stats
- Check recent activity and lifestyle data

### Add Entry Tab
- Fill in your daily/weekly measurements
- You can enter as many or as few fields as you want
- All fields are optional except the date
- Click "Save Entry" to store the data

### Progress Charts Tab
- Visualize your progress over time
- Filter by time period (30, 60, 90 days, etc.)
- Track multiple metrics:
  - Weight and body fat percentage
  - Body measurements (waist, chest, arms, thighs)
  - Activity (steps, cardio, strength training)
  - Lifestyle (water intake, sleep, calories)

### Data Table Tab
- View all your data in table format
- Download your data as CSV for backup or analysis

## Tracked Metrics

### Body Composition
- Weight (kg)
- Body Fat Percentage
- Muscle Mass (kg)
- Lean Body Mass (calculated)

### Body Measurements
- Waist (cm)
- Chest (cm)
- Arms (cm)
- Thighs (cm)

### Activity
- Cardio Minutes
- Strength Training Minutes
- Daily Steps

### Nutrition & Lifestyle
- Calories Consumed
- Water Intake (L)
- Sleep Hours
- Notes (for any additional observations)

## Tips for Best Results

1. **Be Consistent**: Track measurements at the same time of day (preferably morning)
2. **Regular Updates**: Update at least weekly for meaningful progress tracking
3. **Use All Metrics**: While you don't have to fill every field, more data = better insights
4. **Add Notes**: Use the notes field to track important events (illness, vacation, diet changes)
5. **Backup Data**: Periodically download your data as CSV

## Troubleshooting

### Connection Issues
- **"Permission denied"**: Make sure you shared the sheet with the service account email
- **"Invalid credentials"**: Verify you uploaded the correct JSON file
- **"Sheet not found"**: Check that the URL is correct and complete

### Data Not Showing
- Click "Refresh Data" button in the sidebar
- Check that data was actually saved to the Google Sheet
- Verify dates are in proper format

### App Won't Start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (requires Python 3.8+)

## Security Notes

- Keep your service account JSON file secure
- Don't share it publicly or commit it to version control
- The service account only has access to sheets you explicitly share with it
- You can revoke access anytime by removing the service account from the sheet's sharing settings

## Customization

You can customize the app by modifying `fitness_tracker.py`:
- Add new metrics in the data entry form
- Modify chart types and layouts
- Change color schemes
- Add goal tracking features
- Implement progress notifications

## Data Privacy

- Your data is stored in your personal Google Sheet
- The app only accesses the specific sheet you share
- No data is sent to third parties
- You have complete control over your data

## Support

If you encounter issues:
1. Check that Google Sheets API is enabled
2. Verify service account permissions
3. Ensure the sheet URL is correct
4. Check that all dependencies are installed

Happy tracking! 💪
