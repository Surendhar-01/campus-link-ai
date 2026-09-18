import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SyncSessionLocal
from app.models import User, Profile, Document, DocumentExtraction, UserRole, UserSkill

s = SyncSessionLocal()
users = s.query(User).filter(User.role.in_([UserRole.FACULTY, UserRole.ALUMNI])).order_by(User.role, User.email).all()
print(f"Total Faculty and Alumni Users: {len(users)}")
for u in users:
    p = u.profile
    name = p.full_name if p else "No Profile"
    dept = p.department if p else "No Dept"
    docs = s.query(Document).filter(Document.owner_id == u.id).all()
    skills = s.query(UserSkill).filter(UserSkill.user_id == u.id).all()
    print(f"[{u.role.value}] {u.email} -> {name} ({dept}) | Skills: {len(skills)} | Resumes: {len(docs)}")
    for d in docs:
        ext = s.query(DocumentExtraction).filter(DocumentExtraction.document_id == d.id).first()
        print(f"   * Document: {d.original_filename} [{d.processing_status}] | Extracted: {bool(ext)}")

me = s.query(User).filter(User.email.ilike("%surendhar%")).first()
if me:
    docs = s.query(Document).filter(Document.owner_id == me.id).all()
    skills = s.query(UserSkill).filter(UserSkill.user_id == me.id).all()
    print(f"\n[CURRENT USER] {me.email} | Skills: {len(skills)} | Resumes: {len(docs)}")
    for d in docs:
        ext = s.query(DocumentExtraction).filter(DocumentExtraction.document_id == d.id).first()
        print(f"   * Document: {d.original_filename} [{d.processing_status}] | Extracted: {bool(ext)}")

s.close()
