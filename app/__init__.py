"""CerTrack - Student Certification & Event Platform."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


def create_app(config=None):
    """Application factory."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        static_folder=os.path.join(root, "static"),
        template_folder=os.path.join(root, "templates")
    )
    
    # Config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///certrack.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME", "noreply@certrack.dev")

    if config:
        app.config.update(config)
    
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.certifications import cert_bp
    from app.routes.events import events_bp
    from app.routes.portfolio import portfolio_bp
    from app.routes.api import api_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.mentor_routes import mentor_bp
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp)
    app.register_blueprint(mentor_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(cert_bp, url_prefix="/certifications")
    app.register_blueprint(events_bp, url_prefix="/events")
    app.register_blueprint(portfolio_bp, url_prefix="/portfolio")
    app.register_blueprint(api_bp, url_prefix="/api")
    
    @app.context_processor
    def inject_unread_count():
        from flask_login import current_user
        from app.models.mentor import Message
        if current_user.is_authenticated:
            unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
            return dict(unread_messages_count=unread_count)
        return dict(unread_messages_count=0)
    
    with app.app_context():
        from app.models.reminder_log import ReminderLog  # noqa: F401
        from app.models.career_admin import CareerRole, CertificationTemplate, Report, AdminActionLog  # noqa: F401
        from app.models.monthly_goal import MonthlyGoal  # noqa: F401
        from app.models.mentor import MentorAssignment  # noqa: F401
        db.create_all()
        _seed_career_roles(app)
        _seed_default_admin(app)
    
    return app


def _seed_default_admin(app):
    """Create or update default admin account (email and password in code)."""
    from app.models.user import User
    from app.utils.auth import hash_password, generate_slug
    with app.app_context():
        default_admin_email = "indhupriyah10@gmail.com"
        default_admin_password = "admin123"
        user = User.query.filter_by(email=default_admin_email).first()
        if not user:
            user = User(
                email=default_admin_email,
                password_hash=hash_password(default_admin_password),
                username="admin",
                display_name="Admin",
                public_slug=generate_slug(),
                is_admin=True,
            )
            db.session.add(user)
        else:
            user.is_admin = True
            user.username = user.username or "admin"
            user.password_hash = hash_password(default_admin_password)
            user.deleted_at = None
            user.is_suspended = False
        db.session.commit()


def _seed_career_roles(app):
    """Seed career roles for gap analyzer. Adds any role that doesn't exist (by name)."""
    from app.models.career_admin import CareerRole
    with app.app_context():
        defaults = [
            ("Data Analyst", "Python, SQL, Statistics, Excel, Data Visualization, Power BI, Tableau", "Data, Analytics, SQL, Python"),
            ("Backend Developer", "Python, Java, SQL, APIs, REST, Databases, Node.js, C#", "AWS, Cloud, API, Backend"),
            ("Frontend Developer", "JavaScript, HTML, CSS, React, Vue, Angular, TypeScript, Responsive Design", "Frontend, React, JavaScript"),
            ("Full Stack Developer", "JavaScript, Python, SQL, React, Node.js, APIs, REST, Databases", "Full Stack, MERN, MEAN"),
            ("UI/UX Designer", "Design, Figma, User Research, Prototyping, UI, Wireframing, Usability", "Design, UX, UI"),
            ("Cybersecurity Engineer", "Security, Networking, Linux, Python, Cryptography, Penetration Testing", "Security, CISSP, CEH"),
            ("DevOps Engineer", "Linux, CI/CD, Docker, Kubernetes, AWS, Terraform, Scripting, Monitoring", "DevOps, AWS, Kubernetes"),
            ("Cloud Architect", "AWS, Azure, GCP, Cloud Design, Networking, Security, Cost Optimization", "AWS, Azure, GCP"),
            ("Data Engineer", "Python, SQL, ETL, Spark, Data Warehousing, Airflow, Big Data", "Data, ETL, Spark"),
            ("Machine Learning Engineer", "Python, ML, Deep Learning, TensorFlow, PyTorch, Statistics, SQL", "ML, AI, Python"),
            ("Software Engineer", "Programming, Data Structures, Algorithms, OOP, Version Control, Testing", "Software, Coding"),
            ("QA Engineer", "Testing, Automation, Selenium, API Testing, Test Planning, Bug Tracking", "QA, Testing, Selenium"),
            ("Mobile Developer", "Swift, Kotlin, React Native, Flutter, Mobile UI, APIs", "Mobile, iOS, Android"),
            ("Product Manager", "Product Strategy, Roadmaps, Agile, User Stories, Analytics, Stakeholder Management", "Product, Agile"),
            ("Project Manager", "Planning, Agile, Scrum, Risk Management, Budgeting, Communication", "PMP, Agile, Scrum"),
            ("Business Analyst", "Requirements, Process Modeling, SQL, Stakeholder Analysis, Documentation", "Business Analysis"),
            ("Database Administrator", "SQL, Database Design, Performance Tuning, Backup, Security", "DBA, SQL"),
            ("Network Engineer", "Networking, TCP/IP, Firewalls, VPN, Cisco, Monitoring", "Network, CCNA"),
            ("Security Analyst", "SIEM, Threat Detection, Incident Response, Compliance, Vulnerability Assessment", "Security, SOC"),
            ("Solutions Architect", "System Design, Cloud, Integration, Security, Scalability", "Architecture, AWS"),
            ("Site Reliability Engineer", "Monitoring, Incident Response, Automation, Linux, Kubernetes", "SRE, DevOps"),
            ("Blockchain Developer", "Solidity, Smart Contracts, Ethereum, Cryptography, Web3", "Blockchain, Web3"),
            ("Game Developer", "C++, Unity, Unreal, Game Design, 3D, Physics", "Game, Unity"),
            ("Embedded Engineer", "C, C++, RTOS, Microcontrollers, Hardware, Debugging", "Embedded, IoT"),
            ("Technical Writer", "Documentation, API Docs, Technical Communication, Markdown", "Documentation"),
            ("Scrum Master", "Agile, Scrum, Facilitation, Coaching, Sprint Planning", "Scrum, Agile"),
            ("Data Scientist", "Python, Statistics, ML, SQL, Visualization, Experimentation", "Data Science, Python"),
            ("iOS Developer", "Swift, Xcode, UIKit, SwiftUI, iOS APIs", "iOS, Swift"),
            ("Android Developer", "Kotlin, Java, Android Studio, Jetpack, Material Design", "Android, Kotlin"),
            ("Python Developer", "Python, Django, Flask, APIs, Testing, Packaging", "Python, Backend"),
            ("Java Developer", "Java, Spring Boot, Maven, REST, Microservices", "Java, Spring"),
            (".NET Developer", "C#, .NET, ASP.NET, Entity Framework, Azure", ".NET, C#"),
            ("React Developer", "React, JavaScript, Redux, Hooks, Component Design", "React, Frontend"),
            ("Salesforce Developer", "Apex, Lightning, Salesforce Platform, Integration", "Salesforce"),
            ("WordPress Developer", "PHP, WordPress, Themes, Plugins, CSS", "WordPress"),
            ("Technical Support Engineer", "Troubleshooting, Documentation, Customer Communication, Ticketing", "Support"),
            ("IT Administrator", "Windows Server, Active Directory, Backup, Monitoring, Scripting", "IT, Sysadmin"),
            ("Compliance Analyst", "Regulations, Auditing, Risk Assessment, Documentation", "Compliance"),
            ("Penetration Tester", "Ethical Hacking, Vulnerability Assessment, Reporting, Tools", "Pentest, Security"),
        ]
        for name, skills, keywords in defaults:
            if not CareerRole.query.filter_by(name=name).first():
                db.session.add(CareerRole(name=name, required_skills=skills, recommended_cert_keywords=keywords))
        db.session.commit()
