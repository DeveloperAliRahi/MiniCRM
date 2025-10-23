# 🧠 MiniCRM — Simple Local Contact Manager

MiniCRM is a lightweight desktop CRM (Customer Relationship Manager) built with Python and Tkinter.  
It’s designed for freelancers, consultants, and small businesses who want an easy way to manage contacts, track follow-ups, and record interactions — all locally without any server setup.

---

## 🚀 Features

- 🧾 Add, Edit, and Delete Contacts  
  Store names, emails, phone numbers, websites, and status.
  
- 🔗 Clickable Website Links  
  Websites open directly in your browser from the contact table.

- 🗓 Track Contact Dates  
  Automatically records the first contact date, plus optional call/email dates.

- ✉️ Integrated Follow-Up Actions  
  Prepare follow-up emails using your local Mac Mail client.

- 🧭 Status Options
  - Not Contacted  
  - Called  
  - Emailed  
  - Called & Emailed  

- 📅 Date Picker Support  
  Select dates easily via popup calendar (powered by tkcalendar).

- 💾 Local Storage with SQLite  
  Keeps everything on your device — no cloud or external database required.

---

## 🧰 Tech Stack

- Python 3.10+
- Tkinter (GUI)
- SQLite3 (Database)
- tkcalendar (Date picker)

---

## ⚙️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/DeveloperAliRahi/MiniCRM.git
   cd MiniCRM
Install dependencies:

bash
Copy code
pip install tk tkcalendar
Run the app:

bash
Copy code
python3 crm.py
💡 Mac users: You can also double-click the crm.command file to launch the app instantly.

🧩 File Structure
bash
Copy code
MiniCRM/
├── crm.py             # Main entry point
├── db.py              # Database setup and functions
├── gui.py             # User interface (Tkinter)
├── utils.py           # Helper functions
├── crm.command        # Mac executable launcher
├── requirements.txt   # Dependencies
└── README.md
🧠 Future Enhancements
Email template management tab

CSV import/export for contact lists

Cross-platform packaging (macOS, Windows, Linux)

Follow-up reminders and notifications

Cloud sync (optional future module)

🪪 License
This project is licensed under the MIT License.

👨‍💻 Author
Ali Rahi
developer@alirahi.com
https://alirahi.com
