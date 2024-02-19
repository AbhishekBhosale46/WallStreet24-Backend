from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from decimal import Decimal
from core.models import News, Stock, Portfolio, Transaction, Holding
from . import serializers


class NewsList(generics.ListAPIView):
    queryset = News.objects.all()
    serializer_class = serializers.NewsSerializer

    def get_queryset(self):
        return self.queryset.filter(is_published=True).order_by('published_at')


class NewsDetail(generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = serializers.NewsSerializer

    def get_queryset(self):
        return self.queryset.filter(is_published=True)


class StockList(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = serializers.StockSerializer

    def get_queryset(self):
        return self.queryset.order_by("name")


class StockDetail(generics.RetrieveAPIView):
    queryset = Stock.objects.all()
    serializer_class = serializers.StockDetailSerializer


@api_view(["POST"])
def buy_stock(request, id):
    
    user = request.user
    stock = get_object_or_404(Stock, id=id)
    portfolio = Portfolio.objects.get(user=user)

    buy_price = request.data.get("price", None)
    buy_qty = request.data.get("quantity", None)

    if not buy_price:
        return Response({"detail": "Buy price not given"}, status=status.HTTP_400_BAD_REQUEST)

    if not buy_qty:
        return Response({"detail": "Buy quantity not given"}, status=status.HTTP_400_BAD_REQUEST)

    buy_price = Decimal(buy_price)
    buy_qty = int(buy_qty)

    price_diff = ((buy_price-stock.current_price)/(stock.current_price))*100
    if price_diff > 2 or price_diff < -2:
        return Response({"detail": "Cannot buy at this price"}, status=status.HTTP_400_BAD_REQUEST)

    transaction = Transaction.objects.create(
        user=user,
        stock=stock,
        traded_price=buy_price,
        quantity=buy_qty,
        transaction_type="buy"
    )

    holding = Holding.objects.create(
        portfolio=portfolio,
        stock=stock,
        transaction=transaction,
        quantity=buy_qty,
    )

    return Response({"detail": "Transaction completed"}, status=status.HTTP_201_CREATED)
    

