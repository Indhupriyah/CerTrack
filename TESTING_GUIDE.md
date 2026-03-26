# 🚀 Testing the Mentor & Placement Portals

## Quick Start

### 1. Access the Landing Page
Navigate to: `http://127.0.0.1:5002/`

You'll see four login options:
- 🎓 User Login
- 🔐 Admin Login
- 👩‍🏫 **Mentor Login** (NEW)
- 📋 **Placement Login** (NEW)

### 2. Mentor Portal Login
**URL**: `http://127.0.0.1:5002/auth/mentor-login`

**Credentials:**
- Email: `mentor@certrack.local`
- Password: `mentor123`

**Features to Test:**
- ✅ Password visibility toggle (eye icon)
- ✅ "Remember me" option
- ✅ Responsive mobile layout
- ✅ Student monitoring dashboard
- ✅ At-risk/inactive student alerts
- ✅ Performance metrics summary

### 3. Placement Portal Login
**URL**: `http://127.0.0.1:5002/auth/placement-login`

**Credentials:**
- Email: `placement@certrack.local`
- Password: `placement123`

**Features to Test:**
- ✅ Password visibility toggle (eye icon)
- ✅ "Remember me" option
- ✅ Responsive mobile layout
- ✅ Career readiness analytics
- ✅ Institutional skill distribution
- ✅ Certification trends
- ✅ Student filtering and search

### 4. Admin Portal Login
**URL**: `http://127.0.0.1:5002/auth/admin-login`

**Credentials:**
- Email: `admin@certrack.local` OR Username: `admin`
- Password: `admin123`

**Use Admin Panel to:**
- Assign students to mentors
- Enable/disable mentor and placement roles
- Create new user accounts
- Manage permissions

---

## 🔍 Key Features Implemented

### Password Visibility Toggle
All login pages now include an eye icon (👁️) to:
- Show/hide password while typing
- Works on mobile and desktop
- Smooth transition between visibility states

### Responsive Design
All pages optimized for:
- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 💻 Desktops (1024px+)
- Aut adjusts layout and font sizes

### New Login Pages
1. **Mentor Login** (`/auth/mentor-login`)
   - Faculty-specific entry point
   - Mentions student monitoring features
   - Clear description of portal purpose

2. **Placement Login** (`/auth/placement-login`)
   - Placement staff entry point
   - Mentions analytics features
   - Clear description of portal purpose

### Updated Existing Pages
1. **User Login** (`/auth/login`)
   - Added password toggle
   - Responsive improvements

2. **Admin Login** (`/auth/admin-login`)
   - Added password toggle
   - Quick access from menu

3. **Sign Up** (`/auth/signup`)
   - Added password toggle
   - Responsive improvements

4. **Landing Page** (`/`)
   - Direct links to mentor & placement portals
   - Updated navigation buttons

---

## 📊 Mentor Dashboard Features

### Student Monitoring
- View all assigned students
- See certification progress (completed/total)
- Track event participation
- Monitor productivity scores
- Check career readiness scores

### Student Status Tracking
- **On Track**: Students making steady progress
- **Inactive**: No activity for 14+ days
- **At Risk**: Approaching deadlines or low productivity

### Quick Actions
- Click "View Details" to see individual student progress
- Review performance metrics at a glance
- Identify students needing intervention

---

## 📈 Placement Dashboard Features

### Institutional Analytics
- Total student count
- Career readiness distribution
- Certification completion trends (12 months)
- Skill gap analysis

### Student Search
- Search by name or email
- Filter by readiness score
- Filter by certifications
- Filter by skill areas
- Find students for specific opportunities

### Data Visualization
- Certification trends chart
- Skill coverage breakdown
- Readiness distribution percentages
- Quick metrics cards

---

## 🛠️ Database Setup

The following test accounts are automatically available:
- Mentor account with `is_mentor=True` flag
- Placement account with `is_placement=True` flag
- Admin account with `is_admin=True` flag

To set up additional users:

```bash
# Run from project root
python scripts/setup_test_accounts.py
```

---

## 🎨 UI Improvements

### Styling Enhancements
- Added score badges (high/medium/low visual cues)
- Improved alert styling with icons
- Better spacing and typography
- Enhanced color usage for readability

### Interactive Elements
- Hover effects on buttons
- Active states for navigation
- Smooth transitions
- Loading states (where applicable)

---

## 📱 Mobile Testing

**Recommended Test Devices:**
- iPhone 12/13/14/15
- Samsung Galaxy S20/S21/S22
- iPad Air/Pro
- Generic 375px wide phone
- Generic 768px wide tablet

**Test Scenarios:**
1. Login with valid credentials
2. Toggle password visibility
3. Use "Remember me" option
4. Navigate sidebars on small screens
5. View tables on mobile (may need scrolling)
6. Test responsive layout changes

---

## ✅ Testing Checklist

- [ ] Mentor login page displays with password toggle
- [ ] Placement login page displays with password toggle
- [ ] Password visibility toggle works
- [ ] Landing page shows both new login buttons
- [ ] Mentor dashboard loads with student list
- [ ] Placement dashboard loads with analytics
- [ ] All pages are mobile responsive
- [ ] CSS styling is applied correctly
- [ ] Navigation between pages works
- [ ] Logout functionality works

---

## 🐛 Troubleshooting

### Cannot Find Password Toggle Button
- Make sure CSS file is loaded: Check browser DevTools
- Clear browser cache and refresh
- Try different browser (Chrome, Firefox, Safari)

### Login Not Working
- Verify email address is exact: `mentor@certrack.local`
- Verify password is exact: `mentor123` (case-sensitive)
- Check if account has correct role flag enabled

### Pages Not Loading
- Verify application is running on port 5002
- Check Flask console for errors
- Ensure database is initialized
- Try restarting the application

### Mobile Layout Issues
- Check viewport meta tag in base.html
- Verify CSS media queries are working
- Try different mobile browser
- Clear mobile browser cache

---

## 📞 Support

For issues or feature requests:
1. Check MENTOR_PLACEMENT_GUIDE.md for feature details
2. Review application logs in console
3. Test in different browsers
4. Check database connectivity

