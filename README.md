# Amahle Rentals - Rental Booking System

A comprehensive Flask-based rental booking system for managing accommodation listings, bookings, and reviews.

## Features

### User Roles
- **Admin**: Full system management access
- **Landlord**: Can list and manage properties, handle booking requests
- **Student**: Can search and book accommodation (student-specific features)
- **General User**: Can search and book accommodation

### Key Functionality
- User registration and authentication
- Property listing and management
- Advanced search and filtering
- Booking system with approval workflow
- Review and rating system
- Admin dashboard for system management
- Landlord dashboard for property and booking management
- Responsive design with Bootstrap 5

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or navigate to the project directory**
   ```bash
   cd "C:\Users\Mthunzi\Amahle"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the database with sample data**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

## Sample Users

After running `init_db.py`, you can log in with these accounts:

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Access**: Full system administration

### Landlord Accounts
- **Username**: john_landlord | **Password**: password123
- **Username**: sarah_landlord | **Password**: password123
- **Access**: Property management, booking management

### Student Accounts
- **Username**: mary_student | **Password**: password123
- **Username**: david_student | **Password**: password123
- **Access**: Search and book properties

### General User Accounts
- **Username**: jane_user | **Password**: password123
- **Access**: Search and book properties

## Project Structure

```
Amahle/
├── app/
│   ├── __init__.py           # Flask app initialization
│   ├── models.py             # Database models
│   ├── forms.py              # WTForms form classes
│   ├── admin.py              # Flask-Admin configuration
│   ├── routes/
│   │   ├── auth.py           # Authentication routes
│   │   ├── main.py           # Main routes (properties, bookings)
│   │   └── landlord.py       # Landlord-specific routes
│   ├── templates/
│   │   ├── base.html         # Base template
│   │   ├── index.html        # Landing page
│   │   ├── auth/             # Authentication templates
│   │   ├── properties/       # Property templates
│   │   ├── bookings/         # Booking templates
│   │   ├── landlord/         # Landlord dashboard templates
│   │   └── reviews/          # Review templates
│   └── static/
│       ├── css/
│       │   └── style.css     # Custom styles
│       ├── js/
│       │   └── main.js       # Custom JavaScript
│       └── images/           # Image assets
├── config.py                 # Configuration settings
├── run.py                    # Application entry point
├── init_db.py                # Database initialization script
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

## Features in Detail

### For Landlords
- Add new properties with detailed information
- Edit and delete existing properties
- View and manage booking requests
- Approve or reject bookings
- Dashboard with statistics and analytics
- View property reviews

### For Tenants (Students & General Users)
- Browse available properties
- Advanced search with filters (city, price, bedrooms, etc.)
- View detailed property information
- Book properties
- Track booking status
- Write reviews for booked properties
- View booking history

### For Admins
- Full access to Flask-Admin dashboard
- Manage all users, properties, bookings, and reviews
- Monitor system activity
- Moderate content
- System-wide statistics

## Database Models

- **User**: Stores user information and authentication
- **Property**: Property listings with details and amenities
- **Booking**: Booking requests and approvals
- **Review**: Property reviews and ratings

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-Admin
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: SQLite (development), easily upgradeable to PostgreSQL/MySQL
- **Forms**: Flask-WTF, WTForms
- **Security**: Werkzeug password hashing

## Configuration

Edit the `.env` file to configure:
- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Environment (development/production)
- `FLASK_DEBUG`: Debug mode (True/False)

## Future Enhancements

- Image upload for properties
- Email notifications for bookings
- Payment integration
- Advanced analytics
- Property verification system
- Chat system between landlords and tenants
- Map integration for property locations
- Mobile app version

## Security Notes

1. Change the `SECRET_KEY` in production
2. Use a proper database (PostgreSQL/MySQL) in production
3. Enable HTTPS in production
4. Implement rate limiting
5. Add email verification for new users
6. Implement proper file upload validation if adding image uploads

## Troubleshooting

### Common Issues

1. **Database locked error**
   - Solution: Stop all running instances and delete `rental_booking.db`, then run `init_db.py` again

2. **Module not found errors**
   - Solution: Ensure virtual environment is activated and all dependencies are installed

3. **Port already in use**
   - Solution: Change the port in `run.py` or stop the process using port 5000

## Support

For issues or questions, please contact the development team.

## License

This project is for educational purposes.

---

**Note**: This is a development version. Additional security measures should be implemented before deploying to production.
