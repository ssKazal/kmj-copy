"""This file contains project global context value. 
Mostly needed for admin template.
"""

from django.conf import settings


def supported_currencies(request):
    """Showing the supported currencies while adding/updating
    balance of skilled_worker/customer from admin panel

        Returns:
            Context value for admin template
    """
    return {
        "skilled_worker_supported_currency": settings.SKILLED_WORKER_SUPPORTED_CURRENCY,
        "customer_supported_currency": settings.CUSTOMER_SUPPORTED_CURRENCY,
    }
