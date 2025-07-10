import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import base64
import json
import time
import streamlit as st
import pandas as pd
import time
# Read JSON file
with open('llm_user_profiles_analysis.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Now you can work with the data (it will be a dictionary or list)
#print(data)

# Sample data
# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Background image function
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover;
        background-attachment: fixed;
        background-opacity: 0.1;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

def main():
    # Page configuration
    st.set_page_config(
        page_title="User Profile Dashboard", 
        layout="wide",
        page_icon="👤"
    )
    
    # Add custom CSS and background
    local_css("style.css")  # You'll need to create this file
    # add_bg_from_local("background.png")  # Uncomment if you have a background image
    
    # Extract user data
    user = data[0]
    
    # Dashboard header with gradient
    st.markdown(
        """
        <style>
        .header {
            font-size: 50px;
            font-weight: 700;
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding: 20px 0;
            text-align: center;
            margin-bottom: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(f'<h1 class="header">User Profile Dashboard: {user["first_name"]} {user["last_name"]}</h1>', unsafe_allow_html=True)
    
    # Main columns layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile card with image placeholder
        st.markdown(
            """
            <div style="
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                text-align: center;
            ">
                <div style="
                    width: 120px;
                    height: 120px;
                    margin: 0 auto 15px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #6e8efb, #a777e3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 40px;
                    font-weight: bold;
                ">
                    {}{}
                </div>
                <h3 style="margin: 0; color: #333;">{} {}</h3>
                <p style="color: #666; margin: 5px 0;">{}</p>
                <p style="color: #666; margin: 5px 0;">{}, {}</p>
                <hr style="border: 0.5px solid #eee; margin: 15px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <p style="font-weight: bold; margin: 0; color: #333;">Age</p>
                        <p style="margin: 0; color: #666;">{}</p>
                    </div>
                    <div>
                        <p style="font-weight: bold; margin: 0; color: #333;">Gender</p>
                        <p style="margin: 0; color: #666;">{}</p>
                    </div>
                    <div>
                        <p style="font-weight: bold; margin: 0; color: #333;">Status</p>
                        <p style="margin: 0; color: #666;">{}</p>
                    </div>
                </div>
            </div>
            """.format(
                user["first_name"][0],
                user["last_name"][0],
                user["first_name"],
                user["last_name"],
                user["job"],
                user["location"],
                user["education"],
                user["age"],
                user["gender"],
                user["marital_status"]
            ),
            unsafe_allow_html=True
        )
        
        # Key metrics
        st.markdown(
            """
            <div style="
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            ">
                <h3 style="margin-top: 0; color: #333;">Key Metrics</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <div style="text-align: center;">
                        <p style="font-weight: bold; margin: 0; color: #333;">Posts</p>
                        <p style="font-size: 24px; margin: 5px 0; color: #6e8efb;">{}</p>
                    </div>
                    <div style="text-align: center;">
                        <p style="font-weight: bold; margin: 0; color: #333;">Travel</p>
                        <p style="font-size: 24px; margin: 5px 0; color: #a777e3;">{}</p>
                    </div>
                </div>
                <h4 style="margin-bottom: 10px; color: #333;">Top Hobby</h4>
                <div style="
                    background: #f0f2f6;
                    padding: 10px;
                    border-radius: 5px;
                    text-align: center;
                ">
                    <p style="margin: 0; font-weight: bold; color: #6e8efb;">{}</p>
                </div>
            </div>
            """.format(
                user["total_posts"],
                user["travel_indicators"],
                user["top_hobby"]
            ),
            unsafe_allow_html=True
        )
        
        # Habits section
        st.markdown(
            """
            <div style="
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            ">
                <h3 style="margin-top: 0; color: #333;">Top Habits</h3>
                <ul style="padding-left: 20px; margin: 0;">
            """,
            unsafe_allow_html=True
        )
        
        for habit in user["top_habits"]:
            st.markdown(f'<li style="margin-bottom: 8px; color: #555;">{habit}</li>', unsafe_allow_html=True)
        
        st.markdown("</ul></div>", unsafe_allow_html=True)
    
    with col2:
        # Personality summary with nice card
        st.markdown(
            """
            <div style="
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            ">
                <h3 style="margin-top: 0; color: #333;">Personality Summary</h3>
                <p style="color: #555; line-height: 1.6;">{}</p>
            </div>
            """.format(user["personality_summary"]),
            unsafe_allow_html=True
        )
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Interests", "📅 Activities", "💡 Life Indicators", "💰 Spending"])
        
        with tab1:
            st.subheader("Top Interests")
            interests_df = pd.DataFrame(user["top_interests"])
            
            # Create two columns for the chart and data
            chart_col, data_col = st.columns([2, 1])
            
            with chart_col:
                # Create a donut chart
                fig = px.pie(
                    interests_df, 
                    values='percentage', 
                    names='interest',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    marker=dict(line=dict(color='#ffffff', width=2))
                )
                fig.update_layout(
                    showlegend=False,
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with data_col:
                st.markdown(
                    """
                    <div style="
                        background: #f9fafc;
                        padding: 15px;
                        border-radius: 8px;
                        border-left: 4px solid #6e8efb;
                        margin-top: 20px;
                    ">
                        <h4 style="margin-top: 0; color: #333;">Interest Distribution</h4>
                    """,
                    unsafe_allow_html=True
                )
                
                for index, row in interests_df.iterrows():
                    st.markdown(
                        f"""
                        <div style="margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="font-weight: 500; color: #444;">{row['interest']}</span>
                                <span style="font-weight: bold; color: #6e8efb;">{row['percentage']}%</span>
                            </div>
                            <div style="height: 5px; background: #e0e5f0; border-radius: 3px; margin-top: 3px;">
                                <div style="width: {row['percentage']}%; height: 100%; background: linear-gradient(90deg, #6e8efb, #a777e3); border-radius: 3px;"></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Recent Activities")
            st.markdown(
                """
                <div style="
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                """,
                unsafe_allow_html=True
            )
            
            for i, activity in enumerate(user["key_activities"]):
                st.markdown(
                    f"""
                    <div style="
                        padding: 15px;
                        margin-bottom: {'10px' if i != len(user['key_activities'])-1 else '0px'};
                        background: #f9fafc;
                        border-radius: 8px;
                        border-left: 3px solid {'#6e8efb' if i % 2 == 0 else '#a777e3'};
                    ">
                        <div style="display: flex; align-items: flex-start;">
                            <div style="
                                width: 24px;
                                height: 24px;
                                background: {'#6e8efb' if i % 2 == 0 else '#a777e3'};
                                color: white;
                                border-radius: 50%;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 10px;
                                flex-shrink: 0;
                            ">
                                {i+1}
                            </div>
                            <p style="margin: 0; color: #555;">{activity}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab3:
            st.subheader("Life Indicators")
            indicators_df = pd.DataFrame({
                "category": ["Daily Routine", "Work", "Social"],
                "indicators": [
                    user["life_indicators"][0],
                    user["life_indicators"][1],
                    user["life_indicators"][2]
                ]
            })
            
            for index, row in indicators_df.iterrows():
                st.markdown(
                    f"""
                    <div style="
                        background: white;
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    ">
                        <div style="display: flex; align-items: center;">
                            <div style="
                                width: 40px;
                                height: 40px;
                                background: {'#f0f7ff' if index % 2 == 0 else '#f9f0ff'};
                                border-radius: 8px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 15px;
                                color: {'#6e8efb' if index % 2 == 0 else '#a777e3'};
                                font-size: 18px;
                            ">
                                {"⏰" if index == 0 else "💼" if index == 1 else "👥"}
                            </div>
                            <div>
                                <h4 style="margin: 0 0 5px 0; color: #333;">{row['category']}</h4>
                                <p style="margin: 0; color: #555;">{row['indicators']}</p>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with tab4:
            st.subheader("Spending Indicators")
            
            # Create a metric-style display
            col1, col2 = st.columns(2)
            
            for i, spending in enumerate(user["spending_indicators"]):
                with (col1 if i % 2 == 0 else col2):
                    st.markdown(
                        f"""
                        <div style="
                            background: white;
                            padding: 20px;
                            border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                            margin-bottom: 15px;
                        ">
                            <div style="display: flex; align-items: center;">
                                <div style="
                                    width: 40px;
                                    height: 40px;
                                    background: {'#f0f7ff' if i % 2 == 0 else '#f9f0ff'};
                                    border-radius: 50%;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    margin-right: 15px;
                                    color: {'#6e8efb' if i % 2 == 0 else '#a777e3'};
                                ">
                                    {"💰" if i % 2 == 0 else "✈️"}
                                </div>
                                <p style="margin: 0; color: #555; font-size: 15px;">{spending}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

if __name__ == "__main__":
    main()