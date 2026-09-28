import urllib.request
import json
import os

def get_env_var(key, default=""):
    if key in os.environ:
        return os.environ[key]
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    return line.strip().split("=", 1)[1]
    return default

SUPABASE_TOKEN = get_env_var("SUPABASE_TOKEN")
PROJECT_REF = get_env_var("PROJECT_REF", "jhjgapijtayhsuzejbtl")

sql = """
-- 1. Procedures Table
CREATE TABLE IF NOT EXISTS procedures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(64) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    agency VARCHAR(255) NOT NULL,
    statutory_citation TEXT NOT NULL,
    original_text TEXT NOT NULL,
    flesch_grade_before NUMERIC(4,1),
    flesch_grade_after NUMERIC(4,1),
    pruned_percent VARCHAR(16),
    pitfall_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Statutory Constraints
CREATE TABLE IF NOT EXISTS statutory_constraints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    procedure_slug VARCHAR(64) NOT NULL,
    section_citation VARCHAR(128) NOT NULL,
    clause_type VARCHAR(32) NOT NULL,
    raw_clause_text TEXT NOT NULL,
    severity VARCHAR(16) NOT NULL,
    days_offset INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Action Steps
CREATE TABLE IF NOT EXISTS action_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    procedure_slug VARCHAR(64) NOT NULL,
    step_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    plain_text_simple TEXT NOT NULL,
    plain_text_plain TEXT NOT NULL,
    plain_text_pro TEXT NOT NULL,
    time_estimate VARCHAR(32),
    difficulty VARCHAR(32),
    pitfall_warning TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. User Action Plans (Cloud Sync)
CREATE TABLE IF NOT EXISTS user_action_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(128) NOT NULL,
    procedure_slug VARCHAR(64) NOT NULL,
    triage_answers JSONB DEFAULT '{}'::jsonb,
    completed_steps JSONB DEFAULT '[]'::jsonb,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS and public policies for demo access
ALTER TABLE procedures ENABLE ROW LEVEL SECURITY;
ALTER TABLE statutory_constraints ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_action_plans ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow public read procedures') THEN
        CREATE POLICY "Allow public read procedures" ON procedures FOR SELECT USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow public insert procedures') THEN
        CREATE POLICY "Allow public insert procedures" ON procedures FOR INSERT WITH CHECK (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow public read constraints') THEN
        CREATE POLICY "Allow public read constraints" ON statutory_constraints FOR SELECT USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow public insert constraints') THEN
        CREATE POLICY "Allow public insert constraints" ON statutory_constraints FOR INSERT WITH CHECK (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow public read action_steps') THEN
        CREATE POLICY "Allow public read action_steps" ON action_steps FOR SELECT USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow public insert action_steps') THEN
        CREATE POLICY "Allow public insert action_steps" ON action_steps FOR INSERT WITH CHECK (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow public all user_action_plans') THEN
        CREATE POLICY "Allow public all user_action_plans" ON user_action_plans FOR ALL USING (true) WITH CHECK (true);
    END IF;
END $$;
"""

def main():
    if not SUPABASE_TOKEN:
        print("Error: SUPABASE_TOKEN environment variable not set.")
        return
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    data = json.dumps({"query": sql}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {SUPABASE_TOKEN}",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print("Migration successful! Status:", resp.status)
            print("Response:", resp.read().decode())
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code, e.read().decode())

if __name__ == "__main__":
    main()
