"""Custom throttling classes for MtaalamuX API"""
from rest_framework.throttling import UserRateThrottle


class CustomUserRateThrottle(UserRateThrottle):
    """
    Custom throttle for authenticated users with higher limits.
    """
    rate = '500/hour'


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle for burst requests (login, registration, etc.).
    """
    rate = '10/minute'


class ArticleCreateThrottle(UserRateThrottle):
    """
    Throttle for article creation to prevent spam.
    """
    rate = '5/hour'


class MessageThrottle(UserRateThrottle):
    """
    Throttle for messaging to prevent spam.
    """
    rate = '30/hour'


class JobPostThrottle(UserRateThrottle):
    """
    Throttle for job posting.
    """
    rate = '10/hour'


class ReviewThrottle(UserRateThrottle):
    """
    Throttle for review submission.
    """
    rate = '5/hour'
