import os
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.db.session import SyncSessionLocal

s = SyncSessionLocal()

try:
    users = s.execute(text("""
        SELECT u.id, u.email, u.role, u.created_at, u.updated_at, p.full_name, p.department
        FROM public.users u
        LEFT JOIN public.profiles p ON u.id = p.user_id
    """)).fetchall()

    print(f"Syncing {len(users)} users from public.users to auth.users...")
    synced = 0
    for u in users:
        uid, email, role, created_at, updated_at, full_name, dept = u
        raw_user_meta = json.dumps({"full_name": full_name or "", "role": str(role), "department": dept or ""})
        raw_app_meta = json.dumps({"provider": "email", "providers": ["email"]})

        s.execute(text("""
            INSERT INTO auth.users (
                id,
                aud,
                role,
                email,
                raw_app_meta_data,
                raw_user_meta_data,
                email_confirmed_at,
                created_at,
                updated_at,
                is_sso_user,
                is_anonymous
            ) VALUES (
                CAST(:id AS uuid),
                'authenticated',
                'authenticated',
                :email,
                CAST(:raw_app_meta AS jsonb),
                CAST(:raw_user_meta AS jsonb),
                NOW(),
                :created_at,
                :updated_at,
                false,
                false
            )
            ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                raw_user_meta_data = EXCLUDED.raw_user_meta_data,
                updated_at = NOW()
        """), {
            "id": str(uid),
            "email": email,
            "raw_app_meta": raw_app_meta,
            "raw_user_meta": raw_user_meta,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        synced += 1

    s.commit()
    print(f"✅ Successfully synced {synced} users into auth.users!")

    # Verify count
    auth_count = s.execute(text('SELECT count(*) FROM "auth"."users"')).scalar()
    print(f"Total rows in auth.users now: {auth_count}")

except Exception as e:
    s.rollback()
    print(f"Error syncing to auth.users: {e}")
    raise
finally:
    s.close()
