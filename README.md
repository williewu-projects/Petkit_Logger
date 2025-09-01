# 📊 Petkit Logger

A Python-based service that **collects data from Petkit smart devices** and logs it into a **PostgreSQL database** hosted on a Synology NAS.  
Designed for reliability and automation, the logger enables long-term tracking of pet activity (feeding, drinking, weight) for downstream analysis and dashboards.

---

## 📖 Overview
Petkit devices provide rich IoT data, but the information is often siloed in their mobile app.  
This project unlocks that data by **polling the Petkit API** on a schedule and storing it in a structured database.  
The data can then be visualized, queried, and integrated into **custom dashboards** (e.g., Petkit_Dashboard, DAKboard).

---

## 🚀 Features
- ✅ Periodic polling of Petkit API data  
- ✅ Automatic ingestion into PostgreSQL (Synology NAS)  
- ✅ Structured database schema for feeding, drinking, and weight data  
- ✅ Docker-ready for always-on deployment  
- ✅ Configurable environment variables for credentials and connection info  
- ✅ Logging and monitoring for reliability  

---

## 🛠 Tech Stack
- **Languages**: Python 3.11  
- **Libraries**: [pypetkitapi](https://pypi.org/project/pypetkitapi/), psycopg2, python-dotenv  
- **Database**: PostgreSQL (hosted on Synology NAS)  
- **Infra**: Docker, GitHub Actions  
- **Other**: Cron/Task Scheduler for automation  

---

## ⚙️ Installation & Setup

1. Clone the repository:
   ```
   git clone https://github.com/williewu-projects/Petkit_Logger.git
   cd Petkit_Logger
2. Create a virtual environment & install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
3. Configure environment variables in .env:
   ```
   DB_HOST=localhost
   DB_USER=youruser
   DB_PASS=yourpassword
   DB_NAME=petkit
   PETKIT_USER=your_email
   PETKIT_PASS=your_password
5. Run the logger:
   ```
   python main.py
6. (Optional) Run with Docker:
   docker build -t petkit-logger .
   docker run -d --env-file .env petkit-logger

---

## 📊 Demo / Outputs
<img width="1008" height="630" alt="image" src="https://github.com/user-attachments/assets/02415dee-fa9e-43bd-8e94-ff533ec90a60" />

---

## 📜 License
MIT License © 2025 Willie Wu
