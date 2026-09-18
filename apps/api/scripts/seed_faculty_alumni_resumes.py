"""CLI Script to seed faculty and alumni profiles and resumes."""

import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.seed_faculty_alumni import seed_faculty_and_alumni

if __name__ == "__main__":
    print("🌱 Running Faculty and Alumni dataset seed...")
    seed_faculty_and_alumni()
    print("✅ Done!")
