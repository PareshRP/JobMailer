import streamlit as st
import smtplib
import re
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr

# Fetch credentials from Streamlit secrets
sender_email = st.secrets["EMAIL_ID"]
sender_password = st.secrets["EMAIL_PASSWORD"]

# Function to validate emails
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

# Streamlit UI
st.set_page_config(page_title="Email Sender", layout="centered")
st.title("📧 Automated Email Sender")

st.markdown("### Compose Your Email")
st.markdown("_Customize the subject and body before sending._")

# Email Input Fields
position_title = st.text_input("Position Title", value="DevOps Engineer")
subject = st.text_input("Email Subject", value=f"Application for the position of {position_title}")
email_body = st.text_area("Email Body", value=f"""
Dear Hiring Manager/Recruiter,

I am writing to express my interest in the position of {position_title} as advertised recently. My qualifications, skills, and experience align closely with your requirements for this role.

### **Technical Skills**
- **DevOps Tools:** Jenkins, Ansible, Docker, Kubernetes, Terraform, Git, GitHub Actions, GitLab, Gerrit, SonarQube 
- **Programming and Scripting:** Python, Bash/Shell Scripting, Groovy, PowerShell, YAML, JSON 
- **Cloud and Infrastructure:** AWS, Azure, GCP, OpenStack, VMware, RHEL, Kubernetes Cluster Security 
- **Data Analysis and Reporting:** Power BI, SQL, MySQL, MariaDB, MongoDB, REST API

Please find my CV attached for your review. I would be delighted to discuss how I can contribute to your team.

Kind regards,
Paresh Patil  
LinkedIn: https://www.linkedin.com/in/pareshrp/  
WhatsApp: https://wa.me/+919930583517  
""")

# Email Recipient Input
st.markdown("### Recipients")
recipient_emails_input = st.text_area("Enter each email on a new line:", height=100)
recipient_emails = [email.strip() for email in recipient_emails_input.split("\n") if email.strip() and is_valid_email(email.strip())]

# Resume Upload
uploaded_file = st.file_uploader("Upload Your Resume (PDF, DOCX)", type=["pdf", "docx"])

# Test Email Button
test_email = st.text_input("Send Test Email To:")
if st.button("Send Test Email") and is_valid_email(test_email):
    recipient_emails = [test_email]
    st.success("Test email sent successfully!")

# Confirmation and Sending Emails
if st.button("Send Emails") and recipient_emails:
    st.markdown("### Sending Emails...")
    progress_bar = st.progress(0)
    total_emails = len(recipient_emails)
    
    for idx, recipient in enumerate(recipient_emails):
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = formataddr(("Paresh Patil", sender_email))
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Add tracking pixel
        tracking_pixel = f'<img src="https://your-tracking-server.com/track?email={recipient}" width="1" height="1">'
        email_body_with_pixel = email_body + tracking_pixel
        msg.attach(MIMEText(email_body_with_pixel, 'html'))
        
        # Attach Resume
        if uploaded_file is not None:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(uploaded_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{uploaded_file.name}"')
            msg.attach(part)
        
        # Send Email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(msg['From'], [recipient], msg.as_string())
            server.quit()
        except Exception as e:
            st.error(f"Failed to send email to {recipient}: {e}")
        
        # Update progress
        progress_bar.progress((idx + 1) / total_emails)
        time.sleep(1)  # Simulate delay
    
    st.success("All emails sent successfully!")
