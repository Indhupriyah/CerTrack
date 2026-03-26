from app import create_app, db
from app.models.mentor import MentorAssignment, Message

class MentorSuggestion(db.Model):
    __tablename__ = "mentor_suggestions"
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    suggestion_type = db.Column(db.String(20), nullable=False) # 'certificate', 'event'
    status = db.Column(db.String(20), default="pending")  # pending, accepted, rejected, completed
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(500))
    location = db.Column(db.String(255)) # For events: Online/Offline details
    team_size = db.Column(db.String(50)) # For events
    duration = db.Column(db.String(100)) # For certs
    skills = db.Column(db.String(255)) # For certs
    file_path = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

app = create_app()
with app.app_context():
    db.create_all()
    print("Tables created successfully.")
