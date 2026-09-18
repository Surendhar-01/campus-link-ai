"""Seed Faculty & Alumni Profiles with Structured Resumes.

Adds comprehensive datasets for Faculty and Alumni, complete with credentials (Password123!),
full profile metadata, skills, projects, physical PDF files, and confirmed DocumentExtraction records.
Also seeds a resume for surendharkavin01@gmail.com so the active login has full resume intelligence.
"""

import os
import sys
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SyncSessionLocal
from app.models.users import User, UserRole, UserStatus
from app.models.profiles import Profile, ContactVisibility
from app.models.skills import Skill, UserSkill, ProficiencyLevel, SkillSource
from app.models.documents import Document, DocumentExtraction, DocumentType, ProcessingStatus, ExtractionStatus

logger = logging.getLogger("campuslink.seed.faculty_alumni")

DEV_PASSWORD = "Password123!"


def create_minimal_pdf(title: str, author: str) -> bytes:
    """Generate minimal valid PDF bytes with header and text stream."""
    content = (
        f"%PDF-1.4\n"
        f"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        f"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n"
        f"4 0 obj << /Length 55 >> stream\n"
        f"BT /F1 12 Tf 72 712 Td ({title} - {author}) Tj ET\n"
        f"endstream\nendobj\n"
        f"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000115 00000 n \n0000000216 00000 n \n"
        f"trailer << /Size 5 /Root 1 0 R >>\nstartxref\n320\n%%EOF\n"
    )
    return content.encode("utf-8")


FACULTY_DATA = [
    {
        "email": "faculty1@campuslink.test",
        "full_name": "Dr. Kavitha Raman",
        "department": "Electrical Engineering",
        "designation": "Associate Professor & Lab Director",
        "bio": "Principal Investigator in Embedded Systems, Signal Processing, IoT, and Edge AI sensor network topologies. 15+ years of research in microcontrollers and DSP.",
        "portfolio_url": "https://ee.campuslink.test/faculty/kavitharaman",
        "skills": [("Embedded Systems", "EXPERT"), ("DSP", "EXPERT"), ("IoT", "EXPERT"), ("TinyML", "ADVANCED"), ("Signal Processing", "EXPERT")],
        "resume": {
            "title": "Curriculum Vitae - Dr. Kavitha Raman",
            "education": [
                {"institution": "Indian Institute of Technology Madras", "degree": "Ph.D.", "field": "Electrical Engineering", "start_year": 2008, "end_year": 2013},
                {"institution": "Anna University", "degree": "M.E.", "field": "Applied Electronics", "start_year": 2005, "end_year": 2007},
            ],
            "experience": [
                {"company": "KSRCT / CampusLink", "role": "Associate Professor", "start_date": "2018", "end_date": "Present", "description": "Director of Embedded Systems & IoT Research Laboratory."},
                {"company": "Texas Instruments Research Lab", "role": "Visiting Research Scientist", "start_date": "2014", "end_date": "2017", "description": "Researched ultra-low-power DSP architectures for sensory edge processing."},
            ],
            "technologies": ["ESP32", "STM32", "MATLAB", "FreeRTOS", "Simulink", "C/C++", "Oscilloscopes", "Logic Analyzers"],
        }
    },
    {
        "email": "faculty2@campuslink.test",
        "full_name": "Dr. Arjun Rao",
        "department": "Computer Science",
        "designation": "Professor of Artificial Intelligence",
        "bio": "Professor of Computer Science specializing in Deep Learning, model quantization, distributed training, and neural edge deployment.",
        "portfolio_url": "https://cs.campuslink.test/faculty/arjunrao",
        "skills": [("Machine Learning", "EXPERT"), ("Deep Learning", "EXPERT"), ("Python", "EXPERT"), ("PyTorch", "EXPERT"), ("Model Compression", "ADVANCED")],
        "resume": {
            "title": "Academic CV - Dr. Arjun Rao",
            "education": [
                {"institution": "Indian Institute of Science (IISc)", "degree": "Ph.D.", "field": "Computer Science & Automation", "start_year": 2010, "end_year": 2015},
                {"institution": "NIT Tiruchirappalli", "degree": "B.Tech", "field": "Computer Science", "start_year": 2006, "end_year": 2010},
            ],
            "experience": [
                {"company": "KSRCT / CampusLink", "role": "Professor", "start_date": "2020", "end_date": "Present", "description": "Head of Advanced Machine Learning & Deep Computing Lab."},
                {"company": "Google Research India", "role": "Research Fellow", "start_date": "2016", "end_date": "2019", "description": "Focus on neural model compression and mobile inference speedup."},
            ],
            "technologies": ["PyTorch", "TensorFlow", "CUDA", "TensorRT", "Docker", "Kubernetes", "ONNX", "HuggingFace"],
        }
    },
    {
        "email": "faculty.deepa@campuslink.test",
        "full_name": "Dr. Deepa Sundaram",
        "department": "Electronics and Communication",
        "designation": "Professor & Head of 5G/IoT Lab",
        "bio": "Leading research in Software Defined Radio (SDR), Massive MIMO, 5G/6G physical layer protocols, and campus wireless sensor grids.",
        "portfolio_url": "https://ece.campuslink.test/faculty/deepasundaram",
        "skills": [("Wireless Communication", "EXPERT"), ("5G", "EXPERT"), ("SDR", "EXPERT"), ("MATLAB", "ADVANCED"), ("RF Systems", "ADVANCED")],
        "resume": {
            "title": "Research Profile & CV - Dr. Deepa Sundaram",
            "education": [
                {"institution": "IIT Delhi", "degree": "Ph.D.", "field": "Telecommunications & Wireless", "start_year": 2009, "end_year": 2014},
                {"institution": "PSG College of Technology", "degree": "M.Tech", "field": "Communication Systems", "start_year": 2006, "end_year": 2008},
            ],
            "experience": [
                {"company": "KSRCT / CampusLink", "role": "Professor & HOD", "start_date": "2019", "end_date": "Present", "description": "Chair of Wireless Communications & SDR Testbed."},
                {"company": "Qualcomm Research", "role": "Senior Systems Engineer", "start_date": "2014", "end_date": "2018", "description": "5G-NR physical layer simulation and channel estimation algorithms."},
            ],
            "technologies": ["GNU Radio", "USRP SDR", "MATLAB", "Python", "Keysight Spectrum Analyzers", "LabVIEW"],
        }
    },
    {
        "email": "faculty.rajesh@campuslink.test",
        "full_name": "Dr. Rajesh Kannan",
        "department": "Mechatronics and Robotics",
        "designation": "Associate Professor & Robotics Lab Head",
        "bio": "Specialist in Autonomous Mobile Robots (AMR), ROS2 architecture, SLAM, drone navigation, and industrial manipulator kinematics.",
        "portfolio_url": "https://robotics.campuslink.test/faculty/rajeshkannan",
        "skills": [("Robotics", "EXPERT"), ("ROS2", "EXPERT"), ("SLAM", "EXPERT"), ("Computer Vision", "ADVANCED"), ("Autonomous Systems", "EXPERT")],
        "resume": {
            "title": "Faculty CV - Dr. Rajesh Kannan",
            "education": [
                {"institution": "IIT Bombay", "degree": "Ph.D.", "field": "Systems and Control / Robotics", "start_year": 2011, "end_year": 2016},
                {"institution": "College of Engineering Guindy", "degree": "B.E.", "field": "Mechanical Engineering", "start_year": 2006, "end_year": 2010},
            ],
            "experience": [
                {"company": "KSRCT / CampusLink", "role": "Associate Professor", "start_date": "2020", "end_date": "Present", "description": "Director of Robotics & Autonomous Systems Maker Lab."},
                {"company": "DRDO Labs", "role": "Scientist 'C'", "start_date": "2016", "end_date": "2020", "description": "Unmanned aerial vehicle obstacle avoidance and waypoint navigation."},
            ],
            "technologies": ["ROS2", "Gazebo", "Nav2", "C++", "Python", "LiDAR", "PX4 Autopilot", "SolidWorks"],
        }
    },
    {
        "email": "faculty.priya@campuslink.test",
        "full_name": "Dr. Priya Narayanan",
        "department": "Bioengineering & Data Sciences",
        "designation": "Associate Professor of Bioinformatics",
        "bio": "Genomic data science, protein structure prediction using deep learning, next-generation sequencing pipelines, and computational molecular biology.",
        "portfolio_url": "https://bio.campuslink.test/faculty/priyanarayanan",
        "skills": [("Bioinformatics", "EXPERT"), ("Genomics", "EXPERT"), ("Python", "ADVANCED"), ("High Performance Computing", "ADVANCED"), ("Data Analysis", "EXPERT")],
        "resume": {
            "title": "Academic CV - Dr. Priya Narayanan",
            "education": [
                {"institution": "National University of Singapore (NUS)", "degree": "Ph.D.", "field": "Computational Biology", "start_year": 2012, "end_year": 2017},
                {"institution": "Anna University", "degree": "B.Tech", "field": "Industrial Biotechnology", "start_year": 2008, "end_year": 2012},
            ],
            "experience": [
                {"company": "KSRCT / CampusLink", "role": "Associate Professor", "start_date": "2021", "end_date": "Present", "description": "Head of Computational Genomics & Bioinformatics Lab."},
                {"company": "A*STAR Bioinformatics Institute", "role": "Postdoctoral Researcher", "start_date": "2017", "end_date": "2020", "description": "Whole-genome assembly optimization and RNA-seq variance analysis."},
            ],
            "technologies": ["Python", "R", "Nextflow", "Docker", "AlphaFold", "Biopython", "BLAST", "Snakemake"],
        }
    }
]

ALUMNI_DATA = [
    {
        "email": "alumni1@campuslink.test",
        "full_name": "Siddharth Kumar",
        "department": "Electronics and Communication",
        "designation": "Edge AI Solutions Architect at Qualcomm",
        "bio": "Class of 2021. Specializes in commercial microcontroller keyword spotting models, TinyML, and ultra-low power neural inference hardware.",
        "linkedin_url": "https://linkedin.com/in/synthetic-siddharthkumar",
        "skills": [("TinyML", "EXPERT"), ("Embedded Systems", "EXPERT"), ("ESP32", "ADVANCED"), ("C++", "EXPERT"), ("ARM Cortex", "EXPERT")],
        "resume": {
            "title": "Resume - Siddharth Kumar",
            "education": [
                {"institution": "KSRCT / CampusLink", "degree": "B.E.", "field": "Electronics and Communication", "start_year": 2017, "end_year": 2021, "grade": "8.9 CGPA"}
            ],
            "experience": [
                {"company": "Qualcomm", "role": "Edge AI Solutions Architect", "start_date": "2023", "end_date": "Present", "description": "Deploying on-device NPU audio processing models for automotive and smart home chips."},
                {"company": "Silicon Labs", "role": "Embedded Firmware Engineer", "start_date": "2021", "end_date": "2023", "description": "Developed BLE and Zigbee sensory mesh node firmware with low-power sleep modes."},
            ],
            "technologies": ["ARM Cortex-M", "ESP32", "FreeRTOS", "TFLite-Micro", "C++", "Edge Impulse", "GDB", "I2C/SPI"],
        }
    },
    {
        "email": "alumni.harish@campuslink.test",
        "full_name": "Harish Balaji",
        "department": "Computer Science",
        "designation": "Principal Cloud Architect at Amazon Web Services",
        "bio": "Class of 2020. Designs distributed, event-driven cloud systems handling millions of concurrent TPS. Active campus mentor for cloud and DevOps.",
        "linkedin_url": "https://linkedin.com/in/synthetic-harishbalaji",
        "skills": [("Cloud Architecture", "EXPERT"), ("Kubernetes", "EXPERT"), ("Distributed Systems", "EXPERT"), ("Go", "ADVANCED"), ("AWS", "EXPERT")],
        "resume": {
            "title": "Resume - Harish Balaji",
            "education": [
                {"institution": "KSRCT / CampusLink", "degree": "B.Tech", "field": "Computer Science and Engineering", "start_year": 2016, "end_year": 2020, "grade": "9.2 CGPA"}
            ],
            "experience": [
                {"company": "Amazon Web Services (AWS)", "role": "Principal Cloud Architect", "start_date": "2023", "end_date": "Present", "description": "Architecting resilient multi-region infrastructure and serverless streaming platforms."},
                {"company": "Zoho Corporation", "role": "Senior Infrastructure Engineer", "start_date": "2020", "end_date": "2023", "description": "Managed multi-tenant Kubernetes clusters and database partitioning."},
            ],
            "technologies": ["AWS", "Kubernetes", "Terraform", "Go", "Docker", "Apache Kafka", "PostgreSQL", "Prometheus"],
        }
    },
    {
        "email": "alumni.sneha@campuslink.test",
        "full_name": "Sneha Varma",
        "department": "Electrical and Electronics",
        "designation": "Senior Firmware Architect at Texas Instruments",
        "bio": "Class of 2022. Expert in bare-metal C/C++, RTOS kernel tuning, automotive CAN bus networks, and precision hardware interfaces.",
        "linkedin_url": "https://linkedin.com/in/synthetic-snehavarma",
        "skills": [("Embedded C", "EXPERT"), ("RTOS", "EXPERT"), ("STM32", "EXPERT"), ("Hardware Protocols", "EXPERT"), ("Firmware", "EXPERT")],
        "resume": {
            "title": "Resume - Sneha Varma",
            "education": [
                {"institution": "KSRCT / CampusLink", "degree": "B.E.", "field": "Electrical and Electronics Engineering", "start_year": 2018, "end_year": 2022, "grade": "9.0 CGPA"}
            ],
            "experience": [
                {"company": "Texas Instruments", "role": "Senior Firmware Architect", "start_date": "2024", "end_date": "Present", "description": "Driver development for C2000 real-time microcontrollers and motor control systems."},
                {"company": "Bosch Global Software", "role": "Embedded Software Engineer", "start_date": "2022", "end_date": "2024", "description": "Developed AUTOSAR compliant sensor communication layers for electric vehicles."},
            ],
            "technologies": ["C", "C++", "FreeRTOS", "STM32CubeIDE", "CANopen", "JTAG", "Oscilloscopes", "I2C/SPI/UART"],
        }
    },
    {
        "email": "alumni.karthik@campuslink.test",
        "full_name": "Karthik Subramanian",
        "department": "Information Technology",
        "designation": "Lead Machine Learning Scientist at Microsoft Research",
        "bio": "Class of 2019. Researches retrieval-augmented generation (RAG), vector embeddings, and LLM fine-tuning for domain-specific engineering applications.",
        "linkedin_url": "https://linkedin.com/in/synthetic-karthiksubramanian",
        "skills": [("Natural Language Processing", "EXPERT"), ("LLMs", "EXPERT"), ("Vector Search", "EXPERT"), ("PyTorch", "EXPERT"), ("Python", "EXPERT")],
        "resume": {
            "title": "Resume - Karthik Subramanian",
            "education": [
                {"institution": "KSRCT / CampusLink", "degree": "B.Tech", "field": "Information Technology", "start_year": 2015, "end_year": 2019, "grade": "8.8 CGPA"},
                {"institution": "IIIT Hyderabad", "degree": "M.S. by Research", "field": "Computer Science (NLP)", "start_year": 2019, "end_year": 2021}
            ],
            "experience": [
                {"company": "Microsoft Research", "role": "Lead ML Scientist", "start_date": "2023", "end_date": "Present", "description": "Developing neural search algorithms and efficient dense retrieval indexes."},
                {"company": "Flipkart AI Labs", "role": "Applied Scientist", "start_date": "2021", "end_date": "2023", "description": "Semantic catalog search, hybrid lexical-vector ranking, and transformer models."},
            ],
            "technologies": ["PyTorch", "HuggingFace", "FAISS", "pgvector", "LangChain", "FastAPI", "Ray", "Triton"],
        }
    },
    {
        "email": "alumni.divya@campuslink.test",
        "full_name": "Divya Chandran",
        "department": "Mechatronics Engineering",
        "designation": "Senior Robotics Platform Engineer at GreyOrange",
        "bio": "Class of 2023. Specializes in multi-robot fleet dispatching, warehouse AMR navigation, 3D LiDAR SLAM, and safety critical embedded nodes.",
        "linkedin_url": "https://linkedin.com/in/synthetic-divyachandran",
        "skills": [("ROS2", "EXPERT"), ("SLAM", "EXPERT"), ("Mobile Robotics", "EXPERT"), ("C++", "ADVANCED"), ("Kinematics", "ADVANCED")],
        "resume": {
            "title": "Resume - Divya Chandran",
            "education": [
                {"institution": "KSRCT / CampusLink", "degree": "B.E.", "field": "Mechatronics Engineering", "start_year": 2019, "end_year": 2023, "grade": "9.1 CGPA"}
            ],
            "experience": [
                {"company": "GreyOrange Robotics", "role": "Senior Robotics Platform Engineer", "start_date": "2023", "end_date": "Present", "description": "Full-stack robotics development for autonomous warehouse mobile picking robots."},
                {"company": "KSRCT Maker Lab", "role": "Autonomous Systems Lead", "start_date": "2021", "end_date": "2023", "description": "Led student autonomous campus ground rover project with GPS and stereo vision."},
            ],
            "technologies": ["ROS2", "Nav2", "Cartographer", "C++", "Python", "Velodyne LiDAR", "OpenCV", "Gazebo"],
        }
    }
]


def seed_resumes_for_user(session: Session, user: User, full_name: str, resume_info: Dict[str, Any]):
    """Attach Document and DocumentExtraction records with physical storage file."""
    storage_dir = Path(settings.STORAGE_DIR).resolve()
    user_storage_dir = storage_dir / str(user.id)
    user_storage_dir.mkdir(parents=True, exist_ok=True)

    doc_id = uuid.uuid4()
    storage_rel_key = f"{user.id}/{doc_id}.pdf"
    file_path = storage_dir / storage_rel_key

    # 1. Write physical PDF file to local storage
    pdf_bytes = create_minimal_pdf(resume_info.get("title", "Resume"), full_name)
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    # 2. Check if user already has an active resume document
    existing_doc = session.query(Document).filter(
        Document.owner_id == user.id,
        Document.document_type == DocumentType.RESUME
    ).first()

    if existing_doc:
        doc = existing_doc
        doc.processing_status = ProcessingStatus.CONFIRMED
        doc.storage_key = storage_rel_key
        doc.file_size = len(pdf_bytes)
    else:
        doc = Document(
            id=doc_id,
            owner_id=user.id,
            document_type=DocumentType.RESUME,
            original_filename=f"{full_name.replace(' ', '_')}_Resume.pdf",
            storage_key=storage_rel_key,
            mime_type="application/pdf",
            file_size=len(pdf_bytes),
            processing_status=ProcessingStatus.CONFIRMED,
        )
        session.add(doc)
        session.flush()

    # 3. Create or update DocumentExtraction with comprehensive parsed structured intelligence
    existing_ext = session.query(DocumentExtraction).filter(DocumentExtraction.document_id == doc.id).first()

    extracted_data = {
        "personal_info": {
            "full_name": full_name,
            "email": user.email,
            "phone": "+91 98765 43210",
            "location": "Tamil Nadu, India",
            "portfolio_url": getattr(user.profile, "portfolio_url", None) or f"https://portfolio.campuslink.test/{user.email.split('@')[0]}",
            "github_url": getattr(user.profile, "github_url", None) or f"https://github.com/{user.email.split('@')[0]}",
            "linkedin_url": getattr(user.profile, "linkedin_url", None) or f"https://linkedin.com/in/{user.email.split('@')[0]}",
        },
        "education": resume_info.get("education", [
            {
                "institution": "KSRCT / CampusLink University",
                "degree": "B.Tech",
                "field": user.profile.department if user.profile else "Computer Science",
                "start_year": 2021,
                "end_year": 2025,
                "grade": "8.8 CGPA"
            }
        ]),
        "experience": resume_info.get("experience", [
            {
                "company": "CampusLink AI Research Lab",
                "role": "Lead Researcher / Engineer",
                "start_date": "2023",
                "end_date": "Present",
                "description": f"Specialized engineering and practical implementation in {user.profile.department if user.profile else 'Technology'}."
            }
        ]),
        "skills": [
            {"name": s_name, "proficiency": s_prof, "confidence": 0.95, "provenance": "EXPLICIT"}
            for s_name, s_prof in getattr(user.profile, "_skills_to_seed", [])
        ],
        "technologies": [
            {"name": t, "category": "Core Tool", "confidence": 0.95, "provenance": "EXPLICIT"}
            for t in resume_info.get("technologies", ["Python", "Git", "Linux", "Docker"])
        ],
        "summary": getattr(user.profile, "bio", f"Experienced professional in {getattr(user.profile, 'department', 'Engineering')}."),
    }

    if existing_ext:
        existing_ext.extracted_data = extracted_data
        existing_ext.extraction_status = ExtractionStatus.COMPLETED
        existing_ext.confidence = 0.96
        existing_ext.model_name = "gemini-1.5-pro"
        existing_ext.reviewed_at = datetime.now(timezone.utc)
    else:
        extraction = DocumentExtraction(
            document_id=doc.id,
            extracted_data=extracted_data,
            model_name="gemini-1.5-pro",
            model_version="1.5",
            confidence=0.96,
            extraction_status=ExtractionStatus.COMPLETED,
            reviewed_at=datetime.now(timezone.utc),
        )
        session.add(extraction)


def seed_faculty_and_alumni(session: Optional[Session] = None, dev_password_hash: Optional[str] = None):
    """Seed faculties, alumni, skills, resumes, and extractions."""
    should_close = False
    if session is None:
        session = SyncSessionLocal()
        should_close = True

    if dev_password_hash is None:
        dev_password_hash = hash_password(DEV_PASSWORD)

    try:
        # Cache existing skills
        existing_skills = {s.normalized_name: s for s in session.query(Skill).all()}

        def get_or_create_skill(name: str) -> Skill:
            norm = name.strip().lower()
            if norm in existing_skills:
                return existing_skills[norm]
            skill = Skill(name=name, normalized_name=norm, category="Technical")
            session.add(skill)
            session.flush()
            existing_skills[norm] = skill
            return skill

        # 1. PROCESS FACULTIES
        for item in FACULTY_DATA:
            user = session.query(User).filter(User.email == item["email"]).first()
            if not user:
                user = User(
                    email=item["email"],
                    password_hash=dev_password_hash,
                    role=UserRole.FACULTY,
                    status=UserStatus.ACTIVE,
                    email_verified=True,
                )
                session.add(user)
                session.flush()

            profile = session.query(Profile).filter(Profile.user_id == user.id).first()
            if not profile:
                profile = Profile(
                    user_id=user.id,
                    full_name=item["full_name"],
                    department=item["department"],
                    designation=item["designation"],
                    bio=item["bio"],
                    portfolio_url=item.get("portfolio_url"),
                    searchable=True,
                    contact_visibility=ContactVisibility.PUBLIC,
                    show_email=True,
                    show_phone=True,
                    profile_completed=True,
                )
                session.add(profile)
                session.flush()
            else:
                profile.full_name = item["full_name"]
                profile.department = item["department"]
                profile.designation = item["designation"]
                profile.bio = item["bio"]
                profile.searchable = True
                profile.profile_completed = True

            profile._skills_to_seed = item["skills"]

            for s_name, s_prof in item["skills"]:
                sk_obj = get_or_create_skill(s_name)
                user_skill = session.query(UserSkill).filter(
                    UserSkill.user_id == user.id, UserSkill.skill_id == sk_obj.id
                ).first()
                if not user_skill:
                    session.add(UserSkill(
                        user_id=user.id,
                        skill_id=sk_obj.id,
                        proficiency=getattr(ProficiencyLevel, s_prof, ProficiencyLevel.EXPERT),
                        source=SkillSource.USER,
                        confidence=0.95,
                    ))

            seed_resumes_for_user(session, user, item["full_name"], item["resume"])

        # 2. PROCESS ALUMNI
        for item in ALUMNI_DATA:
            user = session.query(User).filter(User.email == item["email"]).first()
            if not user:
                user = User(
                    email=item["email"],
                    password_hash=dev_password_hash,
                    role=UserRole.ALUMNI,
                    status=UserStatus.ACTIVE,
                    email_verified=True,
                )
                session.add(user)
                session.flush()

            profile = session.query(Profile).filter(Profile.user_id == user.id).first()
            if not profile:
                profile = Profile(
                    user_id=user.id,
                    full_name=item["full_name"],
                    department=item["department"],
                    designation=item["designation"],
                    bio=item["bio"],
                    linkedin_url=item.get("linkedin_url"),
                    searchable=True,
                    contact_visibility=ContactVisibility.PUBLIC,
                    show_email=True,
                    show_phone=True,
                    profile_completed=True,
                )
                session.add(profile)
                session.flush()
            else:
                profile.full_name = item["full_name"]
                profile.department = item["department"]
                profile.designation = item["designation"]
                profile.bio = item["bio"]
                profile.searchable = True
                profile.profile_completed = True

            profile._skills_to_seed = item["skills"]

            for s_name, s_prof in item["skills"]:
                sk_obj = get_or_create_skill(s_name)
                user_skill = session.query(UserSkill).filter(
                    UserSkill.user_id == user.id, UserSkill.skill_id == sk_obj.id
                ).first()
                if not user_skill:
                    session.add(UserSkill(
                        user_id=user.id,
                        skill_id=sk_obj.id,
                        proficiency=getattr(ProficiencyLevel, s_prof, ProficiencyLevel.ADVANCED),
                        source=SkillSource.USER,
                        confidence=0.95,
                    ))

            seed_resumes_for_user(session, user, item["full_name"], item["resume"])

        # 3. SEED RESUME FOR CURRENT LOGGED-IN USER
        active_user = session.query(User).filter(User.email.ilike("%surendhar%")).first()
        if active_user:
            surendhar_resume = {
                "title": "Resume - Surendhar Kavin",
                "education": [
                    {"institution": "K.S. Rangasamy College of Technology", "degree": "B.E.", "field": "Computer Science and Engineering", "start_year": 2022, "end_year": 2026, "grade": "8.9 CGPA"}
                ],
                "experience": [
                    {"company": "CampusLink AI", "role": "Lead Full Stack & AI Developer", "start_date": "2024", "end_date": "Present", "description": "Designed agentic campus discovery platform with FastAPI, Next.js, LangGraph, and pgvector."},
                    {"company": "KSRCT Innovation Cell", "role": "Full Stack Developer", "start_date": "2023", "end_date": "2024", "description": "Built reactive web applications with TypeScript, React, and PostgreSQL."},
                ],
                "technologies": ["Next.js", "React", "TypeScript", "Python", "FastAPI", "PostgreSQL", "pgvector", "Docker", "Tailwind CSS", "LangChain"],
            }
            if active_user.profile:
                active_user.profile._skills_to_seed = [
                    ("Next.js", "EXPERT"), ("TypeScript", "EXPERT"), ("Python", "EXPERT"),
                    ("FastAPI", "ADVANCED"), ("PostgreSQL", "ADVANCED"), ("Artificial Intelligence", "ADVANCED")
                ]
                for s_name, s_prof in active_user.profile._skills_to_seed:
                    sk = get_or_create_skill(s_name)
                    if not session.query(UserSkill).filter(UserSkill.user_id == active_user.id, UserSkill.skill_id == sk.id).first():
                        session.add(UserSkill(user_id=active_user.id, skill_id=sk.id, proficiency=ProficiencyLevel.EXPERT, source=SkillSource.USER))
            seed_resumes_for_user(session, active_user, active_user.profile.full_name if active_user.profile else "Surendhar Kavin", surendhar_resume)

        # 4. Sync public.users to auth.users so Supabase Auth UI displays all accounts
        try:
            from sqlalchemy import text
            import json
            all_users = session.execute(text("""
                SELECT u.id, u.email, u.role, u.created_at, u.updated_at, p.full_name, p.department
                FROM public.users u
                LEFT JOIN public.profiles p ON u.id = p.user_id
            """)).fetchall()
            for u in all_users:
                uid, email, role, created_at, updated_at, full_name, dept = u
                raw_user_meta = json.dumps({"full_name": full_name or "", "role": str(role), "department": dept or ""})
                raw_app_meta = json.dumps({"provider": "email", "providers": ["email"]})
                session.execute(text("""
                    INSERT INTO auth.users (
                        id, aud, role, email, raw_app_meta_data, raw_user_meta_data,
                        email_confirmed_at, created_at, updated_at, is_sso_user, is_anonymous
                    ) VALUES (
                        CAST(:id AS uuid), 'authenticated', 'authenticated', :email,
                        CAST(:raw_app_meta AS jsonb), CAST(:raw_user_meta AS jsonb),
                        NOW(), :created_at, :updated_at, false, false
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
        except Exception as auth_sync_err:
            logger.warning(f"Could not sync to auth.users (non-fatal): {auth_sync_err}")

        if should_close:
            session.commit()
            from app.services.embedding_index_service import EmbeddingIndexService
            EmbeddingIndexService().reindex_all(session)

    except Exception:
        if should_close:
            session.rollback()
        raise
    finally:
        if should_close:
            session.close()
