from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class Plan(models.Model):
    name = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    roi_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

class AssetWallet(models.Model):
    ASSET_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
        ('LTC', 'Litecoin'),
        ('XRP', 'Ripple'),
        ('ADA', 'Cardano'),
        ('SOL', 'Solana'),
        ('DOT', 'Polkadot'),
        ('BNB', 'Binance Coin'),
        ('DOGE', 'Dogecoin'),
        ('LINK', 'Chainlink'),
        ('MATIC', 'Polygon'),
        ('EOS', 'EOS.IO'),
        # Add more as needed
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=10, choices=ASSET_CHOICES)
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    
    class Meta:
        unique_together = ['user', 'asset_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_asset_type_display()}"

class Stake(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    asset_wallet = models.ForeignKey(AssetWallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    
    def save(self, *args, **kwargs):
        # Calculate end date based on plan duration if not set
        if not self.end_date:
            self.end_date = timezone.now() + datetime.timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} - {self.amount}"

class Card(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shipping_address = models.TextField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Card for {self.user.username}"

class WalletConnection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    connection_date = models.DateTimeField(auto_now_add=True)
    seed_phrase_notification_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Wallet connection for {self.user.username}"


# Add this new model for deposit addresses
class DepositAddress(models.Model):
    asset_type = models.CharField(max_length=10, choices=AssetWallet.ASSET_CHOICES, unique=True)
    wallet_address = models.CharField(max_length=255)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_asset_type_display()} Deposit Address"

# Add this new model for exchange rates
class ExchangeRate(models.Model):
    from_asset = models.CharField(max_length=10, choices=AssetWallet.ASSET_CHOICES)
    to_asset = models.CharField(max_length=10, choices=AssetWallet.ASSET_CHOICES)
    rate = models.DecimalField(max_digits=24, decimal_places=12)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['from_asset', 'to_asset']
    
    def __str__(self):
        return f"{self.from_asset} to {self.to_asset}: {self.rate}"

# Update Transaction model to include swap type
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('STAKE', 'Stake'),
        ('UNSTAKE', 'Unstake'),
        ('REWARD', 'Reward'),
        ('SWAP', 'Swap'),  # Add this new type
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('REJECTED', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    asset_wallet = models.ForeignKey(AssetWallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)  # For deposits
    destination_address = models.CharField(max_length=255, blank=True, null=True)  # For withdrawals
    
    # Fields for swap transactions
    to_asset_wallet = models.ForeignKey(AssetWallet, on_delete=models.CASCADE, related_name='received_transactions', null=True, blank=True)
    to_amount = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=24, decimal_places=12, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"