# Travel Advisor 🧳✈️

![Travel Advisor](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
![License](https://img.shields.io/badge/license-MIT-orange)

An **AI-powered travel itinerary generator** that creates personalized day-by-day travel plans using Groq API. Built with Flask, this application provides comprehensive travel planning with weather integration, festival calendars, packing lists, and PDF downloads.

## ✨ Features

### 🤖 **AI-Powered Itineraries**
- Personalized day-by-day plans based on destination, duration, budget, and traveler type
- Real-time generation using Groq's Llama 3.3 70B model
- Smart recommendations for activities, food, and accommodations

### 📅 **Interactive Festival Calendar**
- Month-by-month view of local festivals and events
- Color-coded event types (festival, cultural, religious, sports)
- Click months to see detailed event information
- Full calendar view option

### 🎒 **Smart Packing List**
- AI-generated packing lists tailored to destination and weather
- Interactive checkboxes with progress tracker
- 8 categories (essentials, clothing, weather-specific, activities, toiletries, medications, electronics, miscellaneous)
- Saves progress in browser localStorage

### 🌤️ **Weather Integration**
- Real-time weather data from OpenWeatherMap
- Temperature, humidity, wind speed, and conditions
- Weather-based packing tips

### 📄 **PDF Download**
- Professional, clean PDF format
- Blue and white theme matching the website
- Includes all itinerary details, tips, events, gems, and packing list
- No special characters or font errors

### 🔐 **User Authentication**
- Sign up / Login functionality
- Secure password hashing
- Save trips to personal profile
- View and manage saved itineraries

### 💰 **Budget Calculator**
- Quick budget estimates based on trip duration and budget level
- Breakdown by hotel, food, and activities
- Per-person calculations

### 💎 **Hidden Gems**
- AI-discovered offbeat places
- Descriptions and best times to visit
- Location details

### 📱 **Fully Responsive**
- Works perfectly on desktop, tablet, and mobile
- Bootstrap 5 with custom CSS
- Smooth animations and hover effects

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Groq API key (free)
- OpenWeatherMap API key (free)

### Installation

1. **Clone the repository**

   git clone https://github.com/udhaykarthiik/travelAdvicor.git
   cd travelAdvicor

2.  Create virtual environment
   python -m venv venv

3. Activate virtual environment
   venv\Scripts\activate - Windows
   source venv/bin/activate - Mac
   
4. Install dependencies
   pip install -r requirements.txt

5. Create .env file
   GROQ_API_KEY=your_groq_api_key_here
   WEATHER_API_KEY=your_openweather_api_key_here
   SECRET_KEY=your_secret_key_here_change_this

6. Run the application
   python app.py

7. http://127.0.0.1:5000


🔑 API Keys
Groq API
    Go to console.groq.com
    
    
    Sign up / Log in
    
    Create API key
    
    Copy and add to .env

OpenWeatherMap API
    Go to openweathermap.org
    
    Sign up / Log in
    
    Go to API keys section
    Generate new key
    
    Copy and add to .env

📁 Project Structure


    travel_advisor_new/
├── app.py                 # Main application
├── models.py              # Database models
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (not in repo)
├── .gitignore            # Git ignore file
├── README.md             # This file
│
├── utils/                 # Helper modules
│   ├── pdf_generator.py   # PDF generation
│   └── weather.py         # Weather API integration
│
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── result.html        # Itinerary results
│   ├── login.html         # Login page
│   ├── signup.html        # Signup page
│   ├── profile.html       # User profile
│   └── about.html         # About page
│
└── static/                # Static files
    └── css/
        └── style.css      # Custom styles

🎯 How It Works
    
    User Input: Enter destination, days, budget, and traveler type
    
    AI Generation: Groq API generates personalized itinerary with activities, food, tips, events, gems, and packing list
    
    Weather Fetch: Real-time weather data for destination
    
    Display: Beautiful, responsive UI shows all information
    
    Interaction: Check packing items, view calendar, download PDF
    
    Save: Create account to save trips for later

🛠️ Technologies Used
    Backend: Flask, Python
    
    Frontend: HTML5, CSS3, JavaScript, Bootstrap 5
    
    Database: SQLite with SQLAlchemy
    
    APIs: Groq (AI), OpenWeatherMap
    
    Authentication: Flask-Login
    
    PDF Generation: FPDF
    
    Icons: Bootstrap Icons

📦 Dependencies
    text
    Flask==2.3.3
    python-dotenv==1.0.0
    groq==0.9.0
    requests==2.31.0
    fpdf2==2.7.9
    flask-login==0.6.2
    flask-sqlalchemy==3.1.1
    werkzeug==2.3.7
    
🤝 Contributing
    Contributions are welcome! Please feel free to submit a Pull Request.

📝 License
    This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
    Groq for providing free AI API access

OpenWeatherMap for weather data

Bootstrap for the amazing framework

All contributors and testers

📧 Contact
Project Link: https://github.com/udhaykarthiik/travelAdvicor

Made with ❤️ for travelers everywhere...
