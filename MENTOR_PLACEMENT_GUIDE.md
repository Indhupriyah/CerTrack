# CerTrack - Mentor & Placement Portals

## Overview

CerTrack provides two specialized portals for faculty and placement staff to manage student development and career readiness.

---

## 🎓 Mentor Portal

### Core Purpose
The Mentor Portal enables faculty members to monitor assigned students' academic progress and support their career development through data-driven insights.

### Key Features

#### 1. **Monitor Student Progress**
   - Track certification completion rates (completed vs. total)
   - View event participation metrics
   - Monitor activity frequency and engagement levels
   - See progress trends and patterns

#### 2. **Identify Skill Gaps**
   - View Career Gap Analyzer results
   - Understand missing competencies for each student
   - Get personalized recommendations based on gaps
   - Track skill acquisition over time

#### 3. **Provide Academic Guidance**
   - Recommend certifications aligned with career goals
   - Suggest workshops and hackathons for skill development
   - Guide students toward industry-relevant credentials
   - Provide structured learning pathways

#### 4. **Detect Inactive or Struggling Students**
   - Real-time alerts for students inactive 14+ days
   - Identify students with low productivity scores
   - Flag students with approaching deadlines
   - Prioritize at-risk students for intervention

#### 5. **Support Career Development**
   - Guide students toward industry-relevant skills
   - Connect certifications to career outcomes
   - Recommend role-specific learning paths
   - Track career readiness evolution

#### 6. **Track Student Performance Trends**
   - Observe progress patterns across semesters
   - Monitor improvement in productivity scores
   - Track certification milestone achievements
   - Analyze engagement consistency

#### 7. **Encourage Consistent Learning**
   - Celebrate skill milestones
   - Recognize achievement streaks
   - Provide motivation through progress visualization
   - Support continuous skill development

### Dashboard Metrics
- **Total Students**: Overview of assigned student count
- **Active Students**: Students with recent activity
- **Inactive Students**: Quick identification of disengaged learners
- **At-Risk Students**: Students needing immediate attention
- **Certification Progress**: Completion rates per student
- **Productivity Score**: Activity and engagement metrics (0-10 scale)
- **Career Readiness Score**: Job-readiness assessment (0-10 scale)

### Mentor Login
- **URL**: `/auth/mentor-login`
- **Email**: mentor@certrack.local
- **Password**: mentor123

---

## 📋 Placement Cell Portal

### Core Purpose
The Placement Portal provides institutional analytics and recruitment tools to support career placement efforts and identify job-ready students.

### Key Features

#### 1. **Evaluate Career Readiness**
   - Use Career Readiness Scores (0-10) to identify job-ready students (8+)
   - Identify students in different readiness stages
   - Track readiness evolution across the semester
   - Prepare cohorts for placement drives

#### 2. **Analyze Institutional Skill Distribution**
   - View which skills are strong across departments
   - Identify weak or underrepresented competencies
   - Plan institutional training initiatives
   - Support curriculum planning with data

#### 3. **Identify Top Talent**
   - Filter students by readiness score
   - Search by certifications completed
   - Filter by skill areas and expertise
   - Identify high-performing cohorts

#### 4. **Support Recruitment Preparation**
   - Match student profiles with industry role requirements
   - Prepare shortlists for specific companies
   - Plan mock interviews and prep sessions
   - Organize batch-wise placement activities

#### 5. **Plan Training Programs**
   - Detect skill gaps at institutional level
   - Organize certification drives for missing skills
   - Plan workshops for high-demand competencies
   - Track training effectiveness

#### 6. **Track Certification Trends**
   - Analyze monthly certification completion rates
   - Identify trending certifications
   - Measure adoption of new skill domains
   - Support data-driven training decisions

#### 7. **Shortlist Students for Opportunities**
   - Quick search by multiple criteria
   - Filter by career readiness score
   - Filter by certifications and skills
   - Export eligible student lists
   - Support internship and placement matching

### Dashboard Analytics

#### Career Readiness Distribution
- **Job Ready (8+)**: Students ready for immediate placement
- **Nearly Ready (5-7)**: Students needing targeted preparation
- **Early Stage (0-4)**: Students requiring foundational support

#### Certification Trends
- 12-month visualization of certification completions
- Monthly comparison for trend analysis
- Identify peak learning periods

#### Skill Coverage
- Institution-wide skill distribution
- Student count per skill area
- Visual representation of skill gaps
- Identify high-demand vs. underutilized skills

#### Student Search & Filter
- Search by name or email
- Filter by career readiness score (minimum threshold)
- Filter by specific certifications
- Filter by skill areas
- Filter by career role interests

### Placement Login
- **URL**: `/auth/placement-login`
- **Email**: placement@certrack.local
- **Password**: placement123

---

## 🔐 Authentication & Security

### Password Management

All portals support password visibility toggle (eye icon) to help users see/hide passwords while typing.

#### Default Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Mentor | mentor@certrack.local | mentor123 |
| Placement | placement@certrack.local | placement123 |
| Admin | admin@certrack.local | admin123 |

### Responsive Design
- All login pages are fully responsive
- Mobile-optimized for phone and tablet devices
- Desktop view retains full functionality
- Touch-friendly interface elements

---

## 📞 Admin Support

### Setting Up Users

**For Mentors:**
1. Create user account in admin dashboard
2. Enable "Is Mentor" flag
3. Provide mentor login credentials
4. Assign students via admin interface

**For Placement Staff:**
1. Create user account in admin dashboard
2. Enable "Is Placement" flag
3. Provide placement login credentials
4. Grant access to analytics dashboard

---

## 🎯 Best Practices

### For Mentors
1. Review at-risk students weekly
2. Provide timely feedback on certifications
3. Guide students toward relevant skill gaps
4. Celebrate progress and milestones
5. Encourage consistent engagement

### For Placement Cell
1. Use readiness scores to prioritize students
2. Plan training programs based on skill gaps
3. Coordinate with mentors on student development
4. Track placement outcomes
5. Use certification trends for curriculum planning

---

## 📊 Integration with Main Platform

Both portals integrate seamlessly with:
- **Student Certification Tracking**: Real-time updates
- **Career Gap Analyzer**: Personalized insights
- **Event Management**: Participation tracking
- **Portfolio System**: Skill showcasing
- **Admin Dashboard**: User and role management

---

## 🚀 Future Enhancements

- Automated alert notifications
- Batch email communications
- Placement drive management
- Interview scheduling
- Outcome tracking and reporting
- Skill assessment quizzes
- Mentorship matching automation

