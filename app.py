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
from streamlit_quill import st_quill  # Quill editor for rich text formatting
from streamlit_extras import add_vertical_space  # For better UI spacing

TEMPLATE_FILE = "email_templates.json"
# ✅ Set page config (must be first)
st.set_page_config(page_title="Email Sender", layout="centered")

# Hide the GitHub icon
# ✅ Hide GitHub icon & Streamlit branding
hide_streamlit_style = """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load saved templates
# ✅ Template file for saving emails
def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as file:
            return json.load(file)
    return {}

# Save templates
# ✅ Save templates
def save_templates(templates):
    with open(TEMPLATE_FILE, "w") as file:
        json.dump(templates, file)

# ✅ Delete a template
def delete_template(template_name):
    if template_name in templates:
        del templates[template_name]
        save_templates(templates)
        st.experimental_rerun()  # Refresh UI immediately after deletion

# Initialize templates
if "templates" not in st.session_state:
    st.session_state.templates = load_templates()

# ✅ Load templates
templates = load_templates()

# Fetch credentials from Streamlit secrets
# ✅ Fetch credentials from Streamlit secrets
sender_email = st.secrets["EMAIL_ID"]
sender_password = st.secrets["EMAIL_PASSWORD"]

# Function to validate emails
# ✅ Validate email function
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

st.set_page_config(page_title="Email Sender", layout="centered")
# 🎯 **App Title & UI**
st.title("📧 Automated Email Sender")
st.markdown("### Compose Your Email")
st.markdown("_Customize the subject and body before sending._")

# Email Input Fields
# ✅ **Email Fields**
position_title = st.text_input("Position Title", value="DevOps Engineer")
subject = st.text_input("Email Subject", value=f"Application for the position of {position_title}", max_chars=100)
st.markdown(f"**Character Count:** {len(subject)}/100")

# Template Selection
template_names = list(st.session_state.templates.keys())
selected_template = st.selectbox("Select a Template", ["New Template"] + template_names)

# Template Editor
if selected_template == "New Template":
    template_name = st.text_input("Enter Template Name")
    email_body = st_quill(placeholder="Write your email here...", key="new_template_editor")
else:
    template_name = selected_template
    email_body = st_quill(value=st.session_state.templates[selected_template], key="edit_template_editor")

# Save template button
if st.button("💾 Save Template"):
    if template_name and email_body:
        st.session_state.templates[template_name] = email_body
        save_templates(st.session_state.templates)
        st.success(f"Template '{template_name}' saved!")
        st.experimental_rerun()  # Refresh page to reflect the new template

# Character count for the email body
st.markdown(f"**Character Count:** {len(email_body)}/2000")

# Email Recipient Input
# ✅ **Recipient Emails**
st.markdown("### Recipients")
recipient_emails_input = st.text_area("Enter each email on a new line:", height=100)
recipient_emails = [email.strip() for email in recipient_emails_input.split("\n") if email.strip() and is_valid_email(email.strip())]

# Resume Upload (Drag & Drop)
# ✅ **Resume Upload**
uploaded_file = st.file_uploader("Upload Your Resume (PDF, DOCX)", type=["pdf", "docx"], accept_multiple_files=False)

# Send Emails Button
if st.button("🚀 Send Emails") and recipient_emails:
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

    st.success("🎉 All emails sent successfully!")
    with open("sent_emails_log.txt", "a") as log_file:
        for email in sent_emails:
            log_file.write(f"{email}\n")
