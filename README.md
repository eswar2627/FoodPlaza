# FoodPlaza

**FoodPlaza** is a food delivery web application that connects customers with nearby restaurants for seamless food ordering, tracking, and delivery.

---

## Features

-  User-friendly food ordering system
-  Restaurant management dashboard
-  Dynamic menu and cart
-  Order history and past invoices
-  Real-time order tracking and status updates
-  Secure user authentication (login/signup)
-  Google Maps integration for location tracking
-  Multiple payment methods (Cash, Card, UPI, etc.)
-  Downloadable invoice after successful order
-  SQLite3-based backend for easy local setup

---

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Django)
- **Database:** SQLite3
- **APIs:** Google Maps API, Payment Gateway
- **Version Control:** Git & GitHub

---

## Project Structure

```bash
FoodPlaza/
│
├── static/             # CSS, JS, images
├── templates/          # HTML templates
├── db.sqlite3          # SQLite database
├── manage.py           # Django entry point
├── requirements.txt    # Project dependencies
├── README.md           # Project documentation
└── ...


Getting Started

Follow these steps to run the project locally:

1. Prerequisites

Python 3.x

pip (Python package installer)

Git (optional, for cloning)


Setup Instructions:

1. Clone the repository

git clone https://github.com/eswar2627/FoodPlaza.git
cd FoodPlaza


2. Create and activate a virtual environment (recommended)

# On Windows
python -m venv env
env\Scripts\activate

# On macOS/Linux
python3 -m venv env
source env/bin/activate

3. Install required packages

pip install -r requirements.txt


4. Apply database migrations

python manage.py migrate


5.Run the development server

python manage.py runserver


6.Create Superuser for Admin Panel

python manage.py createsuperuser
