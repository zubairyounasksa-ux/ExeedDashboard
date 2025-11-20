# Customer Walk-in & Test Drive Dashboard

This is a simple Streamlit dashboard to visualize showroom performance using data stored in an Excel file.

## Features

- Read data from `data/Book Dashboard.xlsx` or an uploaded Excel file
- KPIs:
  - Total walk-in customers
  - Total test drives
  - Overall conversion rate
  - Average walk-ins per day
- Interactive filters by date range
- Charts:
  - Daily walk-ins and test drives (time series)
  - Performance by weekday
  - Daily conversion rate
- View and download filtered raw data

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── README.md
└── data
    └── Book Dashboard.xlsx
```

## How to Run

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

4. The app will open in your browser. Use the sidebar to:
   - Upload a new Excel file (optional), or
   - Rely on the default `data/Book Dashboard.xlsx`.
