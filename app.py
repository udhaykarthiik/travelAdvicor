from flask import Flask, render_template, request, send_file, jsonify
import os
from dotenv import load_dotenv
from groq import Groq
import json
import re
from utils.pdf_generator import generate_itinerary_pdf, create_pdf
import tempfile
import os

from utils.weather import get_weather, get_weather_icon  # We'll create this next
import logging
logging.basicConfig(level=logging.DEBUG)
# Load environment variables


load_dotenv()

app = Flask(__name__)

# Initialize Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

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

def generate_itinerary_with_groq(destination, days, budget, trip_type):
    """Generate itinerary using Groq API"""
    
    prompt = f"""Create a detailed {days}-day travel itinerary for {destination}, India.

Trip Details:
- Budget: {budget} (budget/medium/luxury)
- Travelers: {trip_type} (family/school/couple/solo)

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
    "tips": ["travel tip 1", "travel tip 2"],
    "local_events": [
        {{
            "event": "festival or event name",
            "location": "venue",
            "dates": "when it happens",
            "type": "festival/cultural"
        }}
    ],
    "hidden_gems": [
        {{
            "name": "place name",
            "description": "brief description",
            "best_time": "when to visit",
            "location": "area"
        }}
    ]
}}

Make sure:
- Activities are REAL places in {destination}
- Food suggestions are AUTHENTIC local dishes
- Create EXACTLY {days} days of itinerary
- No explanations, ONLY the JSON object"""

    try:
        # Call Groq API
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=3000
        )
        
        # Get response text
        result_text = response.choices[0].message.content
        
        # Clean and parse JSON
        cleaned_text = clean_json_response(result_text)
        result = json.loads(cleaned_text)
        
        return result
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        return None

def get_fallback_itinerary(destination, days, budget, trip_type):
    """Fallback mock data if Groq fails"""
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
            "Learn a few local phrases"
        ],
        "local_events": [
            {
                "event": f"Local Festival in {destination}",
                "location": destination,
                "dates": "Check local calendar",
                "type": "cultural"
            }
        ],
        "hidden_gems": [
            {
                "name": f"Hidden spot in {destination}",
                "description": "Less crowded, beautiful place",
                "best_time": "Early morning",
                "location": destination
            }
        ]
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
    
    return render_template('result.html',
                         destination=destination,
                         days=days,
                         budget=budget,
                         trip_type=trip_type,
                         itinerary=itinerary_data.get('itinerary', []),
                         tips=itinerary_data.get('tips', []),
                         events=itinerary_data.get('local_events', []),
                         gems=itinerary_data.get('hidden_gems', []))

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
        
        print(f"📄 Generating PDF for {destination}...")
        
        # Generate PDF HTML
        pdf_html = generate_itinerary_pdf(
            destination, days, budget, trip_type, 
            itinerary, tips, events, gems
        )
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create PDF
        try:
            create_pdf(pdf_html, temp_path)
            print(f"✅ PDF created at {temp_path}")
        except Exception as pdf_error:
            print(f"⚠️ PDF creation error: {pdf_error}")
            # Fall back to HTML
            html_path = temp_path.replace('.pdf', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(pdf_html)
            print(f"📄 Saved HTML to {html_path}")
            raise Exception(f"PDF generation failed. Please check server logs. Error: {str(pdf_error)}")
        
        # Send file
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"{destination}_itinerary.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"❌ PDF Download Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Travel Advisor Starting...")
    print("🤖 Using Groq API as primary")
    print("📁 No JSON files needed")
    print("🌐 http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)