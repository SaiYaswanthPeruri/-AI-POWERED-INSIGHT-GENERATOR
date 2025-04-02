import streamlit as st
import sqlite3
import hashlib  # For basic password hashing
from datetime import datetime

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('app.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create users table with additional safety fields
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, 
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create texts table with foreign key relationship
    c.execute('''CREATE TABLE IF NOT EXISTS texts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  text TEXT NOT NULL, 
                  username TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    conn.commit()
    return conn

conn = init_db()

# Password hashing function
def hash_password(password):
    """Basic password hashing using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Registration Page with improved validation
def register_page():
    st.title("Register")
    
    with st.form("register_form"):
        username = st.text_input("Username", max_chars=20)
        password = st.text_input("Password", type="password", max_chars=50)
        confirm_password = st.text_input("Confirm Password", type="password", max_chars=50)
        
        if st.form_submit_button("Register"):
            if not username or not password:
                st.error("Username and password are required")
                return
                
            if len(username) < 4:
                st.error("Username must be at least 4 characters")
                return
                
            if password != confirm_password:
                st.error("Passwords do not match")
                return
                
            if len(password) < 6:
                st.error("Password must be at least 6 characters")
                return
                
            try:
                hashed_pw = hash_password(password)
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                            (username, hashed_pw))
                conn.commit()
                st.success("Registration successful! Please log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists")
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")

# Login Page with better error handling
def login_page():
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            if not username or not password:
                st.error("Please enter both username and password")
                return
                
            try:
                c = conn.cursor()
                c.execute("SELECT password FROM users WHERE username=?", (username,))
                result = c.fetchone()
                
                if result:
                    stored_hash = result[0]
                    input_hash = hash_password(password)
                    
                    if stored_hash == input_hash:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.selected_text = ""
                        st.rerun()
                    else:
                        st.error("Invalid password")
                else:
                    st.error("Username not found")
                    
            except Exception as e:
                st.error(f"Login failed: {str(e)}")

# Main App Logic
def main():
    st.set_page_config(page_title="Text App", layout="wide")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'selected_text' not in st.session_state:
        st.session_state.selected_text = ""
    
    if not st.session_state.logged_in:
        menu = st.radio("Choose an option", ["Login", "Register"])
        if menu == "Login":
            login_page()
        else:
            register_page()
    else:
        st.success(f"Welcome {st.session_state.username}!")
        # Add your logged-in content here
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

if __name__ == "__main__":
    main()