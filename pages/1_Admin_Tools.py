import streamlit as st
import sqlite3
import hashlib

# Configure page and sidebar
st.set_page_config(page_title="Admin Tools", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 300px;
            transition: width 0.3s, margin 0.3s;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            margin-left: -300px;
            transition: width 0.3s, margin 0.3s;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password(password):
    """Verify password (replace this hash with your desired password)"""
    # Password: admin123
    correct_password_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    return hashed_input == correct_password_hash

# Login form
if not st.session_state.authenticated:
    st.title("Admin Login")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if check_password(password):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()  # Don't show anything else until authenticated

# Only show admin content after authentication
st.title("Resolution Roulette Admin Tools")

# Add logout button in sidebar
with st.sidebar:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

def normalize_text(text):
    """Normalize text for comparison by converting to lowercase and removing extra punctuation"""
    return text.lower().strip().rstrip('!.,')

def remove_duplicates_from_db():
    conn = sqlite3.connect("resolutions.db")
    cursor = conn.cursor()
    
    # Get all resolutions grouped by category
    cursor.execute("SELECT category, resolution, id FROM resolutions")
    all_entries = cursor.fetchall()
    
    # Group by category and normalized text
    seen = {}
    duplicates = []
    
    for category, resolution, id in all_entries:
        normalized = normalize_text(resolution)
        key = (category, normalized)
        
        if key in seen:
            duplicates.append(id)
        else:
            seen[key] = id
    
    # Delete duplicates
    if duplicates:
        cursor.execute("DELETE FROM resolutions WHERE id IN (%s)" % ','.join(map(str, duplicates)))
        conn.commit()
    
    affected_rows = len(duplicates)
    conn.close()
    return affected_rows

# Display all resolutions
def view_all_resolutions():
    conn = sqlite3.connect("resolutions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, resolution FROM resolutions ORDER BY category, resolution")
    results = cursor.fetchall()
    conn.close()
    return results

def bulk_import_resolutions(text_data):
    """Import resolutions from text format: category,resolution"""
    conn = sqlite3.connect("resolutions.db")
    cursor = conn.cursor()
    
    added = 0
    skipped = 0
    
    for line in text_data.strip().split('\n'):
        if ',' not in line:
            continue
            
        category, resolution = line.split(',', 1)
        category = category.strip()
        resolution = resolution.strip()
        
        if not category or not resolution:
            continue
            
        # Check if normalized version already exists
        normalized = normalize_text(resolution)
        cursor.execute("""
            SELECT 1 FROM resolutions 
            WHERE category = ? AND LOWER(TRIM(resolution)) = ?
        """, (category, normalized))
        
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO resolutions (category, resolution) VALUES (?, ?)",
                         (category, resolution))
            added += 1
        else:
            skipped += 1
    
    conn.commit()
    conn.close()
    return added, skipped

def delete_resolution(id):
    """Delete a resolution by ID with proper transaction handling"""
    conn = None
    try:
        conn = sqlite3.connect("resolutions.db")
        conn.execute('BEGIN TRANSACTION')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resolutions WHERE id = ?", (id,))
        deleted = cursor.rowcount
        conn.commit()
        return deleted > 0
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        st.error(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Admin Tools UI
st.header("Database Management")

col1, col2 = st.columns(2)

with col1:
    if st.button("Remove Duplicate Resolutions", key="remove_duplicates"):
        removed = remove_duplicates_from_db()
        if removed > 0:
            st.success(f"Removed {removed} duplicate resolution(s)")
        else:
            st.info("No duplicates found")

with col2:
    if st.button("View All Resolutions", key="view_all"):
        results = view_all_resolutions()
        if results:
            st.write("### All Resolutions")
            for id, category, resolution in results:
                st.write(f"**{category}** ({id}): {resolution}")
        else:
            st.info("No resolutions found in database")

# Add new section for bulk import
st.header("Delete Resolution")
delete_id = st.number_input("Enter Resolution ID to delete", min_value=1, step=1)
if st.button("Delete Resolution", key="delete_single"):
    if st.checkbox("I confirm I want to delete this resolution"):
        if delete_resolution(delete_id):
            st.success(f"Successfully deleted resolution {delete_id}")
        else:
            st.error(f"No resolution found with ID {delete_id}")
    else:
        st.warning("Please confirm deletion by checking the confirmation box")

st.header("Bulk Import")
st.markdown("""
    Paste your resolutions in the format:  
    ```
    category,resolution
    category,resolution
    ```
    Example:
    ```
    Fitness,Run 5k three times a week
    Career,Learn a new programming language
    Fun,Take a cooking class
    ```
""")

bulk_text = st.text_area("Paste resolutions here (category,resolution format)")
if st.button("Import Resolutions", key="bulk_import"):
    if bulk_text:
        added, skipped = bulk_import_resolutions(bulk_text)
        st.success(f"Import complete! Added: {added}, Skipped (duplicates): {skipped}")
    else:
        st.warning("Please enter some resolutions to import")

# Generate hash for a new password
new_password = "your_password"
hashed = hashlib.sha256(new_password.encode()).hexdigest()
print(hashed)
