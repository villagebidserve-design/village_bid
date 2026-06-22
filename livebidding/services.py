"""
OTP and authentication services for live bidding
"""
import random
import string
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model
from livebidding.models import OTPVerification
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class OTPService:
    """Service for handling OTP generation, sending, and verification"""
    
    @staticmethod
    def generate_otp(length=None):
        """Generate a random OTP code"""
        if length is None:
            length = settings.OTP_CODE_LENGTH
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def send_otp_email(email, otp_code):
        """Send OTP via email"""
        subject = 'Your Village Bid verification code'
        body = (
            f"Hello,\n\nYour Village Bid verification code is: {otp_code}.\n"
            f"It is valid for {settings.OTP_EXPIRY_SECONDS // 60} minutes.\n\n"
            "If you did not request this code, please ignore this email.\n\n"
            "Thank you,\nVillage Bid Team"
        )
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Village Bid <noreply@villagebid.local>')
        try:
            send_mail(subject, body, from_email, [email], fail_silently=False)
            logger.info(f"OTP email sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_otp(email):
        """Generate and send OTP to email address"""
        otp_code = OTPService.generate_otp()
        expiry_time = timezone.now() + timedelta(seconds=settings.OTP_EXPIRY_SECONDS)
        otp_record, created = OTPVerification.objects.update_or_create(
            email=email,
            defaults={
                'otp_code': otp_code,
                'is_verified': False,
                'attempts': 0,
                'expires_at': expiry_time,
                'updated_at': timezone.now(),
            }
        )
        
        success = OTPService.send_otp_email(email, otp_code)
        if success:
            logger.info(f"OTP sent successfully to {email}")
            response = {
                'success': True,
                'message': 'OTP sent successfully',
                'email': email,
            }
        else:
            logger.error(f"Failed to send OTP to {email}")
            if settings.DEBUG:
                logger.warning(f"DEBUG MODE: OTP for {email} is {otp_code}")
            response = {
                'success': False,
                'message': 'Failed to send OTP',
            }
        
        # In DEBUG mode, return the OTP code for development/testing
        if settings.DEBUG:
            response['otp_code'] = otp_code
            response['message'] = f'[DEV MODE] OTP sent. Code: {otp_code}'
        
        return response
    
    @staticmethod
    def verify_otp(email, otp_code, create_user=True):
        """Verify OTP code for an email address"""
        try:
            otp_record = OTPVerification.objects.get(email=email)
        except OTPVerification.DoesNotExist:
            return {
                'success': False,
                'message': 'OTP not found or expired',
                'user': None,
            }
        
        if otp_record.is_expired():
            return {
                'success': False,
                'message': 'OTP has expired',
                'user': None,
            }
        
        if otp_record.attempts >= settings.OTP_MAX_ATTEMPTS:
            return {
                'success': False,
                'message': 'Maximum OTP attempts exceeded',
                'user': None,
            }
        
        otp_record.attempts += 1
        otp_record.save()
        
        if otp_record.otp_code != otp_code:
            return {
                'success': False,
                'message': f'Invalid OTP. Attempts remaining: {settings.OTP_MAX_ATTEMPTS - otp_record.attempts}',
                'user': None,
            }
        
        otp_record.is_verified = True
        otp_record.save()
        
        user = User.objects.filter(email=email).first()
        if user is None:
            if create_user:
                base_username = email.split('@')[0] or 'user'
                username = base_username
                count = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{count}"
                    count += 1
                user = User.objects.create(
                    username=username,
                    email=email,
                    email_verified=True,
                )
        else:
            user.email_verified = True
            user.save()
        
        logger.info(f"OTP verified successfully for {email}")
        return {
            'success': True,
            'message': 'OTP verified successfully',
            'user': user,
        }
    
    @staticmethod
    def resend_otp(email):
        """Resend OTP to email address"""
        try:
            otp_record = OTPVerification.objects.get(email=email)
            if otp_record.is_verified:
                return {
                    'success': False,
                    'message': 'Email already verified',
                }
            time_diff = (timezone.now() - otp_record.updated_at).total_seconds()
            if time_diff < 30:
                return {
                    'success': False,
                    'message': f'Please wait {30 - int(time_diff)} seconds before requesting another OTP',
                }
        except OTPVerification.DoesNotExist:
            pass
        return OTPService.send_otp(email)
