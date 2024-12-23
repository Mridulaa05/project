import sqlite3
import os
import hashlib
import logging

# Specify the database path here
db_path = os.path.join(os.getcwd(), 'notes.db')  # Creates the database in the current working directory

# Setup logging
logging.basicConfig(filename='app.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(error_message):
    """Logs error messages to the log file."""
    logging.error(error_message)

def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_database():
    print(f"Creating database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create NOTES table
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS NOTE (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            TITLE TEXT NOT NULL,
            CONTENT TEXT NOT NULL,
            MODIFIED_TIME TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES USERS(id)
        )
    ''')

    # Create USERS table for user login
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS USERS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create trigger to update MODIFIED_TIME on note updates
    cursor.execute(''' 
        CREATE TRIGGER IF NOT EXISTS update_modified_time
        AFTER UPDATE ON NOTE
        FOR EACH ROW
        BEGIN
            UPDATE NOTE SET MODIFIED_TIME = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;
    ''')

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

def connect_to_database():
    """Connects to the SQLite database and returns the connection object."""
    return sqlite3.connect(db_path)

def signup(username, password):
    """Handles user signup by checking for existing usernames and inserting new ones."""
    conn = connect_to_database()  
    cursor = conn.cursor()

    # Check if the username already exists (case-insensitive)
    cursor.execute("SELECT * FROM USERS WHERE username = ?", (username.lower(),))
    existing_user = cursor.fetchone()

    if existing_user:
        print("Username already exists.")
        conn.close()
        return False  # Username already exists

    # If not, insert the new user (store username in lowercase for consistency)
    cursor.execute("INSERT INTO USERS (username, password) VALUES (?, ?)", (username.lower(), hash_password(password)))
    conn.commit()
    conn.close()
    print("Signup successful.")
    return True  # Signup successful

def login(username, password):
    """Checks if the username and hashed password are valid."""
    hashed_password = hash_password(password)
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM USERS WHERE username = ? AND password = ?', (username.lower(), hashed_password))
            user = cursor.fetchone()
            if user:
                print("Login successful.")
                return user[0]  # Return user ID for further operations
            else:
                print("Invalid username or password.")
                return None
    except sqlite3.Error as e:
        log_error(f"An error occurred during login: {e}")
        print("An unexpected error occurred.")
        return None

def insert_data(title, content, user_id):
    """Inserts a new note into the database for a specific user."""
    if not title or not content:
        print("Title and content cannot be empty.")
        return
    
    print(f"Inserting note for user_id: {user_id}")  # Debugging line
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(''' 
                INSERT INTO NOTE (TITLE, CONTENT, user_id) VALUES (?, ?, ?)
            ''', (title, content, user_id))
            print("Note inserted successfully.")
    except sqlite3.Error as e:
        log_error(f"An error occurred while inserting data: {e}")
        print("An unexpected error occurred.")

def update_data(title, content, note_id):
    """Updates the title and content of a note."""
    if not title or not content:
        print("Title and content cannot be empty.")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(''' 
                UPDATE NOTE SET TITLE = ?, CONTENT = ? WHERE id = ?
            ''', (title, content, note_id))
            print("Note updated successfully.")
    except sqlite3.Error as e:
        log_error(f"An error occurred while updating data: {e}")
        print("An unexpected error occurred.")

def delete_data(note_id):
    """Deletes a note by its ID."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM NOTE WHERE id = ?', (note_id,))
            print("Note deleted successfully.")
    except sqlite3.Error as e:
        log_error(f"An error occurred while deleting data: {e}")
        print("An unexpected error occurred.")

def retrieve_data(user_id):
    """Retrieves all notes for a specific user from the database."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, TITLE, CONTENT, MODIFIED_TIME FROM NOTE WHERE user_id = ?', (user_id,))
            notes = cursor.fetchall()
            return notes
    except sqlite3.Error as e:
        log_error(f"An error occurred while retrieving data: {e}")
        print("An unexpected error occurred.")
        return []

def get_note_by_id(note_id):
    """Retrieves a specific note by its ID."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM NOTE WHERE id = ?', (note_id,))
            note = cursor.fetchone()
            return note
    except sqlite3.Error as e:
        log_error(f"An error occurred while retrieving note: {e}")
        print("An unexpected error occurred.")
        return None

def backup_note_to_file(note_id):
    """Backs up a note to a text file with an absolute path."""
    note = get_note_by_id(note_id)
    if note:
        filename = os.path.join(os.getcwd(), f"backup_note_{note_id}.txt")
        with open(filename, 'w') as f:
            f.write(f"Title: {note[1]}\n")
            f.write(f"Content: {note[2]}\n")
            f.write(f"Last Modified: {note[3]}\n")
        print(f"Note backed up to file: {filename}")
        return filename
    print("Note not found.")
    return None

# Ensure the database is created when this script is run
if __name__ == "__main__":
    create_database()
