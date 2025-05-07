from django.core.management.base import BaseCommand
from staking.models import ExchangeRate, AssetWallet
from decimal import Decimal

class Command(BaseCommand):
    help = 'Initialize exchange rates for cryptocurrencies'

    def handle(self, *args, **options):
        # Real-world exchange rates (as of your example)
        # These are rates for converting TO USDT (USD equivalent)
        usdt_rates = {
            'BTC': Decimal('97305.60'),  # 1 BTC = $97,305.60
            'ETH': Decimal('3000.00'),   # 1 ETH = $3,000.00
            'USDT': Decimal('1.00'),     # 1 USDT = $1.00
            'LTC': Decimal('85.00'),
            'XRP': Decimal('0.50'),
            'ADA': Decimal('0.40'),
            'SOL': Decimal('150.00'),
            'DOT': Decimal('6.50'),
            'BNB': Decimal('550.00'),
            'DOGE': Decimal('0.15'),
            'LINK': Decimal('15.00'),
            'MATIC': Decimal('0.60'),
            'EOS': Decimal('0.70'),
        }
        
        # Get all asset types
        asset_types = [choice[0] for choice in AssetWallet.ASSET_CHOICES]
        
        created_count = 0
        updated_count = 0
        
        # Create rates for all pairs
        for from_asset in asset_types:
            for to_asset in asset_types:
                if from_asset != to_asset:
                    # Calculate rate based on USD values
                    if from_asset in usdt_rates and to_asset in usdt_rates:
                        # Rate = (USD value of from_asset) / (USD value of to_asset)
                        # For example: BTC to ETH rate = $97,305.60 / $3,000 = 32.435
                        if to_asset == 'USDT':
                            # Direct rate to USDT
                            rate = usdt_rates[from_asset]
                        elif from_asset == 'USDT':
                            # USDT to other crypto
                            rate = Decimal('1') / usdt_rates[to_asset]
                        else:
                            # Crypto to crypto
                            rate = usdt_rates[from_asset] / usdt_rates[to_asset]
                        
                        # Create or update the exchange rate
                        exchange_rate, created = ExchangeRate.objects.update_or_create(
                            from_asset=from_asset,
                            to_asset=to_asset,
                            defaults={'rate': rate}
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} and updated {updated_count} exchange rates'))