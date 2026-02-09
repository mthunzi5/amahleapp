# Quick Start Guide - Amahle Rentals

## Step-by-Step Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_db.py
```

This will create the database and populate it with sample data including:
- 1 Admin user
- 2 Landlords with 6 properties
- 2 Students
- 1 General user
- Sample bookings and reviews

### 3. Run the Application
```bash
python run.py
```

### 4. Access the Application
Open your browser and go to: **http://localhost:5000**

## Test Accounts

### Admin Dashboard
- Go to: http://localhost:5000/admin
- Username: `admin`
- Password: `admin123`

### Landlord Account
- Username: `john_landlord` or `sarah_landlord`
- Password: `password123`
- After login, you'll be redirected to the landlord dashboard

### Student/User Account
- Username: `mary_student` or `david_student` or `jane_user`
- Password: `password123`
- After login, you can browse and book properties

## What to Try

### As a Landlord:
1. Login with `john_landlord`
2. Go to Dashboard to see your properties and bookings
3. Click "Add Property" to list a new property
4. Approve or reject pending booking requests

### As a Student/User:
1. Login with `mary_student`
2. Browse properties on the home page
3. Use search filters to find properties
4. Click on a property to view details
5. Book a property
6. View your bookings in "My Bookings"

### As Admin:
1. Login with `admin`
2. Access admin panel at http://localhost:5000/admin
3. Manage all users, properties, bookings, and reviews
4. View system statistics

## Key Features to Explore

✓ User registration with role selection (Student, General, Landlord)
✓ Property browsing with filters (city, price, bedrooms)
✓ Detailed property pages with reviews and ratings
✓ Booking system with approval workflow
✓ Landlord dashboard with statistics
✓ Review and rating system
✓ Admin panel for system management
✓ Responsive design (mobile-friendly)

## Troubleshooting

**Problem**: Port 5000 already in use
**Solution**: Edit `run.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Problem**: Database errors
**Solution**: Delete `rental_booking.db` and run `python init_db.py` again

**Problem**: Module not found
**Solution**: Make sure you installed all dependencies with `pip install -r requirements.txt`

## Next Steps

- Customize the design in `app/static/css/style.css`
- Add real property images to `app/static/images/`
- Implement image upload functionality
- Add email notifications
- Deploy to a production server

Enjoy exploring Amahle Rentals! 🏡
