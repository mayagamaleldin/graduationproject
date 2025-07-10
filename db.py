# db.py
import pymysql
import json
from typing import Dict, Any

class Database:
    def __init__(self, host: str, user: str, password: str, db: str):
        try:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                db=db,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.connection.cursor()
            print(" Database connection successful") 
        except pymysql.Error as e:
            print(f" Database connection failed: {e}")
            raise

    def _create_table_if_not_exists(self):
        """Ensure the table exists with correct structure"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    age INT,
                    gender VARCHAR(20),
                    marital_status VARCHAR(50),
                    education VARCHAR(100),
                    job VARCHAR(100),
                    location VARCHAR(100),
                    first_interest VARCHAR(50),
                    first_interest_percentage INT,
                    second_interest VARCHAR(50),
                    second_interest_percentage INT,
                    third_interest VARCHAR(50),
                    third_interest_percentage INT,
                    personality_summary TEXT,
                    key_activities TEXT,
                    total_posts INT,
                    top_habits TEXT,
                    top_hobby VARCHAR(100),
                    travel_indicators VARCHAR(50),
                    life_indicators TEXT,
                    spending_indicators TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
            print(" Table verified/created successfully")
        except pymysql.Error as e:
            print(f" Table creation failed: {e}")
            raise

    def insert_user_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Insert a user profile with transaction handling"""
        try:
            self._create_table_if_not_exists()  # Ensure table exists
            
            interests = profile_data.get("top_interests", [{} for _ in range(3)])
            
            sql = """
            INSERT INTO user_profiles (
                first_name, last_name, age, gender, marital_status, education, job, location,
                first_interest, first_interest_percentage,
                second_interest, second_interest_percentage,
                third_interest, third_interest_percentage,
                personality_summary, key_activities, total_posts, top_habits,
                top_hobby, travel_indicators, life_indicators, spending_indicators
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            values = (
                profile_data.get("first_name", ""),
                profile_data.get("last_name", ""),
                profile_data.get("age"),
                profile_data.get("gender", ""),
                profile_data.get("marital_status", ""),
                profile_data.get("education", ""),
                profile_data.get("job", ""),
                profile_data.get("location", ""),
                interests[0].get("interest", ""),
                interests[0].get("percentage", 0),
                interests[1].get("interest", ""),
                interests[1].get("percentage", 0),
                interests[2].get("interest", ""),
                interests[2].get("percentage", 0),
                profile_data.get("personality_summary", ""),
                json.dumps(profile_data.get("key_activities", [])),
                profile_data.get("total_posts", 0),
                json.dumps(profile_data.get("top_habits", [])),
                profile_data.get("top_hobby", ""),
                profile_data.get("travel_indicators", ""),
                json.dumps(profile_data.get("life_indicators", [])),
                json.dumps(profile_data.get("spending_indicators", []))
            )

            self.cursor.execute(sql, values)
            self.connection.commit()
            print("Profile inserted successfully")
            return True

        except pymysql.Error as e:
            self.connection.rollback()
            print(f" Database error: {e}")
            return False
        except Exception as e:
            self.connection.rollback()
            print(f" Unexpected error: {e}")
            return False
        finally:
            self.close()

    def close(self):
        """Close the connection properly"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection.open:
            self.connection.close()
        print("🔌 Database connection closed")