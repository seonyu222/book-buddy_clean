# send_email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(name, user_email, book_title, message):
    try:
        sender_email = "your_email@gmail.com"           # 너의 Gmail 주소
        sender_password = "your_app_password"           # 앱 비밀번호
        receiver_email = "YOUR_RECEIVING_EMAIL@example.com"  # 받을 이메일 주소

        subject = f"[BookBuddy 퀴즈 요청] {book_title} 요청 by {name}"
        body = f"""
📚 BookBuddy 퀴즈 요청 도착:

👤 이름: {name}
📧 이메일: {user_email}
📖 요청 책 제목: {book_title}
💬 메시지:
{message}
        """

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        return True
    except Exception as e:
        print("❌ 이메일 전송 오류:", e)
        return False
