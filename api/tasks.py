from celery import shared_task
from core.models import Holding, News, Portfolio, Stock, Market, Transaction
from datetime import datetime, timedelta
from celery import shared_task
import random
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db import transaction as django_transaction


@shared_task
def publish_news():
    try:
        market = Market.objects.get(id=1)
    except ObjectDoesNotExist:
        market = Market.objects.create(is_open=False)
        market.save()
        print('MARKET OBJECT CREATED')
    finally:
        market = Market.objects.get(id=1)
        if market.is_open:
            news = News.objects.filter(is_published=False).first()
            if news:
                news.is_published = True
                news.published_at = datetime.now()  
                news.save()
                print(f'NEWS PUBLISHED : {news}')
        else:
            print('MARKET IS CLOSED')


@shared_task
def update_prices():
    try:
        market = Market.objects.get(id=1)
    except ObjectDoesNotExist:
        market = Market.objects.create(is_open=False)
        market.save()
        print('MARKET OBJECT CREATED')
    finally:
        market = Market.objects.get(id=1)
        if market.is_open:
            for stock in Stock.objects.all():
                news = News.objects.filter(stock=stock, is_published=True, published_at__gte=datetime.now() - timedelta(minutes=15)).last()
                if news:
                    impact = news.impact
                    impact_no = news.impact_no
                    sentiment = (1 if news.sentiment == "positive" else -1)
                    change = (impact*(news.impacts[impact_no]/100))/100 
                    total_change = Decimal((stock.price_history[-impact_no]).get('price')) * Decimal(change) * Decimal(sentiment)
                    stock.current_price += Decimal(total_change)
                    news.impact_no += 1
                    news.save()  
                    print("UPDATED PRICE BY IMPACT", stock)   
                else:
                    random_factor = random.uniform(-0.02, 0.02)
                    change = stock.current_price * Decimal(random_factor)
                    stock.current_price += change
                    stock.save()
                    print("UPDATED PRICE RANDOM", stock)   
                stock.price_history.append({'price': str(stock.current_price), 'datetime': str(datetime.now())})
                stock.save()
                print(f'UPDATE PRICE OF {stock.name} IS {stock.current_price}')
        else:
            print('MARKET IS CLOSED')


@shared_task
def process_buy_order(user_id, stock_id, transaction_id, buy_price, buy_qty, required_cash):
    
    stock = get_object_or_404(Stock, id=stock_id)
    portfolio = Portfolio.objects.get(user=user_id)
    transaction = Transaction.objects.get(id=transaction_id)

    buy_price = Decimal(buy_price)
    buy_qty = int(buy_qty)
    required_cash = int(required_cash)

    price_diff = ((buy_price-stock.current_price)/(stock.current_price))*100
    
    with django_transaction.atomic():
        if price_diff>2 and stock.remaining_shares>=buy_qty:
            stock.remaining_shares -= buy_qty
            transaction_fees = 0.02 * required_cash
            portfolio.cash -= (required_cash + transaction_fees)
            transaction.transaction_status = "success"
            holding = Holding.objects.create(
                portfolio=portfolio,
                stock=stock,
                transaction=transaction,
                quantity=buy_qty,
            )
            stock.save()
            portfolio.save()
            transaction.save()
        else:
            transaction.transaction_status = "failed"
            transaction.save()


@shared_task
def process_sell_order(user_id, stock_id, transaction_id, sell_price, sell_qty):

    stock = get_object_or_404(Stock, id=stock_id)
    portfolio = Portfolio.objects.get(user=user_id)
    transaction = Transaction.objects.get(id=transaction_id)

    sell_price = Decimal(sell_price)
    sell_qty = int(sell_qty)

    price_diff = ((sell_price-stock.current_price)/(stock.current_price))*100

    with django_transaction.atomic():
        if price_diff<2:
            available_holdings = Holding.objects.filter(portfolio=portfolio, stock=stock).order_by("transaction__transaction_datetime")
            temp_qty = sell_qty
            for holding in available_holdings:
                if sell_qty==0:
                    break
                diff = min(holding.quantity, sell_qty)
                holding.quantity -= diff
                sell_qty -= diff
                holding.save()
                if holding.quantity == 0:
                    holding.delete()
            stock.remaining_shares += temp_qty
            transaction_fees = Decimal(0.02) * (temp_qty * sell_price)
            portfolio.cash += ((temp_qty * sell_price) - transaction_fees)
            transaction.transaction_status = "success"
            stock.save()
            portfolio.save()
            transaction.save()
        else:
            transaction.transaction_status = "failed"
            transaction.save()