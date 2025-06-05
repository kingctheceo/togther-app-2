import streamlit as st
import sqlite3
from datetime import datetime
import uuid
import json
import base64
from PIL import Image
import io

# Page config with Instagram-like styling
st.set_page_config(page_title="Together - Family Social App",
                   page_icon="📱",
                   layout="wide",
                   initial_sidebar_state="collapsed")

# Custom CSS for true Instagram-like interface
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main > div {
        padding: 0;
        max-width: 100%;
    }
    
    .block-container {
        padding: 0;
        max-width: 100%;
    }
    
    /* Mobile-first responsive design */
    .app-container {
        max-width: 500px;
        margin: 0 auto;
        background: #fafafa;
        min-height: 100vh;
        padding-bottom: 80px;
    }
    
    /* Welcome screen styles */
    .welcome-screen {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
        padding: 20px;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-screen::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="20" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
        animation: float 20s infinite linear;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    
    .welcome-content {
        z-index: 2;
        position: relative;
    }
    
    .app-logo {
        font-size: 72px;
        font-weight: 800;
        margin-bottom: 24px;
        background: linear-gradient(45deg, #fff, #f8f9fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        letter-spacing: -2px;
    }
    
    .app-tagline {
        font-size: 24px;
        margin-bottom: 16px;
        font-weight: 300;
        opacity: 0.95;
    }
    
    .app-description {
        font-size: 16px;
        margin-bottom: 48px;
        opacity: 0.8;
        max-width: 400px;
        line-height: 1.6;
    }
    
    .cta-button {
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 16px 48px;
        border-radius: 50px;
        font-size: 18px;
        font-weight: 600;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .cta-button:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .auth-container {
        background: white;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
        margin: 20px;
        backdrop-filter: blur(20px);
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 32px;
    }
    
    .auth-title {
        font-size: 28px;
        font-weight: 700;
        color: #262626;
        margin-bottom: 8px;
    }
    
    .auth-subtitle {
        font-size: 16px;
        color: #8e8e8e;
    }
    
    .invite-code-display {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin: 24px 0;
        color: white;
    }
    
    .invite-code {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 4px;
        margin: 8px 0;
    }
    
    /* Instagram-style header */
    .header {
        background: white;
        border-bottom: 1px solid #dbdbdb;
        padding: 16px;
        position: sticky;
        top: 0;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(45deg, #405de6, #833ab4, #e1306c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .user-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #e1306c;
    }
    
    /* Kids mode styling */
    .kids-mode {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .kids-mode .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    
    .kids-mode .logo {
        color: white;
        background: none;
        -webkit-text-fill-color: white;
    }
    
    .kids-mode .post {
        background: rgba(255,255,255,0.95);
        border-radius: 20px;
        margin: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .kids-mode .form-container {
        background: rgba(255,255,255,0.95);
        border-radius: 20px;
        margin: 16px;
    }
    
    /* Stories section */
    .stories-container {
        background: white;
        border-bottom: 1px solid #dbdbdb;
        padding: 16px;
        overflow-x: auto;
        white-space: nowrap;
    }
    
    .story-item {
        display: inline-block;
        text-align: center;
        margin-right: 16px;
        cursor: pointer;
    }
    
    .story-avatar {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        border: 3px solid #e91e63;
        padding: 2px;
        object-fit: cover;
    }
    
    .story-username {
        font-size: 12px;
        margin-top: 4px;
        color: #262626;
        max-width: 70px;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Post styles */
    .post {
        background: white;
        border: 1px solid #dbdbdb;
        margin-bottom: 1px;
    }
    
    .post-header {
        padding: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .post-user-info {
        display: flex;
        align-items: center;
    }
    
    .post-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        margin-right: 12px;
        object-fit: cover;
    }
    
    .post-username {
        font-weight: 600;
        font-size: 15px;
        color: #262626;
    }
    
    .post-location {
        font-size: 11px;
        color: #8e8e8e;
    }
    
    .post-content {
        padding: 0 16px 16px;
        font-size: 15px;
        line-height: 20px;
        color: #262626;
    }
    
    .post-actions {
        padding: 8px 16px;
        display: flex;
        align-items: center;
        gap: 16px;
        border-top: 1px solid #efefef;
    }
    
    .action-btn {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        padding: 8px;
        transition: transform 0.2s ease;
    }
    
    .action-btn:hover {
        transform: scale(1.1);
    }
    
    .post-likes {
        padding: 8px 16px 0;
        font-weight: 600;
        font-size: 14px;
        color: #262626;
    }
    
    .post-timestamp {
        padding: 8px 16px 16px;
        font-size: 11px;
        color: #8e8e8e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Bottom navigation */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 500px;
        background: white;
        border-top: 1px solid #dbdbdb;
        display: flex;
        justify-content: space-around;
        padding: 12px 0 20px;
        z-index: 1000;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    .kids-mode .bottom-nav {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-decoration: none;
        color: #262626;
        font-size: 24px;
        padding: 8px;
        transition: all 0.2s ease;
        border-radius: 12px;
    }
    
    .nav-item:hover {
        background: #f8f9fa;
    }
    
    .nav-item.active {
        color: #e1306c;
        background: #fce4ec;
    }
    
    .nav-label {
        font-size: 11px;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Form styles */
    .form-container {
        background: white;
        padding: 24px;
        margin-bottom: 1px;
    }
    
    .form-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 16px;
        color: #262626;
    }
    
    /* Profile styles */
    .profile-header {
        background: white;
        padding: 32px 24px;
        text-align: center;
    }
    
    .profile-avatar {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        margin: 0 auto 20px;
        object-fit: cover;
        border: 4px solid #e1306c;
    }
    
    .profile-name {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 8px;
        color: #262626;
    }
    
    .profile-username {
        font-size: 18px;
        color: #8e8e8e;
        margin-bottom: 12px;
    }
    
    .profile-bio {
        font-size: 16px;
        color: #262626;
        margin-bottom: 20px;
        line-height: 1.4;
    }
    
    .profile-stats {
        display: flex;
        justify-content: center;
        gap: 24px;
        font-size: 14px;
        color: #8e8e8e;
    }
    
    /* Parental controls indicator */
    .parental-controls {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: white;
        padding: 12px 16px;
        margin: 16px;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
    }
    
    /* Safe browser styles */
    .browser-container {
        background: white;
        margin: 16px;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .browser-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        text-align: center;
    }
    
    .safe-site {
        padding: 16px;
        border-bottom: 1px solid #efefef;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .site-info h4 {
        margin: 0 0 4px 0;
        font-size: 16px;
        font-weight: 600;
    }
    
    .site-info p {
        margin: 0;
        font-size: 14px;
        color: #8e8e8e;
    }
    
    /* Learning hub styles */
    .learning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 20px;
        padding: 24px;
        margin: 16px;
        text-align: center;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .app-container {
            max-width: 100%;
        }
        
        .auth-container {
            margin: 16px;
            padding: 32px 24px;
        }
        
        .app-logo {
            font-size: 60px;
        }
        
        .app-tagline {
            font-size: 20px;
        }
    }
    
    /* Hide streamlit elements */
    .stDeployButton {
        display: none;
    }
    
    header[data-testid="stHeader"] {
        display: none;
    }
    
    div[data-testid="stSidebar"] {
        display: none;
    }
    
    .stMainBlockContainer {
        padding: 0;
    }
    
    /* Streamlit form styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border: 1px solid #dbdbdb !important;
        border-radius: 8px !important;
        padding: 14px !important;
        font-size: 15px !important;
    }
    
    .stButton button {
        background: linear-gradient(45deg, #405de6, #833ab4) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 24px !important;
        font-weight: 600 !important;
        width: 100% !important;
        font-size: 15px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(64, 93, 230, 0.3) !important;
    }
</style>
""",
            unsafe_allow_html=True)

# Database setup with proper schema
conn = sqlite3.connect("together_app.db", check_same_thread=False)
c = conn.cursor()

# Check if users table needs migration
try:
    c.execute("SELECT username FROM users LIMIT 1")
except sqlite3.OperationalError:
    # Table exists but doesn't have username column, need to recreate
    c.execute("DROP TABLE IF EXISTS users")

# Create all tables with proper schema
tables = [
    '''CREATE TABLE IF NOT EXISTS families (
        id TEXT PRIMARY KEY, 
        name TEXT, 
        invite_code TEXT UNIQUE, 
        created_by TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, 
        name TEXT, 
        username TEXT UNIQUE, 
        age INTEGER, 
        avatar TEXT, 
        role TEXT, 
        bio TEXT, 
        family_code TEXT,
        parental_controls BOOLEAN DEFAULT 0,
        linked_parent TEXT
    )''', '''CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        avatar TEXT, 
        username TEXT, 
        content TEXT, 
        image TEXT, 
        location TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS post_likes (
        id TEXT PRIMARY KEY, 
        post_id TEXT, 
        user_id TEXT
    )''', '''CREATE TABLE IF NOT EXISTS post_comments (
        id TEXT PRIMARY KEY, 
        post_id TEXT, 
        user_id TEXT, 
        comment TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY, 
        sender TEXT, 
        recipient TEXT, 
        message TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS moods (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        username TEXT, 
        mood TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS journals (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        content TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS books (
        id TEXT PRIMARY KEY, 
        title TEXT, 
        author TEXT, 
        url TEXT, 
        added_by TEXT, 
        age_group TEXT
    )''', '''CREATE TABLE IF NOT EXISTS book_reviews (
        id TEXT PRIMARY KEY, 
        book_id TEXT, 
        reviewer TEXT, 
        rating INTEGER, 
        review TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS achievements (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        username TEXT, 
        title TEXT, 
        description TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS chores (
        id TEXT PRIMARY KEY, 
        task TEXT, 
        assigned_to TEXT, 
        reward INTEGER, 
        status TEXT, 
        added_by TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY, 
        sender TEXT, 
        message TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS learning (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        topic TEXT, 
        score TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS locations (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        username TEXT, 
        location_name TEXT, 
        latitude REAL, 
        longitude REAL, 
        notes TEXT, 
        timestamp TEXT
    )''', '''CREATE TABLE IF NOT EXISTS safe_sites (
        id TEXT PRIMARY KEY,
        name TEXT,
        url TEXT,
        description TEXT,
        approved_by TEXT,
        timestamp TEXT
    )'''
]

for table in tables:
    c.execute(table)

# Add default safe sites if not exists
default_sites = [
    ("National Geographic Kids", "https://kids.nationalgeographic.com",
     "Learn about animals and nature", "system"),
    ("NASA Kids", "https://www.nasa.gov/audience/forkids/",
     "Space exploration for kids", "system"),
    ("Smithsonian for Kids", "https://www.si.edu/kids", "Museums and learning",
     "system"),
    ("Fun Brain", "https://www.funbrain.com", "Educational games and books",
     "system"),
    ("Scratch Programming", "https://scratch.mit.edu",
     "Learn to code with Scratch", "system"),
    ("Khan Academy Kids", "https://www.khanacademy.org/kids",
     "Educational videos and exercises", "system")
]

for site in default_sites:
    c.execute("INSERT OR IGNORE INTO safe_sites VALUES (?, ?, ?, ?, ?, ?)",
              (str(uuid.uuid4()), site[0], site[1], site[2], site[3],
               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

conn.commit()


# Helper functions
def process_uploaded_image(uploaded_file):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image = image.resize((150, 150), Image.Resampling.LANCZOS)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    return None


def check_login():
    return st.session_state.get('current_user') is not None


def is_child():
    user = st.session_state.get('current_user')
    return user and user['age'] < 13


def has_parental_controls():
    user = st.session_state.get('current_user')
    return user and (user.get('parental_controls', False) or user['age'] < 13)


# Session state initialization
if 'page' not in st.session_state:
    st.session_state.page = "Feed"
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'family_code' not in st.session_state:
    st.session_state.family_code = None
if 'auth_step' not in st.session_state:
    st.session_state.auth_step = "welcome"

# Apply kids mode styling if user has parental controls
if has_parental_controls():
    st.markdown('<div class="kids-mode">', unsafe_allow_html=True)

# Welcome/Login Flow
if not check_login():
    if st.session_state.auth_step == "welcome":
        st.markdown("""
        <div class="welcome-screen">
            <div class="welcome-content">
                <div class="app-logo">Together</div>
                <div class="app-tagline">Where Families Connect</div>
                <div class="app-description">
                    A safe, private social space designed for families to share moments, 
                    stay connected, and grow together with smart parental controls.
                </div>
            </div>
        </div>
        """,
                    unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Your Family Journey",
                         key="welcome_btn",
                         use_container_width=True):
                st.session_state.auth_step = "auth"
                st.rerun()

    elif st.session_state.auth_step == "auth":
        st.markdown('<div class="app-container">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 10, 1])
        with col2:
            st.markdown("""
            <div class="auth-container">
                <div class="auth-header">
                    <div class="auth-title">Welcome to Together</div>
                    <div class="auth-subtitle">Choose how you'd like to join your family</div>
                </div>
            </div>
            """,
                        unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(
                ["🏠 Create Family", "👥 Join Family", "🔑 Sign In"])

            with tab1:
                st.markdown("### Start Your Family")
                with st.form("create_family", clear_on_submit=True):
                    family_name = st.text_input("Family Name",
                                                placeholder="The Smith Family")
                    creator_name = st.text_input("Your Full Name",
                                                 placeholder="John Smith")
                    creator_username = st.text_input("Choose Username",
                                                     placeholder="johnsmith")
                    creator_age = st.number_input("Your Age",
                                                  min_value=1,
                                                  max_value=100,
                                                  value=30)
                    creator_bio = st.text_area(
                        "About You (Optional)",
                        placeholder="Tell your family about yourself...")

                    uploaded_file = st.file_uploader(
                        "Upload Profile Picture", type=['png', 'jpg', 'jpeg'])
                    avatar_url = process_uploaded_image(uploaded_file)

                    if not avatar_url:
                        avatar_options = [
                            "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face"
                        ]
                        avatar_url = st.selectbox("Or Choose Default Avatar",
                                                  avatar_options)

                    if st.form_submit_button("Create Family",
                                             use_container_width=True):
                        if family_name and creator_name and creator_username:
                            try:
                                family_id = str(uuid.uuid4())
                                invite_code = str(uuid.uuid4())[:8].upper()
                                user_id = str(uuid.uuid4())
                                role = "parent" if creator_age >= 18 else "child"
                                parental_controls = creator_age < 13

                                c.execute(
                                    "INSERT INTO families VALUES (?, ?, ?, ?, ?)",
                                    (family_id, family_name, invite_code,
                                     creator_username, datetime.now().strftime(
                                         "%Y-%m-%d %H:%M:%S")))

                                c.execute(
                                    "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    (user_id, creator_name, creator_username,
                                     creator_age, avatar_url, role,
                                     creator_bio, invite_code,
                                     parental_controls, None))

                                conn.commit()

                                st.session_state.current_user = {
                                    'id': user_id,
                                    'name': creator_name,
                                    'username': creator_username,
                                    'age': creator_age,
                                    'avatar': avatar_url,
                                    'role': role,
                                    'bio': creator_bio,
                                    'family_code': invite_code,
                                    'parental_controls': parental_controls,
                                    'linked_parent': None
                                }
                                st.session_state.family_code = invite_code

                                st.markdown(f"""
                                <div class="invite-code-display">
                                    <div style="font-size: 18px; margin-bottom: 12px;">🎉 Family Created Successfully!</div>
                                    <div style="font-size: 16px; margin-bottom: 8px;">Your Family Invite Code:</div>
                                    <div class="invite-code">{invite_code}</div>
                                    <div style="font-size: 14px; margin-top: 12px; opacity: 0.8;">Share this code with family members to invite them!</div>
                                </div>
                                """,
                                            unsafe_allow_html=True)

                                if st.button("Enter Your Family App",
                                             use_container_width=True):
                                    st.rerun()

                            except sqlite3.IntegrityError:
                                st.error(
                                    "Username already exists. Please choose a different one."
                                )
                        else:
                            st.error("Please fill in all required fields")

            with tab2:
                st.markdown("### Join Your Family")
                with st.form("join_family", clear_on_submit=True):
                    invite_code = st.text_input(
                        "Family Invite Code",
                        placeholder="Enter 8-character code")
                    joiner_name = st.text_input("Your Full Name",
                                                placeholder="Jane Smith")
                    joiner_username = st.text_input("Choose Username",
                                                    placeholder="janesmith")
                    joiner_age = st.number_input("Your Age",
                                                 min_value=1,
                                                 max_value=100,
                                                 value=25)
                    joiner_bio = st.text_area(
                        "About You (Optional)",
                        placeholder="Tell your family about yourself...")

                    # If user is under 13, require parent linking
                    linked_parent = None
                    if st.number_input("temp_age",
                                       min_value=1,
                                       max_value=100,
                                       value=joiner_age,
                                       key="temp_age_check") < 13:
                        st.info(
                            "👨‍👩‍👧 Since you're under 13, you'll need to be linked to a parent account for safety."
                        )
                        family_parents = []
                        if invite_code:
                            family_parents = c.execute(
                                """
                                SELECT username FROM users 
                                WHERE family_code = ? AND role = 'parent' AND age >= 18
                            """, (invite_code, )).fetchall()

                        if family_parents:
                            linked_parent = st.selectbox(
                                "Select Your Parent/Guardian",
                                [p[0] for p in family_parents])
                        else:
                            st.warning(
                                "Please ask a parent to create the family first, then try joining."
                            )

                    uploaded_file = st.file_uploader(
                        "Upload Profile Picture",
                        type=['png', 'jpg', 'jpeg'],
                        key="join_upload")
                    avatar_url = process_uploaded_image(uploaded_file)

                    if not avatar_url:
                        avatar_options = [
                            "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face"
                        ]
                        avatar_url = st.selectbox("Or Choose Default Avatar",
                                                  avatar_options)

                    if st.form_submit_button("Join Family",
                                             use_container_width=True):
                        if invite_code and joiner_name and joiner_username:
                            if joiner_age < 13 and not linked_parent:
                                st.error(
                                    "Children under 13 must be linked to a parent account."
                                )
                            else:
                                try:
                                    family = c.execute(
                                        "SELECT * FROM families WHERE invite_code = ?",
                                        (invite_code, )).fetchone()
                                    if family:
                                        user_id = str(uuid.uuid4())
                                        role = "parent" if joiner_age >= 18 else "child"
                                        parental_controls = joiner_age < 13

                                        c.execute(
                                            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                            (user_id, joiner_name,
                                             joiner_username, joiner_age,
                                             avatar_url, role, joiner_bio,
                                             invite_code, parental_controls,
                                             linked_parent))
                                        conn.commit()

                                        st.session_state.current_user = {
                                            'id': user_id,
                                            'name': joiner_name,
                                            'username': joiner_username,
                                            'age': joiner_age,
                                            'avatar': avatar_url,
                                            'role': role,
                                            'bio': joiner_bio,
                                            'family_code': invite_code,
                                            'parental_controls':
                                            parental_controls,
                                            'linked_parent': linked_parent
                                        }
                                        st.session_state.family_code = invite_code

                                        st.success(
                                            f"Welcome to the {family[1]} family! 🎉"
                                        )
                                        st.rerun()
                                    else:
                                        st.error(
                                            "Invalid invite code. Please check and try again."
                                        )
                                except sqlite3.IntegrityError:
                                    st.error(
                                        "Username already exists. Please choose a different one."
                                    )
                        else:
                            st.error("Please fill in all required fields")

            with tab3:
                st.markdown("### Welcome Back")
                with st.form("login", clear_on_submit=True):
                    username = st.text_input("Username",
                                             placeholder="Enter your username")

                    if st.form_submit_button("Sign In",
                                             use_container_width=True):
                        if username:
                            user = c.execute(
                                "SELECT * FROM users WHERE username = ?",
                                (username, )).fetchone()
                            if user:
                                st.session_state.current_user = {
                                    'id':
                                    user[0],
                                    'name':
                                    user[1],
                                    'username':
                                    user[2],
                                    'age':
                                    user[3],
                                    'avatar':
                                    user[4],
                                    'role':
                                    user[5],
                                    'bio':
                                    user[6],
                                    'family_code':
                                    user[7],
                                    'parental_controls':
                                    bool(user[8])
                                    if len(user) > 8 else user[3] < 13,
                                    'linked_parent':
                                    user[9] if len(user) > 9 else None
                                }
                                st.session_state.family_code = user[7]
                                st.rerun()
                            else:
                                st.error(
                                    "User not found. Please check your username or create a new account."
                                )
                        else:
                            st.error("Please enter your username")

        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

# Main app container
st.markdown('<div class="app-container">', unsafe_allow_html=True)

# Header
user = st.session_state.get("current_user")
if user:
    st.markdown(f"""
    <div class="header">
        <div class="logo">Together</div>
        <div class="user-info">
            <img src="{user['avatar']}" class="user-avatar">
            <div>
                <div style="font-weight: 600; font-size: 16px;">{user['username']}</div>
                <div style="font-size: 12px; color: #8e8e8e;">{user['role'].title()}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("User not logged in.")

# Parental controls indicator for children
if has_parental_controls():
    st.markdown("""
    <div class="parental-controls">
        🛡️ Parental Controls Active - Safe & Secure Experience
    </div>
    """,
                unsafe_allow_html=True)

# Bottom Navigation - Everyone gets the same features, but with different access levels
nav_items = [("Feed", "🏠"), ("Chores", "✅"), ("Mood", "😊"),
             ("Family", "👨‍👩‍👧‍👦")]

# Add Learning and Browser for users with parental controls (kids)
if has_parental_controls():
    nav_items.insert(1, ("Learning", "🧠"))
    nav_items.insert(2, ("Browser", "🌐"))

# Get navigation from URL
query_params = st.query_params
if 'page' in query_params:
    st.session_state.page = query_params['page']

nav_html = '<div class="bottom-nav">'
for page, icon in nav_items:
    active_class = "active" if st.session_state.page == page else ""
    nav_html += f'''
    <a href="?page={page}" class="nav-item {active_class}">
        <div>{icon}</div>
        <div class="nav-label">{page}</div>
    </a>
    '''
nav_html += '</div>'
st.markdown(nav_html, unsafe_allow_html=True)

# Page Content
if st.session_state.page == "Feed":
    # Stories Section
    family_users = c.execute(
        "SELECT name, username, avatar FROM users WHERE family_code = ?",
        (st.session_state.family_code, )).fetchall()

    if family_users:
        stories_html = '<div class="stories-container">'
        for user_data in family_users:
            stories_html += f'''
            <div class="story-item">
                <img src="{user_data[2]}" class="story-avatar">
                <div class="story-username">{user_data[1]}</div>
            </div>
            '''
        stories_html += '</div>'
        st.markdown(stories_html, unsafe_allow_html=True)

    # Create Post
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown(
        '<div class="form-title">Share a moment with your family</div>',
        unsafe_allow_html=True)

    with st.form("create_post", clear_on_submit=True):
        post_content = st.text_area(
            "What's happening?",
            placeholder="Share your day with the family...",
            height=100)
        post_location = st.text_input("Location (optional)",
                                      placeholder="Where are you?")

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.form_submit_button("Share", use_container_width=True):
                if post_content:
                    post_id = str(uuid.uuid4())
                    c.execute(
                        "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (post_id, user['id'], user['avatar'],
                         user['username'], post_content, "", post_location,
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Display Posts
    posts = c.execute(
        """
        SELECT p.* FROM posts p 
        JOIN users u ON p.user_id = u.id 
        WHERE u.family_code = ? 
        ORDER BY p.timestamp DESC
    """, (st.session_state.family_code, )).fetchall()

    for post in posts:
        like_count = c.execute(
            "SELECT COUNT(*) FROM post_likes WHERE post_id = ?",
            (post[0], )).fetchone()[0]
        user_liked = c.execute(
            "SELECT COUNT(*) FROM post_likes WHERE post_id = ? AND user_id = ?",
            (post[0], user['id'])).fetchone()[0] > 0

        st.markdown(f'''
        <div class="post">
            <div class="post-header">
                <div class="post-user-info">
                    <img src="{post[2]}" class="post-avatar">
                    <div>
                        <div class="post-username">{post[3]}</div>
                        {f'<div class="post-location">📍 {post[6]}</div>' if post[6] else ''}
                    </div>
                </div>
            </div>
            <div class="post-content">{post[4]}</div>
            <div class="post-actions">
                <span style="color: {'#ed4956' if user_liked else '#262626'}">
                    {'❤️' if user_liked else '🤍'}
                </span>
                <span>💬</span>
                <span>📤</span>
            </div>
            {f'<div class="post-likes">{like_count} likes</div>' if like_count > 0 else ''}
            <div class="post-timestamp">{post[7]}</div>
        </div>
        ''',
                    unsafe_allow_html=True)

        # Like functionality
        col1, col2, col3, col4 = st.columns([1, 1, 1, 5])
        with col1:
            if st.button("❤️" if not user_liked else "💔",
                         key=f"like_{post[0]}"):
                if not user_liked:
                    like_id = str(uuid.uuid4())
                    c.execute("INSERT INTO post_likes VALUES (?, ?, ?)",
                              (like_id, post[0], user['id']))
                else:
                    c.execute(
                        "DELETE FROM post_likes WHERE post_id = ? AND user_id = ?",
                        (post[0], user['id']))
                conn.commit()
                st.rerun()

elif st.session_state.page == "Learning":
    st.markdown("""
    <div class="learning-card">
        <h2>🧠 Learning Hub</h2>
        <p>Track your learning progress and earn stars!</p>
    </div>
    """,
                unsafe_allow_html=True)

    # Add learning activity
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">What did you learn today?</div>',
                unsafe_allow_html=True)

    with st.form("add_learning"):
        topic = st.text_input("Learning Topic",
                              placeholder="Math, Reading, Science, Art...")
        score = st.selectbox("How did you do?", [
            "⭐ Good try!", "⭐⭐ Pretty good!", "⭐⭐⭐ Great job!",
            "⭐⭐⭐⭐ Amazing!", "⭐⭐⭐⭐⭐ Perfect!"
        ])

        if st.form_submit_button("Save Learning Progress",
                                 use_container_width=True):
            if topic:
                learning_id = str(uuid.uuid4())
                c.execute("INSERT INTO learning VALUES (?, ?, ?, ?, ?)",
                          (learning_id, user['id'], topic, score,
                           datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.success("🎉 Great job learning! Keep it up!")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Display learning history
    learning_records = c.execute(
        "SELECT * FROM learning WHERE user_id = ? ORDER BY timestamp DESC",
        (user['id'], )).fetchall()

    for record in learning_records:
        st.markdown(f'''
        <div class="post">
            <div class="post-header">
                <div class="post-user-info">
                    <img src="{user['avatar']}" class="post-avatar">
                    <div>
                        <div class="post-username">📚 {record[2]}</div>
                        <div class="post-location" style="font-size: 18px;">{record[3]}</div>
                    </div>
                </div>
            </div>
            <div class="post-timestamp">{record[4]}</div>
        </div>
        ''',
                    unsafe_allow_html=True)

elif st.session_state.page == "Browser":
    st.markdown("""
    <div class="browser-container">
        <div class="browser-header">
            <h2>🌐 Safe Family Browser</h2>
            <p>Explore approved websites safely with parental controls</p>
        </div>
    </div>
    """,
                unsafe_allow_html=True)

    # Get approved safe sites
    safe_sites = c.execute("SELECT * FROM safe_sites ORDER BY name").fetchall()

    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Choose a website to visit:</div>',
                unsafe_allow_html=True)

    for site in safe_sites:
        st.markdown(f'''
        <div class="safe-site">
            <div class="site-info">
                <h4>{site[1]}</h4>
                <p>{site[3]}</p>
            </div>
        </div>
        ''',
                    unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("Visit", key=f"visit_{site[0]}"):
                st.markdown(f'''
                <iframe src="{site[2]}" width="100%" height="600" 
                        style="border: 2px solid #dbdbdb; border-radius: 12px; margin-top: 16px;">
                </iframe>
                ''',
                            unsafe_allow_html=True)

    # Allow parents to add new safe sites
    if user['role'] == 'parent':
        st.markdown(
            '<div class="form-title">Add New Safe Site (Parents Only)</div>',
            unsafe_allow_html=True)
        with st.form("add_safe_site"):
            site_name = st.text_input("Website Name")
            site_url = st.text_input("Website URL", placeholder="https://...")
            site_description = st.text_input("Description")

            if st.form_submit_button("Add Safe Site"):
                if site_name and site_url and site_description:
                    site_id = str(uuid.uuid4())
                    c.execute(
                        "INSERT INTO safe_sites VALUES (?, ?, ?, ?, ?, ?)",
                        (site_id, site_name,
                         site_url, site_description, user['username'],
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("Safe site added!")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Chores":
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">✅ Family Chores</div>',
                unsafe_allow_html=True)

    # Parents can add chores, everyone can see them
    if user['role'] == 'parent':
        with st.form("add_chore"):
            task = st.text_input("Chore Description",
                                 placeholder="Take out trash, clean room...")
            family_members = c.execute(
                "SELECT username FROM users WHERE family_code = ?",
                (st.session_state.family_code, )).fetchall()
            assigned_to = st.selectbox(
                "Assign To", [member[0] for member in family_members])
            reward = st.slider("Reward Stars", 1, 10, 5)

            if st.form_submit_button("Add Chore", use_container_width=True):
                if task:
                    chore_id = str(uuid.uuid4())
                    c.execute(
                        "INSERT INTO chores VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (chore_id, task,
                         assigned_to, reward, "Pending", user['username'],
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("Chore assigned! 🎯")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Display chores
    chores = c.execute(
        """
        SELECT c.* FROM chores c 
        JOIN users u ON c.added_by = u.username 
        WHERE u.family_code = ? 
        ORDER BY c.timestamp DESC
    """, (st.session_state.family_code, )).fetchall()

    for chore in chores:
        status_color = "#00d851" if chore[4] == "Completed" else "#ed4956"
        is_assigned_to_user = chore[2] == user['username']
        can_complete = is_assigned_to_user or user['role'] == 'parent'

        st.markdown(f'''
        <div class="post">
            <div class="post-header">
                <div class="post-user-info">
                    <div>
                        <div class="post-username">{chore[1]}</div>
                        <div class="post-location">👤 {chore[2]} • ⭐ {chore[3]} stars</div>
                    </div>
                </div>
                <div style="color: {status_color}; font-weight: 600; font-size: 14px;">
                    {chore[4]}
                </div>
            </div>
            <div class="post-timestamp">Added by {chore[5]} • {chore[6]}</div>
        </div>
        ''',
                    unsafe_allow_html=True)

        if chore[4] == "Pending" and can_complete:
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("✅ Complete", key=f"complete_{chore[0]}"):
                    c.execute(
                        "UPDATE chores SET status = 'Completed' WHERE id = ?",
                        (chore[0], ))
                    conn.commit()
                    st.success(f"🎉 Great job! You earned {chore[3]} stars!")
                    st.rerun()

elif st.session_state.page == "Mood":
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">😊 How are you feeling today?</div>',
                unsafe_allow_html=True)

    mood_options = [
        "😊 Happy", "😐 Okay", "😢 Sad", "😠 Angry", "🤩 Excited", "😴 Tired",
        "😟 Worried", "🥰 Loved", "😎 Cool", "🤔 Thoughtful"
    ]

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_mood = st.selectbox("Choose your mood", mood_options)
    with col2:
        if st.button("Share Mood", use_container_width=True):
            mood_id = str(uuid.uuid4())
            c.execute("INSERT INTO moods VALUES (?, ?, ?, ?, ?)",
                      (mood_id, user['id'], user['username'], selected_mood,
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            st.success("Mood shared with your family! 💕")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Family mood board
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Family Mood Board</div>',
                unsafe_allow_html=True)

    moods = c.execute(
        """
        SELECT m.username, m.mood, m.timestamp, u.avatar 
        FROM moods m 
        JOIN users u ON m.user_id = u.id 
        WHERE u.family_code = ? 
        ORDER BY m.timestamp DESC LIMIT 10
    """, (st.session_state.family_code, )).fetchall()

    for mood in moods:
        st.markdown(f'''
        <div class="post">
            <div class="post-header">
                <div class="post-user-info">
                    <img src="{mood[3]}" class="post-avatar">
                    <div>
                        <div class="post-username">{mood[0]}</div>
                        <div class="post-location">is feeling {mood[1]}</div>
                    </div>
                </div>
            </div>
            <div class="post-timestamp">{mood[2]}</div>
        </div>
        ''',
                    unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Private journal (only if not restricted by parental controls or parent allows)
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📓 Private Journal</div>',
                unsafe_allow_html=True)

    journal_entry = st.text_area(
        "Write your thoughts (private)...",
        height=150,
        placeholder="How was your day? What are you thinking about?")
    if st.button("Save Journal Entry",
                 use_container_width=True) and journal_entry:
        journal_id = str(uuid.uuid4())
        c.execute("INSERT INTO journals VALUES (?, ?, ?, ?)",
                  (journal_id, user['id'], journal_entry,
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        st.success("Journal saved privately! 📝")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Family":
    # Profile section
    st.markdown(f'''
    <div class="profile-header">
        <img src="{user['avatar']}" class="profile-avatar">
        <div class="profile-name">{user['name']}</div>
        <div class="profile-username">@{user['username']}</div>
        <div class="profile-bio">{user['bio'] if user['bio'] else 'No bio yet'}</div>
        <div class="profile-stats">
            <span>Age: {user['age']}</span>
            <span>Role: {user['role'].title()}</span>
            {f"<span>Linked to: {user['linked_parent']}</span>" if user.get('linked_parent') else ""}
        </div>
    </div>
    ''',
                unsafe_allow_html=True)

    # Update profile picture
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Update Profile Picture</div>',
                unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload new profile picture",
                                     type=['png', 'jpg', 'jpeg'],
                                     key="profile_update")
    if uploaded_file:
        new_avatar = process_uploaded_image(uploaded_file)
        if st.button("Update Picture", use_container_width=True):
            c.execute("UPDATE users SET avatar = ? WHERE id = ?",
                      (new_avatar, user['id']))
            c.execute("UPDATE posts SET avatar = ? WHERE user_id = ?",
                      (new_avatar, user['id']))
            conn.commit()
            st.session_state.current_user['avatar'] = new_avatar
            st.success("Profile picture updated! 📸")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Family members
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">👨‍👩‍👧‍👦 Family Members</div>',
                unsafe_allow_html=True)
    family_members = c.execute(
        "SELECT name, username, avatar, age, role, bio FROM users WHERE family_code = ?",
        (st.session_state.family_code, )).fetchall()

    for member in family_members:
        st.markdown(f'''
        <div class="post">
            <div class="post-header">
                <div class="post-user-info">
                    <img src="{member[2]}" class="post-avatar">
                    <div>
                        <div class="post-username">{member[0]} (@{member[1]})</div>
                        <div class="post-location">Age {member[3]} • {member[4].title()}</div>
                    </div>
                </div>
            </div>
            {f'<div class="post-content">{member[5]}</div>' if member[5] else ''}
        </div>
        ''',
                    unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Location sharing
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📍 Family Locations</div>',
                unsafe_allow_html=True)

    with st.form("share_location"):
        location_name = st.text_input(
            "Location Name", placeholder="Home, School, Work, Park...")
        location_notes = st.text_area("Notes (optional)",
                                      placeholder="What are you doing here?")

        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude",
                                       value=40.7128,
                                       format="%.4f")
        with col2:
            longitude = st.number_input("Longitude",
                                        value=-74.0060,
                                        format="%.4f")

        if st.form_submit_button("Share Location", use_container_width=True):
            if location_name:
                location_id = str(uuid.uuid4())
                c.execute(
                    "INSERT INTO locations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (location_id, user['id'], user['username'],
                     location_name, latitude, longitude, location_notes,
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.success("Location shared with family! 📍")
                st.rerun()

    # Display family locations
    locations = c.execute(
        """
        SELECT l.username, l.location_name, l.latitude, l.longitude, l.notes, l.timestamp, u.avatar 
        FROM locations l 
        JOIN users u ON l.user_id = u.id 
        WHERE u.family_code = ? 
        ORDER BY l.timestamp DESC LIMIT 10
    """, (st.session_state.family_code, )).fetchall()

    for location in locations:
        st.markdown(f'''
        <div class="post">
            <div class="post-header">
                <div class="post-user-info">
                    <img src="{location[6]}" class="post-avatar">
                    <div>
                        <div class="post-username">📍 {location[1]}</div>
                        <div class="post-location">{location[0]} • {location[5]}</div>
                    </div>
                </div>
            </div>
            <div class="post-content">
                📌 {location[2]:.4f}, {location[3]:.4f}
                {f'<br>{location[4]}' if location[4] else ''}
            </div>
        </div>
        ''',
                    unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Additional features - Available to everyone but some with restrictions
    with st.expander("📚 Family Library"):
        # Anyone can add books, but parents can control access
        with st.form("add_book"):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            url = st.text_input("URL (optional)")
            age_group = st.selectbox("Appropriate For",
                                     ["Kids", "Teens", "Adults", "Everyone"])

            if st.form_submit_button("Add Book"):
                if title and author:
                    book_id = str(uuid.uuid4())
                    c.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?)",
                              (book_id, title, author, url, user['username'],
                               age_group))
                    conn.commit()
                    st.success("Book added to family library! 📚")

    with st.expander("🏆 Achievements"):
        with st.form("add_achievement"):
            title = st.text_input("Achievement Title")
            description = st.text_area("Description")

            if st.form_submit_button("Add Achievement"):
                if title and description:
                    ach_id = str(uuid.uuid4())
                    c.execute(
                        "INSERT INTO achievements VALUES (?, ?, ?, ?, ?, ?)",
                        (ach_id,
                         user['id'], user['username'], title, description,
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("Achievement added! 🏆")

    # Only parents can send emergency alerts
    if user['role'] == 'parent':
        with st.expander("🚨 Emergency Alert (Parents Only)"):
            st.warning("⚠️ Use only for real emergencies!")
            emergency_msg = st.text_area("Emergency Message")
            if st.button("🚨 Send Alert") and emergency_msg:
                alert_id = str(uuid.uuid4())
                c.execute("INSERT INTO alerts VALUES (?, ?, ?, ?)",
                          (alert_id, user['username'], emergency_msg,
                           datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.error("Emergency alert sent to all family members!")

# Close containers
if has_parental_controls():
    st.markdown('</div>', unsafe_allow_html=True)  # Close kids-mode
st.markdown('</div>', unsafe_allow_html=True)  # Close app-container

# Add bottom spacing for navigation
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
# Sign In Flow
    st.markdown("### Welcome Back")
    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">
            <div class="auth-title">Welcome Back!</div>
            <div class="auth-subtitle">Please enter your username to sign in.</div>
        </div>
    </div>
    """,
                unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username",
                                 placeholder="Enter your username",
                                 max_chars=20,
                                 disabled=False)

        if st.form_submit_button("Sign In", use_container_width=True):
            if username:
                user = c.execute("SELECT * FROM users WHERE username = ?",
                                 (username, )).fetchone()
                if user:
                    st.session_state.current_user = {
                        'id':
                        user[0],
                        'name':
                        user[1],
                        'username':
                        user[2],
                        'age':
                        user[3],
                        'avatar':
                        user[4],
                        'role':
                        user[5],
                        'bio':
                        user[6],
                        'family_code':
                        user[7],
                        'parental_controls':
                        bool(user[8]) if len(user) > 8 else user[3] < 13,
                        'linked_parent':
                        user[9] if len(user) > 9 else None
                    }
                    st.success("Successfully signed in! 🎉")
                    st.session_state.page = "Feed"
                    st.rerun()
                else:
                    st.error("User not found. Please check your username.")
            else:
                st.error("Please enter your username.")
