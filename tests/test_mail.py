import smtplib

smtp_host = "smtp.gmail.com"
smtp_port = 587
username = "example@gmail.com"
password = "my 16 character app password"

server = smtplib.SMTP(smtp_host, smtp_port)
server.starttls()
server.login(username, password)

server.sendmail(
    username,
    username,
    "Subject: Test\n\nTo jest test z systemu."
)

server.quit()

print("Mail sent.")