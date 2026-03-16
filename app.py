from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash
import os
from dotenv import load_dotenv
from groq import Groq
import json
import re
from utils.pdf_generator import generate_itinerary_pdf
import tempfile
from utils.weather import get_weather, get_weather_icon
import logging
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, SavedTrip
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please sign in to access this page.'
login_manager.login_message_category = 'info'

logging.basicConfig(level=logging.DEBUG)

# Initialize Groq client
# Initialize Groq client with error handling
try:
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    print("✅ Groq client initialized successfully")
except TypeError as e:
    print(f"⚠️ Groq client initialization error: {e}")
    print("⚠️ Using fallback mode (no Groq API)")
    groq_client = None
except Exception as e:
    print(f"⚠️ Unexpected error initializing Groq: {e}")
    groq_client = None

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def clean_json_response(text):
    """Extract JSON from Groq response"""
    # Remove markdown code blocks
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0]
    elif '```' in text:
        text = text.split('```')[1].split('```')[0]
    
    # Find JSON object
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    
    return text.strip()

def get_current_month():
    """Get current month name"""
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    return months[datetime.now().month - 1]

def generate_itinerary_with_groq(destination, days, budget, trip_type):
    """Generate itinerary using Groq API with month information and packing list"""
    
    current_month = get_current_month().capitalize()
    
    prompt = f"""Create a detailed {days}-day travel itinerary for {destination}, India.

Trip Details:
- Budget: {budget} (budget/medium/luxury)
- Travelers: {trip_type} (family/school/couple/solo)
- Duration: {days} days

IMPORTANT: Generate events for DIFFERENT MONTHS throughout the year. Don't put all events in the same month.
Current month is {current_month}, but please include events from:
- January (winter festivals)
- March (Holi festival)
- August (Independence day, Onam in Kerala)
- October (Diwali, Dussehra)
- December (Christmas, New Year)

Return ONLY a valid JSON object with this exact structure:
{{
    "itinerary": [
        {{
            "day": 1,
            "morning": "specific morning activity in {destination}",
            "afternoon": "specific afternoon activity in {destination}",
            "evening": "specific evening activity in {destination}",
            "food_suggestion": "specific local dish to try",
            "accommodation_tip": "where to stay tip"
        }}
    ],
    "tips": ["travel tip 1", "travel tip 2", "travel tip 3"],
    "local_events": [
        {{
            "event": "festival or event name in {destination}",
            "location": "venue or area",
            "dates": "specific dates (e.g., March 25-27)",
            "type": "festival/cultural/religious/sports",
            "month": "month name in lowercase (e.g., march, april)"
        }}
    ],
    "hidden_gems": [
        {{
            "name": "offbeat place name in {destination}",
            "description": "brief description why it's special",
            "best_time": "best time to visit",
            "location": "specific area in {destination}"
        }}
    ],
    "packing_list": {{
        "essentials": ["essential items like passport, tickets, etc."],
        "clothing": ["clothing items based on weather and duration"],
        "weather_specific": ["items specific to {destination}'s weather"],
        "activities": ["items needed for planned activities"],
        "toiletries": ["toiletry items"],
        "medications": ["medications and first aid"],
        "electronics": ["electronic gadgets and chargers"],
        "miscellaneous": ["other useful items"]
    }}
}}

Make sure:
- Activities are REAL places in {destination}
- Food suggestions are AUTHENTIC local dishes
- Create EXACTLY {days} days of itinerary
- Include at least 5-6 local events spread across DIFFERENT MONTHS (Jan, Mar, Aug, Oct, Dec etc.)
- Events should be real festivals for {destination}
- Packing list should be tailored to {destination}'s weather and {days}-day duration
- No explanations, ONLY the JSON object"""

    try:
        # Call Groq API
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=5000
        )
        
        # Get response text
        result_text = response.choices[0].message.content
        
        # Clean and parse JSON
        cleaned_text = clean_json_response(result_text)
        result = json.loads(cleaned_text)
        
        # Ensure events have month field
        if 'local_events' in result:
            for event in result['local_events']:
                if 'month' not in event:
                    if 'dates' in event:
                        date_lower = event['dates'].lower()
                        months = ['january', 'february', 'march', 'april', 'may', 'june',
                                 'july', 'august', 'september', 'october', 'november', 'december']
                        for month in months:
                            if month in date_lower:
                                event['month'] = month
                                break
                        else:
                            event['month'] = get_current_month()
                    else:
                        event['month'] = get_current_month()
        
        # Ensure packing list exists
        if 'packing_list' not in result:
            result['packing_list'] = generate_fallback_packing_list(destination, days)
        
        return result
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        return None

def generate_fallback_packing_list(destination, days):
    """Generate fallback packing list"""
    return {
        "essentials": [
            f"Passport/ID proof",
            f"Travel insurance documents",
            f"Flight/train tickets",
            f"Hotel booking confirmations",
            f"Cash and credit/debit cards",
            f"Phone and charger",
            f"Power bank"
        ],
        "clothing": [
            f"{days} pairs of underwear",
            f"{days} pairs of socks",
            "3-4 t-shirts",
            "2 pairs of jeans/pants",
            "1 pair of comfortable walking shoes",
            "Sleepwear",
            "Light jacket/sweater"
        ],
        "weather_specific": [
            "Sunscreen (SPF 30+)",
            "Sunglasses",
            "Hat/cap",
            "Umbrella (just in case)"
        ],
        "activities": [
            "Camera",
            "Comfortable backpack",
            "Water bottle",
            "Snacks for the day"
        ],
        "toiletries": [
            "Toothbrush and toothpaste",
            "Shampoo and conditioner",
            "Soap/body wash",
            "Deodorant",
            "Face wash",
            "Hair brush/comb"
        ],
        "medications": [
            "Basic first aid kit",
            "Personal medications",
            "Pain relievers",
            "Motion sickness pills",
            "Band-aids"
        ],
        "electronics": [
            "Phone charger",
            "Power bank",
            "Camera and charger",
            "Universal travel adapter",
            "Headphones"
        ],
        "miscellaneous": [
            "Reusable water bottle",
            "Travel pillow",
            "Eye mask",
            "Ear plugs",
            "Wet wipes/tissues",
            "Hand sanitizer"
        ]
    }

def get_fallback_itinerary(destination, days, budget, trip_type):
    """Fallback mock data if Groq fails - with events across multiple months"""
    current_month = get_current_month()
    
    # Default events based on destination
    if destination.lower() == 'kerala':
        events = [
            {
                "event": "Onam Festival",
                "location": "Entire Kerala",
                "dates": "August-September",
                "type": "cultural",
                "month": "august"
            },
            {
                "event": "Nehru Trophy Boat Race",
                "location": "Alleppey",
                "dates": "August 15",
                "type": "sports",
                "month": "august"
            },
            {
                "event": "Christmas Celebrations",
                "location": "Kochi",
                "dates": "December 25",
                "type": "religious",
                "month": "december"
            },
            {
                "event": "New Year Eve Party",
                "location": "Kovalam Beach",
                "dates": "December 31",
                "type": "festival",
                "month": "december"
            },
            {
                "event": "Vishu",
                "location": "State-wide",
                "dates": "April 14",
                "type": "cultural",
                "month": "april"
            },
            {
                "event": "Thrissur Pooram",
                "location": "Thrissur",
                "dates": "April-May",
                "type": "religious",
                "month": "april"
            }
        ]
    elif destination.lower() == 'delhi':
        events = [
            {
                "event": "Republic Day Parade",
                "location": "Rajpath, Delhi",
                "dates": "January 26",
                "type": "national",
                "month": "january"
            },
            {
                "event": "Holi Festival",
                "location": "Delhi",
                "dates": "March 25",
                "type": "festival",
                "month": "march"
            },
            {
                "event": "Independence Day",
                "location": "Red Fort, Delhi",
                "dates": "August 15",
                "type": "national",
                "month": "august"
            },
            {
                "event": "Diwali Celebrations",
                "location": "Delhi",
                "dates": "October-November",
                "type": "festival",
                "month": "october"
            },
            {
                "event": "Qutub Festival",
                "location": "Qutub Minar",
                "dates": "November-December",
                "type": "cultural",
                "month": "november"
            },
            {
                "event": "Christmas Market",
                "location": "Connaught Place",
                "dates": "December 24-25",
                "type": "festival",
                "month": "december"
            }
        ]
    else:
        events = [
            {
                "event": f"New Year Celebration in {destination}",
                "location": f"Main Square, {destination}",
                "dates": "January 1",
                "type": "festival",
                "month": "january"
            },
            {
                "event": f"Holi Festival in {destination}",
                "location": destination,
                "dates": "March 25",
                "type": "festival",
                "month": "march"
            },
            {
                "event": f"Independence Day Celebration",
                "location": destination,
                "dates": "August 15",
                "type": "national",
                "month": "august"
            },
            {
                "event": f"Diwali Festival",
                "location": destination,
                "dates": "October-November",
                "type": "festival",
                "month": "october"
            },
            {
                "event": f"Christmas Celebration",
                "location": destination,
                "dates": "December 25",
                "type": "religious",
                "month": "december"
            }
        ]
    
    return {
        "itinerary": [
            {
                "day": i+1,
                "morning": f"Explore local market in {destination}",
                "afternoon": f"Visit famous temple in {destination}",
                "evening": f"Try local street food in {destination}",
                "food_suggestion": f"Local {destination} thali",
                "accommodation_tip": "Book hotels in advance"
            } for i in range(days)
        ],
        "tips": [
            f"Best time to visit {destination} is Oct-Mar",
            "Carry local currency",
            "Learn a few local phrases",
            "Try street food but ensure it's hygienic",
            "Book accommodations in advance during peak season"
        ],
        "local_events": events,
        "hidden_gems": [
            {
                "name": f"Hidden spot near {destination}",
                "description": "Less crowded, beautiful place with amazing views",
                "best_time": "Early morning",
                "location": f"Near {destination}"
            },
            {
                "name": f"Local village experience",
                "description": "Experience authentic local culture and traditions",
                "best_time": "Afternoon",
                "location": f"Outskirts of {destination}"
            }
        ],
        "packing_list": generate_fallback_packing_list(destination, days)
    }

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle search and generate itinerary"""
    # Get form data
    destination = request.form.get('destination', '').strip()
    days = int(request.form.get('days', 3))
    budget = request.form.get('budget', 'medium')
    trip_type = request.form.get('trip_type', 'family')
    
    print(f"\n🔍 Planning trip to {destination} for {days} days")
    
    # Try Groq API first
    itinerary_data = generate_itinerary_with_groq(destination, days, budget, trip_type)
    
    # If Groq fails, use fallback
    if not itinerary_data:
        print("⚠️ Groq failed, using fallback data")
        itinerary_data = get_fallback_itinerary(destination, days, budget, trip_type)
    
    # Get weather data
    weather_api_key = os.getenv('WEATHER_API_KEY', '666093f96e49489f1c009d4e2ef4bf9d')
    weather_data = get_weather(destination, weather_api_key)
    weather_icon = get_weather_icon(weather_data.get('description') if weather_data else '')
    
    # Get current month
    current_month = get_current_month().capitalize()
    
    print(f"✅ Itinerary generated with {len(itinerary_data.get('itinerary', []))} days")
    print(f"📋 Packing list includes {len(itinerary_data.get('packing_list', {}))} categories")
    
    return render_template('result.html',
                         destination=destination,
                         days=days,
                         budget=budget,
                         trip_type=trip_type,
                         itinerary=itinerary_data.get('itinerary', []),
                         tips=itinerary_data.get('tips', []),
                         events=itinerary_data.get('local_events', []),
                         gems=itinerary_data.get('hidden_gems', []),
                         packing_list=itinerary_data.get('packing_list', {}),
                         weather_data=weather_data,
                         weather_icon=weather_icon,
                         current_month=current_month)

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF itinerary"""
    try:
        # Get data from form
        data = request.get_json()
        
        destination = data.get('destination', '').strip()
        days = int(data.get('days', 3))
        budget = data.get('budget', 'medium')
        trip_type = data.get('trip_type', 'family')
        itinerary = data.get('itinerary', [])
        tips = data.get('tips', [])
        events = data.get('events', [])
        gems = data.get('gems', [])
        packing_list = data.get('packing_list', {})
        
        print(f"📄 Generating PDF for {destination}...")
        print(f"📊 Data: {days} days, {len(itinerary)} itinerary items, {len(packing_list)} packing categories")
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()
        
        # Generate PDF
        success = generate_itinerary_pdf(
            destination, days, budget, trip_type,
            itinerary, tips, events, gems, packing_list,
            temp_path
        )
        
        if not success:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        # Send file
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"{destination}_itinerary.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"❌ PDF Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page"""
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required')
            return render_template('signup.html')
        
        if password != confirm:
            flash('Passwords do not match')
            return render_template('signup.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('signup.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return render_template('signup.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash('Account created successfully! Welcome to Travel Advisor!')
        return redirect(url_for('profile'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill in all fields')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.username}!')
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    saved_trips = SavedTrip.query.filter_by(user_id=current_user.id).order_by(SavedTrip.created_at.desc()).all()
    return render_template('profile.html', saved_trips=saved_trips)

@app.route('/save-trip', methods=['POST'])
@login_required
def save_trip():
    """Save current itinerary"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Check if trip already saved
        existing = SavedTrip.query.filter_by(
            user_id=current_user.id,
            destination=data.get('destination'),
            days=data.get('days')
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Trip already saved'}), 400
        
        # Include packing list in saved data
        trip_data = {
            'itinerary': data.get('itinerary', []),
            'tips': data.get('tips', []),
            'events': data.get('events', []),
            'gems': data.get('gems', []),
            'packing_list': data.get('packing_list', {})
        }
        
        new_trip = SavedTrip(
            user_id=current_user.id,
            destination=data.get('destination'),
            days=data.get('days'),
            budget=data.get('budget'),
            trip_type=data.get('trip_type'),
            itinerary_data=json.dumps(trip_data)
        )
        
        db.session.add(new_trip)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Trip saved successfully!'})
        
    except Exception as e:
        print(f"Save trip error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/trip/<int:trip_id>')
@login_required
def view_trip(trip_id):
    """View a saved trip"""
    trip = SavedTrip.query.get_or_404(trip_id)
    
    # Check if trip belongs to current user
    if trip.user_id != current_user.id:
        flash('You do not have permission to view this trip')
        return redirect(url_for('profile'))
    
    # Parse itinerary data
    try:
        trip_data = json.loads(trip.itinerary_data)
        itinerary = trip_data.get('itinerary', [])
        tips = trip_data.get('tips', [])
        events = trip_data.get('events', [])
        gems = trip_data.get('gems', [])
        packing_list = trip_data.get('packing_list', {})
    except:
        itinerary = []
        tips = []
        events = []
        gems = []
        packing_list = {}
    
    return render_template('result.html',
                         destination=trip.destination,
                         days=trip.days,
                         budget=trip.budget,
                         trip_type=trip.trip_type,
                         itinerary=itinerary,
                         tips=tips,
                         events=events,
                         gems=gems,
                         packing_list=packing_list,
                         weather_data=None,
                         weather_icon='bi-cloud-sun-fill',
                         current_month=get_current_month().capitalize())

@app.route('/delete-trip/<int:trip_id>', methods=['POST'])
@login_required
def delete_trip(trip_id):
    """Delete a saved trip"""
    trip = SavedTrip.query.get_or_404(trip_id)
    
    if trip.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    db.session.delete(trip)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Trip deleted successfully'})

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# Create database tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created")

# if __name__ == '__main__':
#     print("\n" + "="*70)
#     print("🚀 Travel Advisor Starting...")
#     print("="*70)
#     print("🤖 Using Groq API as primary")
#     print("🔐 User authentication enabled")
#     print("📁 SQLite database: users.db")
#     print("🌤️  Weather API: Connected")
#     print("📄 PDF generation: Ready")
#     print("📅 Festival Calendar: Ready")
#     print("🎒 Packing List Generator: Ready")
#     print("🌐 http://127.0.0.1:5000")
#     print("="*70 + "\n")
#     app.run(debug=True)
#     app = app

# At the very bottom of app.py - ADD THIS
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render gives us a PORT
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False for production