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
                total_bid_price += subs.bid_price * subs.bid_quantity
                total_bid_qty += subs.bid_quantity
            avg_bid_price = 0
            if total_bid_qty > 0:
                avg_bid_price = total_bid_price / total_bid_qty
            avg_bid_price = int(avg_bid_price)
            ipo.listing_price=avg_bid_price
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

        for subs in ipo_subscriptions:
            user = subs.user
            ipo = subs.ipo
            portfolio = models.Portfolio.objects.get(user=user)
            if subs.bid_price >= ipo.listing_price:
                offset_price = subs.bid_price - ipo.listing_price
                refund_amount = offset_price * subs.bid_quantity * ipo.lot_size
                portfolio.cash = portfolio.cash + refund_amount
                portfolio.save()
                transaction = models.Transaction.objects.create(
                    user=user,
                    stock=ipo.stock,
                    traded_price=ipo.listing_price,
                    quantity=subs.bid_quantity*ipo.lot_size,
                    transaction_type="buy"
                )
                holding = models.Holding.objects.create(
                    portfolio=portfolio,
                    stock=ipo.stock,
                    transaction=transaction,
                    quantity=subs.bid_quantity*ipo.lot_size,
                )
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