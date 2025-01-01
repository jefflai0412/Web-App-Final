from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import date


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

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
    """Initialize the database."""
    db.create_all()
    print("Database initialized!")

@app.route('/')
def index():
    # bookings = Booking.query.all()
    return render_template('index.html', bookings=None)

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
@app.route('/book', methods=['GET', 'POST'])
def book():
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
    return render_template('booking.html', min_date=min_date)

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
