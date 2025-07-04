import streamlit as st
from connection import get_session
from db_setup import User  

def auth_page():
    session = get_session()

    st.subheader("Login or Sign Up")
    tab = st.tabs(["Login", "Sign Up"])

    with tab[0]:
        st.write("### Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        organization = st.text_input("Organization Name", key="login_org")

        if st.button("Login"):
            if not username or not password or not organization:
                st.error("Please fill in all fields.")
            else:
                user = session.query(User).filter_by(username=username, organization=organization).first()
                if user and user.password == password:
                    st.success("Logged in successfully!")
                    st.session_state.is_logged_in = True  
                    st.session_state.username = username
                    st.session_state.organization = organization
                    st.rerun()  # safe rerun
                else:
                    st.error("Invalid username, password, or organization.")

    with tab[1]:
        st.write("### Sign Up")
        new_username = st.text_input("Choose Username", key="signup_username")
        new_password = st.text_input("Choose Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        new_organization = st.text_input("Organization Name", key="signup_org")

        if st.button("Sign Up"):
            if not new_username or not new_password or not confirm_password or not new_organization:
                st.error("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                existing_user = session.query(User).filter_by(username=new_username).first()
                if existing_user:
                    st.error("Username already exists. Please choose another.")
                else:
                    user = User(username=new_username, password=new_password, organization=new_organization)
                    session.add(user)
                    session.commit()
                    st.success("Account created successfully! Please login now.")
                    