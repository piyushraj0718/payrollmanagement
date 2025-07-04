import os
import base64
import streamlit as st

# page config
st.set_page_config(page_title="Payroll Management System", layout="centered")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "tp2-removebg-preview.png")
background_path = os.path.join(BASE_DIR, "background.jpg")

#  Session State Initialization 
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'organization' not in st.session_state:
    st.session_state.organization = None

# Import  page modules
from employee_module import employee_page
from attendance_module import attendance_page
from payslip_module import payslip_page
from auth_module import auth_page
from contact_module import contact_page

# Set background image
def set_bg_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

# Set background for all pages 
set_bg_image(background_path)

# Show login page 
if not st.session_state.is_logged_in:
    login_style = """
    <style>
    html, body, [class*="stApp"] {{
        height: 100%;
    }}
    .login-container {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 95vh;
        text-align: center;
    }}
    .logo-img {{
        max-width: 220px;
        margin-bottom: 20px;
    }}
    .quote {{
        font-family: 'Georgia', serif;
        font-size: 1.3rem;
        font-style: italic;
        color: #ffffff;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
        margin-bottom: 30px;
        padding: 0 20px;
    }}
    </style>
    """
    st.markdown(login_style, unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as logo_file:
            encoded_logo = base64.b64encode(logo_file.read()).decode()
        st.markdown(
            f'<img class="logo-img" src="data:image/png;base64,{encoded_logo}" alt="Logo" />',
            unsafe_allow_html=True,
        )

    st.markdown("""
    <div class="quote">
        From <b>Attendance</b> to <b>salary</b> — Manage it all, effortlessly.
    </div>
    """, unsafe_allow_html=True)


    auth_page()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

#  After login, show logo at top on every page 
if os.path.exists(logo_path):
    with open(logo_path, "rb") as logo_file:
        encoded_logo = base64.b64encode(logo_file.read()).decode()
    st.markdown(
        f'<img src="data:image/png;base64,{encoded_logo}" alt="Logo" style="max-width: 200px; display: block; margin-left: auto; margin-right: auto; margin-bottom: 20px;" />',
        unsafe_allow_html=True,
    )

#  Sidebar and content after login 
with st.sidebar:
    st.title("📂 Navigation")
    menu = st.selectbox("Choose Section", ["Home", "Employee", "Attendance", "Payslip", "Contact Us"])

    if st.button("🔒 Logout"):
        st.session_state.is_logged_in = False
        st.session_state.username = None
        st.session_state.organization = None
        st.success("Logged out successfully.")
        try:
            st.experimental_rerun()
        except Exception:
            pass

# Main content
if menu == "Home":
    st.title("🏠 Payroll Management System")

    st.markdown("---")

    st.markdown(
        f"""
        <div style="background-color:#f0f2f6; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <h3 style="color:#4B0082;">Welcome, <span style="color:#FF6347;">{st.session_state.username}</span>! 👋</h3>
            <p style="font-size:16px; color:#333;">
                You are logged in under the organization: <strong>{st.session_state.organization}</strong>.<br><br>
                Use the sidebar to:<br>
                <ul>
                    <li>🧑‍💼 Manage Employees</li>
                    <li>📅 Mark Attendance</li>
                    <li>🧾 Generate Payslips</li>
                </ul>
            </p>
            <p style="font-style: italic; color:#555;">
                Have a productive day! 🚀
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")


elif menu == "Employee":
    employee_page()

elif menu == "Attendance":
    attendance_page()

elif menu == "Payslip":
    payslip_page()

elif menu == "Contact Us":
    contact_page()

#  Footer 
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <center>
        © 2025 Payroll Management System<br>
        Developed by <b>GROUP - 117</b> | Batch - 01
    </center>
    """,
    unsafe_allow_html=True,
)
