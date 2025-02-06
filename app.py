import streamlit as st
import smtplib
import re
import time
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from streamlit_quill import st_quill
from streamlit_modal import modal

TEMPLATE_FILE = "email_templates.json"

# Load saved templates
def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as file:
            return json.load(file)
    return {}

# Save templates
def save_templates(templates):
    with open(TEMPLATE_FILE, "w") as file:
        json.dump(templates, file)

# Initialize templates
templates = load_templates()

# Fetch credentials from Streamlit secrets
sender_email = st.secrets["EMAIL_ID"]
sender_password = st.secrets["EMAIL_PASSWORD"]

# Function to validate emails
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

# Page Configuration
st.set_page_config(page_title="Automated Email Sender", page_icon="📧", layout="wide")

# Custom CSS to hide GitHub icon and add styling
st.markdown(
    """
    <style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f4f7f6;
    }

    .title {
        font-size: 36px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-top: 40px;
    }

    .subheader {
        font-size: 20px;
        font-weight: 300;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 40px;
    }

    .input-label {
        font-size: 18px;
        font-weight: 600;
        color: #34495e;
    }

    .email-recipient {
        padding: 10px;
        border-radius: 5px;
        border: 2px solid #ccc;
    }

    .send-button {
        background-color: #2F9BFE;
        color: white;
        font-size: 16px;
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        width: 200px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .send-button:hover {
        background-color: #3498db;
    }

    .footer {
        text-align: center;
        color: #7f8c8d;
        margin-top: 40px;
        font-size: 14px;
    }

    /* Hide GitHub Icon */
    #GithubIcon {
        visibility: hidden;
    }

    /* Menu bar styling */
    .menu-bar {
        background-color: #2F9BFE;
        padding: 10px 20px;
        text-align: center;
        color: white;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True
)

# Menu Bar
st.markdown('<div class="menu-bar">Automated Email Sender</div>', unsafe_allow_html=True)

# Title and Subheader
st.markdown('<div class="title">📧 Automated Email Sender</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Compose, Save, Load & Send Emails with Attachments</div>', unsafe_allow_html=True)

# Email Input Fields
position_title = st.text_input("Position Title", value="DevOps Engineer", label_visibility="collapsed")
subject = st.text_input("Email Subject", value=f"Application for the position of {position_title}", max_chars=100)
st.markdown(f"**Character Count:** {len(subject)}/100")

# Template Selection
template_options = ["New Template"] + list(templates.keys())
selected_template = st.selectbox("Select a Template", template_options)

if selected_template == "New Template":
    template_name = st.text_input("Enter Template Name")
    email_body = st_quill(label="Email Body", height=200, placeholder="Write your email here...")
else:
    template_name = selected_template
    email_body = templates[selected_template]

# Save template button
if st.button("Save Template"):
    if template_name and email_body:
        templates[template_name] = email_body
        save_templates(templates)
        st.success(f"Template '{template_name}' saved!")

# Email Recipient Input
st.markdown('<div class="input-label">Recipients:</div>', unsafe_allow_html=True)
recipient_emails_input = st.text_area("Enter each email on a new line:", height=100, label_visibility="collapsed", key="recipients")
recipient_emails = [email.strip() for email in recipient_emails_input.split("\n") if email.strip() and is_valid_email(email.strip())]

# Resume Upload (Drag & Drop)
uploaded_file = st.file_uploader("Upload Your Resume (PDF, DOCX)", type=["pdf", "docx"], accept_multiple_files=False)

# Check if email body and recipients are not empty
if st.button("Send Emails"):
    if not email_body:
        st.error("Email body should not be empty")
    elif not recipient_emails:
        st.error("Please provide at least one valid recipient email.")
    else:
        if uploaded_file is None:
            # Pop-up confirmation for sending without attachment
            with st.modal("Send Email without Attachment?", key="popup_modal"):
                if st.button("Yes"):
                    st.success("Sending Email without attachment.")
                    # Send Email Logic
                    send_emails()
                elif st.button("No"):
                    st.stop()
        else:
            # Send Email Logic
            send_emails()

# Function to send emails
def send_emails():
    st.markdown("### Sending Emails...")
    progress_bar = st.progress(0)
    total_emails = len(recipient_emails)
    sent_emails = []
    
    for idx, recipient in enumerate(recipient_emails):
        msg = MIMEMultipart()
        msg['From'] = formataddr(("Paresh Patil", sender_email))
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(email_body, 'html'))
        
        if uploaded_file is not None:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(uploaded_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{uploaded_file.name}"')
            msg.attach(part)
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(msg['From'], [recipient], msg.as_string())
            server.quit()
            sent_emails.append(recipient)
        except Exception as e:
            st.error(f"Failed to send email to {recipient}: {e}")
        
        progress_bar.progress((idx + 1) / total_emails)
        time.sleep(1)
    
    st.success("All emails sent successfully!")
    with open("sent_emails_log.txt", "a") as log_file:
        for email in sent_emails:
            log_file.write(f"{email}\n")

# Footer Section
st.markdown('<div class="footer">Made by Paresh Patil</div>', unsafe_allow_html=True)
