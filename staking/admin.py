from django.contrib import admin
from .models import Plan, AssetWallet, Transaction, Stake, Card, WalletConnection, DepositAddress, ExchangeRate
from decimal import Decimal


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'roi_percentage', 'minimum_amount')

@admin.register(AssetWallet)
class AssetWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'asset_type', 'balance')
    list_filter = ('asset_type',)
    search_fields = ('user__username',)

@admin.register(Stake)
class StakeAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'start_date', 'end_date', 'is_active')
    list_filter = ('plan', 'is_active', 'start_date')
    search_fields = ('user__username',)
    actions = ['complete_stakes']
    
    def complete_stakes(self, request, queryset):
        completed_count = 0
        
        for stake in queryset.filter(is_active=True):
            try:
                # Calculate reward amount based on ROI percentage
                roi_decimal = stake.plan.roi_percentage / Decimal('100')
                reward_amount = stake.amount * roi_decimal
                
                # Get the wallet
                wallet = stake.asset_wallet
                
                # Return the original staked amount plus the reward
                total_return = stake.amount + reward_amount
                wallet.balance += total_return
                wallet.save()
                
                # Create a transaction record for the reward
                Transaction.objects.create(
                    user=stake.user,
                    asset_wallet=wallet,
                    transaction_type='REWARD',
                    amount=reward_amount,
                    status='CONFIRMED',
                )
                
                # Mark the stake as inactive
                stake.is_active = False
                stake.save()
                
                completed_count += 1
            
            except Exception as e:
                self.message_user(request, f"Error completing stake #{stake.id}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"Successfully completed {completed_count} stakes and distributed rewards.")
    complete_stakes.short_description = "Complete selected stakes and distribute rewards"

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'order_date', 'tracking_number')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username', 'tracking_number')
    
    actions = ['update_to_processing', 'update_to_shipped', 'update_to_delivered']
    
    def update_to_processing(self, request, queryset):
        queryset.update(status='PROCESSING')
        self.message_user(request, f"{queryset.count()} cards updated to processing.")
    update_to_processing.short_description = "Mark selected cards as processing"
    
    def update_to_shipped(self, request, queryset):
        queryset.update(status='SHIPPED')
        self.message_user(request, f"{queryset.count()} cards updated to shipped.")
    update_to_shipped.short_description = "Mark selected cards as shipped"
    
    def update_to_delivered(self, request, queryset):
        queryset.update(status='DELIVERED')
        self.message_user(request, f"{queryset.count()} cards updated to delivered.")
    update_to_delivered.short_description = "Mark selected cards as delivered"

@admin.register(WalletConnection)
class WalletConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'connection_date', 'seed_phrase_notification_sent')
    list_filter = ('connection_date', 'seed_phrase_notification_sent')
    search_fields = ('user__username',)



# Register the new models
@admin.register(DepositAddress)
class DepositAddressAdmin(admin.ModelAdmin):
    list_display = ('asset_type', 'wallet_address', 'is_active', 'updated_at')
    list_filter = ('asset_type', 'is_active')
    search_fields = ('wallet_address',)
    actions = ['activate_addresses', 'deactivate_addresses']
    
    def activate_addresses(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} deposit addresses were activated.")
    activate_addresses.short_description = "Activate selected deposit addresses"
    
    def deactivate_addresses(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} deposit addresses were deactivated.")
    deactivate_addresses.short_description = "Deactivate selected deposit addresses"

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('from_asset', 'to_asset', 'rate', 'last_updated')
    list_filter = ('from_asset', 'to_asset')
    search_fields = ('from_asset', 'to_asset')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('from_asset', 'to_asset')
        return ()

# Update the Transaction admin to handle swaps
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'status', 'timestamp')
    list_filter = ('transaction_type', 'status', 'timestamp')
    search_fields = ('user__username', 'transaction_hash', 'destination_address')
    
    actions = ['approve_transactions', 'reject_transactions']
    
    def approve_transactions(self, request, queryset):
        # Update selected transactions to confirmed
        queryset.update(status='CONFIRMED')
        
        # Update wallet balances for deposits
        for transaction in queryset.filter(transaction_type='DEPOSIT', status='CONFIRMED'):
            wallet = transaction.asset_wallet
            wallet.balance += transaction.amount
            wallet.save()
            
        # Process withdrawals
        for transaction in queryset.filter(transaction_type='WITHDRAWAL', status='CONFIRMED'):
            # In a real app, you'd trigger the actual blockchain transaction here
            pass
            
        # Process swaps - they're already processed when created, so nothing to do here
            
        self.message_user(request, f"{queryset.count()} transactions were approved.")
    approve_transactions.short_description = "Approve selected transactions"
    
    def reject_transactions(self, request, queryset):
        # For withdrawals that are rejected, refund the amount back to the wallet
        for transaction in queryset.filter(transaction_type='WITHDRAWAL', status='PENDING'):
            wallet = transaction.asset_wallet
            wallet.balance += transaction.amount
            wallet.save()
            
        # For swaps that are rejected, refund both wallets
        for transaction in queryset.filter(transaction_type='SWAP', status='PENDING'):
            from_wallet = transaction.asset_wallet
            to_wallet = transaction.to_asset_wallet
            
            from_wallet.balance += transaction.amount
            if to_wallet and transaction.to_amount:
                to_wallet.balance -= transaction.to_amount
                
            from_wallet.save()
            if to_wallet:
                to_wallet.save()
            
        queryset.update(status='REJECTED')
        self.message_user(request, f"{queryset.count()} transactions were rejected.")
    reject_transactions.short_description = "Reject selected transactions"