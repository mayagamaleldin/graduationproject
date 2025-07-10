import json
import google.generativeai as genai
from typing import Dict, List, Tuple, Optional
import os
from dataclasses import dataclass
import time
#from db import Database

# db = Database(host="", user="", password="", db="")

@dataclass
class UserProfile:
    first_name: str
    last_name: str
    age: str
    gender: str
    marital_status: str
    education: str
    job: str
    location: str
    top_interests: List[Dict[str, float]]  
    personality_summary: str
    key_activities: List[str]
    total_posts: int
    top_habits: List[str]
    top_hobby: str
    travel_frequency: str
    life_indicators: List[str]
    spending_indicators: List[str]

class LLMUserProfileAnalyzer:
    def __init__(self, api_key: str = None):
        """Initialize the LLM-based analyzer with Gemini Flash"""
        if api_key:
            genai.configure(api_key=api_key)
        else:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Please provide a Gemini API key either as parameter or set GEMINI_API_KEY environment variable")
            genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.interest_categories = [
            "technology", "education", "fashion", "food", "sports", "traveling",
            "music", "health", "finance", "automotive", "agriculture", "art",
            "entertainment", "fitness", "gaming", "photography", "reading",
            "cooking", "nature", "science", "business", "politics", "religion",
            "volunteer work", "family", "social activities"
        ]
    
    def extract_name_parts(self, UserName: str) -> Tuple[str, str]:
        """Extract first name and last name from full name (handles Arabic and English)"""
        if not UserName or UserName == "Unknown":
            return "Unknown", ""
        
        name_parts = UserName.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
        else:
            first_name = UserName
            last_name = ""
        return first_name, last_name
    
    def load_users_from_file(self, file_path: str) -> List[Dict]:
        """Load users data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if not content.strip().startswith('['):
                    content = '[' + content
                if not content.strip().endswith(']'):
                    content = content + ']'
                
                users = json.loads(content)
                return users
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found!")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return []
    
    def safe_parse_json(self, text: str, default=None):
        """Safely parse JSON with fallback to default value"""
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return default
        except Exception:
            return default
    
    def extract_top_interests(self, user_data: Dict) -> List[Dict[str, float]]:
        """Extract top 3 interests with percentage distribution"""
        posts_text = ' '.join(user_data.get('Posts', []))
        job = user_data.get('Job', '')
        education = user_data.get('Education', '')

        prompt = f"""
        Analyze the following user profile and extract the top 3 most prominent interests/hobbies with percentage distribution:
        The content may be in English, Arabic, or mixed.

        JOB: {job}
        EDUCATION: {education}
        
        POSTS/ACTIVITIES (may contain Arabic):
        {posts_text}

        Available interest categories:
        {', '.join(self.interest_categories)}

        Instructions:
        1. Analyze posts in both English and Arabic
        2. Identify the 3 most prominent interests
        3. Assign percentage values to each (sum must equal 100)
        4. Return ONLY the interest names and percentages in this exact format:
        interest1,percentage1,interest2,percentage2,interest3,percentage3
        5. Use only the interest categories from the provided list
        6. Ensure percentages are whole numbers that sum to 100

        Example output: 
        art,50,technology,30,business,20
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
           
            if response_text.startswith('[') and response_text.endswith(']'):
                try:
                    interests = json.loads(response_text)
                    if isinstance(interests, list) and len(interests) >= 3:
                        
                        valid_interests = []
                        for item in interests[:3]:
                            if isinstance(item, dict) and 'interest' in item and 'percentage' in item:
                                valid_interests.append({
                                    'interest': item['interest'],
                                    'percentage': int(item['percentage'])
                                })
                        if len(valid_interests) == 3:
                            total = sum(item['percentage'] for item in valid_interests)
                            if total == 100:
                                return valid_interests
                except json.JSONDecodeError:
                    pass
            
            
            parts = [p.strip() for p in response_text.split(',')]
            if len(parts) >= 6:
                try:
                    interests = [
                        {'interest': parts[0], 'percentage': int(parts[1])},
                        {'interest': parts[2], 'percentage': int(parts[3])},
                        {'interest': parts[4], 'percentage': int(parts[5])}
                    ]
                    total = sum(item['percentage'] for item in interests)
                    if total == 100:
                        return interests
                except (ValueError, IndexError):
                    pass
            
            found_interests = []
            for interest in self.interest_categories:
                if (interest.lower() in posts_text.lower() or 
                    interest.lower() in job.lower() or 
                    interest.lower() in education.lower()):
                    found_interests.append(interest)
                    if len(found_interests) >= 3:
                        break
            
            if found_interests:
                base_pct = 100 // len(found_interests)
                interests = []
                for i, interest in enumerate(found_interests):
                    if i == len(found_interests) - 1:
                        pct = 100 - (base_pct * (len(found_interests) - 1))
                    else:
                        pct = base_pct
                    interests.append({'interest': interest, 'percentage': pct})
                return interests
            
        except Exception as e:
            print(f"Error extracting interests: {e}")
        

        return [
            {"interest": "art", "percentage": 34},
            {"interest": "technology", "percentage": 33},
            {"interest": "business", "percentage": 33}
        ]

    def generate_personality_summary(self, user_data: Dict) -> str:
        """Generate personality summary (handles Arabic content)"""
        posts_text = ' '.join(user_data.get('Posts', []))
        job = user_data.get('Job', '')
        education = user_data.get('Education', '')
        age = user_data.get('Age', '')
        marital_status = user_data.get('MaritalStatus', '')
        
        prompt = f"""
        Create a personality summary for this user who may post in English or Arabic:

        BASIC INFO:
        - Age: {age}
        - Job: {job}
        - Education: {education}
        - Marital Status: {marital_status}
        
        POSTS/ACTIVITIES (may contain Arabic):
        {posts_text}

        Instructions:
        1. Analyze content in both English and Arabic
        2. Create a 2-3 sentence summary in English
        3. Highlight cultural aspects if relevant
        4. Focus on professional and personal traits

        Generate the summary:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating personality summary: {e}")
            return "Shows a balanced personality with diverse interests."
    
    def extract_key_activities(self, user_data: Dict) -> List[str]:
        """Use LLM to extract key activities from posts"""
        posts_text = ' '.join(user_data.get('Posts', []))
        
        if not posts_text.strip():
            return []
        
        prompt = f"""
        Extract the top 5 most significant activities/experiences from these posts:

        POSTS:
        {posts_text}

        Instructions:
        1. Identify concrete activities, events, or experiences mentioned
        2. Focus on specific actions rather than general statements
        3. Prioritize recent or frequently mentioned activities
        4. Include both professional and personal activities
        5. Make each activity concise but descriptive (10-50 words)
        6. Return as a numbered list, one activity per line
        7. If less than 5 activities are found, return what you can find

        Example format:
        1. Attended a technology conference on AI and machine learning
        2. Completed a cooking class focusing on Mediterranean cuisine
        3. Organized a family gathering for holiday celebration
        4. Started a new fitness routine with gym workouts
        5. Traveled to Italy for vacation and cultural exploration
        """
        
        try:
            response = self.model.generate_content(prompt)
            activities = []
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.strip() and any(char.isdigit() for char in line[:3]):
                    # Remove numbering and clean up
                    activity = line.split('.', 1)[-1].strip()
                    if activity:
                        activities.append(activity)
            return activities[:5]
        except Exception as e:
            print(f"Error extracting activities: {e}")
            return []
    
    def extract_habits_hobbies(self, user_data: Dict) -> Tuple[List[str], str]:
        """Extract top 2 habits and top 1 hobby from posts"""
        posts_text = ' '.join(user_data.get('Posts', []))
        
        prompt = f"""
        Analyze the following posts to identify habits and hobbies:
        
        POSTS (may contain Arabic):
        {posts_text}

        Instructions:
        1. Identify 2 most frequent habits (regular behaviors)
        2. Identify 1 most prominent hobby (leisure activity)
        3. Return habits as a comma-separated list
        4. Return hobby as a single item
        5. Use English terms
        6. Be specific (e.g., "night reading" not just "reading")

        Example output:
        habits: morning jogging, daily journaling
        hobby: photography
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            
            habits = []
            hobby = ""
            
            if "habits:" in text.lower() and "hobby:" in text.lower():
                habits_part = text.split("habits:")[1].split("hobby:")[0].strip()
                habits = [h.strip() for h in habits_part.split(',')][:2]
                hobby = text.split("hobby:")[1].strip().split('\n')[0].strip()
            else:
                lines = text.split('\n')
                if len(lines) >= 2:
                    habits = [h.strip() for h in lines[0].split(':')[-1].split(',')][:2]
                    hobby = lines[1].split(':')[-1].strip()
            
            return habits, hobby
        except Exception as e:
            print(f"Error extracting habits/hobbies: {e}")
            return [], ""
    
    def extract_travel_frequency(self, user_data: Dict) -> str:
        """Determine overall travel frequency classification"""
        posts = user_data.get('Posts', [])
        
        travel_keywords = {
            'travel': 0,
            'trip': 0, 
            'visit': 0,
            'go to': 0,
            'vacation': 0,
            'journey': 0,
            'tour': 0,
            'destination': 0,
            'flight': 0,
            'hotel': 0
        }
        
        for post in posts:
            lower_post = post.lower()
            for kw in travel_keywords:
                travel_keywords[kw] += lower_post.count(kw)
        
        total_mentions = sum(travel_keywords.values())
        
        if total_mentions == 0:
            return "no travel"
        elif total_mentions <= 2:
            return "rare"
        elif total_mentions <= 5:
            return "occasional"
        else:
            return "frequent"
    def _generate_frequency_based_indicators(self, keyword_counts: Dict[str, int]) -> List[str]:
        """Generate indicators when parsing fails"""
        indicators = []
        
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        for kw, count in sorted_keywords:
            if count > 0:
                freq = self._get_frequency(count)
                if kw == 'trip':
                    indicators.append(f"{freq} trips")
                elif kw == 'visit':
                    indicators.append(f"{freq} visits to locations")
                elif kw == 'travel':
                    indicators.append(f"{freq} travel activities")
                elif kw == 'go to':
                    indicators.append(f"{freq} outings")
                    
            if len(indicators) >= 3:
                break
        
        return indicators if indicators else ["none"]

    def extract_life_indicators(self, user_data: Dict) -> List[str]:
        """Extract lifestyle indicators without frequency labels"""
        
        posts = user_data.get('Posts', [])
        key_activities = user_data.get('key_activities', [])
        top_habits = user_data.get('top_habits', [])
        top_hobby = user_data.get('top_hobby', '')
        job = user_data.get('job', '')
        personality = user_data.get('personality_summary', '')
        interests = [i['interest'] for i in user_data.get('top_interests', [])[:3]]

        lifestyle_patterns = {
            'morning': {'keywords': ['morning', 'wake up', 'breakfast'], 'count': 0},
            'evening': {'keywords': ['evening', 'night', 'dinner'], 'count': 0},
            'work': {'keywords': ['work', 'job', 'office', 'career'], 'count': 0},
            'fitness': {'keywords': ['exercise', 'gym', 'yoga', 'run'], 'count': 0},
            'social': {'keywords': ['friend', 'family', 'social', 'meet'], 'count': 0},
            'leisure': {'keywords': ['read', 'movie', 'game', 'hobby'], 'count': 0},
            'health': {'keywords': ['health', 'sleep', 'meal', 'diet'], 'count': 0}
        }

        for post in posts:
            lower_post = post.lower()
            for pattern in lifestyle_patterns.values():
                pattern['count'] += sum(lower_post.count(kw) for kw in pattern['keywords'])

        for activity in key_activities:
            lower_act = activity.lower()
            for pattern in lifestyle_patterns.values():
                pattern['count'] += sum(lower_act.count(kw) for kw in pattern['keywords'])

        top_patterns = sorted(lifestyle_patterns.items(), 
                            key=lambda x: x[1]['count'], reverse=True)[:3]


        indicators = []
        for pattern, data in top_patterns:
            if data['count'] > 0:
                if pattern == 'morning':
                    indicators.append("Maintains morning routines")
                elif pattern == 'evening':
                    indicators.append("Evening relaxation activities")
                elif pattern == 'work':
                    indicators.append("Dedicated work engagement")
                elif pattern == 'fitness':
                    indicators.append("Regular fitness practice")
                elif pattern == 'social':
                    indicators.append("Active social interactions")
                elif pattern == 'leisure':
                    indicators.append("Enjoyable leisure time")
                elif pattern == 'health':
                    indicators.append("Health-conscious lifestyle")


        if not indicators:
            if top_habits:
                indicators.extend(f"Maintains {habit}" for habit in top_habits[:2])
            if key_activities:
                indicators.extend(f"Engages in {act.split('.')[0].lower()}" 
                                for act in key_activities[:2])
            if top_hobby:
                indicators.append(f"Enjoys {top_hobby}")

        if not indicators:
            if interests:
                indicators.append(f"Interested in {interests[0]}")
                if len(interests) > 1:
                    indicators.append(f"Also likes {interests[1]}")
            if job:
                indicators.append(f"Works as {job}")

        while len(indicators) < 3:
            indicators.append(self._get_general_lifestyle_indicator(len(indicators)))

        return indicators[:3]

    def _get_general_lifestyle_indicator(self, index: int) -> str:
        """Provide meaningful generic indicators when needed"""
        general_indicators = [
            "Maintains a balanced lifestyle",
            "Engages in personal development",
            "Values work-life balance"
        ]
        return general_indicators[index % len(general_indicators)]

    def extract_spending_indicators(self, user_data: Dict) -> List[str]:
        """Extract spending patterns with financial behavior analysis"""
        posts = user_data.get('Posts', [])
        posts_text = ' '.join(posts)
        key_activities = user_data.get('key_activities', [])
        top_habits = user_data.get('top_habits', [])
        job = user_data.get('job', '')
        
    
        spending_categories = {
            'professional': ['buy', 'purchase', 'tool', 'equipment', 'conference'],
            'leisure': ['dine', 'movie', 'concert', 'hobby', 'game'],
            'education': ['course', 'book', 'learn', 'class', 'workshop'],
            'travel': ['trip', 'hotel', 'flight', 'vacation', 'resort']
        }
        
        category_counts = {cat: 0 for cat in spending_categories}
        for post in posts:
            lower_post = post.lower()
            for cat, keywords in spending_categories.items():
                category_counts[cat] += sum(lower_post.count(kw) for kw in keywords)
        
        prompt = f"""
        Analyze spending behaviors from:
        
        JOB: {job}
        ACTIVITIES: {key_activities}
        HABITS: {top_habits}
        SPENDING CATEGORY COUNTS: {category_counts}
        
        Generate 2 spending indicators covering:
        1. Primary expenditure category (highest count)
        2. Secondary spending pattern
        3. Include frequency descriptors when possible
        
        Example outputs:
        ["Regular investments in professional development",
        "Occasional luxury leisure purchases"]
        """
        
        try:
            response = self.model.generate_content(prompt)
            indicators = self.safe_parse_json(response.text, default=[])
            
            if not indicators:
                sorted_categories = sorted(category_counts.items(), 
                                        key=lambda x: x[1], reverse=True)
                
                if sorted_categories[0][1] > 0:
                    main_cat = sorted_categories[0][0]
                    indicators.append(f"Spends on {main_cat} activities")
                    
                if len(sorted_categories) > 1 and sorted_categories[1][1] > 0:
                    sec_cat = sorted_categories[1][0]
                    indicators.append(f"Secondary {sec_cat} expenditures")
                    
            if len(indicators) < 2:
                if job:
                    indicators.append(f"Career-related spending")
                if len(indicators) < 2:
                    indicators.append("Visible lifestyle expenditures")
                    
            return indicators[:2]
            
        except Exception as e:
            print(f"Error extracting spending indicators: {e}")
            return [
                "Discernible spending patterns in posts",
                "Visible financial behaviors"
            ]
    def analyze_user_profile(self, user: Dict) -> UserProfile:
        """Analyze a single user's complete profile using LLM"""
        full_name = user.get('UserName') or user.get('FullName', 'Unknown')
        first_name, last_name = self.extract_name_parts(full_name)
        age = user.get('Age', 'Unknown')
        gender = user.get('Gender', 'Unknown')
        marital_status = user.get('MaritalStatus', 'Unknown')
        education = user.get('Education', 'Unknown')
        job = user.get('Job', 'Unknown')
        location = user.get('Location', 'Unknown')
        posts = user.get('Posts', [])
        
        print(f"Analyzing profile for {full_name}...")
        

        top_interests = self.extract_top_interests(user)
        personality_summary = self.generate_personality_summary(user)
        key_activities = self.extract_key_activities(user)
        top_habits, top_hobby = self.extract_habits_hobbies(user)
        travel_frequency  = self.extract_travel_frequency(user)
        life_indicators = self.extract_life_indicators(user)
        spending_indicators = self.extract_spending_indicators(user)
        
        time.sleep(0.5)  
        
        return UserProfile(
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            marital_status=marital_status,
            education=education,
            job=job,
            location=location,
            top_interests=top_interests,
            personality_summary=personality_summary,
            key_activities=key_activities,
            total_posts=len(posts),
            top_habits=top_habits if top_habits else ["none"],
            top_hobby=top_hobby if top_hobby else "none",
            travel_frequency=travel_frequency,
            life_indicators=life_indicators,
            spending_indicators=spending_indicators
        )
    
    def analyze_all_users(self, file_path: str) -> List[UserProfile]:
        """Analyze all users and return their complete profiles"""
        users = self.load_users_from_file(file_path)
        profiles = []
        
        for i, user in enumerate(users):
            print(f"Processing user {i+1}/{len(users)}")
            profile = self.analyze_user_profile(user)
            profiles.append(profile)
        
        return profiles
    
    def print_user_profile(self, profile: UserProfile):
        """Print a single user's profile in a formatted way"""
        print("=" * 80)
        print(f" USER PROFILE: {profile.first_name} {profile.last_name}")
        print("=" * 80)
        
        
        print(" BASIC INFORMATION:")
        print(f"   • First Name: {profile.first_name}")
        print(f"   • Last Name: {profile.last_name}")
        print(f"   • Age: {profile.age}")
        print(f"   • Gender: {profile.gender}")
        print(f"   • Marital Status: {profile.marital_status}")
        print(f"   • Education: {profile.education}")
        print(f"   • Job: {profile.job}")
        print(f"   • Location: {profile.location}")
        
        
        print("\n INTERESTS:")
        for interest in profile.top_interests:
            print(f"   • {interest['interest']}: {interest['percentage']}%")
        

        print("\n HABITS & HOBBIES:")
        print(f"   • Top 2 Habits: {', '.join(profile.top_habits)}")
        print(f"   • Top Hobby: {profile.top_hobby}")
        
        
        print("\n TRAVEL INDICATORS:")
        for indicator in profile.travel_frequency:
            print(f"   • {indicator}")
        
        
        print("\n LIFE INDICATORS:")
        for indicator in profile.life_indicators:
            print(f"   • {indicator}")
        
        print("\n SPENDING INDICATORS:")
        for indicator in profile.spending_indicators:
            print(f"   • {indicator}")
        
    
        print(f"\n PERSONALITY SUMMARY:")
        print(f"   {profile.personality_summary}")
        
        
        print(f"\n KEY ACTIVITIES FROM POSTS:")
        for i, activity in enumerate(profile.key_activities, 1):
            print(f"   {i}. {activity}")
        
        print(f"\n TOTAL POSTS ANALYZED: {profile.total_posts}")
        print("\n")
    
    def print_all_profiles(self, profiles: List[UserProfile]):
        """Print all user profiles"""
        for profile in profiles:
            self.print_user_profile(profile)
    
    def save_results(self, profiles: List[UserProfile], output_file: str):
        """Save results to JSON file"""
        profiles_dict = []
        for profile in profiles:
            profile_dict = {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'age': profile.age,
                'gender': profile.gender,
                'marital_status': profile.marital_status,
                'education': profile.education,
                'job': profile.job,
                'location': profile.location,
                'top_interests': profile.top_interests,
                'personality_summary': profile.personality_summary,
                'key_activities': profile.key_activities,
                'total_posts': profile.total_posts,
                'top_habits': profile.top_habits,
                'top_hobby': profile.top_hobby,
                'travel_indicators': profile.travel_frequency,
                'life_indicators': profile.life_indicators,
                'spending_indicators': profile.spending_indicators
            }
            profiles_dict.append(profile_dict)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(profiles_dict, f, indent=2, ensure_ascii=False)

def main():
    try:
        analyzer = LLMUserProfileAnalyzer(api_key='')
        file_path = "dummy_users.json"
        
        users = analyzer.load_users_from_file(file_path)
        profiles = []
        for user in users[18:19]:
            profiles.append(analyzer.analyze_user_profile(user))
        
        analyzer.print_all_profiles(profiles)
        output_file = "llm_user_profiles_analysis.json"
        analyzer.save_results(profiles, output_file)
        print(f" Results saved to: {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
