# app.py
import streamlit as st
from typing import Dict
import json
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Gemini API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

class GeminiAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def generate_text(self, prompt: str) -> str:
        """Generate text using the Gemini API."""
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        response = requests.post(
            f"{self.base_url}?key={self.api_key}",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_msg = f"API request failed with status {response.status_code}: {response.text}"
            print(error_msg)
            raise Exception(error_msg)

class TravelPlanner:
    def __init__(self):
        # Initialize Gemini API
        self.api = GeminiAPI(GEMINI_API_KEY)

    def parse_travel_preferences(self, text: str) -> Dict:
        """Parse user's travel preferences."""
        prompt = f"""
        Extract travel preferences from the following text and return only a JSON object with these keys:
        destination, start_date, duration, budget, interests, accommodation_type

        Text: {text}
        
        Return only the JSON object, nothing else.
        """
        try:
            response = self.api.generate_text(prompt)
            # Extract JSON from response
            json_str = response.strip()
            if not json_str.startswith("{"):
                json_str = "{" + json_str.split("{", 1)[1]
            if not json_str.endswith("}"):
                json_str = json_str.split("}", 1)[0] + "}"
            return json.loads(json_str)
        except Exception as e:
            print(f"Error parsing preferences: {str(e)}")
            return {
                "destination": text.split("to")[1].split("for")[0].strip() if "to" in text else "",
                "start_date": "",
                "duration": text.split("for")[1].split("days")[0].strip() if "days" in text else "",
                "budget": "",
                "interests": [],
                "accommodation_type": ""
            }

    def generate_itinerary(self, preferences: Dict) -> str:
        """Generate a detailed travel itinerary."""
        prompt = f"""
        Create a detailed day-by-day travel itinerary based on these preferences:
        Destination: {preferences.get('destination')}
        Duration: {preferences.get('duration')} days
        Budget: {preferences.get('budget')}
        Interests: {preferences.get('interests')}
        Accommodation: {preferences.get('accommodation_type')}

        Format the itinerary day by day with activities, recommended times, and estimated costs.
        Use bullet points for each day and ensure the output is well-structured and easy to read.
        """
        try:
            return self.api.generate_text(prompt)
        except Exception as e:
            print(f"Error generating itinerary: {str(e)}")
            return "Unable to generate itinerary. Please check your API key and try again."

    def get_travel_tips(self, destination: str) -> str:
        """Get additional travel tips."""
        prompt = f"Provide 3-5 essential travel tips for visiting {destination}."
        try:
            return self.api.generate_text(prompt)
        except Exception as e:
            print(f"Error getting travel tips: {str(e)}")
            return "Unable to generate travel tips. Please check your API key and try again."

    def plan_trip(self, user_input: str) -> Dict:
        """Main function to plan a trip."""
        try:
            # Parse preferences
            preferences = self.parse_travel_preferences(user_input)
            
            # Generate itinerary
            itinerary = self.generate_itinerary(preferences)
            
            # Get additional tips
            tips = self.get_travel_tips(preferences.get('destination', ''))
            
            return {
                "preferences": preferences,
                "itinerary": itinerary,
                "additional_tips": tips
            }
        except Exception as e:
            print(f"Error in plan_trip: {str(e)}")
            return None

def main():
    # Set page title and icon
    st.set_page_config(page_title="🌍 Travel Planner", page_icon="✈️")

    # Custom CSS for better UI
    st.markdown("""
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stTextArea textarea {
        font-size: 16px;
        padding: 10px;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #2E86C1;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌍 Travel Planner App")
    st.write("Welcome to the Travel Planner! Enter your travel preferences below to generate a personalized travel plan.")

    # User input
    st.markdown("### ✈️ Describe Your Travel Preferences")
    st.write("Please provide details about your trip. For example:")
    st.markdown("""
    - **Destination**: Country or city (e.g., Japan, Paris)
    - **Duration**: Number of days (e.g., 10 days)
    - **Budget**: Total amount (e.g., $5000)
    - **Interests**: Activities or experiences (e.g., cultural tours, hiking, food)
    - **Accommodation**: Type of stay (e.g., boutique hotel, Airbnb)
    """)

    user_input = st.text_area(
        "Enter your travel preferences here:",
        placeholder="Example: 'I want to plan a trip to Japan for 10 days in April 2025. My budget is $5000, and I'm interested in cultural experiences, food tours, and historic temples. I prefer boutique hotels.'",
        height=150
    )

    if st.button("🚀 Generate Travel Plan"):
        if user_input:
            try:
                # Create the planner instance
                planner = TravelPlanner()
                
                # Plan the trip
                result = planner.plan_trip(user_input)
                
                if result:
                    # Display the results
                    st.success("🎉 Your travel plan has been generated successfully!")
                    
                    # Display preferences in a clean format
                    st.markdown("### 📋 Travel Preferences")
                    with st.expander("View Preferences", expanded=True):
                        st.json(result["preferences"])
                    
                    # Display itinerary in a structured way
                    st.markdown("### 📅 Travel Itinerary")
                    with st.expander("View Itinerary", expanded=True):
                        # Format itinerary with bullet points
                        itinerary = result["itinerary"].replace("\n", "  \n")  # Ensure markdown line breaks
                        st.markdown(itinerary)
                    
                    # Display additional tips
                    st.markdown("### 💡 Additional Travel Tips")
                    with st.expander("View Tips", expanded=True):
                        tips = result["additional_tips"].replace("\n", "  \n")  # Ensure markdown line breaks
                        st.markdown(tips)
                else:
                    st.error("❌ Failed to generate travel plan. Please check your input and try again.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.write("Please check your API key and try again.")
        else:
            st.warning("⚠️ Please enter your travel preferences to generate a plan.")

if __name__ == "__main__":
    main()