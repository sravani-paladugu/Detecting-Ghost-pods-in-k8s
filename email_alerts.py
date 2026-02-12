import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-security-bot@gmail.com"
SENDER_PASSWORD = "your-app-password"  # Use App Passwords, not your real password
RECEIVER_EMAIL = "soc-team@yourcompany.com"
HONEYPOT_LABEL = "app=shadow-db"

def send_email_alert(log_line):
    """Sub-function: Sends a critical alert email to the SOC team."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "🚨 CRITICAL: Honeypot Breach Detected in K8s"

    body = f"""
    Security Alert: Internal Lateral Movement Detected.
    
    A Shadow Service (Honeypot) was accessed by an unauthorized source.
    
    RAW LOG ENTRY:
    {log_line}
    
    Recommended Action:
    1. Identify Source IP from the log above.
    2. Run 'kubectl get pods -A -o wide | grep <Source_IP>' to find the compromised pod.
    3. Isolate the pod immediately.
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[+] Email Alert Sent Successfully to {RECEIVER_EMAIL}")
    except Exception as e:
        print(f"[-] Failed to send email: {e}")

def monitor_honeypot():
    """Continuous Daemon: Streams logs and triggers alerts."""
    print(f"[*] Monitoring Shadow Services ({HONEYPOT_LABEL})...")
    
    # Streaming command
    cmd = ["kubectl", "logs", "-l", HONEYPOT_LABEL, "--follow", "--tail=0"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    try:
        for line in process.stdout:
            # Detect the interaction
            if "POST /api/v1/admin/login" in line:
                print(f"\n[!!!] BREACH DETECTED: {line.strip()}")
                send_email_alert(line.strip())
    except KeyboardInterrupt:
        process.kill()
        print("\n[*] Monitoring Stopped.")

if __name__ == "__main__":
    monitor_honeypot()
