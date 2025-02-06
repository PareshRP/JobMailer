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
from streamlit_quill import st_quill  # Import Quill editor for rich text formatting

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

st.set_page_config(page_title="Email Sender", layout="centered")
st.title("📧 Automated Email Sender")
st.markdown("### Compose Your Email")
st.markdown("_Customize the subject and body before sending._")

# Email Input Fields
position_title = st.text_input("Position Title", value="DevOps Engineer")
subject = st.text_input("Email Subject", value=f"Application for the position of {position_title}", max_chars=100)
st.markdown(f"**Character Count:** {len(subject)}/100")

# Template Selection
template_options = ["New Template"] + list(templates.keys())
selected_template = st.selectbox("Select a Template", template_options)

if selected_template == "New Template":
    template_name = st.text_input("Enter Template Name")
    email_body = st_quill(placeholder="Write your email here...")
else:
    template_name = selected_template
    email_body = st_quill(value=templates[selected_template])

# Save template button
if st.button("Save Template"):
    if template_name and email_body:
        templates[template_name] = email_body
        save_templates(templates)
        st.success(f"Template '{template_name}' saved!")

st.markdown(f"**Character Count:** {len(email_body)}/2000")

# Email Recipient Input
st.markdown("### Recipients")
recipient_emails_input = st.text_area("Enter each email on a new line:", height=100)
recipient_emails = [email.strip() for email in recipient_emails_input.split("\n") if email.strip() and is_valid_email(email.strip())]

# Resume Upload (Drag & Drop)
uploaded_file = st.file_uploader("Upload Your Resume (PDF, DOCX)", type=["pdf", "docx"], accept_multiple_files=False)

# Send Emails Button
if st.button("Send Emails") and recipient_emails:
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
