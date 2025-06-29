from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ridewave.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Add context processor for current date
@app.context_processor
def inject_now():
    return {'now': datetime.now}

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Bike Model
class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    speed = db.Column(db.String(50), nullable=False)
    bookings = db.relationship('Booking', backref='bike', lazy=True)

# Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bike_id = db.Column(db.Integer, db.ForeignKey('bike.id'), nullable=False)
    pickup_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='upcoming')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_bikes():
    bikes = [
        # Adventure Bikes
        {
            'name': 'BMW',
            'model': 'R 1250 GS',
            'category': 'adventure',
            'price': 3500,  # ₹3,500 per day
            'description': 'The ultimate adventure machine with advanced technology and comfort features.',
            'image': 'bmw-gs.jpg',
            'speed': '220 km/h'
        },
        {
            'name': 'KTM',
            'model': '1290 Super Adventure',
            'category': 'adventure',
            'price': 3200,  # ₹3,200 per day
            'description': 'Powerful adventure tourer with cutting-edge technology and off-road capabilities.',
            'image': 'ktm-super-adventure.jpg',
            'speed': '230 km/h'
        },
        {
            'name': 'Ducati',
            'model': 'Multistrada V4',
            'category': 'adventure',
            'price': 3800,  # ₹3,800 per day
            'description': 'Italian engineering meets adventure touring with superb performance.',
            'image': 'ducati-multistrada.jpg',
            'speed': '240 km/h'
        },
        {
            'name': 'Honda',
            'model': 'Africa Twin',
            'category': 'adventure',
            'price': 3000,  # ₹3,000 per day
            'description': 'Reliable adventure companion with excellent off-road capabilities.',
            'image': 'honda-africa.jpg',
            'speed': '210 km/h'
        },

        # Sport Bikes
        {
            'name': 'Yamaha',
            'model': 'YZF-R1',
            'category': 'sport',
            'price': 4000,  # ₹4,000 per day
            'description': 'Track-focused superbike with race-derived technology.',
            'image': 'yamaha-r1.jpg',
            'speed': '300 km/h'
        },
        {
            'name': 'Kawasaki',
            'model': 'Ninja ZX-10R',
            'category': 'sport',
            'price': 4200,  # ₹4,200 per day
            'description': 'World Superbike championship-winning machine with extreme performance.',
            'image': 'kawasaki-ninja.jpg',
            'speed': '299 km/h'
        },
        {
            'name': 'Aprilia',
            'model': 'RSV4',
            'category': 'sport',
            'price': 4500,  # ₹4,500 per day
            'description': 'Italian superbike with championship-winning pedigree and V4 engine.',
            'image': 'aprilia-rsv4.jpg',
            'speed': '285 km/h'
        },
        {
            'name': 'Suzuki',
            'model': 'GSX-R1000',
            'category': 'sport',
            'price': 3800,  # ₹3,800 per day
            'description': 'Legendary sportbike with proven performance and reliability.',
            'image': 'suzuki-gsxr.jpg',
            'speed': '290 km/h'
        },

        # Naked Bikes
        {
            'name': 'Yamaha',
            'model': 'MT-09',
            'category': 'naked',
            'price': 2800,  # ₹2,800 per day
            'description': 'Torque-rich naked bike with aggressive styling and excellent handling.',
            'image': 'yamaha-mt09.jpg',
            'speed': '225 km/h'
        },
        {
            'name': 'KTM',
            'model': 'Duke 790',
            'category': 'naked',
            'price': 3000,  # ₹3,000 per day
            'description': 'Lightweight and powerful naked bike with premium components.',
            'image': 'ktm-duke.jpg',
            'speed': '220 km/h'
        },
        {
            'name': 'Triumph',
            'model': 'Street Triple',
            'category': 'naked',
            'price': 3200,  # ₹3,200 per day
            'description': 'British triple-cylinder naked with superb handling and character.',
            'image': 'triumph-street-triple.jpg',
            'speed': '230 km/h'
        },
        {
            'name': 'Ducati',
            'model': 'Monster',
            'category': 'naked',
            'price': 3500,  # ₹3,500 per day
            'description': 'Iconic Italian naked bike with premium build quality and performance.',
            'image': 'ducati-monster.jpg',
            'speed': '240 km/h'
        },

        # Cruiser Bikes
        {
            'name': 'Harley-Davidson',
            'model': 'Sportster',
            'category': 'cruiser',
            'price': 2500,  # ₹2,500 per day
            'description': 'Classic American cruiser with iconic styling and V-twin character.',
            'image': 'harley-sportster.jpg',
            'speed': '180 km/h'
        },
        {
            'name': 'Indian',
            'model': 'Scout',
            'category': 'cruiser',
            'price': 2800,  # ₹2,800 per day
            'description': 'Modern American cruiser with premium features and comfort.',
            'image': 'indian-scout.jpg',
            'speed': '190 km/h'
        },
        {
            'name': 'Honda',
            'model': 'Rebel 1100',
            'category': 'cruiser',
            'price': 2200,  # ₹2,200 per day
            'description': 'Modern cruiser with Honda reliability and advanced features.',
            'image': 'honda-rebel.jpg',
            'speed': '200 km/h'
        },
        {
            'name': 'Triumph',
            'model': 'Bonneville',
            'category': 'cruiser',
            'price': 3000,  # ₹3,000 per day
            'description': 'Classic British cruiser with modern technology and timeless style.',
            'image': 'triumph-bonneville.jpg',
            'speed': '210 km/h'
        }
    ]

    for bike_data in bikes:
        bike = Bike(**bike_data)
        db.session.add(bike)
    
    db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('explore'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/explore')
def explore():
    # Group bikes by category
    adventure_bikes = Bike.query.filter_by(category='adventure').all()
    sport_bikes = Bike.query.filter_by(category='sport').all()
    naked_bikes = Bike.query.filter_by(category='naked').all()
    cruiser_bikes = Bike.query.filter_by(category='cruiser').all()
    
    return render_template('explore.html', 
                         adventure_bikes=adventure_bikes,
                         sport_bikes=sport_bikes,
                         naked_bikes=naked_bikes,
                         cruiser_bikes=cruiser_bikes,
                         now=datetime.now)

@app.route('/bookings')
@login_required
def bookings():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.pickup_date.desc()).all()
    return render_template('bookings.html', bookings=user_bookings)

@app.route('/booking/<int:booking_id>')
@login_required
def booking_details(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('You are not authorized to view this booking', 'error')
        return redirect(url_for('bookings'))
    return render_template('booking_details.html', booking=booking)

@app.route('/cancel/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('You are not authorized to cancel this booking', 'error')
        return redirect(url_for('bookings'))
    
    if booking.status != 'upcoming':
        flash('Only upcoming bookings can be cancelled', 'error')
        return redirect(url_for('bookings'))
    
    booking.status = 'cancelled'
    db.session.commit()
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('bookings'))

@app.route('/confirmation', methods=['GET', 'POST'])
@login_required
def confirmation():
    if request.method == 'POST':
        try:
            # Get form data
            bike_id = request.form.get('bike_id')
            pickup_date_str = request.form.get('pickup_date')
            return_date_str = request.form.get('return_date')
            total_cost = request.form.get('total_cost')
            
            # Debug logging
            print(f"Form data received: bike_id={bike_id}, pickup_date={pickup_date_str}, return_date={return_date_str}, total_cost={total_cost}")
            
            # Validate required fields
            if not all([bike_id, pickup_date_str, return_date_str, total_cost]):
                flash('Missing required fields. Please select dates and try again.', 'error')
                return redirect(url_for('explore'))
            
            # Parse dates
            try:
                pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d')
                return_date = datetime.strptime(return_date_str, '%Y-%m-%d')
            except ValueError as e:
                flash('Invalid date format. Please try again.', 'error')
                return redirect(url_for('explore'))
            
            # Validate dates
            if pickup_date < datetime.now():
                flash('Pickup date cannot be in the past', 'error')
                return redirect(url_for('explore'))
            
            if return_date <= pickup_date:
                flash('Return date must be after pickup date', 'error')
                return redirect(url_for('explore'))
            
            # Get bike
            bike = Bike.query.get_or_404(bike_id)
            
            # Create new booking
            booking = Booking(
                user_id=current_user.id,
                bike_id=bike_id,
                pickup_date=pickup_date,
                return_date=return_date,
                total_cost=float(total_cost),
                status='upcoming'
            )
            
            db.session.add(booking)
            db.session.commit()
            
            # Store booking details in session for confirmation page
            session['booking_details'] = {
                'bike_id': bike.id,
                'bike_name': bike.name,
                'bike_model': bike.model,
                'pickup_date': pickup_date.strftime('%B %d, %Y'),
                'return_date': return_date.strftime('%B %d, %Y'),
                'duration': (return_date - pickup_date).days,
                'total_cost': total_cost
            }
            
            print("Booking created successfully, redirecting to confirmation_success")
            return redirect(url_for('confirmation_success'))
        
        except Exception as e:
            print(f"Error in confirmation route: {str(e)}")
            flash('Error processing your booking. Please try again.', 'error')
            return redirect(url_for('explore'))
    
    return redirect(url_for('explore'))

@app.route('/confirmation/success')
@login_required
def confirmation_success():
    booking_details = session.get('booking_details')
    if not booking_details:
        flash('No booking details found. Please make a booking first.', 'error')
        return redirect(url_for('explore'))
    
    # Get the bike object to include image
    bike = Bike.query.get(booking_details['bike_id'])
    
    return render_template('confirmation.html', 
                         bike={'id': bike.id,
                              'name': bike.name,
                              'model': bike.model,
                              'image': bike.image},
                         duration=booking_details['duration'],
                         total_cost=booking_details['total_cost'],
                         pickup_date=booking_details['pickup_date'],
                         return_date=booking_details['return_date'])

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Admin required decorator with additional security
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
            
        # Check if user is admin and has the specific admin credentials
        if not current_user.is_admin or current_user.email != 'ridewave@info.com':
            flash('You do not have permission to access this page', 'error')
            return redirect(url_for('home'))
            
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter_by(status='upcoming').count()
    total_revenue = db.session.query(db.func.sum(Booking.total_cost)).scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_bookings=total_bookings,
                         active_bookings=active_bookings,
                         total_revenue=total_revenue)

@app.route('/admin/bookings')
@login_required
@admin_required
def admin_bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/booking/<int:booking_id>/update', methods=['POST'])
@login_required
@admin_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    
    if new_status in ['upcoming', 'completed', 'cancelled']:
        booking.status = new_status
        db.session.commit()
        flash('Booking status updated successfully', 'success')
    else:
        flash('Invalid status', 'error')
    
    return redirect(url_for('admin_bookings'))

# Create admin user function
def create_admin_user():
    # Only create admin if no admin exists
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            username='bharath',  # Updated admin username
            email='ridewave@info.com',  # Your email
            is_admin=True
        )
        admin.set_password('Annadi@123')  # Updated password
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully')
    return admin

# Add admin link to navbar only for admin user
@app.context_processor
def inject_admin_link():
    def get_admin_link():
        if current_user.is_authenticated and current_user.is_admin and current_user.email == 'ridewave@info.com':
            return '<a href="{}" class="admin-link">Admin Panel</a>'.format(url_for('admin_dashboard'))
        return ''
    return dict(admin_link=get_admin_link())

@app.route('/view-users')
@login_required
@admin_required
def view_users():
    users = User.query.all()
    user_data = []
    
    for user in users:
        # Get user's total bookings and total spent
        total_bookings = Booking.query.filter_by(user_id=user.id).count()
        total_spent = db.session.query(db.func.sum(Booking.total_cost)).filter_by(user_id=user.id).scalar() or 0
        
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'total_bookings': total_bookings,
            'total_spent': total_spent
        })
    
    return render_template('admin/users.html', users=user_data)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Drop existing tables
        db.create_all()  # Create new tables with updated schema
        create_bikes()
        create_admin_user()  # Create admin user
    app.run(debug=True) 