import streamlit as st
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Fetch credentials from Streamlit secrets
sender_email = st.secrets["EMAIL_ID"]
sender_password = st.secrets["EMAIL_PASSWORD"]

def send_email(to_emails, subject, body, attachment=None):
    try:
        recipient_list = [email.strip() for email in to_emails.split(",")]

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipient_list)
        msg['Subject'] = subject

        # Attach the HTML body
        msg.attach(MIMEText(body, 'html'))

        # Attach file if uploaded
        if attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment.name}')
            msg.attach(part)

        # SMTP setup
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_list, text)
        server.quit()
        
        return "Email sent successfully!"
    
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("📧 Bulk Email Sender")

to_emails = st.text_input("Enter recipient emails (comma-separated):")
position_title = st.text_input("Enter Position Title:", value="DevOps Engineer")
resume = st.file_uploader("Upload your resume (PDF)", type=['pdf'])

if st.button("Send Email"):
    email_subject = f"Application for the position of {position_title}"
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Dear Hiring Manager/Recruiter,</p>

        <p>I am writing to express my interest in the position of <b>{position_title}</b> as advertised recently. My qualifications, skills, and experience align closely with your requirements for this role.</p>

        <h3 style="color: #007bff;">Technical Skills</h3>
        <ul>
            <li><b>DevOps Tools:</b> Jenkins, Ansible, Docker, Kubernetes, Terraform, Git, GitHub Actions, GitLab, Gerrit, SonarQube</li>
            <li><b>Programming and Scripting:</b> Python, Bash/Shell Scripting, Groovy, PowerShell, YAML, JSON</li>
            <li><b>Cloud and Infrastructure:</b> AWS, Azure, GCP, OpenStack, VMware, RHEL, Kubernetes Cluster Security</li>
            <li><b>Data Analysis and Reporting:</b> Power BI, SQL, MySQL, MariaDB, MongoDB, REST API</li>
        </ul>

        <p>Please find my resume attached for your review. I would be delighted to discuss how I can contribute to your team and look forward to hearing from you soon about this exciting opportunity.</p>

        <p>Kind regards,</p>
        <p><b>Paresh Patil</b></p>
        <p>
            <a href="https://www.linkedin.com/in/pareshrp/" style="color: #007bff;">LinkedIn</a> | 
            <a href="https://wa.me/+919930583517" style="color: #007bff;">WhatsApp</a>
        </p>
    </body>
    </html>
    """

    result = send_email(to_emails, email_subject, email_body, resume)
    st.success(result)
