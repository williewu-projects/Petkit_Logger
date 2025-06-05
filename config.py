import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@nas-ip:5432/petkit")
PETKIT_EMAIL = os.getenv("PETKIT_EMAIL")
PETKIT_PASSWORD = os.getenv("PETKIT_PASSWORD")
POLL_INTERVAL_SEC = 600
POOPING_THRESHOLD = 90      # seconds to spend in litterbox to be considered pooping