from celery import shared_task
from core.models import News, Stock
from datetime import datetime, timedelta
from celery import shared_task
import random
from decimal import Decimal


@shared_task
def publish_news():
    news = News.objects.filter(is_published=False).first()
    news.is_published = True
    news.published_at = datetime.now()
    news.save()
    print(f'NEWS PUBLISHED : {news}')


@shared_task
def update_prices():
    for stock in Stock.objects.all():
        news = News.objects.filter(stock=stock, is_published=True, published_at__gte=datetime.now() - timedelta(minutes=15)).last()
        if news:
            random_factor = random.uniform(0.9,1.1)
            decay_factor = news.decay_factor
            impact = Decimal(news.impact) \
                    * Decimal(1 if news.sentiment == 'positive' else -1) \
                    * Decimal(decay_factor) * Decimal(random_factor)
            change = Decimal(stock.current_price) * Decimal(impact/100)
            stock.current_price += Decimal(change)
            news.decay_factor = news.decay_factor * news.decay_rate
            news.save()
        else:
            random_factor = random.uniform(-0.02, 0.02)
            change = stock.current_price * Decimal(random_factor)
            stock.current_price += change
            stock.save()
        stock.price_history.append({'price': str(stock.current_price), 'datetime': str(datetime.now())})
        stock.save()
        print(f'UPDATE PRICE OF {stock.name} IS {stock.current_price}')