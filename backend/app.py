from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Enable CORS for all origins and all routes
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://10.85.67.48:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not found in .env file")
else:
    print("✅ Gemini API Key loaded successfully")

genai.configure(api_key=GEMINI_API_KEY)

def clean_json_response(response_text):
    """Clean and parse JSON response from Gemini"""
    try:
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return {
            "itinerary": {
                "summary": "AI-generated travel itinerary",
                "total_estimated_cost": "Budget-friendly",
                "days": [
                    {
                        "day": 1,
                        "date": "Day 1",
                        "theme": "City Exploration",
                        "activities": [
                            {
                                "time": "10:00-12:00",
                                "activity": "City Center Tour",
                                "description": "Explore the main attractions",
                                "cost": "Free",
                                "location": "City Center",
                                "type": "sightseeing"
                            }
                        ]
                    }
                ]
            }
        }

def generate_itinerary_with_gemini(destination, days, budget, interests, travel_style):
    """Generate itinerary using Gemini AI"""
    
    prompt = f"""
    Create a detailed {days}-day budget-friendly travel itinerary for {destination} specifically for students.

    CRITICAL CONSTRAINTS:
    - Total budget: {budget} EUR for entire trip
    - Travel style: {travel_style}
    - Interests: {', '.join(interests)}
    - MUST be realistic and budget-friendly for students

    Return ONLY valid JSON in this exact structure:
    {{
        "itinerary": {{
            "summary": "Brief overview",
            "total_estimated_cost": "X-X EUR",
            "days": [
                {{
                    "day": 1,
                    "date": "Day 1 - Arrival",
                    "theme": "Theme",
                    "activities": [
                        {{
                            "time": "09:00-11:00",
                            "activity": "Activity name",
                            "description": "Description",
                            "cost": "Free or X EUR",
                            "location": "Location",
                            "type": "sightseeing/food/transport"
                        }}
                    ]
                }}
            ]
        }}
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        print("✅ Gemini API call successful")
        return clean_json_response(response.text)
        
    except Exception as e:
        print(f"❌ Gemini API error: {str(e)}")
        return {"error": f"AI generation failed: {str(e)}"}

@app.route('/api/generate-itinerary', methods=['POST', 'OPTIONS'])
def generate_itinerary():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        print(f"📨 Received request for: {data.get('destination', 'Unknown')}")
        
        # Get itinerary from Gemini
        itinerary_data = generate_itinerary_with_gemini(
            destination=data['destination'],
            days=data['days'],
            budget=data['budget'],
            interests=data['interests'],
            travel_style=data['travel_style']
        )
        
        if 'error' in itinerary_data:
            return jsonify({'error': itinerary_data['error']}), 500
            
        return jsonify({
            'success': True,
            'itinerary': itinerary_data
        })
        
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'status': 'healthy', 
        'service': 'Student Travel Planner API',
        'version': '1.0',
        'port': 5000,
        'cors': 'enabled'
    })

@app.route('/test-cors', methods=['GET', 'OPTIONS'])
def test_cors():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'message': 'CORS test successful',
        'allowed_origins': ['http://localhost:3000', 'http://127.0.0.1:3000']
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Student Travel Planner API...")
    print("📡 Server running on: http://localhost:5000")
    print("🌐 CORS Enabled for: http://localhost:3000")
    print("🔑 Gemini API Status:", "✅ Loaded" if GEMINI_API_KEY else "❌ Missing")
    print("=" * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')