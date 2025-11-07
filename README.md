# FAQ Bot (SQLite)

A simple command-line chatbot that answers FAQs using an SQLite database.  
If a question is not found, it allows the user to enter their email so the admin can reply later.

---

## Overview

This project is a small **CLI chatbot** built with **Python** and **SQLite**.  
It connects to a local database of predefined FAQ questions and answers.  
If a question is missing, the user can leave their email and question for follow-up.  
An admin can later review and respond to these pending queries.

---

## Folder Structure

faq_bot/
│
├── bot.py # Main chatbot logic
├── admin_tools.py # View and manage pending queries
├── create_db.py # Creates a new SQLite database using schema.sql
├── check_db.py # Verifies if database and tables exist
├── inspect_db.py # Optional script to view database contents
│
├── schema.sql # Database schema definition
├── seed.sql # Populates FAQ data (120 entries)
├── .gitignore # Ignores unnecessary files
└── README.md # Documentation

yaml
Copy code

---

## Setup Instructions

### 1. Clone the Repository
Open your terminal or command prompt and run:
```bash
git clone https://github.com/Krrish768/faq_bot.git
cd faq_bot
2. Make Sure Python is Installed
Check your Python version:

bash
Copy code
python --version
If Python is not installed, download and install it from https://www.python.org/downloads.

3. Create the Database
Run this script to create a new empty SQLite database named db.sqlite:

bash
Copy code
python create_db.py
4. Populate the Database
After creating the database, insert all FAQ data using:

bash
Copy code
sqlite3 db.sqlite < seed.sql
This adds all the preloaded FAQ entries to the database.

5. Verify Setup (Optional)
You can confirm that the database was created properly by running:

bash
Copy code
python check_db.py
6. Run the Chatbot
Start the chatbot by running:

bash
Copy code
python bot.py
You can now type any question directly in the terminal.

If the question exists in the database → the bot will display the answer.

If it doesn’t → the bot will ask for your email and save your question in the pending queries table.

7. View Pending Queries (Admin Tool)
To view questions that users asked but weren’t found in the database, run:

bash
Copy code
python admin_tools.py
This will display all pending queries along with the email addresses of users who submitted them.

Notes
Do not upload the db.sqlite file to GitHub.
Each user should create it locally by running create_db.py and then loading data using seed.sql.

The .gitignore file ensures that local databases, cache files, and other temporary files are ignored.

The inspect_db.py file is optional and can be used to check database contents while testing.

Troubleshooting
If sqlite3 is not recognized, install it or use the Python sqlite3 module directly.

Make sure Python is added to your PATH during installation.

If create_db.py doesn’t work, ensure that schema.sql is in the same directory as the Python script.

Developer
Developed by: Krrish Singh
Project: SQL Chatbot (FAQ Bot)
Language: Python + SQLite

yaml
Copy code

---

✅ **Instructions for you:**
1. Open your `README.md` file.
2. Delete everything currently in it.
3. Paste this exact content.
4. Save and commit changes:
   ```bash
   git add README.md
   git commit -m "Updated final README with setup steps"
   git push origin main