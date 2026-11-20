
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing!")

# Create Supabase client
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
