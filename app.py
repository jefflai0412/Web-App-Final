from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

# Room Model
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    max_occupancy = db.Column(db.String(20), nullable=False)
    image_urls = db.Column(db.Text, nullable=False)  # Store as a comma-separated string
    features = db.Column(db.JSON, nullable=False)  # Store features as a JSON object

# Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)

# Initialize the database and populate room data
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
            "image_urls": "imgs/single_1.webp,imgs/single_2.webp,imgs/single_3.webp",
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
            "image_urls": "imgs/double_1.webp,imgs/double_2.webp,imgs/double_3.webp",
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
    ]

    for data in room_data:
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

# Routes
@app.route('/')
def index():
    rooms_data = Room.query.all()
    return render_template('index.html', rooms=rooms_data)

@app.route('/intro')
def intro():
    return render_template('intro.html')

@app.route('/nearby')
def nearby():
    return render_template('nearby.html')

@app.route('/rooms/<string:room_type>')
def room(room_type):
    room = Room.query.filter_by(type=room_type.lower()).first()
    if not room:
        return "Room not found", 404
    return render_template('room.html', room=room)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    query = Booking.query

    # Handle Editing Bookings
    if request.method == 'POST':
        for key in request.form.keys():
            if key.startswith("edit_booking_"):
                booking_id = int(key.split("_")[-1])
                booking = Booking.query.get(booking_id)
                if booking:
                    booking.user_name = request.form.get(f"user_name_{booking_id}")
                    booking.check_in = datetime.strptime(request.form.get(f"check_in_{booking_id}"), '%Y-%m-%d')
                    booking.check_out = datetime.strptime(request.form.get(f"check_out_{booking_id}"), '%Y-%m-%d')
                    booking.room_type = request.form.get(f"room_type_{booking_id}")
                    db.session.commit()
                    flash(f"Booking {booking_id} updated successfully!", "success")

        # Handle Filters
        booking_id = request.form.get('booking_id')
        user_name = request.form.get('user_name')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        sort_by = request.form.get('sort_by')

        if booking_id:
            query = query.filter_by(id=booking_id)
        if user_name:
            query = query.filter(Booking.user_name.ilike(f"%{user_name}%"))
        if date_from and date_to:
            query = query.filter(Booking.check_in.between(date_from, date_to))

        if sort_by:
            if sort_by == "check_in":
                query = query.order_by(Booking.check_in)
            elif sort_by == "check_out":
                query = query.order_by(Booking.check_out)
            elif sort_by == "user_name":
                query = query.order_by(Booking.user_name)
            else:
                query = query.order_by(Booking.id)

    # Fetch All Bookings if No Filters Applied
    results = query.all()
    return render_template('admin.html', results=results)



@app.route('/edit_booking/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if request.method == 'POST':
        try:
            booking.check_in = datetime.strptime(request.form['check_in'], '%Y-%m-%d')
            booking.check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d')
            booking.room_type = request.form['room_type']
            booking.user_name = request.form['user_name']
            db.session.commit()
            flash('Booking updated successfully!', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating booking: {str(e)}", 'error')
    return render_template('edit_booking.html', booking=booking)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    try:
        db.session.delete(booking)
        db.session.commit()
        # flash('Booking deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        # flash(f"Error deleting booking: {str(e)}", 'error')
    return redirect(url_for('admin'))

@app.route('/book_room', methods=['GET', 'POST'])
def book_room():
    room_type = request.args.get('room_type', None)
    min_date = date.today().strftime('%Y-%m-%d')
    if request.method == 'POST':
        try:
            check_in = datetime.strptime(request.form['check_in'], '%Y-%m-%d')
            check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d')
            if check_out <= check_in:
                flash('Check-out date must be later than check-in date', 'error')
                return redirect(url_for('book_room', room_type=room_type))
            new_booking = Booking(
                check_in=check_in,
                check_out=check_out,
                room_type=request.form['room_type'],
                user_name=request.form['user_name']
            )
            db.session.add(new_booking)
            db.session.commit()
            flash('Booking successful!', 'success')
            # return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'error')
            return redirect(url_for('book_room', room_type=room_type))
    return render_template('booking.html', room_type=room_type, min_date=min_date)


if __name__ == '__main__':
    app.run(debug=True)
