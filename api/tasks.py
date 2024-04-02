from celery import shared_task
from core.models import News, Stock
from datetime import datetime, timedelta
from celery import shared_task
import random
from decimal import Decimal


@shared_task
def publish_news():
    news = News.objects.filter(is_published=False).first()
    if news:
        news.is_published = True
        news.published_at = datetime.now()  
        news.save()
        print(f'NEWS PUBLISHED : {news}')


@shared_task
def update_prices():
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