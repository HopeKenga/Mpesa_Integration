from django.db import models
from django.utils import timezone

# Enumerations
class PaymentMethod(models.TextChoices):
    MPESA = 'MPESA', 'Mpesa'
    BANK = 'BANK', 'Bank'
    CASH = 'CASH', 'Cash'

class PaymentStatus(models.TextChoices):
    PAID = 'PAID', 'Paid'
    UNPAID = 'UNPAID', 'Unpaid'

class TransactionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PAID = 'PAID', 'Paid'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELED = 'CANCELED', 'Canceled'

# Models
class User(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

class Ride(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, unique=True, related_name='invoices')
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

class MpesaTransaction(models.Model):
    merchant_request_id = models.CharField(max_length=255)
    checkout_request_id = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255)
    transaction_time = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    transaction_amount = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

class B2CTransaction(models.Model):
    transaction_amount = models.FloatField()
    transaction_receipt = models.CharField(max_length=255)
    receiver_party_public_name = models.CharField(max_length=255)
    transaction_completed_date_time = models.CharField(max_length=255)
    b2c_recipient_is_registered_customer = models.CharField(max_length=255)
    b2c_utility_account_available_funds = models.FloatField()
    b2c_working_account_available_funds = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

class Payment(models.Model):
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.MPESA)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField()
    merchant_request_id = models.CharField(max_length=255, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=255, blank=True, null=True)
    reference_code = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

class TransactionEscrow(models.Model):
    transaction_number = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_escrows')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='transaction_escrows')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transaction_escrows')
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
