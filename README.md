# README.md

## Project: Hotel Booking and Management System

### Overview
This project is a comprehensive hotel booking and management system developed as part of an assignment. It features two main components:

1. **Booking Frontend**
   - A user-friendly interface for browsing and booking hotel rooms.
   - Display of room types, descriptions, pricing, and features.
   - A booking form with input validation to ensure proper data entry.
   - User authentication for secure access.

2. **Admin Dashboard**
   - A management interface for administrators to handle bookings.
   - Features include searching, filtering, modifying, and deleting bookings.
   - CLI commands for managing rooms and users.

---

### Features

#### 1. **Frontend**
- **Responsive Design:** The interface adapts to various screen sizes, ensuring usability on all devices.
- **Room Details:** Users can view detailed room descriptions, images, and features.
- **Booking Form:** An easy-to-use form for booking rooms, with validation for check-in and check-out dates.
- **Authentication:** Secure login system for admin access and session-based user authentication.

#### 2. **Backend**
- **Flask Application:**
  - Routes for booking, user authentication, and admin functionalities.
  - Integration with PostgreSQL for data storage and retrieval.
- **Database Models:**
  - `Room` model for storing room details.
  - `Booking` model for managing booking records.
  - `User` model for handling admin accounts.

#### 3. **Admin Dashboard**
- View all bookings with the ability to search and filter by various criteria.
- Edit and delete bookings directly from the dashboard.
- Add and update room data via CLI commands.

#### 4. Chatbot

Integrated chatbot to assist users with questions about room options, bookings, and nearby attractions.

Powered by OpenAI GPT-3.5 for natural and interactive conversations.

Provides personalized responses based on user queries.

#### 5. **Email Notifications (Planned)**
- Functionality for sending email confirmations for bookings (not yet implemented).

#### 6. **Deployment (Planned)**
- The project is ready for deployment on platforms like Heroku, AWS, or GCP.
- Configurable for deployment with environment variables for sensitive data.

---

### Technical Stack
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Backend:** Flask (Python)
- **Database:** PostgreSQL

---

### Setup Instructions

#### Prerequisites
- Python 3.8+
- PostgreSQL installed and configured

#### Steps
1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**
   - Update the `SQLALCHEMY_DATABASE_URI` in `app.config` to match your PostgreSQL setup.
   - Initialize the database:
     ```bash
     flask init-db
     ```

4. **Run the application**
   ```bash
   flask run
   ```
   Access the application at `http://127.0.0.1:5000/`.

5. **Create an admin user**
   ```bash
   flask create-user
   ```

---

### Usage

#### User Portal
- Access the homepage to browse available room options.
- View room details and initiate a booking.
- Fill in the booking form with required details.

#### Admin Dashboard
- Log in with admin credentials.
- Manage bookings by searching, editing, or deleting records.
- View and update room data as necessary.

---

### Database Schema

#### Tables
1. **Users**
   - `id`: Primary key
   - `username`: Unique username
   - `password`: Hashed password

2. **Rooms**
   - `id`: Primary key
   - `type`: Room type (e.g., single, double)
   - `name`: Room name
   - `price`: Price per night
   - `max_occupancy`: Maximum number of guests
   - `image_urls`: Image URLs (comma-separated)
   - `features`: JSON object of room features

3. **Bookings**
   - `id`: Primary key
   - `check_in`: Check-in date
   - `check_out`: Check-out date
   - `room_type`: Type of room booked
   - `user_name`: Name of the user
   - `user_email`: Email of the user

---

### Future Improvements
- Integration with a payment gateway for secure transactions.
- Automated email notifications for booking confirmations and reminders.
- Enhanced admin functionalities, such as room availability visualization.
- Multi-language support for international users.

---

### Contact
For any questions or feedback, please contact:
- **Email:** jefflai0412@gmail.com
- **Developer:** 賴致帆&周翰文

