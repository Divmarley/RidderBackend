from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

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
            # 'logo_url': f"{settings.SITE_URL}/static/logolightnobg.png"
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