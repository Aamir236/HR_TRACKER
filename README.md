# HR Client Tracker

A Streamlit app for keeping track of HR client contacts, communication status, and follow-up dates.

## Features

- Add client contact details, including optional CC email addresses.
- Track contact dates, job positions, status, follow-up dates, and notes.
- Search client records by client, company, email, or phone.
- View dashboard totals and follow-up reminders.
- Download client records as a CSV file.
- Save records in a local SQLite database (`hr_clients.db`).

## Requirements

- Python 3.9 or later
- Streamlit
- pandas

Install the required packages:

```bash
python -m pip install streamlit pandas
```

## Run the app

From the project directory, run:

```bash
streamlit run TRACKER.py
```

Streamlit will print a local URL to open in your browser. The SQLite database is created in the working directory when the app first runs.
