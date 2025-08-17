import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_email_delivery():
    # Gmail SMTP settings
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'somuuppara43@gmail.com'
    password = 'lucsiluqpzqgmzxt'  # Your Gmail App Password
    
    # Test recipients
    test_recipients = [
        'aitsprathyun@gmail.com',
        'somuuppara39@gmail.com',
        'somuuppara43@gmail.com'  # Send to yourself as well
    ]
    
    for receiver_email in test_recipients:
        print(f"\n🧪 Testing email delivery to: {receiver_email}")
        
        # Create the message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"🧪 Email Delivery Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Reply-To"] = sender_email
        
        # HTML content with tracking info
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #f5ebe0, #ffb300); padding: 30px; border-radius: 12px;">
              <h2 style="color: #6d4c41; text-align: center;">📧 Email Delivery Test</h2>
              <p style="color: #3e2723; font-size: 16px;">This is a test email from your Personal Storage app.</p>
              
              <div style="background: #ffb300; color: #3e2723; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <strong>✅ If you receive this email, delivery is working!</strong>
              </div>
              
              <h3 style="color: #6d4c41;">Test Details:</h3>
              <ul style="color: #3e2723;">
                <li><strong>Sent to:</strong> {receiver_email}</li>
                <li><strong>From:</strong> {sender_email}</li>
                <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}</li>
                <li><strong>Server:</strong> Gmail SMTP</li>
              </ul>
              
              <p style="color: #6d4c41; font-size: 12px; margin-top: 30px;">
                Please reply to this email to confirm receipt.
              </p>
            </div>
          </body>
        </html>
        """
        
        # Plain text version
        text = f"""
        EMAIL DELIVERY TEST
        
        This is a test email from your Personal Storage app.
        
        Test Details:
        - Sent to: {receiver_email}
        - From: {sender_email}
        - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}
        - Server: Gmail SMTP
        
        If you receive this email, delivery is working!
        Please reply to confirm receipt.
        """
        
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        message.attach(part1)
        message.attach(part2)
        
        # Send the email and track status
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.set_debuglevel(1)  # Enable detailed logging
            server.starttls()
            server.login(sender_email, password)
            
            # Send email
            result = server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            
            if result:
                print(f"⚠️  Email sent with warnings to {receiver_email}: {result}")
            else:
                print(f"✅ Email sent successfully to {receiver_email}")
                
        except smtplib.SMTPRecipientsRefused as e:
            print(f"❌ Recipient refused: {e}")
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Authentication error: {e}")
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error: {e}")
        except Exception as e:
            print(f"❌ Failed to send email to {receiver_email}: {e}")

def check_gmail_settings():
    print("🔍 Checking Gmail account settings...")
    print("\n📋 Please verify these settings in your Gmail account:")
    print("1. ✅ 2-Step Verification is enabled")
    print("2. ✅ App Password is generated for 'Mail'")
    print("3. ✅ App Password is 16 characters: lucsiluqpzqgmzxt")
    print("4. ✅ 'Less secure app access' is DISABLED (use App Password instead)")
    print("5. ✅ IMAP is enabled in Gmail settings")
    
    print("\n🚨 Common delivery issues:")
    print("1. Emails may be going to SPAM/JUNK folder")
    print("2. Recipient's email provider may block automated emails")
    print("3. Your Gmail account may have sending limits")
    print("4. Recipient email addresses may be invalid")

if __name__ == "__main__":
    print("🚀 Starting Email Delivery Test...")
    check_gmail_settings()
    test_email_delivery()
    
    print("\n" + "="*60)
    print("📝 NEXT STEPS:")
    print("1. Check recipient's SPAM/JUNK folders")
    print("2. Ask recipients to check their email")
    print("3. Send test email to your own Gmail (somuuppara43@gmail.com)")
    print("4. If still no delivery, try different email provider")
    print("="*60)
