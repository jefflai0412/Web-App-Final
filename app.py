import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, request, flash, redirect, url_for , jsonify
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


from openai import OpenAI 
# 設置 OpenAI API Key
client = OpenAI(
    api_key="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"
)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 25  # Use STARTTLS
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'ntuthotel@gmail.com'  # Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'jeffharvey'  
app.config['MAIL_DEFAULT_SENDER'] = 'ntuthotel@gmail.com'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    user_email = db.Column(db.String(120), nullable=False)  # Email field

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.cli.command('create-user')
def create_user():
    username = input('Enter username: ')
    password = input('Enter password: ')
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    print(f"User {username} created successfully!")


# Initialize the database and populate room data
@app.cli.command('init-db')
def init_db():
    db.create_all()
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'log_success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials, please try again.', 'log_error')
    return render_template('login.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access the admin page.', 'log_error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'log_success')
    return redirect(url_for('login'))



@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    query = Booking.query
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
                    booking.user_email = request.form.get(f"user_email_{booking_id}")
                    db.session.commit()
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
            # flash(f"Error updating booking: {str(e)}", 'error')
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
            user_name = request.form['user_name']
            user_email = request.form['user_email']
            room_type = request.form['room_type']
            if check_out <= check_in:
                flash('Check-out date must be later than check-in date', 'error')
                return redirect(url_for('book_room', room_type=room_type))
            new_booking = Booking(
                check_in=check_in,
                check_out=check_out,
                room_type=room_type,
                user_name=user_name,
                user_email=user_email
            )
            db.session.add(new_booking)
            db.session.commit()
            # send_confirmation_email(user_name, user_email, check_in, check_out, room_type)
            flash('Booking successful!', 'success')
            # return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'error')
    return render_template('booking.html', room_type=room_type, min_date=min_date)


@app.route('/chat',  methods=["GET", "POST"])
def chat():
    data = request.get_json()
    
    print("CALLED")
    def generate():
        '''
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful hotel assistant."},
                {"role": "user", "content": data["message"]}
            ]
        )
'''
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "這是一個平行時空，不過所有的資訊建立在現實中台北科大附近(附近以在華山文創、三創等地區走路可到的為附近(大安區中正區為例))，**唯一不同是台北科大現在是一間飯店，名為北科大飯店**，而現在你是一位很不錯的導引機器人，幫使用者回答問題。這裡最好的房間選像是DOUBLE ROOM，回味一下學生時期的點點滴滴吧(以及美好的睡眠體驗)"},
                {"role": "user", "content": data["message"]},
            ],
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
        #reply = response.choices[0].message.content
        #return jsonify({"reply": reply}), 200
                
    #return generate(), {"Content-Type": "text/plain"}
    reply = generate()
    return jsonify({"reply": reply}), 200

#我好像成功了!FK
if __name__ == '__main__':
    app.run(debug=True)





