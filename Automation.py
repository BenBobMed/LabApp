import win32com.client as win32

def send_email_via_outlook(to, subject, body):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = to
    mail.Subject = subject
    mail.Body = body
    mail.Send()

# Example usage
send_email_via_outlook('ibnboubakr.mohamed@gmail.com', 'Subject', 'This is the email body.')
