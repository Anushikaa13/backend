"""
Security utilities: Rate limiting, input validation, and hardening
"""
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from functools import wraps
import time
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# ===========================
# RATE LIMITING
# ===========================
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
RATE_LIMITS = {
    "signup": "5/minute",      # 5 signups per minute per IP
    "login": "10/minute",      # 10 login attempts per minute per IP
    "products": "30/minute",   # 30 product operations per minute per IP
    "get_products": "60/minute", # 60 reads per minute per IP
}


# ===========================
# INPUT SANITIZATION
# ===========================
def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input to prevent injection attacks
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Limit length
    value = value[:max_length]
    
    # Strip leading/trailing whitespace
    return value.strip()


def validate_price(price: float) -> float:
    """
    Validate price input
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if price > 1_000_000:
        raise ValueError("Price exceeds maximum limit of 1,000,000")
    if not isinstance(price, (int, float)):
        raise ValueError("Price must be a number")
    return round(price, 2)


def validate_quantity(quantity: int) -> int:
    """
    Validate quantity input
    """
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    if quantity > 1_000_000:
        raise ValueError("Quantity exceeds maximum limit of 1,000,000")
    if not isinstance(quantity, int):
        raise ValueError("Quantity must be an integer")
    return quantity


# ===========================
# REQUEST LOGGING & MONITORING
# ===========================
class RequestLogger:
    """Log and monitor API requests"""
    
    def __init__(self):
        self.request_times: Dict[str, list] = {}
    
    def log_request(self, endpoint: str, user: str, status_code: int, duration: float):
        """Log request details"""
        logger.info(
            f"Request: {endpoint} | User: {user} | Status: {status_code} | Duration: {duration:.3f}s"
        )
    
    def check_suspicious_activity(self, ip_address: str, endpoint: str) -> bool:
        """Check for suspicious patterns"""
        key = f"{ip_address}:{endpoint}"
        
        if key not in self.request_times:
            self.request_times[key] = []
        
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_times[key] = [
            t for t in self.request_times[key] 
            if current_time - t < 60
        ]
        
        # Add current request
        self.request_times[key].append(current_time)
        
        # Flag if more than 100 requests in 1 minute
        if len(self.request_times[key]) > 100:
            logger.warning(
                f"Suspicious activity detected: {len(self.request_times[key])} requests "
                f"from {ip_address} to {endpoint} in 1 minute"
            )
            return True
        
        return False


request_logger = RequestLogger()


# ===========================
# SECURITY HEADERS
# ===========================
def get_security_headers() -> Dict[str, str]:
    """Get security headers for responses"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
    }


# ===========================
# SQL INJECTION PREVENTION
# ===========================
def validate_sort_parameter(sort_by: str, allowed_fields: list) -> str:
    """Validate sort parameter to prevent SQL injection"""
    if sort_by not in allowed_fields:
        raise ValueError(f"Invalid sort field. Allowed: {', '.join(allowed_fields)}")
    return sort_by


def validate_sort_order(order: str) -> str:
    """Validate sort order"""
    if order.lower() not in ["asc", "desc"]:
        raise ValueError("Sort order must be 'asc' or 'desc'")
    return order.lower()
