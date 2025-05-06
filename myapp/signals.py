from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.db import transaction
from django.dispatch import receiver
from django.utils.timezone import now

from myapp.middleware import get_current_user
from myapp.models import DatabaseLog, OperationLookup, TableLookup, UserProfile, FinanceReport

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

from threading import local
import logging

logger = logging.getLogger("myapp.signals")
local = local()

@receiver(valid_ipn_received)
def process_payment(sender, **kwargs):
    logger.info("IPN signal received")
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        if ipn_obj.receiver_email != "business@headlights.com":
            logger.warning(f"Incorrect receiver email, received: {ipn_obj.receiver_email}")
            return

        invoice = FinanceReport.objects.get(finance_report_id=ipn_obj.invoice)
        invoice.paid = True
        invoice.save()

valid_ipn_received.connect(process_payment)

def prevent_recursion():
    """Prevent recursion by checking if the signal is already handled."""
    return getattr(local, "in_signal", False)

def set_in_signal(value):
    """Set the flag indicating that the signal is being processed."""
    local.in_signal = value

@receiver(post_save)
def log_create_or_update(sender, instance, created, **kwargs):
    """Logs create and update operations for all models."""

    # Don't write logs in tests or if a log is already being written.
    if getattr(settings, "TESTING", False) or prevent_recursion():
        return

    set_in_signal(True)

    try:
        # 1 = CREATE, 3 = UPDATE
        operation_id = 1 if created else 3

        # Get UserProfile object if action performed by user.
        user = get_current_user()
        user_profile = UserProfile.objects.filter(auth_id=user).first()

        # Use atomic commits to create new DatabaseLog
        with transaction.atomic():
            DatabaseLog.objects.create(
                log_time=now(),
                user_id=user_profile,
                affected_table_id=TableLookup.objects.get(table_name=sender.__name__),
                operation_performed=OperationLookup.objects.get(pk=operation_id),
                successful=True
            )
    except Exception as e:
        logger.info(f"Failed to save logging to DB: {e}")
    finally:
        set_in_signal(False)

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Logs delete operations for all models."""

    # Don't write logs in tests or if a log is already being written.
    if getattr(settings, "TESTING", False) or prevent_recursion():
        return

    set_in_signal(True)

    try:
        # 4 = DELETE
        operation_id = 4

        # Get UserProfile object if action performed by user.
        user = get_current_user()
        user_profile = UserProfile.objects.filter(auth_id=user).first()

        # Use atomic commits to create new DatabaseLog
        with transaction.atomic():
            DatabaseLog.objects.create(
                log_time=now(),
                user_id=user_profile,  
                affected_table_id=TableLookup.objects.get(table_name=sender.__name__),
                operation_performed=OperationLookup.objects.get(pk=operation_id),
                successful=True
            )
    except Exception as e:
        logger.info(f"Failed to save logging to DB: {e}")
    finally:
        set_in_signal(False)
