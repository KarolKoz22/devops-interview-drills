#lets write a script to monitor state of a service and sending alerts if it is down

#suggest the code

import subprocess
import email
import smtlib

def check_service_status(service_name):
    try:
        # Use systemctl to check the status of the service
        result = subprocess.run(['systemctl', 'is-active', service_name], capture_output=True, text=True)
        if result.returncode == 0:
            return True  # Service is active
        else:
            return False  # Service is inactive or failed
    except Exception as e:
        print(f"Error checking service status: {e}")
        return False

def send_email_alert(service_name):
    # Set up the email parameters
    sender = 'exampleemail@example.com'
    recipient = 'exampleemail2@example.com'
    subject = f'Alert: {service_name} is down'
    body = f'The service {service_name} is currently down. Please check the system
    immediately.'

    