import streamlit as st
import sqlite3
from datetime import datetime
import uuid
import hashlib
import base64
from PIL import Image
import io

# Page config with Instagram-like styling
st.set_page_config(
    page_title="Together - Family Social App",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for true Instagram-like interface
st.markdown("""
<style>
/* Core Layout Styling */
body {
    background: #ffffff;
    font-family: 'Inter', sans-serif;
    color: #262626;
}

.app-container {
    max-width: 500px;
    margin: 0 auto;
    background: #fafafa;
    min-height: 100vh;
    padding-bottom: 80px;
}

/* Feed Header Styling */
.header {
    background: white;
    padding: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e0e0e0;
}

.logo {
    font-size: 28px;
    font-weight: bold;
    color: #262626;
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

/* Bottom Navigation Bar */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 500px;
    background: #fff;
    border-top: 1px solid #dbdbdb;
    display: flex;
    justify-content: space-around;
    padding: 10px 0;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 12px;
    text-decoration: none;
    color: #262626;
    transition: all 0.2s ease;
    padding: 5px;
    border-radius: 8px;
}

.nav-item:hover {
    background-color: #f2f2f2;
}

.nav-item svg {
    font-size: 22px;
    margin-bottom: 4px;
    color: #262626;
}

.nav-item.active {
    color: #e1306c;
    background-color: #fce4ec;
}

.nav-label {
    font-weight: 500;
    font-size: 10px;
}

/* Feed Stories Bar */
.stories-container {
    display: flex;
    overflow-x: auto;
    padding: 10px 0;
    border-bottom: 1px solid #f1f1f1;
    background-color: #fff;
}

.story-item {
    text-align: center;
    margin: 0 8px;
}

.story-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #e1306c;
}

.story-username {
    font-size: 11px;
    margin-top: 4px;
    color: #555;
    max-width: 60px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Feed Post Styling */
.post {
    border-bottom: 1px solid #efefef;
    padding: 16px;
    background: #fff;
}

.post-header {
    display: flex;
    align-items: center;
    gap: 10px;
}

.post-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}

.post-username {
    font-weight: 600;
}

.post-location,
.post-timestamp {
    font-size: 11px;
    color: #8e8e8e;
}

.post-content {
    margin-top: 8px;
    font-size: 14px;
}

.post-actions {
    display: flex;
    gap: 12px;
    margin-top: 12px;
    font-size: 20px;
}

/* Profile Page Styling */
.profile-header {
    text-align: center;
    padding: 20px;
    background: #fff;
}

.profile-avatar {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #e1306c;
    margin-bottom: 10px;
}

.profile-name {
    font-size: 18px;
    font-weight: bold;
}

.profile-username,
.profile-bio,
.profile-stats {
    font-size: 13px;
    color: #555;
    margin-top: 4px;
}

.profile-stats {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 10px;
}

/* Form Styling */
.form-container {
    background: #fff;
    padding: 16px;
    margin: 12px;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}

.form-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
    color: #262626;
}

/* Kids Mode Enhancements */
.kids-mode {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.kids-mode .header,
.kids-mode .bottom-nav {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
}

.kids-mode .logo {
    color: white;
    background: none;
    -webkit-text-fill-color: white;
}

.kids-mode .post,
.kids-mode .form-container {
    background: rgba(255,255,255,0.95);
    border-radius: 20px;
    margin: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# --- Database Setup ---
conn = sqlite3.connect("together_app.db", check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist, including a 'password' column in users
tables = [
    '''CREATE TABLE IF NOT EXISTS families (
        id TEXT PRIMARY KEY, 
        name TEXT, 
        invite_code TEXT UNIQUE, 
        created_by TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, 
        name TEXT, 
        username TEXT UNIQUE, 
        password TEXT, 
        age INTEGER, 
        avatar TEXT, 
        role TEXT, 
        bio TEXT, 
        family_code TEXT,
        parental_controls BOOLEAN DEFAULT 0,
        linked_parent TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        avatar TEXT, 
        username TEXT, 
        content TEXT, 
        image TEXT, 
        location TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS post_likes (
        id TEXT PRIMARY KEY, 
        post_id TEXT, 
        user_id TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS post_comments (
        id TEXT PRIMARY KEY, 
        post_id TEXT, 
        user_id TEXT, 
        comment TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY, 
        sender TEXT, 
        recipient TEXT, 
        message TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS moods (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        username TEXT, 
        mood TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS journals (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        content TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS books (
        id TEXT PRIMARY KEY, 
        title TEXT, 
        author TEXT, 
        url TEXT, 
        added_by TEXT, 
        age_group TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS book_reviews (
        id TEXT PRIMARY KEY, 
        book_id TEXT, 
        reviewer TEXT, 
        rating INTEGER, 
        review TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS achievements (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        username TEXT, 
        title TEXT, 
        description TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS chores (
        id TEXT PRIMARY KEY, 
        task TEXT, 
        assigned_to TEXT, 
        reward INTEGER, 
        status TEXT, 
        added_by TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY, 
        sender TEXT, 
        message TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS learning (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        topic TEXT, 
        score TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS locations (
        id TEXT PRIMARY KEY, 
        user_id TEXT, 
        username TEXT, 
        location_name TEXT, 
        latitude REAL, 
        longitude REAL, 
        notes TEXT, 
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS safe_sites (
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

# Insert default safe sites if not present
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

# --- Helper Functions ---

def process_uploaded_image(uploaded_file):
    """Resize and convert uploaded image to base64-encoded JPEG."""
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

def hash_password(password: str) -> str:
    """Return the SHA-256 hash of the provided password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_login():
    """Return True if a user is logged in (current_user in session state)."""
    return st.session_state.get('current_user') is not None

def is_child():
    """Return True if logged-in user is under 13."""
    user = st.session_state.get('current_user')
    return user and user['age'] < 13

def has_parental_controls():
    """Return True if logged-in user is under 13 or has parental_controls flag."""
    user = st.session_state.get('current_user')
    return user and (user.get('parental_controls', False) or user['age'] < 13)

# --- Session State Initialization ---
if 'page' not in st.session_state:
    st.session_state.page = "Feed"
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'family_code' not in st.session_state:
    st.session_state.family_code = None
if 'auth_step' not in st.session_state:
    st.session_state.auth_step = "welcome"

# If user has parental controls (i.e., is a child), wrap main UI in .kids-mode
if has_parental_controls():
    st.markdown('<div class="kids-mode">', unsafe_allow_html=True)

# --- Welcome / Login Flow ---
if not check_login():
    if st.session_state.auth_step == "welcome":
        # Display Welcome Screen
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

        # Centered Start Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Your Family Journey", key="welcome_btn", use_container_width=True):
                st.session_state.auth_step = "auth"
                st.rerun()

    elif st.session_state.auth_step == "auth":
        # Render Auth Container
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

            # Tabs: Create Family | Join Family | Sign In
            tab1, tab2, tab3 = st.tabs(["🏠 Create Family", "👥 Join Family", "🔑 Sign In"])

            # --- Tab 1: Create Family ---
            with tab1:
                st.markdown("### Start Your Family")
                with st.form("create_family", clear_on_submit=True):
                    family_name = st.text_input("Family Name", placeholder="The Smith Family")
                    creator_name = st.text_input("Your Full Name", placeholder="John Smith")
                    creator_username = st.text_input("Choose Username", placeholder="johnsmith")
                    creator_password = st.text_input("Create Password", type="password")
                    creator_age = st.number_input("Your Age", min_value=1, max_value=100, value=30)
                    creator_bio = st.text_area("About You (Optional)", placeholder="Tell your family about yourself...")

                    uploaded_file = st.file_uploader("Upload Profile Picture", type=['png', 'jpg', 'jpeg'])
                    avatar_url = process_uploaded_image(uploaded_file)
                    if not avatar_url:
                        avatar_options = [
                            "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face"
                        ]
                        avatar_url = st.selectbox("Or Choose Default Avatar", avatar_options)

                    if st.form_submit_button("Create Family", use_container_width=True):
                        if family_name and creator_name and creator_username and creator_password:
                            try:
                                family_id = str(uuid.uuid4())
                                invite_code = str(uuid.uuid4())[:8].upper()
                                user_id = str(uuid.uuid4())
                                role = "parent" if creator_age >= 18 else "child"
                                parental_controls = creator_age < 13
                                hashed_pw = hash_password(creator_password)

                                # Insert family and user into DB
                                c.execute(
                                    "INSERT INTO families VALUES (?, ?, ?, ?, ?)",
                                    (family_id, family_name, invite_code, creator_username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                )
                                c.execute(
                                    "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    (user_id, creator_name, creator_username, hashed_pw, creator_age, avatar_url, role, creator_bio, invite_code, parental_controls, None)
                                )
                                conn.commit()

                                # Update session state
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

                                # Show invite code display
                                st.markdown(f"""
                                <div class="invite-code-display">
                                    <div style="font-size: 18px; margin-bottom: 12px;">🎉 Family Created Successfully!</div>
                                    <div style="font-size: 16px; margin-bottom: 8px;">Your Family Invite Code:</div>
                                    <div class="invite-code">{invite_code}</div>
                                    <div style="font-size: 14px; margin-top: 12px; opacity: 0.8;">Share this code with family members to invite them!</div>
                                </div>
                                """, unsafe_allow_html=True)

                                if st.button("Enter Your Family App", use_container_width=True):
                                    st.rerun()

                            except sqlite3.IntegrityError:
                                st.error("Username already exists. Please choose a different one.")
                        else:
                            st.error("Please fill in all required fields")

            # --- Tab 2: Join Family ---
            with tab2:
                st.markdown("### Join Your Family")
                with st.form("join_family", clear_on_submit=True):
                    invite_code = st.text_input("Family Invite Code", placeholder="Enter 8-character code")
                    joiner_name = st.text_input("Your Full Name", placeholder="Jane Smith")
                    joiner_username = st.text_input("Choose Username", placeholder="janesmith")
                    joiner_password = st.text_input("Create Password", type="password")
                    joiner_age = st.number_input("Your Age", min_value=1, max_value=100, value=25)
                    joiner_bio = st.text_area("About You (Optional)", placeholder="Tell your family about yourself...")

                    linked_parent = None
                    if joiner_age < 13:
                        st.info("👨‍👩‍👧 Since you're under 13, you'll need to be linked to a parent account for safety.")
                        family_parents = []
                        if invite_code:
                            family_parents = c.execute(
                                "SELECT username FROM users WHERE family_code = ? AND role = 'parent' AND age >= 18",
                                (invite_code,)
                            ).fetchall()
                        if family_parents:
                            linked_parent = st.selectbox("Select Your Parent/Guardian", [p[0] for p in family_parents])
                        else:
                            st.warning("Please ask a parent to create the family first, then try joining.")

                    uploaded_file = st.file_uploader("Upload Profile Picture", type=['png', 'jpg', 'jpeg'], key="join_upload")
                    avatar_url = process_uploaded_image(uploaded_file)
                    if not avatar_url:
                        avatar_options = [
                            "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face",
                            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face"
                        ]
                        avatar_url = st.selectbox("Or Choose Default Avatar", avatar_options)

                    if st.form_submit_button("Join Family", use_container_width=True):
                        if invite_code and joiner_name and joiner_username and joiner_password:
                            if joiner_age < 13 and not linked_parent:
                                st.error("Children under 13 must be linked to a parent account.")
                            else:
                                try:
                                    family = c.execute("SELECT * FROM families WHERE invite_code = ?", (invite_code,)).fetchone()
                                    if family:
                                        user_id = str(uuid.uuid4())
                                        role = "parent" if joiner_age >= 18 else "child"
                                        parental_controls = joiner_age < 13
                                        hashed_pw = hash_password(joiner_password)

                                        c.execute(
                                            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                            (user_id, joiner_name, joiner_username, hashed_pw, joiner_age, avatar_url, role, joiner_bio, invite_code, parental_controls, linked_parent)
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

                                        st.success(f"Welcome to the {family[1]} family! 🎉")
                                        st.rerun()
                                    else:
                                        st.error("Invalid invite code. Please check and try again.")
                                except sqlite3.IntegrityError:
                                    st.error("Username already exists. Please choose a different one.")
                        else:
                            st.error("Please fill in all required fields")

            # --- Tab 3: Sign In ---
            with tab3:
                st.markdown("### Welcome Back")
                with st.form("login_form", clear_on_submit=True):
                    login_username = st.text_input("Username", placeholder="Enter your username")
                    login_password = st.text_input("Password", type="password")
                    if st.form_submit_button("Sign In", use_container_width=True):
                        if login_username and login_password:
                            user = c.execute("SELECT * FROM users WHERE username = ?", (login_username,)).fetchone()
                            if user and hash_password(login_password) == user[3]:
                                st.session_state.current_user = {
                                    'id': user[0],
                                    'name': user[1],
                                    'username': user[2],
                                    'age': user[4],
                                    'avatar': user[5],
                                    'role': user[6],
                                    'bio': user[7],
                                    'family_code': user[8],
                                    'parental_controls': bool(user[9]) if len(user) > 9 else user[4] < 13,
                                    'linked_parent': user[10] if len(user) > 10 else None
                                }
                                st.success("Welcome back!")
                                st.session_state.page = "Feed"
                                st.rerun()
                            else:
                                st.error("Invalid username or password.")
                        else:
                            st.warning("Enter both username and password to continue.")

# If logged in, show main app UI
if check_login():
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
        """, unsafe_allow_html=True)

    # Bottom Navigation - Everyone gets the same features, but with different access levels
    nav_items = [("Feed", "🏠"), ("Chores", "✅"), ("Mood", "😊"), ("Family", "👨‍👩‍👧‍👦")]

    # Add Learning and Browser for users with parental controls (kids)
    if has_parental_controls():
        nav_items.insert(1, ("Learning", "🧠"))
        nav_items.insert(2, ("Browser", "🌐"))

    # Get navigation from URL
    query_params = st.experimental_get_query_params()
    if 'page' in query_params:
        st.session_state.page = query_params['page'][0]

    # Render Bottom Navigation
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

    # --- Page Content ---

    # --- PAGE: Feed ---
    if st.session_state.page == "Feed":
        # Stories Section
        family_users = c.execute(
            "SELECT name, username, avatar FROM users WHERE family_code = ?",
            (st.session_state.family_code,)
        ).fetchall()
        if family_users:
            stories_html = '<div class="stories-container">'
            for u in family_users:
                stories_html += f'''
                    <div class="story-item">
                        <img src="{u[2]}" class="story-avatar">
                        <div class="story-username">{u[1]}</div>
                    </div>
                '''
            stories_html += '</div>'
            st.markdown(stories_html, unsafe_allow_html=True)

        # Create Post Form
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">Share a moment with your family</div>', unsafe_allow_html=True)
        with st.form("create_post", clear_on_submit=True):
            post_content = st.text_area("What's happening?", placeholder="Share your day with the family...", height=100)
            post_location = st.text_input("Location (optional)", placeholder="Where are you?")
            if st.form_submit_button("Share", use_container_width=True):
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
            """,
            (st.session_state.family_code,)
        ).fetchall()

        for post in posts:
            like_count = c.execute(
                "SELECT COUNT(*) FROM post_likes WHERE post_id = ?",
                (post[0],)
            ).fetchone()[0]
            user_liked = c.execute(
                "SELECT COUNT(*) FROM post_likes WHERE post_id = ? AND user_id = ?",
                (post[0], user['id'])
            ).fetchone()[0] > 0

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
            ''', unsafe_allow_html=True)

            # Like functionality (buttons below each post)
            col1, col2, col3, col4 = st.columns([1, 1, 1, 5])
            with col1:
                if st.button("❤️" if not user_liked else "💔", key=f"like_{post[0]}"):
                    if not user_liked:
                        like_id = str(uuid.uuid4())
                        c.execute("INSERT INTO post_likes VALUES (?, ?, ?)", (like_id, post[0], user['id']))
                    else:
                        c.execute("DELETE FROM post_likes WHERE post_id = ? AND user_id = ?", (post[0], user['id']))
                    conn.commit()
                    st.experimental_rerun()

    # --- PAGE: Learning (Kids Mode Only) ---
    elif st.session_state.page == "Learning":
        st.markdown("""
        <div class="learning-card">
            <h2>🧠 Learning Hub</h2>
            <p>Track your learning progress and earn stars!</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">What did you learn today?</div>', unsafe_allow_html=True)
        with st.form("add_learning", clear_on_submit=True):
            topic = st.text_input("Learning Topic", placeholder="Math, Reading, Science, Art...")
            score = st.selectbox("How did you do?", [
                "⭐ Good try!", "⭐⭐ Pretty good!", "⭐⭐⭐ Great job!",
                "⭐⭐⭐⭐ Amazing!", "⭐⭐⭐⭐⭐ Perfect!"
            ])
            if st.form_submit_button("Save Learning Progress", use_container_width=True):
                if topic:
                    learning_id = str(uuid.uuid4())
                    c.execute(
                        "INSERT INTO learning VALUES (?, ?, ?, ?, ?)",
                        (learning_id, user['id'], topic, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    conn.commit()
                    st.success("🎉 Great job learning! Keep it up!")
                    st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Display learning history
        learning_records = c.execute(
            "SELECT * FROM learning WHERE user_id = ? ORDER BY timestamp DESC",
            (user['id'],)
        ).fetchall()

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
            ''', unsafe_allow_html=True)

    # --- PAGE: Browser (Kids Mode Only) ---
    elif st.session_state.page == "Browser":
        st.markdown("""
        <div class="browser-container">
            <div class="browser-header">
                <h2>🌐 Safe Family Browser</h2>
                <p>Explore approved websites safely with parental controls</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        safe_sites = c.execute("SELECT * FROM safe_sites ORDER BY name").fetchall()
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">Choose a website to visit:</div>', unsafe_allow_html=True)
        for site in safe_sites:
            st.markdown(f'''
            <div class="safe-site">
                <div class="site-info">
                    <h4>{site[1]}</h4>
                    <p>{site[3]}</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("Visit", key=f"visit_{site[0]}"):
                    st.markdown(f'''
                    <iframe src="{site[2]}" width="100%" height="600" 
                            style="border: 2px solid #dbdbdb; border-radius: 12px; margin-top: 16px;">
                    </iframe>
                    ''', unsafe_allow_html=True)

        # Allow parents to add new safe sites
        if user['role'] == 'parent':
            st.markdown('<div class="form-title">Add New Safe Site (Parents Only)</div>', unsafe_allow_html=True)
            with st.form("add_safe_site", clear_on_submit=True):
                site_name = st.text_input("Website Name")
                site_url = st.text_input("Website URL", placeholder="https://...")
                site_description = st.text_input("Description")
                if st.form_submit_button("Add Safe Site"):
                    if site_name and site_url and site_description:
                        site_id = str(uuid.uuid4())
                        c.execute(
                            "INSERT INTO safe_sites VALUES (?, ?, ?, ?, ?, ?)",
                            (site_id, site_name, site_url, site_description, user['username'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        )
                        conn.commit()
                        st.success("Safe site added!")
                        st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- PAGE: Chores ---
    elif st.session_state.page == "Chores":
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">✅ Family Chores</div>', unsafe_allow_html=True)

        # Parents can add chores, everyone can see them
        if user['role'] == 'parent':
            with st.form("add_chore", clear_on_submit=True):
                task = st.text_input("Chore Description", placeholder="Take out trash, clean room...")
                family_members = c.execute(
                    "SELECT username FROM users WHERE family_code = ?",
                    (st.session_state.family_code,)
                ).fetchall()
                assigned_to = st.selectbox("Assign To", [member[0] for member in family_members])
                reward = st.slider("Reward Stars", 1, 10, 5)
                if st.form_submit_button("Add Chore", use_container_width=True):
                    if task:
                        chore_id = str(uuid.uuid4())
                        c.execute(
                            "INSERT INTO chores VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (chore_id, task, assigned_to, reward, "Pending", user['username'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        )
                        conn.commit()
                        st.success("Chore assigned! 🎯")
                        st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Display chores
        chores = c.execute(
            """
            SELECT c.* FROM chores c 
            JOIN users u ON c.added_by = u.username 
            WHERE u.family_code = ? 
            ORDER BY c.timestamp DESC
            """,
            (st.session_state.family_code,)
        ).fetchall()

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
            ''', unsafe_allow_html=True)
            if chore[4] == "Pending" and can_complete:
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("✅ Complete", key=f"complete_{chore[0]}"):
                        c.execute("UPDATE chores SET status = 'Completed' WHERE id = ?", (chore[0],))
                        conn.commit()
                        st.success(f"🎉 Great job! You earned {chore[3]} stars!")
                        st.experimental_rerun()

    # --- PAGE: Mood ---
    elif st.session_state.page == "Mood":
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">😊 How are you feeling today?</div>', unsafe_allow_html=True)

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
                c.execute(
                    "INSERT INTO moods VALUES (?, ?, ?, ?, ?)",
                    (mood_id, user['id'], user['username'], selected_mood, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                st.success("Mood shared with your family! 💕")
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Family mood board
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">Family Mood Board</div>', unsafe_allow_html=True)

        moods = c.execute(
            """
            SELECT m.username, m.mood, m.timestamp, u.avatar 
            FROM moods m 
            JOIN users u ON m.user_id = u.id 
            WHERE u.family_code = ? 
            ORDER BY m.timestamp DESC LIMIT 10
            """,
            (st.session_state.family_code,)
        ).fetchall()

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
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Private journal (always available)
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">📓 Private Journal</div>', unsafe_allow_html=True)
        journal_entry = st.text_area("Write your thoughts (private)...", height=150, placeholder="How was your day? What are you thinking about?")
        if st.button("Save Journal Entry", use_container_width=True) and journal_entry:
            journal_id = str(uuid.uuid4())
            c.execute(
                "INSERT INTO journals VALUES (?, ?, ?, ?)",
                (journal_id, user['id'], journal_entry, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            st.success("Journal saved privately! 📝")
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- PAGE: Family ---
    elif st.session_state.page == "Family":
        # Profile Section
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
        ''', unsafe_allow_html=True)

        # Update Profile Picture
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">Update Profile Picture</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload new profile picture", type=['png', 'jpg', 'jpeg'], key="profile_update")
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
        st.markdown('<div class="form-title">👨‍👩‍👧‍👦 Family Members</div>', unsafe_allow_html=True)
        family_members = c.execute(
            "SELECT name, username, avatar, age, role, bio FROM users WHERE family_code = ?",
            (st.session_state.family_code,)
        ).fetchall()
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
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Location Sharing
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">📍 Family Locations</div>', unsafe_allow_html=True)
        with st.form("share_location", clear_on_submit=True):
            location_name = st.text_input("Location Name", placeholder="Home, School, Work, Park...")
            location_notes = st.text_area("Notes (optional)", placeholder="What are you doing here?")
            col1, col2 = st.columns(2)
            with col1:
                latitude = st.number_input("Latitude", value=40.7128, format="%.4f")
            with col2:
                longitude = st.number_input("Longitude", value=-74.0060, format="%.4f")
            if st.form_submit_button("Share Location", use_container_width=True):
                if location_name:
                    location_id = str(uuid.uuid4())
                    c.execute(
                        "INSERT INTO locations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (location_id, user['id'], user['username'], location_name, latitude, longitude, location_notes, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    conn.commit()
                    st.success("Location shared with family! 📍")
                    st.experimental_rerun()

        # Display Family Locations
        locations = c.execute(
            """
            SELECT l.username, l.location_name, l.latitude, l.longitude, l.notes, l.timestamp, u.avatar 
            FROM locations l 
            JOIN users u ON l.user_id = u.id 
            WHERE u.family_code = ? 
            ORDER BY l.timestamp DESC LIMIT 10
            """,
            (st.session_state.family_code,)
        ).fetchall()

        for loc in locations:
            st.markdown(f'''
            <div class="post">
                <div class="post-header">
                    <div class="post-user-info">
                        <img src="{loc[6]}" class="post-avatar">
                        <div>
                            <div class="post-username">📍 {loc[1]}</div>
                            <div class="post-location">{loc[0]} • {loc[5]}</div>
                        </div>
                    </div>
                </div>
                <div class="post-content">
                    📌 {loc[2]:.4f}, {loc[3]:.4f}
                    {f'<br>{loc[4]}' if loc[4] else ''}
                </div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Additional Features (Family Library, Achievements, Emergency Alerts)
        with st.expander("📚 Family Library"):
            with st.form("add_book", clear_on_submit=True):
                title = st.text_input("Book Title")
                author = st.text_input("Author")
                url = st.text_input("URL (optional)")
                age_group = st.selectbox("Appropriate For", ["Kids", "Teens", "Adults", "Everyone"])
                if st.form_submit_button("Add Book"):
                    if title and author:
                        book_id = str(uuid.uuid4())
                        c.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?)", (book_id, title, author, url, user['username'], age_group))
                        conn.commit()
                        st.success("Book added to family library! 📚")

            books = c.execute("SELECT * FROM books").fetchall()
            for book in books:
                st.markdown(f"#### [{book[1]}]({book[3]}) by *{book[2]}* — For: **{book[5]}**")
                avg, count = c.execute("SELECT AVG(rating), COUNT(*) FROM book_reviews WHERE book_id = ?", (book[0],)).fetchone()
                if count:
                    st.markdown(f"⭐ {round(avg,1)} ({count} reviews)")
                with st.expander("Leave a Review"):
                    rating = st.slider("Your Rating", 1, 5, 5)
                    review_text = st.text_area("Write your review")
                    if st.button(f"Submit Review for {book[1]}", key="review"+book[0]):
                        review_id = str(uuid.uuid4())
                        c.execute("INSERT INTO book_reviews VALUES (?, ?, ?, ?, ?, ?)", (review_id, book[0], user['username'], rating, review_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        st.success("Review submitted!")
                        st.experimental_rerun()
                reviews = c.execute("SELECT reviewer, rating, review, timestamp FROM book_reviews WHERE book_id = ? ORDER BY timestamp DESC", (book[0],)).fetchall()
                for r in reviews:
                    st.markdown(f"**{r[0]}** rated it ⭐ {r[1]}")
                    st.write(r[2])
                    st.caption(f"Reviewed on {r[3]}")
                st.markdown("---")

        with st.expander("🏆 Achievements"):
            with st.form("add_achievement", clear_on_submit=True):
                ach_title = st.text_input("Achievement Title")
                ach_desc = st.text_area("Description of the achievement")
                if st.form_submit_button("Add Achievement"):
                    if ach_title and ach_desc:
                        ach_id = str(uuid.uuid4())
                        c.execute("INSERT INTO achievements VALUES (?, ?, ?, ?, ?, ?)", (ach_id, user['id'], user['username'], ach_title, ach_desc, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        st.success("Achievement added! 🏆")
            achievements = c.execute("SELECT * FROM achievements ORDER BY timestamp DESC").fetchall()
            for ach in achievements:
                st.image(user['avatar'], width=40)
                st.markdown(f"**{ach[2]}** - *{ach[3]}*")
                st.write(ach[4])
                st.caption(f"Awarded on {ach[5]}")
                st.markdown("---")

        if user['role'] == 'parent':
            with st.expander("🚨 Emergency Alert (Parents Only)"):
                st.warning("⚠️ Use only for real emergencies!")
                emergency_msg = st.text_area("Emergency Message")
                if st.button("🚨 Send Alert") and emergency_msg:
                    alert_id = str(uuid.uuid4())
                    c.execute("INSERT INTO alerts VALUES (?, ?, ?, ?)", (alert_id, user['username'], emergency_msg, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.error("Emergency alert sent to all family members!")

    # Close containers
    if has_parental_controls():
        st.markdown('</div>', unsafe_allow_html=True)  # Close kids-mode
    st.markdown('</div>', unsafe_allow_html=True)  # Close app-container

    # Add bottom spacing for navigation
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

# End of app


