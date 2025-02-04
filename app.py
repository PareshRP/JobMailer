import streamlit as st
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ---- UI Configuration ----
st.set_page_config(page_title="Job Application Mailer", layout="centered")
st.title("📧 Job Application Email Sender")

# ---- User Inputs ----
position_title = st.text_input("Enter Position Title", "DevOps Engineer")
receiver_email = st.text_input("Enter Recipient Email", placeholder="example@company.com")
resume_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

# ---- Email Body ----
email_body = f"""
Dear Hiring Manager/Recruiter,<br><br>

I am writing to express my interest in the position of <b>{position_title}</b> as advertised recently. My qualifications, skills, and experience align closely with your requirements for this role.<br><br>

<b>Technical Skills</b><br>
<ul>
<li><b>DevOps Tools:</b> Jenkins, Ansible, Docker, Kubernetes, Terraform, Git, GitHub Actions, GitLab, Gerrit, SonarQube</li>
<li><b>Programming and Scripting:</b> Python, Bash/Shell Scripting, Groovy, PowerShell, YAML, JSON</li>
<li><b>Cloud and Infrastructure:</b> AWS, Azure, GCP, OpenStack, VMware, RHEL, Kubernetes Cluster Security</li>
<li><b>Data Analysis and Reporting:</b> Power BI, SQL, MySQL, MariaDB, MongoDB, REST API</li>
</ul>

Please find my CV and supporting documents attached for your review. I would be delighted to discuss how I can contribute to your team and look forward to hearing from you soon about this exciting opportunity.<br><br>

<b>Kind regards,</b><br>
Paresh Patil<br>
<a href="https://www.linkedin.com/in/pareshrp/">LinkedIn</a><br>
<a href="https://wa.me/+919930583517">WhatsApp</a><br>
"""

# ---- Email Sending Logic ----
def send_email(receiver_email, subject, email_body, resume_file):
    sender_email = os.getenv("EMAIL_ID")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        st.error("Sender email credentials are missing. Set them as environment variables.")
        return

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(email_body, "html"))

    if resume_file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(resume_file.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={resume_file.name}")
        msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        st.success(f"✅ Email sent successfully to {receiver_email}!")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")

# ---- Send Button ----
if st.button("Send Email"):
    if not receiver_email:
        st.warning("Please enter recipient email.")
    elif not resume_file:
        st.warning("Please upload your resume.")
    else:
        send_email(receiver_email, f"Application for the position of {position_title}", email_body, resume_file)
