from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import date


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)


single = {
        "type": "single",
        "name": "Single Room",
        "price": "$100",
        "max_occupancy": "1 guests",
        "image_url": ["imgs/single_1.webp", "imgs/single_2.webp", "imgs/single_3.webp", "imgs/lobby_1.webp", "imgs/gym_1.webp", "imgs/parking_1.webp", "imgs/pool.webp"],
        "features": {
            "Bathroom": True,
            "Bathtub": False,
            "Hardwood Floors": True,
            "TV": True,
            "Wi-Fi": False,
            "Mini-fridge": True,
            "Balcony": False
        }
    }
double = {
        "type": "double",
        "name": "Double Room",
        "price": "$200",
        "max_occupancy": "2 guests",
        "image_url": ["imgs/double_1.webp", "imgs/double_2.webp", "imgs/double_3.webp", "imgs/lobby_1.webp", "imgs/gym_1.webp", "imgs/parking_1.webp", "imgs/pool.webp"],
        "features": {
            "Bathroom": True,
            "Bathtub": True,
            "Hardwood Floors": True,
            "TV": True,
            "Wi-Fi": False,
            "Mini-fridge": True,
            "Balcony": False
        }
    }
family = {
        "type": "family",
        "name": "Family Room",
        "price": "$100",
        "max_occupancy": "4 guests",
        "image_url": ["imgs/family_1.webp", "imgs/family_2.webp", "imgs/family_3.webp", "imgs/lobby_1.webp", "imgs/gym_1.webp", "imgs/parking_1.webp", "imgs/pool.webp"],
        "features": {
            "Bathroom": True,
            "Bathtub": True,
            "Hardwood Floors": True,
            "TV": True,
            "Wi-Fi": False,
            "Mini-fridge": True,
            "Balcony": False
        }
    }
deluxe = {
    "type": "deluxe",
    "name": "Deluxe Suite",
    "price": "$200",
    "max_occupancy": "4 guests",
    "image_url": ["imgs/deluxe_1.webp", "imgs/deluxe_2.webp", "imgs/deluxe_3.webp", "imgs/deluxe_4.webp", "imgs/lobby_1.webp", "imgs/gym_1.webp", "imgs/parking_1.webp", "imgs/pool.webp"],
    "features": {
        "Bathroom": True,
        "Bathtub": True,
        "Hardwood Floors": True,
        "TV": True,
        "Wi-Fi": True,
        "Mini-fridge": False,
        "Balcony": True
    }
}

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    max_occupancy = db.Column(db.String(20), nullable=False)
    image_urls = db.Column(db.Text, nullable=False)  # Store as a comma-separated string
    features = db.Column(db.JSON, nullable=False)  # Store features as a JSON object


# Database Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)

# Initialize the database
@app.cli.command('init-db')
def init_db():
    """Initialize the database and populate it with initial data."""
    db.create_all()

    # Add predefined room data
    room_data = [
        {
            "type": "single",
            "name": "Single Room",
            "price": "$100",
            "max_occupancy": "1 guests",
            "image_urls": "imgs/single_1.webp,imgs/single_2.webp,imgs/single_3.webp,imgs/lobby_1.webp,imgs/gym_1.webp,imgs/parking_1.webp,imgs/pool.webp",
            "features": {
                "Bathroom": True,
                "Bathtub": False,
                "Hardwood Floors": True,
                "TV": True,
                "Wi-Fi": False,
                "Mini-fridge": True,
                "Balcony": False
            }
        },
        {
            "type": "double",
            "name": "Double Room",
            "price": "$200",
            "max_occupancy": "2 guests",
            "image_urls": "imgs/double_1.webp,imgs/double_2.webp,imgs/double_3.webp,imgs/lobby_1.webp,imgs/gym_1.webp,imgs/parking_1.webp,imgs/pool.webp",
            "features": {
                "Bathroom": True,
                "Bathtub": True,
                "Hardwood Floors": True,
                "TV": True,
                "Wi-Fi": False,
                "Mini-fridge": True,
                "Balcony": False
            }
        },
        {
            "type": "family",
            "name": "Family Room",
            "price": "$150",
            "max_occupancy": "4 guests",
            "image_urls": "imgs/family_1.webp,imgs/family_2.webp,imgs/family_3.webp,imgs/lobby_1.webp,imgs/gym_1.webp,imgs/parking_1.webp,imgs/pool.webp",
            "features": {
                "Bathroom": True,
                "Bathtub": True,
                "Hardwood Floors": True,
                "TV": True,
                "Wi-Fi": False,
                "Mini-fridge": True,
                "Balcony": False
            }
        },
        {
            "type": "deluxe",
            "name": "Deluxe Suite",
            "price": "$250",
            "max_occupancy": "4 guests",
            "image_urls": "imgs/deluxe_1.webp,imgs/deluxe_2.webp,imgs/deluxe_3.webp,imgs/deluxe_4.webp,imgs/lobby_1.webp,imgs/gym_1.webp,imgs/parking_1.webp,imgs/pool.webp",
            "features": {
                "Bathroom": True,
                "Bathtub": True,
                "Hardwood Floors": True,
                "TV": True,
                "Wi-Fi": True,
                "Mini-fridge": False,
                "Balcony": True
            }
        }
    ]

    for data in room_data:
        # Check if the room type already exists to avoid duplicate entries
        if not Room.query.filter_by(type=data['type']).first():
            room = Room(
                type=data['type'],
                name=data['name'],
                price=data['price'],
                max_occupancy=data['max_occupancy'],
                image_urls=data['image_urls'],
                features=data['features']
            )
            db.session.add(room)

    db.session.commit()
    print("Database initialized and room data added!")


@app.route('/')
def index():
    rooms_data = Room.query.all()
    return render_template('index.html', rooms=rooms_data)


@app.route('/rooms/<string:room_type>')
def room(room_type):
    room = Room.query.filter_by(type=room_type.lower()).first()
    if not room:
        return "Room not found", 404
    return render_template('room.html', room=room)



@app.route('/search_booking', methods=['POST'])
def search_booking():
    booking_id = request.form.get('booking_id')
    if booking_id.isdigit():
        booking = Booking.query.filter_by(id=booking_id).first()
        if booking:
            flash('Booking found', 'success')
            return render_template('index.html', bookings=[booking])
        else:
            flash('Booking not found', 'error')
    else:
        flash('Please enter a valid numeric Booking ID', 'error')
    return redirect(url_for('index'))



# Add a new booking
@app.route('/book_room', methods=['GET', 'POST'])
def book_room():
    room_type = request.args.get('room_type', None)  # Default to None if not provided
    min_date = date.today().strftime('%Y-%m-%d')  # Set the minimum date to today
    if request.method == 'POST':
        try:
            check_in = datetime.strptime(request.form['check_in'], '%Y-%m-%d')
            check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d')
            if check_out <= check_in:
                flash('Check-out date must be later than check-in date', 'error')
                return redirect(url_for('book'))
            new_booking = Booking(
                check_in=check_in,
                check_out=check_out,
                room_type=request.form['room_type'],
                user_name=request.form['user_name']
            )
            db.session.add(new_booking)
            db.session.commit()
            flash('Booking successful!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'error')
    return render_template('booking.html', room_type=room_type, min_date=min_date)

# Delete a booking
@app.route('/delete/<int:id>', methods=['POST'])
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    try:
        db.session.delete(booking)
        db.session.commit()
        flash('Booking deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting booking: {str(e)}", 'error')
    return redirect(url_for('index'))



@app.route('/admin', methods=['GET', 'POST'])
def admin():
    results = []
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        user_name = request.form.get('user_name')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')

        query = Booking.query
        if booking_id:
            query = query.filter_by(id=booking_id)
        if user_name:
            query = query.filter(Booking.user_name.ilike(f"%{user_name}%"))
        if date_from and date_to:
            query = query.filter(Booking.check_in.between(date_from, date_to))

        results = query.all()

    return render_template('admin.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
