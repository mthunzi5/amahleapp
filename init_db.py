"""
Initialize the database with sample data for testing
"""
from app import create_app, db
from app.models import User, Property, Booking, Review
from datetime import datetime, timedelta

def init_db():
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@amahle.com',
            full_name='System Administrator',
            phone='0123456789',
            role='admin',
            is_active=True,
            is_verified=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create landlords
        print("Creating landlord users...")
        landlord1 = User(
            username='john_landlord',
            email='john@amahle.com',
            full_name='John Smith',
            phone='0111234567',
            role='landlord',
            is_active=True,
            is_verified=True
        )
        landlord1.set_password('password123')
        db.session.add(landlord1)
        
        landlord2 = User(
            username='sarah_landlord',
            email='sarah@amahle.com',
            full_name='Sarah Johnson',
            phone='0112345678',
            role='landlord',
            is_active=True,
            is_verified=True
        )
        landlord2.set_password('password123')
        db.session.add(landlord2)
        
        # Create student users
        print("Creating student users...")
        student1 = User(
            username='mary_student',
            email='mary@student.com',
            full_name='Mary Williams',
            phone='0113456789',
            role='student',
            is_active=True,
            is_verified=True
        )
        student1.set_password('password123')
        db.session.add(student1)
        
        student2 = User(
            username='david_student',
            email='david@student.com',
            full_name='David Brown',
            phone='0114567890',
            role='student',
            is_active=True,
            is_verified=True
        )
        student2.set_password('password123')
        db.session.add(student2)
        
        # Create general users
        print("Creating general users...")
        general1 = User(
            username='jane_user',
            email='jane@email.com',
            full_name='Jane Davis',
            phone='0115678901',
            role='general',
            is_active=True,
            is_verified=True
        )
        general1.set_password('password123')
        db.session.add(general1)
        
        db.session.commit()
        
        # Create properties
        print("Creating sample properties...")
        
        property1 = Property(
            landlord_id=landlord1.id,
            title='Modern 2-Bedroom Apartment in Sandton',
            description='Beautiful modern apartment with stunning city views. Close to Sandton City and Gautrain station. Perfect for young professionals or students.',
            property_type='apartment',
            address='123 Rivonia Road',
            city='Johannesburg',
            province='Gauteng',
            postal_code='2196',
            bedrooms=2,
            bathrooms=2,
            total_rooms=5,
            available_rooms=5,
            price_per_month=8500.00,
            amenities='WiFi, Parking, 24/7 Security, Pool, Gym',
            is_available=True,
            is_featured=True
        )
        db.session.add(property1)
        
        property2 = Property(
            landlord_id=landlord1.id,
            title='Cozy Bachelor Pad in Rosebank',
            description='Affordable bachelor apartment near shopping centers and public transport. Ideal for students.',
            property_type='studio',
            address='45 Oxford Road',
            city='Johannesburg',
            province='Gauteng',
            postal_code='2196',
            bedrooms=1,
            bathrooms=1,
            total_rooms=3,
            available_rooms=2,
            price_per_month=4500.00,
            amenities='WiFi, Parking, Security',
            is_available=True,
            is_featured=True
        )
        db.session.add(property2)
        
        property3 = Property(
            landlord_id=landlord2.id,
            title='Spacious 3-Bedroom House in Pretoria',
            description='Family-friendly house with large garden in quiet neighborhood. Close to schools and shopping centers.',
            property_type='house',
            address='78 Church Street',
            city='Pretoria',
            province='Gauteng',
            postal_code='0002',
            bedrooms=3,
            bathrooms=2,
            total_rooms=7,
            available_rooms=7,
            price_per_month=12000.00,
            amenities='WiFi, Parking, Garden, Pet Friendly',
            is_available=True,
            is_featured=True
        )
        db.session.add(property3)
        
        property4 = Property(
            landlord_id=landlord2.id,
            title='Student Accommodation near WITS',
            description='Perfect for WITS students. Walking distance to campus. Shared kitchen and lounge area.',
            property_type='room',
            address='12 Yale Road, Braamfontein',
            city='Johannesburg',
            province='Gauteng',
            postal_code='2001',
            bedrooms=1,
            bathrooms=1,
            total_rooms=10,
            available_rooms=6,
            price_per_month=3200.00,
            amenities='WiFi, Study Area, Laundry, Security',
            is_available=True,
            is_featured=False
        )
        db.session.add(property4)
        
        property5 = Property(
            landlord_id=landlord1.id,
            title='Luxury Apartment in Cape Town',
            description='High-end apartment with ocean views. Modern finishes and top-class amenities.',
            property_type='apartment',
            address='55 Beach Road, Sea Point',
            city='Cape Town',
            province='Western Cape',
            postal_code='8005',
            bedrooms=2,
            bathrooms=2,
            total_rooms=4,
            available_rooms=3,
            price_per_month=15000.00,
            amenities='WiFi, Parking, Pool, Gym, Ocean View, 24/7 Security',
            is_available=True,
            is_featured=True
        )
        db.session.add(property5)
        
        property6 = Property(
            landlord_id=landlord2.id,
            title='Affordable Room in Durban',
            description='Budget-friendly accommodation near UKZN. Great for students on a budget.',
            property_type='room',
            address='34 King George Avenue',
            city='Durban',
            province='KwaZulu-Natal',
            postal_code='4001',
            bedrooms=1,
            bathrooms=1,
            total_rooms=8,
            available_rooms=8,
            price_per_month=2800.00,
            amenities='WiFi, Shared Kitchen, Security',
            is_available=True,
            is_featured=False
        )
        db.session.add(property6)
        
        db.session.commit()
        
        # Create some bookings
        print("Creating sample bookings...")
        
        booking1 = Booking(
            user_id=student1.id,
            property_id=property2.id,
            check_in_date=datetime.now().date() + timedelta(days=30),
            num_rooms=1,
            total_price=4500.00,
            status='approved',
            message='Looking forward to moving in!',
            response='Welcome! Looking forward to having you.'
        )
        db.session.add(booking1)
        
        booking2 = Booking(
            user_id=student2.id,
            property_id=property4.id,
            check_in_date=datetime.now().date() + timedelta(days=15),
            num_rooms=1,
            total_price=3200.00,
            status='pending',
            message='I am a WITS student looking for accommodation close to campus.'
        )
        db.session.add(booking2)
        
        booking3 = Booking(
            user_id=general1.id,
            property_id=property1.id,
            check_in_date=datetime.now().date() + timedelta(days=45),
            num_rooms=1,
            total_price=8500.00,
            status='pending',
            message='Interested in viewing the property. When can I schedule a visit?'
        )
        db.session.add(booking3)
        
        # Update available rooms for approved bookings
        property2.available_rooms -= 1
        
        db.session.commit()
        
        # Create some reviews
        print("Creating sample reviews...")
        
        review1 = Review(
            user_id=student1.id,
            property_id=property2.id,
            rating=5,
            title='Excellent Location!',
            comment='Great place, close to everything. The landlord is very responsive and helpful. Highly recommended!'
        )
        db.session.add(review1)
        
        review2 = Review(
            user_id=general1.id,
            property_id=property1.id,
            rating=4,
            title='Very Nice Apartment',
            comment='Beautiful apartment with great amenities. Only minor issue is parking can be tight during peak hours.'
        )
        db.session.add(review2)
        
        review3 = Review(
            user_id=student2.id,
            property_id=property4.id,
            rating=5,
            title='Perfect for Students',
            comment='Walking distance to WITS. Clean and secure. Study area is perfect for exam prep!'
        )
        db.session.add(review3)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print("\nSample Users Created:")
        print("-" * 50)
        print("Admin:")
        print("  Username: admin | Password: admin123")
        print("\nLandlords:")
        print("  Username: john_landlord | Password: password123")
        print("  Username: sarah_landlord | Password: password123")
        print("\nStudents:")
        print("  Username: mary_student | Password: password123")
        print("  Username: david_student | Password: password123")
        print("\nGeneral Users:")
        print("  Username: jane_user | Password: password123")
        print("="*50)
        print(f"\n{Property.query.count()} properties created")
        print(f"{Booking.query.count()} bookings created")
        print(f"{Review.query.count()} reviews created")
        print("\nYou can now run the application with: python run.py")
        print("="*50)

if __name__ == '__main__':
    init_db()
