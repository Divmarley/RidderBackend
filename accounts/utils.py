from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging
from django.core.mail import send_mail
logger = logging.getLogger(__name__)

def send_verification_email(user):
    """
    Send verification email with HTML template
    """
    try:
        # Context for email template
        context = {
            'user': user,
            'verification_code': user.verification_code,
            'logo_url': f"{settings.SITE_URL}/static/logolightnobg.png"
        }
        
        # Render HTML content
        html_content = render_to_string(
            'emails/verification_email.html', 
            context
        )
        
        # Create plain text content
        text_content = strip_tags(html_content)
        
        # Create email
        subject = 'Verify Your Email - Yawigo'
        from_email = settings.EMAIL_HOST_USER
        to = [user.email]
        
        # Create message container
        msg = EmailMultiAlternatives(
            subject, 
            text_content, 
            from_email, 
            to
        )
        
        # Attach HTML content
        msg.attach_alternative(html_content, "text/html")
        
        # Send email
        msg.send()
        return True, None
        
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {str(e)}")
        return False, str(e)
    




 

def send_temporary_password_email(email, temp_password):
    # subject = "Your Temporary Password"
    # message = f"""
    #             Hello,

    #             A request was made to reset your Ubintax password.

    #             Your temporary password is: {temp_password}

    #             Please log in and change your password immediately.

    #             Thank you.
    #         """

    # send_mail(
    #     subject,
    #     message,
    #     settings.DEFAULT_FROM_EMAIL,
    #     [email],
    #     fail_silently=False,
    # )


    try:
        # Context for email template
        context = {
            'email': email,
            'temp_password': temp_password,
            'logo_url': f"{settings.SITE_URL}/static/logolightnobg.png"
        }
        
        # Render HTML content
        html_content = render_to_string(
            'password/reset_email.html', 
            context
        )
        
        # Create plain text content
        text_content = strip_tags(html_content)
        
        # Create email
        subject = "Your Temporary Password"
        from_email = settings.EMAIL_HOST_USER
        to = [email]
        
        # Create message container
        msg = EmailMultiAlternatives(
            subject, 
            text_content, 
            from_email, 
            to
        )
        
        # Attach HTML content
        msg.attach_alternative(html_content, "text/html")
        
        # Send email
        msg.send()
        return True, None
        
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {str(e)}")
        return False, str(e)
    


