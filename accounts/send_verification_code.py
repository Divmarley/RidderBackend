from twilio.rest import Client
from django.conf import settings

def send_verification_code(phone_number, verification_code):
    # Your Twilio Account SID and Auth Token
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    # Initialize Twilio Client
    client = Client(account_sid, auth_token)

    # Compose and send SMS message
    message = client.messages.create(
        body=f"Your verification code is: {verification_code}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )

    # Optionally, you can log the message SID or handle any errors
    print(f"Message SID: {message.sid}")
