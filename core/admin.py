from django.contrib import admin
from django.db.models import Avg
from . import models
from datetime import datetime

class IpoAdmin(admin.ModelAdmin):

    actions = ["calculate_listing_price"]

    @admin.action(description="Calculate listing price")
    def calculate_listing_price(self, request, queryset):

        ipo_subscriptions = models.IpoSubscription.objects.all()
        ipos = queryset
        
        for ipo in ipos:
            ipo_subs = ipo_subscriptions.filter(ipo=ipo)
            total_bid_price = 0
            total_bid_qty = 0
            for subs in ipo_subs:
                total_bid_price += subs.bid_price * (subs.bid_quantity * ipo.lot_size)
                total_bid_qty += (subs.bid_quantity * ipo.lot_size)
            avg_bid_price = 0
            if total_bid_qty > 0:
                avg_bid_price = total_bid_price / total_bid_qty
            avg_bid_price = int(avg_bid_price)
            ipo.listing_price=avg_bid_price
            ipo.total_shares_demanded = total_bid_qty
            stock_id = ipo.stock.id
            stock = models.Stock.objects.get(id=stock_id)
            stock.is_listed = True
            stock.current_price = avg_bid_price
            stock.price_history.append({'price': str(avg_bid_price), 'datetime': str(datetime.now())})
            stock.price_history.append({'price': str(avg_bid_price), 'datetime': str(datetime.now())})
            ipo.save()
            stock.save()


class IpoSubscriptionAdmin(admin.ModelAdmin):

    actions = ["allocate_shares"]

    @admin.action(description="Allocate shares")
    def allocate_shares(self, request, queryset):
        
        ipo_subscriptions = queryset

        # Subtract the no of shares which are below the avg bid price
        for subs in ipo_subscriptions:
            ipo_id = subs.ipo.id
            ipo = models.Ipo.objects.get(id=ipo_id)
            total_shares_demanded = ipo.total_shares_demanded
            if subs.bid_price < ipo.listing_price:
                total_shares_demanded -= (subs.bid_quantity * ipo.lot_size)
                ipo.total_shares_demanded = total_shares_demanded
                ipo.save()

        # Allocate the shares
        for subs in ipo_subscriptions:
            user = subs.user
            ipo_id = subs.ipo.id
            ipo = models.Ipo.objects.get(id=ipo_id)
            portfolio = models.Portfolio.objects.get(user=user)
            total_shares_available = ipo.issue_size
            total_shares_demanded = ipo.total_shares_demanded
            remaining_shares = ipo.remaining_shares

            if subs.bid_price >= ipo.listing_price:
                
                shares_allotted = 0

                # Ipo is undersubscribed 
                if total_shares_demanded < total_shares_available:
                    # Number of shares to be allocated remains the same
                    shares_allotted = (subs.bid_quantity*ipo.lot_size)
                
                # Ipo is oversubscribed
                else:
                    # Number of shares to be allocated according to prorata
                    prorata_ratio = (subs.bid_quantity*ipo.lot_size) / total_shares_demanded
                    shares_allotted = min(int(prorata_ratio * total_shares_available), remaining_shares)
                
                # Update the remaining shares field in ipo and stock object
                remaining_shares -= shares_allotted
                ipo.remaining_shares = remaining_shares
                stock_id = ipo.stock.id
                stock = models.Stock.objects.get(id=stock_id)
                stock.remaining_shares = remaining_shares

                # Calculate the refund amount
                offset_price = subs.bid_price - ipo.listing_price
                refund_amount = offset_price * shares_allotted

                # Update the portfolio cash with refund amount
                portfolio.cash = portfolio.cash + refund_amount

                # Add the stock in holdings and transactions
                transaction = models.Transaction.objects.create(
                    user=user,
                    stock=ipo.stock,
                    traded_price=ipo.listing_price,
                    quantity=shares_allotted,
                    transaction_type="buy"
                )
                holding = models.Holding.objects.create(
                    portfolio=portfolio,
                    stock=ipo.stock,
                    transaction=transaction,
                    quantity=shares_allotted,
                )

                ipo.save()
                stock.save()
                portfolio.save()
                transaction.save()
                holding.save()               

            else:
                refund_amount = subs.bid_price * subs.bid_quantity * ipo.lot_size
                portfolio.cash = portfolio.cash + refund_amount
                portfolio.save()


admin.site.register(models.User)
admin.site.register(models.Stock)
admin.site.register(models.News)
admin.site.register(models.Transaction)
admin.site.register(models.Portfolio)
admin.site.register(models.Holding)
admin.site.register(models.Market)
admin.site.register(models.IpoSubscription, IpoSubscriptionAdmin)
admin.site.register(models.Ipo, IpoAdmin)