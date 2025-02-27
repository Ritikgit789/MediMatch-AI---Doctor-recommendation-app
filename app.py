import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import pydeck as pdk
from dotenv import load_dotenv

# ✅ Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ✅ Load Doctor Data
DATA_PATH = "E:/Immedcure_Doctor recommendation/Backend/Data/scraped_placidway_data (1).csv"
df = pd.read_csv(DATA_PATH, encoding="ISO-8859-1", encoding_errors="ignore")

# ✅ Streamlit Customization
st.set_page_config(
    page_title="MediMatch AI - Find Your Best Doctor",
    page_icon="🩺",
    layout="wide"
)

# ✅ Apply Custom CSS (Deep Blue Theme & Modern UI)
st.markdown("""
    <style>
        body {
            font-family: 'Serif', sans-serif;
            background-color: #001f3f;
            color: white;
        }
        .stTextInput > div > div > input {
            font-size: 16px;
            padding: 8px;
            background-color: #001f3f;
            color: white;
            border-radius: 8px;
        }
        .stButton > button {
            background: linear-gradient(to right, #0074D9, #00A8E8);
            color: white;
            font-size: 18px;
            border-radius: 8px;
            padding: 10px 20px;
            border: none;
        }
        .doctor-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: black;
        }
        .doctor-card h4 {
            color: #0074D9;
        }
        .profile-link {
            text-decoration: none;
            color: #00A8E8;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ Sidebar for More Options
with st.sidebar:
    st.header("🔧 Advanced Search Filters")
    display_ai_suggestions = st.checkbox("Enable AI-Enhanced Doctor Recommendations", value=True)
    expand_overview = st.checkbox("Expand Doctor Overview with AI", value=True)
    top_n = st.slider("🔍 Number of AI Recommendations", min_value=1, max_value=10, value=5)

# ✅ UI Header
st.title("🔍 MediMatch AI - Find the Best Doctors Near You")
st.markdown("🚀 **Discover expert doctors worldwide with AI-powered recommendations!**")

# ✅ User Input Fields
specialization = st.text_input("🩺 Enter Specialization (e.g., Cardiologist, Dentist):", "")
location = st.text_input("📍 Enter Location (e.g., New York, Mumbai):", "")
submit = st.button("🔎 Search")

# ✅ Function to Expand Overview Using AI
def expand_overview_ai(doctor_name, overview):
    prompt = f"""
    Provide a detailed but concise 3-4 line summary for the following doctor's profile:
    
    Doctor Name: {doctor_name}
    Overview: {overview}

    The summary should highlight expertise, patient care, and specialties.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip() if response else overview

# ✅ When Search Button is Clicked
if submit:
    if specialization and location:
        # 🔹 **Filter Unique Doctors (Remove Duplicates)**
        filtered_doctors = df[
            (df["specialties"].str.contains(specialization, case=False, na=False)) &
            (df["location"].str.contains(location, case=False, na=False))
        ].drop_duplicates(subset=["name"])

        if filtered_doctors.empty:
            st.warning("⚠️ No doctors found. Trying AI-powered recommendations...")

        else:
            # 🔹 **Display Doctors in Cards**
            st.subheader("🏥 Best Matched Doctors:")
            for _, row in filtered_doctors.iterrows():
                doctor_overview = expand_overview_ai(row["name"], row["overview"]) if expand_overview else row["overview"]

                st.markdown(f"""
                    <div class="doctor-card">
                        <h4>👨‍⚕️ {row['name']} - {row['specialties'].strip()}</h4>  
                        <p><strong>📍 Location:</strong> {row['location'].strip()}</p>
                        <p><strong>📝 Overview:</strong> {doctor_overview}</p>
                        <a class="profile-link" href="{row['profile_link']}" target="_blank">🔗 View Profile</a>
                    </div>
                """, unsafe_allow_html=True)

        # 🔹 **Use Gemini AI to Recommend Additional Doctors**
        if display_ai_suggestions:
            st.subheader("🤖 AI-Powered Additional Recommendations:")
            model = genai.GenerativeModel("gemini-2.0-flash")

            doctor_list = "\n".join([
                f"{row['name']} (Specialties: {row['specialties']}, Location: {row['location']})\nOverview: {row['overview']}"
                for _, row in filtered_doctors.iterrows()
            ])

            prompt = f"""
            You are an AI assistant that helps patients find the best doctors. Based on the list of doctors below,
            suggest {top_n} additional doctors who might be a good fit for the patient.

            Doctors Found:
            {doctor_list}

            Return recommendations in this format:
            - Doctor Name (Specialization) - Location
            - Short reasoning for recommendation.
            """

            response = model.generate_content(prompt)
            st.write(response.text)

    else:
        st.warning("⚠️ Please enter both Specialization and Location.")

# # ✅ **Interactive Map for Doctor Locations**
# st.subheader("🌍 Doctor Locations on the Map")

# # Convert location column into latitude & longitude (Assumes lat/lon is available)
# if "latitude" in df.columns and "longitude" in df.columns:
#     map_data = df[["latitude", "longitude", "name", "location"]].dropna()

#     # Display Map with Doctors' Locations
#     st.pydeck_chart(pdk.Deck(
#         map_style="mapbox://styles/mapbox/dark-v10",
#         initial_view_state=pdk.ViewState(
#             latitude=map_data["latitude"].mean(),
#             longitude=map_data["longitude"].mean(),
#             zoom=2,
#             pitch=50,
#         ),
#         layers=[
#             pdk.Layer(
#                 "ScatterplotLayer",
#                 data=map_data,
#                 get_position=["longitude", "latitude"],
#                 get_color=[0, 128, 255, 200],
#                 get_radius=200000,
#                 pickable=True,
#             ),
#         ],
#     ))

#     # Show location details
#     st.write(map_data[["name", "location"]])

# else:
#     st.warning("⚠️ No latitude/longitude data found. Unable to generate the map.")
