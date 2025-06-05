import streamlit as st
import sqlite3
from datetime import datetime
import uuid
import hashlib
import json
import base64
from PIL import Image
import io

# ---------------------------------------
# Helper Functions
# ---------------------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

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

def has_parental_controls():
    user = st.session_state.get('current_user')
    return user and (user.get('parental_controls', False) or user['age'] < 13)

# ---------------------------------------
# Streamlit Page Configuration & CSS
# ---------------------------------------
st.set_page_config(
    page_title="Together - Family Social App",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; color: #262626; }
    .app-container { max-width: 500px; margin: 0 auto; background: #fff; min-height: 100vh; padding-bottom: 80px; }
    .header { background: white; padding: 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e0e0e0; }
    .logo { font-size: 28px; font-weight: bold; color: #262626; }
    .user-info { display: flex; align-items: center; gap: 12px; }
    .user-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 2px solid #e1306c; }
    .bottom-nav { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 500px; background: #fff; border-top: 1px solid #dbdbdb; display: flex; justify-content: space-around; padding: 10px 0; box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05); }
    .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 12px; text-decoration: none; color: #262626; transition: all 0.2s ease; padding: 5px; border-radius: 8px; }
    .nav-item:hover { background-color: #f2f2f2; }
    .nav-item svg { font-size: 22px; margin-bottom: 4px; color: #262626; }
    .nav-item.active { color: #e1306c; background-color: #fce4ec; }
    .nav-label { font-weight: 500; font-size: 10px; }
    .stories-container { display: flex; overflow-x: auto; padding: 10px 0; border-bottom: 1px solid #f1f1f1; background-color: #fff; }
    .story-item { text-align: center; margin: 0 8px; }
    .story-avatar { width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 2px solid #e1306c; }
    .story-username { font-size: 11px; margin-top: 4px; color: #555; max-width: 60px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .post { border-bottom: 1px solid #efefef; padding: 16px; background: #fff; }
    .post-header { display: flex; align-items: center; gap: 10px; }
    .post-avatar { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
    .post-username { font-weight: 600; }
    .post-location, .post-timestamp { font-size: 11px; color: #8e8e8e; }
    .post-content { margin-top: 8px; font-size: 14px; }
    .post-actions { display: flex; gap: 12px; margin-top: 12px; font-size: 20px; }
    .profile-header { text-align: center; padding: 20px; background: #fff; }
    .profile-avatar { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 3px solid #e1306c; margin-bottom: 10px; }
    .profile-name { font-size: 18px; font-weight: bold; }
    .profile-username, .profile-bio, .profile-stats { font-size: 13px; color: #555; margin-top: 4px; }
    .profile-stats { display: flex; justify-content: center; gap: 12px; margin-top: 10px; }
    .form-container { background: #fff; padding: 16px; margin: 12px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
    .form-title { font-size: 18px; font-weight: 600; margin-bottom: 10px; color: #262626; }
    .kids-mode { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .kids-mode .header, .kids-mode .bottom-nav { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); }
    .kids-mode .logo { color: white; background: none; -webkit-text-fill-color: white; }
    .kids-mode .post, .kids-mode .form-container { background: rgba(255,255,255,0.95); border-radius: 20px; margin: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
    .parental-controls { background: linear-gradient(45deg, #ff6b6b, #feca57); color: white; padding: 12px 16px; margin: 16px; border-radius: 12px; text-align: center; font-weight: 600; }
    header[data-testid="stHeader"], div[data-testid="stSidebar"] { display: none; }
    .stTextInput input, .stTextArea textarea, .stSelectbox select { border: 1px solid #dbdbdb !important; border-radius: 8px !important; padding: 14px !important; font-size: 15px !important; }
    .stButton button { background: linear-gradient(45deg, #405de6, #833ab4) !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 14px 24px !important; font-weight: 600 !important; width: 100% !important; font-size: 15px !important; transition: all 0.2s ease !important; }
    .stButton button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 15px rgba(64, 93, 230, 0.3) !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# Database Setup
# ---------------------------------------
conn = sqlite3.connect("together_app.db", check_same_thread=False)
c = conn.cursor()

# Create tables (families, users w/ password hash, posts, likes, comments, moods, journals, books, reviews, achievements, chores, alerts, learning, locations, safe_sites)
c.execute("""CREATE TABLE IF NOT EXISTS families (
    id TEXT PRIMARY KEY,
    name TEXT,
    invite_code TEXT UNIQUE,
    created_by TEXT,
    password_hash TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT,
    username TEXT UNIQUE,
    age INTEGER,
    password_hash TEXT,
    avatar TEXT,
    role TEXT,
    bio TEXT,
    family_code TEXT,
    parental_controls BOOLEAN DEFAULT 0,
    linked_parent TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    avatar TEXT,
    username TEXT,
    content TEXT,
    image TEXT,
    location TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS post_likes (
    id TEXT PRIMARY KEY,
    post_id TEXT,
    user_id TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS post_comments (
    id TEXT PRIMARY KEY,
    post_id TEXT,
    user_id TEXT,
    comment TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    sender TEXT,
    recipient TEXT,
    message TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS moods (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    username TEXT,
    mood TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS journals (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    content TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    title TEXT,
    author TEXT,
    url TEXT,
    added_by TEXT,
    age_group TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS book_reviews (
    id TEXT PRIMARY KEY,
    book_id TEXT,
    reviewer TEXT,
    rating INTEGER,
    review TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS achievements (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    username TEXT,
    title TEXT,
    description TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS chores (
    id TEXT PRIMARY KEY,
    task TEXT,
    assigned_to TEXT,
    reward INTEGER,
    status TEXT,
    added_by TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    sender TEXT,
    message TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS learning (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    topic TEXT,
    score TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    username TEXT,
    location_name TEXT,
    latitude REAL,
    longitude REAL,
    notes TEXT,
    timestamp TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS safe_sites (
    id TEXT PRIMARY KEY,
    name TEXT,
    url TEXT,
    description TEXT,
    approved_by TEXT,
    timestamp TEXT
)""")
conn.commit()

# Insert default safe sites
default_sites = [
    ("National Geographic Kids", "https://kids.nationalgeographic.com", "Learn about animals and nature", "system"),
    ("NASA Kids", "https://www.nasa.gov/audience/forkids/", "Space exploration for kids", "system"),
    ("Smithsonian for Kids", "https://www.si.edu/kids", "Museums and learning", "system"),
    ("Fun Brain", "https://www.funbrain.com", "Educational games and books", "system"),
    ("Scratch Programming", "https://scratch.mit.edu", "Learn to code with Scratch", "system"),
    ("Khan Academy Kids", "https://www.khanacademy.org/kids", "Educational videos and exercises", "system")
]
for site in default_sites:
    c.execute(
        "INSERT OR IGNORE INTO safe_sites VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), site[0], site[1], site[2], site[3], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
conn.commit()

# ---------------------------------------
# Session State Initialization
# ---------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = "Feed"
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'family_code' not in st.session_state:
    st.session_state.family_code = None
if 'auth_step' not in st.session_state:
    st.session_state.auth_step = "welcome"

# Apply kids mode styling if needed
if has_parental_controls():
    st.markdown('<div class="kids-mode">', unsafe_allow_html=True)

# ---------------------------------------
# Welcome / Authentication Flow
# ---------------------------------------
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
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Start Your Family Journey", key="welcome_btn", use_container_width=True):
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
            """, unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["Create Family", "Join Family", "Sign In"])

            # -------- Create Family --------
            with tab1:
                st.markdown("### Start Your Family")
                with st.form("create_family_form", clear_on_submit=True):
                    family_name = st.text_input("Family Name", placeholder="The Smith Family")
                    creator_name = st.text_input("Your Full Name", placeholder="John Smith")
                    creator_username = st.text_input("Choose Username", placeholder="johnsmith")
                    creator_age = st.number_input("Your Age", min_value=1, max_value=100, value=30)
                    creator_bio = st.text_area("About You (Optional)", placeholder="Tell your family about yourself...")
                    creator_password = st.text_input("Create Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    uploaded_file = st.file_uploader("Upload Profile Picture (Optional)", type=['png', 'jpg', 'jpeg'])
                    avatar_url = process_uploaded_image(uploaded_file)
                    if not avatar_url:
                        avatar_options = [
                            "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face"
                        ]
                        avatar_url = st.selectbox("Or Choose Default Avatar", avatar_options)

                    if st.form_submit_button("Create Family", use_container_width=True):
                        if not (family_name and creator_name and creator_username and creator_password and confirm_password):
                            st.error("Please fill in all required fields")
                        elif creator_password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            # Generate IDs and hashes
                            family_id = str(uuid.uuid4())
                            invite_code = str(uuid.uuid4())[:8].upper()
                            user_id = str(uuid.uuid4())
                            role = "parent" if creator_age >= 18 else "child"
                            parental_controls = creator_age < 13
                            family_pw_hash = hash_password(creator_password)
                            user_pw_hash = family_pw_hash  # same password for family admin

                            try:
                                # Insert into families
                                c.execute(
                                    "INSERT INTO families VALUES (?, ?, ?, ?, ?, ?)",
                                    (family_id, family_name, invite_code, creator_username, family_pw_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                )
                                # Insert into users
                                c.execute(
                                    "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    (user_id, creator_name, creator_username, creator_age, user_pw_hash, avatar_url, role, creator_bio, invite_code, parental_controls, None)
                                )
                                conn.commit()
                                # Set session
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
                                st.success(f"Family '{family_name}' created! Invite code: {invite_code}")
                                if st.button("Enter Your Family App", use_container_width=True):
                                    st.session_state.page = "Feed"
                                    st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("Username already exists. Please choose a different one.")

            # -------- Join Family --------
            with tab2:
                st.markdown("### Join Your Family")
                with st.form("join_family_form", clear_on_submit=True):
                    invite_code = st.text_input("Family Invite Code", placeholder="Enter 8-character code")
                    joiner_name = st.text_input("Your Full Name", placeholder="Jane Smith")
                    joiner_username = st.text_input("Choose Username", placeholder="janesmith")
                    joiner_age = st.number_input("Your Age", min_value=1, max_value=100, value=25)
                    joiner_bio = st.text_area("About You (Optional)", placeholder="Tell your family about yourself...")
                    joiner_password = st.text_input("Create Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    # If under 13, require parent linking
                    linked_parent = None
                    if joiner_age < 13:
                        st.info("Under 13: Must be linked to a parent.")
                        if invite_code:
                            parents = c.execute(
                                "SELECT username FROM users WHERE family_code = ? AND role = 'parent' AND age >= 18",
                                (invite_code,)
                            ).fetchall()
                            if parents:
                                linked_parent = st.selectbox("Select Parent/Guardian", [p[0] for p in parents])
                            else:
                                st.warning("Ask a parent to join first.")
                    uploaded_file = st.file_uploader("Upload Profile Picture (Optional)", type=['png', 'jpg', 'jpeg'], key="join_upload")
                    avatar_url = process_uploaded_image(uploaded_file)
                    if not avatar_url:
                        avatar_options = [
                            "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face"
                        ]
                        avatar_url = st.selectbox("Or Choose Default Avatar", avatar_options)

                    if st.form_submit_button("Join Family", use_container_width=True):
                        if not (invite_code and joiner_name and joiner_username and joiner_password and confirm_password):
                            st.error("Please fill in all required fields")
                        elif joiner_password != confirm_password:
                            st.error("Passwords do not match")
                        elif joiner_age < 13 and not linked_parent:
                            st.error("Under-13 must link to a parent.")
                        else:
                            family = c.execute("SELECT * FROM families WHERE invite_code = ?", (invite_code,)).fetchone()
                            if not family:
                                st.error("Invalid invite code.")
                            else:
                                try:
                                    user_id = str(uuid.uuid4())
                                    role = "parent" if joiner_age >= 18 else "child"
                                    parental_controls = joiner_age < 13
                                    pw_hash = hash_password(joiner_password)
                                    c.execute(
                                        "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                        (user_id, joiner_name, joiner_username, joiner_age, pw_hash, avatar_url, role, joiner_bio, invite_code, parental_controls, linked_parent)
                                    )
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
                                        'parental_controls': parental_controls,
                                        'linked_parent': linked_parent
                                    }
                                    st.session_state.family_code = invite_code
                                    st.success(f"Welcome to the family, {joiner_name}!")
                                    st.session_state.page = "Feed"
                                    st.rerun()
                                except sqlite3.IntegrityError:
                                    st.error("Username already exists. Please choose a different one.")

            # -------- Sign In --------
            with tab3:
                st.markdown("### Sign In")
                with st.form("login_form", clear_on_submit=True):
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Sign In", use_container_width=True):
                        if not (username and password):
                            st.error("Please enter username and password.")
                        else:
                            user = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                            if not user:
                                st.error("User not found.")
                            else:
                                stored_hash = user[4]  # password_hash column
                                if verify_password(password, stored_hash):
                                    st.session_state.current_user = {
                                        'id': user[0],
                                        'name': user[1],
                                        'username': user[2],
                                        'age': user[3],
                                        'avatar': user[5],
                                        'role': user[6],
                                        'bio': user[7],
                                        'family_code': user[8],
                                        'parental_controls': bool(user[9]),
                                        'linked_parent': user[10]
                                    }
                                    st.session_state.family_code = user[8]
                                    st.success("Sign in successful!")
                                    st.session_state.page = "Feed"
                                    st.rerun()
                                else:
                                    st.error("Incorrect password.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

# ---------------------------------------
# Main App Container
# ---------------------------------------
st.markdown('<div class="app-container">', unsafe_allow_html=True)
user = st.session_state.get("current_user")
if user and user.get('avatar'):
    st.markdown(f'<div class="header"><div class="logo">Together</div><div class="user-info"><img src="{user["avatar"]}" class="user-avatar"><div style="font-weight:600;">{user["username"]}</div></div></div>', unsafe_allow_html=True)
else:
    st.warning("User not logged in.")

# Parental controls indicator
if has_parental_controls():
    st.markdown('<div class="parental-controls">🛡️ Parental Controls Active</div>', unsafe_allow_html=True)

# Navigation
nav_items = [("Feed", "🏠"), ("Chores", "✅"), ("Mood", "😊"), ("Family", "👨‍👩‍👧‍👦")]
if has_parental_controls():
    nav_items.insert(1, ("Learning", "🧠"))
    nav_items.insert(2, ("Browser", "🌐"))

# Update page from URL query param if present
query_params = st.experimental_get_query_params()
if 'page' in query_params:
    st.session_state.page = query_params['page'][0]

# Render navigation bar
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

# ---------------------------------------
# Page Content
# ---------------------------------------
# --- Feed Page ---
if st.session_state.page == "Feed":
    # Stories Section
    family_users = c.execute(
        "SELECT name, username, avatar FROM users WHERE family_code = ?",
        (st.session_state.family_code,)
    ).fetchall()
    if family_users:
        stories_html = '<div class="stories-container">'
        for udata in family_users:
            stories_html += f'''
                <div class="story-item">
                    <img src="{udata[2]}" class="story-avatar">
                    <div class="story-username">{udata[1]}</div>
                </div>
            '''
        stories_html += '</div>'
        st.markdown(stories_html, unsafe_allow_html=True)

    # Post Creation
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Share a Moment</div>', unsafe_allow_html=True)
    with st.form("create_post_form", clear_on_submit=True):
        post_content = st.text_area("What's happening?", placeholder="Share your day...", height=100)
        post_location = st.text_input("Location (optional)", placeholder="Where are you?")
        if st.form_submit_button("Post", use_container_width=True):
            if post_content:
                post_id = str(uuid.uuid4())
                c.execute(
                    "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (post_id, user['id'], user['avatar'], user['username'], post_content, "", post_location, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Display Posts
    posts = c.execute(
        """
        SELECT p.* FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE u.family_code = ?
        ORDER BY p.timestamp DESC
        """, (st.session_state.family_code,)
    ).fetchall()
    for p in posts:
        like_count = c.execute("SELECT COUNT(*) FROM post_likes WHERE post_id = ?", (p[0],)).fetchone()[0]
        user_liked = bool(c.execute("SELECT COUNT(*) FROM post_likes WHERE post_id = ? AND user_id = ?", (p[0], user['id'])).fetchone()[0])
        st.markdown(f'''
            <div class="post">
                <div class="post-header">
                    <img src="{p[2]}" class="post-avatar">
                    <div>
                        <div class="post-username">{p[3]}</div>
                        {f'<div class="post-location">📍 {p[6]}</div>' if p[6] else ''}
                    </div>
                </div>
                <div class="post-content">{p[4]}</div>
                <div class="post-actions">
                    <span style="cursor: pointer;">{'❤️' if user_liked else '🤍'} {like_count}</span>
                    <span style="cursor: pointer;">💬</span>
                </div>
                <div class="post-timestamp">{p[7]}</div>
            </div>
        ''', unsafe_allow_html=True)
        # Like button functionality
        col1, col2 = st.columns([1, 9])
        with col1:
            if st.button("Unlike" if user_liked else "Like", key=f"like_{p[0]}"):
                if not user_liked:
                    like_id = str(uuid.uuid4())
                    c.execute("INSERT INTO post_likes VALUES (?, ?, ?)", (like_id, p[0], user['id']))
                else:
                    c.execute("DELETE FROM post_likes WHERE post_id = ? AND user_id = ?", (p[0], user['id']))
                conn.commit()
                st.experimental_rerun()

# --- Learning Page (Kids Only) ---
elif st.session_state.page == "Learning" and has_parental_controls():
    st.markdown("""
    <div class="learning-card">
        <h2>Learning Hub</h2>
        <p>Track your learning progress and earn stars!</p>
    </div>
    """, unsafe_allow_html=True)

    # Add learning entry
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">What did you learn today?</div>', unsafe_allow_html=True)
    with st.form("add_learning_form", clear_on_submit=True):
        topic = st.text_input("Learning Topic", placeholder="Math, Reading, Science...")
        score = st.selectbox("How did you do?", ["⭐ Good try!", "⭐⭐ Pretty good!", "⭐⭐⭐ Great job!", "⭐⭐⭐⭐ Amazing!", "⭐⭐⭐⭐⭐ Perfect!"])
        if st.form_submit_button("Save Learning", use_container_width=True):
            if topic:
                learning_id = str(uuid.uuid4())
                c.execute("INSERT INTO learning VALUES (?, ?, ?, ?, ?)", (learning_id, user['id'], topic, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.success("Great job learning! Keep it up!")
                st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Show history
    records = c.execute("SELECT * FROM learning WHERE user_id = ? ORDER BY timestamp DESC", (user['id'],)).fetchall()
    for r in records:
        st.markdown(f'''
            <div class="post">
                <div class="post-header">
                    <img src="{user['avatar']}" class="post-avatar">
                    <div>
                        <div class="post-username">📚 {r[2]}</div>
                        <div class="post-location" style="font-size:14px;">{r[3]}</div>
                    </div>
                </div>
                <div class="post-timestamp">{r[4]}</div>
            </div>
        ''', unsafe_allow_html=True)

# --- Browser Page (Kids Only) ---
elif st.session_state.page == "Browser" and has_parental_controls():
    st.markdown("""
    <div class="browser-container">
        <div class="browser-header">
            <h2>Safe Browser</h2>
            <p>Explore approved websites safely</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    safe_sites = c.execute("SELECT * FROM safe_sites ORDER BY name").fetchall()
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Choose a Site:</div>', unsafe_allow_html=True)
    for site in safe_sites:
        st.markdown(f'''
            <div>
                <strong>{site[1]}</strong><br><span style="color:#555;">{site[3]}</span>
            </div>
        ''', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("Visit", key=f"visit_{site[0]}"):
                st.markdown(f'<iframe src="{site[2]}" width="100%" height="600px" style="border:2px solid #dbdbdb; border-radius:12px;"></iframe>', unsafe_allow_html=True)
    # Parents can add new safe site
    if user['role'] == 'parent':
        st.markdown('<div class="form-title">Add New Safe Site</div>', unsafe_allow_html=True)
        with st.form("add_safe_site_form", clear_on_submit=True):
            site_name = st.text_input("Website Name")
            site_url = st.text_input("Website URL", placeholder="https://...")
            site_desc = st.text_input("Description")
            if st.form_submit_button("Add Site", use_container_width=True):
                if site_name and site_url and site_desc:
                    site_id = str(uuid.uuid4())
                    c.execute("INSERT INTO safe_sites VALUES (?, ?, ?, ?, ?, ?)", (site_id, site_name, site_url, site_desc, user['username'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("Safe site added!")
                    st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- Chores Page ---
elif st.session_state.page == "Chores":
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Family Chores</div>', unsafe_allow_html=True)
    if user['role'] == 'parent':
        with st.form("add_chore_form", clear_on_submit=True):
            task = st.text_input("Chore Description", placeholder="Take out trash...")
            members = c.execute("SELECT username FROM users WHERE family_code = ?", (st.session_state.family_code,)).fetchall()
            assigned_to = st.selectbox("Assign To", [m[0] for m in members])
            reward = st.slider("Reward Stars", 1, 10, 5)
            if st.form_submit_button("Assign Chore", use_container_width=True):
                if task:
                    chore_id = str(uuid.uuid4())
                    c.execute("INSERT INTO chores VALUES (?, ?, ?, ?, ?, ?, ?)", (chore_id, task, assigned_to, reward, "Pending", user['username'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("Chore assigned!")
                    st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Display chores
    chores = c.execute(
        """
        SELECT c.* FROM chores c
        JOIN users u ON c.added_by = u.username
        WHERE u.family_code = ?
        ORDER BY c.timestamp DESC
        """, (st.session_state.family_code,)
    ).fetchall()
    for ch in chores:
        status_color = "#00d851" if ch[4] == "Completed" else "#ed4956"
        is_assigned = (ch[2] == user['username'])
        can_complete = is_assigned or (user['role'] == 'parent')
        st.markdown(f'''
            <div class="post">
                <div class="post-header">
                    <div>
                        <div class="post-username">{ch[1]}</div>
                        <div class="post-location">👤 {ch[2]} • ⭐ {ch[3]} stars</div>
                    </div>
                    <div style="color:{status_color};font-weight:600;">{ch[4]}</div>
                </div>
                <div class="post-timestamp">Added by {ch[5]} • {ch[6]}</div>
            </div>
        ''', unsafe_allow_html=True)
        if ch[4] == "Pending" and can_complete:
            if st.button("Complete", key=f"complete_{ch[0]}"):
                c.execute("UPDATE chores SET status = 'Completed' WHERE id = ?", (ch[0],))
                conn.commit()
                st.success(f"You earned {ch[3]} stars!")
                st.experimental_rerun()

# --- Mood Page ---
elif st.session_state.page == "Mood":
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">How are you feeling?</div>', unsafe_allow_html=True)
    mood_opts = ["😊 Happy", "😐 Okay", "😢 Sad", "😠 Angry", "🤩 Excited", "😴 Tired", "😟 Worried", "🥰 Loved", "😎 Cool", "🤔 Thoughtful"]
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_mood = st.selectbox("Choose Mood", mood_opts)
    with col2:
        if st.button("Share Mood", use_container_width=True):
            mood_id = str(uuid.uuid4())
            c.execute("INSERT INTO moods VALUES (?, ?, ?, ?, ?)", (mood_id, user['id'], user['username'], selected_mood, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            st.success("Mood shared! 💕")
            st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Family Mood Board</div>', unsafe_allow_html=True)
    moods = c.execute(
        """
        SELECT m.username, m.mood, m.timestamp, u.avatar
        FROM moods m
        JOIN users u ON m.user_id = u.id
        WHERE u.family_code = ?
        ORDER BY m.timestamp DESC LIMIT 10
        """, (st.session_state.family_code,)
    ).fetchall()
    for m in moods:
        st.markdown(f'''
            <div class="post">
                <div class="post-header">
                    <img src="{m[3]}" class="post-avatar">
                    <div>
                        <div class="post-username">{m[0]}</div>
                        <div class="post-location">is feeling {m[1]}</div>
                    </div>
                </div>
                <div class="post-timestamp">{m[2]}</div>
            </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Private Journal
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Private Journal</div>', unsafe_allow_html=True)
    journal_entry = st.text_area("Write your private journal entry...", height=150, placeholder="How was your day?")
    if st.button("Save Journal", use_container_width=True) and journal_entry:
        journal_id = str(uuid.uuid4())
        c.execute("INSERT INTO journals VALUES (?, ?, ?, ?)", (journal_id, user['id'], journal_entry, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        st.success("Journal saved privately! 📝")
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- Family Page (Profile, Library, Achievements, Messaging, Emergency, Locations) ---
elif st.session_state.page == "Family":
    # Profile Header
    st.markdown(f'''
    <div class="profile-header">
        <img src="{user['avatar']}" class="profile-avatar">
        <div class="profile-name">{user['name']}</div>
        <div class="profile-username">@{user['username']}</div>
        <div class="profile-bio">{user['bio'] if user['bio'] else "No bio yet"}</div>
        <div class="profile-stats">
            <span>Age: {user['age']}</span>
            <span>Role: {user['role'].title()}</span>
            {f"<span>Linked to: {user['linked_parent']}</span>" if user.get('linked_parent') else ""}
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Update Profile Picture
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Update Profile Picture</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload New Profile Picture", type=['png','jpg','jpeg'], key="profile_upload")
    if uploaded_file:
        new_avatar = process_uploaded_image(uploaded_file)
        if st.button("Update Picture", use_container_width=True):
            c.execute("UPDATE users SET avatar = ? WHERE id = ?", (new_avatar, user['id']))
            c.execute("UPDATE posts SET avatar = ? WHERE user_id = ?", (new_avatar, user['id']))
            conn.commit()
            st.session_state.current_user['avatar'] = new_avatar
            st.success("Profile picture updated! 📸")
            st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Family Members List
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Family Members</div>', unsafe_allow_html=True)
    members = c.execute(
        "SELECT name, username, avatar, age, role, bio FROM users WHERE family_code = ?",
        (st.session_state.family_code,)
    ).fetchall()
    for m in members:
        st.markdown(f'''
            <div class="post">
                <div class="post-header">
                    <img src="{m[2]}" class="post-avatar">
                    <div>
                        <div class="post-username">{m[0]} (@{m[1]})</div>
                        <div class="post-location">Age {m[3]} • {m[4].title()}</div>
                    </div>
                </div>
                {f'<div class="post-content">{m[5]}</div>' if m[5] else ''}
            </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Location Sharing
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Share Location</div>', unsafe_allow_html=True)
    with st.form("share_location_form", clear_on_submit=True):
        loc_name = st.text_input("Location Name", placeholder="Home, School, Park...")
        loc_notes = st.text_area("Notes (Optional)", placeholder="What are you doing here?")
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=40.7128, format="%.4f")
        with col2:
            longitude = st.number_input("Longitude", value=-74.0060, format="%.4f")
        if st.form_submit_button("Share Location", use_container_width=True):
            if loc_name:
                loc_id = str(uuid.uuid4())
                c.execute(
                    "INSERT INTO locations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (loc_id, user['id'], user['username'], loc_name, latitude, longitude, loc_notes, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                st.success("Location shared!")
                st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Display Latest Locations
    locations = c.execute(
        """
        SELECT l.username, l.location_name, l.latitude, l.longitude, l.notes, l.timestamp, u.avatar
        FROM locations l
        JOIN users u ON l.user_id = u.id
        WHERE u.family_code = ?
        ORDER BY l.timestamp DESC LIMIT 10
        """, (st.session_state.family_code,)
    ).fetchall()
    for loc in locations:
        st.markdown(f'''
            <div class="post">
                <div class="post-header">
                    <img src="{loc[6]}" class="post-avatar">
                    <div>
                        <div class="post-username">📍 {loc[1]}</div>
                        <div class="post-location">{loc[0]} • {loc[5]}</div>
                    </div>
                </div>
                <div class="post-content">
                    📌 {loc[2]:.4f}, {loc[3]:.4f}
                    {f'<br>{loc[4]}' if loc[4] else ''}
                </div>
            </div>
        ''', unsafe_allow_html=True)

    # Family Library
    with st.expander("Family Library"):
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">Add a New Book</div>', unsafe_allow_html=True)
        with st.form("add_book_form", clear_on_submit=True):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            url = st.text_input("URL (Optional)")
            age_group = st.selectbox("Appropriate For", ["Kids", "Teens", "Adults", "Everyone"])
            if st.form_submit_button("Add Book", use_container_width=True):
                if title and author:
                    book_id = str(uuid.uuid4())
                    c.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?)", (book_id, title, author, url, user['username'], age_group))
                    conn.commit()
                    st.success("Book added to library!")
                    st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Show books
        books = c.execute("SELECT * FROM books").fetchall()
        for b in books:
            st.markdown(f"### [{b[1]}]({b[3] if b[3] else '#'}) by *{b[2]}* — For: **{b[5]}**")
            avg, cnt = c.execute("SELECT AVG(rating), COUNT(*) FROM book_reviews WHERE book_id = ?", (b[0],)).fetchone()
            if cnt:
                st.markdown(f"⭐ {round(avg,1)} ({cnt} reviews)")
            with st.expander("Leave a Review"):
                rating = st.slider("Your Rating", 1, 5, 5)
                review = st.text_area("Write your review")
                if st.button(f"Submit Review", key=f"review_{b[0]}"):
                    if review:
                        review_id = str(uuid.uuid4())
                        c.execute("INSERT INTO book_reviews VALUES (?, ?, ?, ?, ?, ?)", (review_id, b[0], user['username'], rating, review, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        st.success("Review submitted!")
                        st.experimental_rerun()

            reviews = c.execute("SELECT reviewer, rating, review, timestamp FROM book_reviews WHERE book_id = ? ORDER BY timestamp DESC", (b[0],)).fetchall()
            for r in reviews:
                st.markdown(f"**{r[0]}** rated it ⭐ {r[1]}")
                st.write(r[2])
                st.caption(f"Reviewed on {r[3]}")
            st.markdown("---")

    # Achievements
    with st.expander("Achievements"):
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">Add Achievement</div>', unsafe_allow_html=True)
        with st.form("add_achievement_form", clear_on_submit=True):
            ach_title = st.text_input("Title")
            ach_desc = st.text_area("Description")
            if st.form_submit_button("Add Achievement", use_container_width=True):
                if ach_title and ach_desc:
                    ach_id = str(uuid.uuid4())
                    c.execute("INSERT INTO achievements VALUES (?, ?, ?, ?, ?, ?)", (ach_id, user['id'], user['username'], ach_title, ach_desc, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("Achievement added!")
                    st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Display hall of fame
        achs = c.execute("SELECT user_id, username, title, description, timestamp FROM achievements ORDER BY timestamp DESC").fetchall()
        for a in achs:
            st.markdown(f"**{a[1]}** unlocked *{a[2]}* on {a[4]}<br>{a[3]}", unsafe_allow_html=True)
            st.markdown("---")

    # Messaging
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Send Message</div>', unsafe_allow_html=True)
    with st.form("send_message_form", clear_on_submit=True):
        recipients = [m[1] for m in members if m[1] != user['username']]
        recipient = st.selectbox("Recipient", recipients)
        msg_text = st.text_area("Message")
        if st.form_submit_button("Send", use_container_width=True):
            if recipient and msg_text:
                msg_id = str(uuid.uuid4())
                c.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?)", (msg_id, user['username'], recipient, msg_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.success("Message sent!")
                st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Inbox
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">Inbox</div>', unsafe_allow_html=True)
    inbox = c.execute("SELECT sender, message, timestamp FROM messages WHERE recipient = ? ORDER BY timestamp DESC", (user['username'],)).fetchall()
    for im in inbox:
        st.markdown(f"**{im[0]}** said: {im[1]}<br><small style='color:#8e8e8e;'>{im[2]}</small>", unsafe_allow_html=True)
        st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)

    # Emergency Alerts (Parents only)
    if user['role'] == 'parent':
        with st.expander("Emergency Alerts"):
            st.warning("⚠️ Use only for real emergencies!")
            emergency_msg = st.text_area("Emergency Message")
            if st.button("Send Alert", key="send_alert") and emergency_msg:
                alert_id = str(uuid.uuid4())
                c.execute("INSERT INTO alerts VALUES (?, ?, ?, ?)", (alert_id, user['username'], emergency_msg, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.error("Emergency alert sent!")

        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">Alert Log</div>', unsafe_allow_html=True)
        alerts = c.execute("SELECT sender, message, timestamp FROM alerts ORDER BY timestamp DESC").fetchall()
        for a in alerts:
            st.markdown(f"**{a[0]}** 🚨 {a[1]}<br><small style='color:#8e8e8e;'>{a[2]}</small>", unsafe_allow_html=True)
            st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)

# Close kids-mode container
if has_parental_controls():
    st.markdown('</div>', unsafe_allow_html=True)
# Close main container
st.markdown('</div>', unsafe_allow_html=True)

# Bottom spacing
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
