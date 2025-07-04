import streamlit as st
from connection import get_session
from db_setup import ContactMessage
import re
import smtplib
from email.mime.text import MIMEText

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def send_email(name, email, message):
    sender_email = "piyushraj071845@gmail.com"
    sender_password = "ciri gqbx bjop jdqx"
    receiver_email = "piyushraj071845@gmail.com"

    subject = f"New Contact Message from {name}"
    body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.sendmail(sender_email, receiver_email, msg.as_string())

def contact_page():
    session = get_session()

    st.title("Contact Us")
    st.write("Please fill in the form below to get in touch.")

    with st.form("contact_form"):
        name = st.text_input("Your Name", placeholder="Enter your full name")
        email = st.text_input("Your Email", placeholder="name@example.com")
        message = st.text_area("Your Message", placeholder="Type your message here...", max_chars=1000)

        submitted = st.form_submit_button("Send")

        if submitted:
            if not (name and email and message):
                st.error("Please fill in all the fields.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            else:
                with st.spinner("Sending your message..."):
                    new_message = ContactMessage(name=name, email=email, message=message)
                    session.add(new_message)
                    session.commit()
                    try:
                        send_email(name, email, message)
                    except Exception as e:
                        st.warning(f"Message saved but email notification failed: {e}")
                st.success("Your message has been sent. Thank you!")
                st.rerun()
