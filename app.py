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
TEMPLATE_FILE = "email_templates.json"
# ✅ Load saved templates
def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as file:
            return json.load(file)
    return {}

# Save templates
# ✅ Save templates
def save_templates(templates):
    with open(TEMPLATE_FILE, "w") as file:
        json.dump(templates, file, ensure_ascii=False, indent=4)

# ✅ Initialize templates
if "templates" not in st.session_state:
    st.session_state.templates = load_templates()

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

# Default template to be used if the user doesn't choose or create a template
default_template = """
Dear [Recipient Name],

I hope this message finds you well. My name is [Your Name], and I am a [Your Profession] with [X years] of experience in [Your Field]. I am writing to express my interest in the [Specific Role] at [Company Name].

In my current role at [Current Company], I [Briefly Describe a Key Achievement or Responsibility]. My skills in [List Relevant Skills] have enabled me to [Key Result/Impact].

I admire [Company Name] for [Specific Reason, e.g., its innovation, impact, or mission], and I am eager to contribute to [Specific Project or Goal].

Would you be open to a brief conversation to explore how my background might align with your team’s needs?

Best regards,<br>[Your Name]<br>[Your Email]<br>[LinkedIn Profile]
"""

# Store default template in templates
if "default template" not in st.session_state.templates:
    st.session_state.templates["default template"] = default_template
    save_templates(st.session_state.templates)

# App UI
st.title("📧 Automated Email Sender")
st.markdown("### Compose Your Email")
st.markdown("_Customize the subject and body before sending._")

# Email Input Fields
position_title = st.text_input("Job Role", value="DevOps Engineer")
company_name = st.text_input("Company Name", value="")
subject = st.text_input("Email Subject", value=f"Application for {position_title} | {company_name}", max_chars=100)
st.markdown(f"**Character Count:** {len(subject)}/100")

# Input for Recipient Name (New input added here)
recipient_name = st.text_input("Enter Recipient's Name", value="Hiring Manager")

# Template Selection
template_names = list(st.session_state.templates.keys())
selected_template = st.selectbox("Select a Template", ["New Template"] + template_names)

# Instruction to guide users
st.markdown("**Tip:** Use `[Recipient Name]` in your email body where you want the recipient's name to appear dynamically.")

# Template Editor
if selected_template == "New Template":
    template_name = st.text_input("Enter Template Name")
    email_body = st_quill(placeholder="Write your email here... (Use [Recipient Name] for dynamic name replacement)", html=True)
else:
    template_name = selected_template
    email_body = st_quill(value=st.session_state.templates[selected_template], html=True)

# Automatically prepend "Dear [Recipient Name]," if not included in the template
if "[Recipient Name]" not in email_body:
    email_body = f"Dear [Recipient Name],\n\n{email_body}"

# Save template button
if st.button("💾 Save Template"):
    if template_name and email_body:
        st.session_state.templates[template_name] = email_body  # Store as raw HTML
        save_templates(st.session_state.templates)
        st.success(f"Template '{template_name}' saved!")
        st.rerun()  # Refresh page to reflect updated template

st.markdown(f"**Character Count:** {len(email_body)}/2000")

# Email Recipient Input
st.markdown("### Recipients")
recipient_emails_input = st.text_area("Enter each email on a new line:", height=100)
recipient_emails = [email.strip() for email in recipient_emails_input.split("\n") if email.strip() and is_valid_email(email.strip())]

# Resume Upload (Drag & Drop)
uploaded_file = st.file_uploader("Upload Your Resume (PDF, DOCX)", type=["pdf", "docx"], accept_multiple_files=False)

# Send Emails Button
if st.button("🚀 Send Emails"):
    if not recipient_emails:  # Check if no valid email was entered
        st.warning("Please enter at least one valid email address.")
    else:
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
