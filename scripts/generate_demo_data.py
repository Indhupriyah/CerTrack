import sys
import os
import random
from datetime import datetime, timedelta
import uuid

# Add the project root to the python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models.user import User
from app.models.mentor import MentorAssignment
from app.models.certification import Certification
from app.models.event import Event
from app.utils.auth import hash_password, generate_slug

app = create_app()

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Aryan", "Krishna", "Ishaan", "Shaurya", "Atharva", "Ayaan", "Dhruv", "Rishi", "Saanvi", "Aanya", "Aadhya", "Aaradhya", "Ananya", "Pari", "Diya", "Navya", "Anushka", "Avni", "Mahi", "Kiara", "Kriti", "Sneha", "Aditi", "John", "David", "Michael", "Sarah", "Jessica", "Laura", "Emma", "Olivia", "James", "William", "Sophia", "Liam", "Noah", "Jackson", "Lucas", "Mateo", "Harper", "Evelyn", "Abigail"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Malhotra", "Singh", "Kumar", "Patel", "Reddy", "Rao", "Das", "Joshi", "Chawla", "Mehta", "Bose", "Nair", "Iyer", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson"]

FIELDS = ["Python", "Java", "AI", "Cybersecurity", "IoT", "Cloud Computing", "Data Science", "Web Development", ".NET"]

CERT_PLATFORMS = ["Coursera", "Udemy", "edX", "AWS", "Google", "Microsoft", "IBM", "Cisco", "Oracle"]
CERT_STATUSES = ["upcoming", "in_progress", "completed", "missed"]

EVENT_TYPES = ["hackathon", "workshop", "coding_contest", "paper_presentation", "webinar"]
EVENT_ORGANIZERS = ["Tech Club", "IEEE", "ACM", "GDG", "Microsoft Student Learn", "AWS Educate", "University", "Local Tech Community"]
EVENT_MODES = ["online", "offline"]
EVENT_STAGES = ["upcoming", "registered", "participated", "result_declared", "archived"]

def generate_user(is_mentor=False):
    fname = random.choice(FIRST_NAMES)
    lname = random.choice(LAST_NAMES)
    display_name = f"{fname} {lname}"
    
    unique_suffix = str(uuid.uuid4())[:6]
    domain = "mentor.certrack.local" if is_mentor else "student.certrack.local"
    email = f"{fname.lower()}.{lname.lower()}_{unique_suffix}@{domain}"
    
    password = "mentor123" if is_mentor else "user123"
    
    user = User(
        email=email,
        password_hash=hash_password(password),
        display_name=display_name,
        is_mentor=is_mentor,
        public_slug=generate_slug()
    )
    if is_mentor:
        user.department = random.choice(["Computer Science", "Information Technology", "AI & Data Science"])
    else:
        user.year_of_study = random.choice(["1st Year", "2nd Year", "3rd Year", "4th Year"])
        user.department = random.choice(["CSE", "IT", "AI&DS", "ECE"])
        user.study_streak = random.randint(0, 30)
    
    return user

def generate_certification(user_id):
    field = random.choice(FIELDS)
    platform = random.choice(CERT_PLATFORMS)
    status = random.choice(CERT_STATUSES)
    
    name_templates = [
        f"Introduction to {field}",
        f"Advanced {field} Specialization",
        f"{platform} Certified {field} Developer",
        f"Mastering {field}",
        f"{field} for Beginners"
    ]
    name = random.choice(name_templates)
    
    now = datetime.utcnow()
    deadline = now + timedelta(days=random.randint(5, 60))
    expected = deadline + timedelta(days=random.randint(10, 60))
    completed = expected if status == "completed" else None
    
    return Certification(
        user_id=user_id,
        name=name,
        platform=platform,
        status=status,
        skill_tags=f"{field},{random.choice(['Development','Security','Cloud','AI'])}",
        registration_deadline=deadline.date(),
        expected_completion=expected.date(),
        completed_date=completed.date() if completed else None
    )

def generate_event(user_id):
    field = random.choice(FIELDS)
    event_type = random.choice(EVENT_TYPES)
    
    name_templates = [
        f"Global {field} Challenge",
        f"{field} Innovation Hackathon",
        f"National Workshop on {field}",
        f"Learn {field} in 24 Hours",
        f"{field} Summit 2026"
    ]
    name = random.choice(name_templates)
    
    now = datetime.utcnow()
    event_date = now + timedelta(days=random.randint(-30, 60))
    deadline = event_date - timedelta(days=random.randint(5, 20))
    result = event_date + timedelta(days=random.randint(2, 14))
    
    return Event(
        user_id=user_id,
        name=name,
        event_type=event_type,
        organizer=random.choice(EVENT_ORGANIZERS),
        participation_mode=random.choice(EVENT_MODES),
        location="Virtual" if random.choice(EVENT_MODES) == "online" else "Main Auditorium",
        registration_deadline=deadline.date(),
        event_date=event_date.date(),
        result_date=result.date(),
        stage=random.choice(EVENT_STAGES)
    )

def main():
    with app.app_context():
        print("Starting data generation process...")
        
        # Determine current user counts to display later
        mentors_count = 0
        students_count = 0
        
        print("Creating 20 mentors...")
        mentors = []
        for _ in range(20):
            mentor = generate_user(is_mentor=True)
            db.session.add(mentor)
            mentors.append(mentor)
        
        print("Creating 150 normal users (students)...")
        students = []
        for _ in range(150):
            student = generate_user(is_mentor=False)
            db.session.add(student)
            students.append(student)
            
        # Commit to generate IDs for users
        db.session.commit()
        
        print("Generating certifications and events for users...")
        for user in students + mentors:
            # Add 1 to 4 certifications
            for _ in range(random.randint(1, 4)):
                cert = generate_certification(user.id)
                db.session.add(cert)
            
            # Add 1 to 4 events
            for _ in range(random.randint(1, 4)):
                event = generate_event(user.id)
                db.session.add(event)
                
        # Assign students to mentors randomly
        print("Creating mentor-student assignments...")
        # Each mentor gets a random number of students between 4 and 9 to keep it under 10
        # and distribute 150 students among 20 mentors.
        # We will iterate students and assign them to a mentor randomly, 
        # but check until we find a mentor with less than 9 students
        
        mentor_student_count = {m.id: 0 for m in mentors}
        
        for student in students:
            # find available mentors
            available_mentors = [m for m in mentors if mentor_student_count[m.id] < 9]
            if not available_mentors:
                # If all mentors somehow full, relax restriction to 10
                available_mentors = [m for m in mentors if mentor_student_count[m.id] < 10]
                
            if available_mentors:
                selected_mentor = random.choice(available_mentors)
                assignment = MentorAssignment(
                    mentor_id=selected_mentor.id,
                    student_id=student.id,
                    status="accepted"
                )
                db.session.add(assignment)
                mentor_student_count[selected_mentor.id] += 1
                
        db.session.commit()
        
        print(f"Data generation complete!")
        print(f"Added 150 students with password 'user123'.")
        print(f"Added 20 mentors with password 'mentor123'.")
        print("Added random certifications and events.")
        print("Students assigned to mentors (max 9 students per mentor).")
        
if __name__ == "__main__":
    main()
