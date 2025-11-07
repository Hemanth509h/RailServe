"""
Centralized validation utilities for all forms in RailServe
Provides comprehensive validation functions for reuse across the application
"""

import re
from email_validator import validate_email, EmailNotValidError


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class FormValidator:
    """Comprehensive form validation utilities"""
    
    @staticmethod
    def validate_required_fields(fields_dict, field_names):
        """
        Validate that all required fields are present and non-empty
        
        Args:
            fields_dict: Dictionary of form fields
            field_names: List of required field names
            
        Returns:
            tuple: (is_valid, error_message)
        """
        missing_fields = []
        for field_name in field_names:
            value = fields_dict.get(field_name)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field_name.replace('_', ' ').title())
        
        if missing_fields:
            return False, f"Please fill in all required fields: {', '.join(missing_fields)}"
        return True, None
    
    @staticmethod
    def validate_username(username):
        """
        Validate username format
        
        Rules:
        - 3-50 characters
        - Alphanumeric, underscore, hyphen, dot only
        - Cannot start or end with special characters
        
        Args:
            username: String to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"
        
        username = username.strip()
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 50:
            return False, "Username cannot exceed 50 characters"
        
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$', username):
            return False, "Username can only contain letters, numbers, dots, hyphens, and underscores"
        
        # Check for SQL injection patterns
        dangerous_patterns = ['--', ';', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute', 'select', 'union', 'insert', 'update', 'delete', 'drop', 'create', 'alter']
        username_lower = username.lower()
        if any(pattern in username_lower for pattern in dangerous_patterns):
            return False, "Username contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_email_address(email):
        """
        Validate email format using email-validator library
        
        Args:
            email: Email address to validate
            
        Returns:
            tuple: (is_valid, error_message, normalized_email)
        """
        if not email:
            return False, "Email address is required", None
        
        email = email.strip()
        
        if len(email) > 254:  # RFC 5321
            return False, "Email address is too long", None
        
        try:
            # Validate email format
            email_info = validate_email(email, check_deliverability=False)
            normalized_email = email_info.normalized
            return True, None, normalized_email
        except EmailNotValidError as e:
            return False, "Please enter a valid email address", None
    
    @staticmethod
    def validate_password(password, confirm_password=None):
        """
        Validate password strength
        
        Rules:
        - Minimum 8 characters
        - Must contain at least one letter
        - Must contain at least one number
        - Can contain special characters: @$!%*?&
        
        Args:
            password: Password to validate
            confirm_password: Optional confirmation password
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password is too long (maximum 128 characters)"
        
        # Check for at least one letter
        if not re.search(r'[A-Za-z]', password):
            return False, "Password must contain at least one letter"
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        # Validate allowed characters
        if not re.match(r'^[A-Za-z\d@$!%*?&]+$', password):
            return False, "Password contains invalid characters. Allowed: letters, numbers, @$!%*?&"
        
        # Check confirmation if provided
        if confirm_password is not None and password != confirm_password:
            return False, "Passwords do not match"
        
        return True, None
    
    @staticmethod
    def validate_phone_number(phone, required=False):
        """
        Validate phone number (Indian format)
        
        Args:
            phone: Phone number to validate
            required: Whether phone is required
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not phone or not phone.strip():
            if required:
                return False, "Phone number is required"
            return True, None
        
        phone = phone.strip()
        
        # Remove common separators
        phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Indian phone number: 10 digits, optionally starting with +91
        if phone_clean.startswith('+91'):
            phone_clean = phone_clean[3:]
        elif phone_clean.startswith('91') and len(phone_clean) == 12:
            phone_clean = phone_clean[2:]
        
        if not re.match(r'^[6-9]\d{9}$', phone_clean):
            return False, "Please enter a valid 10-digit Indian phone number"
        
        return True, None
    
    @staticmethod
    def validate_text_field(text, field_name, min_length=1, max_length=500, required=True):
        """
        Validate generic text field
        
        Args:
            text: Text to validate
            field_name: Name of the field for error messages
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            required: Whether field is required
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not text or not text.strip():
            if required:
                return False, f"{field_name} is required"
            return True, None
        
        text = text.strip()
        
        if len(text) < min_length:
            return False, f"{field_name} must be at least {min_length} characters"
        
        if len(text) > max_length:
            return False, f"{field_name} cannot exceed {max_length} characters"
        
        return True, None
    
    @staticmethod
    def validate_number(value, field_name, min_val=None, max_val=None, required=True):
        """
        Validate numeric field
        
        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            required: Whether field is required
            
        Returns:
            tuple: (is_valid, error_message, parsed_value)
        """
        if value is None or value == '':
            if required:
                return False, f"{field_name} is required", None
            return True, None, None
        
        try:
            num = float(value) if '.' in str(value) else int(value)
            
            if min_val is not None and num < min_val:
                return False, f"{field_name} must be at least {min_val}", None
            
            if max_val is not None and num > max_val:
                return False, f"{field_name} cannot exceed {max_val}", None
            
            return True, None, num
            
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid number", None
    
    @staticmethod
    def sanitize_input(text):
        """
        Sanitize user input to prevent XSS and other injection attacks
        
        Args:
            text: Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        if not text:
            return text
        
        # Strip whitespace
        text = text.strip()
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        return text
