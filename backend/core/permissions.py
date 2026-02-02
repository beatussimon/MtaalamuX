"""Custom permissions for MtaalamuX API"""
from rest_framework import permissions
from .models import UserTier


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: only allow owners of an object to edit it.
    Read-only permissions are allowed to any authenticated user.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsProfessionalOrReadOnly(permissions.BasePermission):
    """
    Custom permission: only professionals can create/edit certain objects.
    Read-only permissions are allowed to any authenticated user.
    """
    
    def has_permission(self, request, view):
        # Allow read-only for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Require professional status for write operations
        if request.method in ['POST', 'PUT', 'PATCH']:
            return (
                request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.tier in [UserTier.PLUS, UserTier.PREMIUM]
            )
        
        return False


class IsOwner(permissions.BasePermission):
    """
    Custom permission: only allow owners to access the object.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsProfessionalOwner(permissions.BasePermission):
    """
    Custom permission: only professional owners can edit.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'professional') and
            obj.author == request.user.professional
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission: only admins can write, anyone can read.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff


class IsVerifiedProfessional(permissions.BasePermission):
    """
    Custom permission: only verified professionals can access.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            hasattr(request.user, 'professional') and
            request.user.professional.is_verified
        )


class CanUpgradeUser(permissions.BasePermission):
    """
    Custom permission: check if user can request upgrade.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user already has pending upgrade request
        from .models import UpgradeRequest
        has_pending = UpgradeRequest.objects.filter(
            user=request.user,
            status='pending'
        ).exists()
        
        return not has_pending


# =============================================================================
# TIER-BASED PERMISSIONS (Non-negotiable)
# =============================================================================

class IsBasicUser(permissions.BasePermission):
    """
    Permission for Basic tier users.
    Basic users can only browse and read - cannot initiate consultations or post content.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            hasattr(request.user, 'profile') and
            request.user.profile.tier == UserTier.BASIC
        )


class IsProfessionalUser(permissions.BasePermission):
    """
    Permission for Professional tier and above.
    Professional users can initiate consultations and use messaging.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            hasattr(request.user, 'profile') and
            request.user.profile.tier in [UserTier.PLUS, UserTier.PREMIUM]
        )


class IsPremiumUser(permissions.BasePermission):
    """
    Permission for Premium tier users only.
    Premium users can post articles, research, and sell items.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            hasattr(request.user, 'profile') and
            request.user.profile.tier == UserTier.PREMIUM
        )


class CanPostContent(permissions.BasePermission):
    """
    Permission to check if user can post articles/research.
    Only Premium users can post content.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        # Check tier
        if request.user.profile.tier != UserTier.PREMIUM:
            return False
        
        # Must be a verified professional
        return hasattr(request.user, 'professional') and request.user.professional.is_verified


class CanInitiateConsultation(permissions.BasePermission):
    """
    Permission to check if user can initiate consultations.
    Basic users cannot initiate consultations.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        return request.user.profile.can_initiate_consultation


class CanSellItems(permissions.BasePermission):
    """
    Permission to check if user can sell digital items/merch.
    Only Premium users can sell.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        return request.user.profile.can_sell_items


class IsVerifiedExpert(permissions.BasePermission):
    """
    Permission for verified experts (green or gold checkmark).
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            hasattr(request.user, 'professional') and
            request.user.professional.has_verification
        )


class IsGoldVerifiedExpert(permissions.BasePermission):
    """
    Permission for gold-verified experts only.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            hasattr(request.user, 'professional') and
            request.user.professional.verification_level == 'gold'
        )


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission: staff can do everything, others can only read.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff
