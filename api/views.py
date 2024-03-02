from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db.models import Sum
from core.models import News, Stock, Portfolio, Transaction, Holding
from . import serializers
from rest_framework.views import APIView


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

    available_cash = Decimal(portfolio.cash)
    required_cash = buy_price * buy_qty

    if required_cash > available_cash:
        return Response({"detail": "You don't have enough cash to buy this stock"}, status=status.HTTP_400_BAD_REQUEST)

    available_cash = available_cash - required_cash
    portfolio.cash = available_cash
    portfolio.save()

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


@api_view(["POST"])
def sell_stock(request, id):

    user = request.user
    stock = get_object_or_404(Stock, id=id)
    portfolio = Portfolio.objects.get(user=user)

    sell_price = request.data.get("price", None)
    sell_qty = request.data.get("quantity", None)

    if not sell_price:
        return Response({"detail": "Sell price not given"}, status=status.HTTP_400_BAD_REQUEST)

    if not sell_qty:
        return Response({"detail": "Sell quantity not given"}, status=status.HTTP_400_BAD_REQUEST)

    sell_price = Decimal(sell_price)
    sell_qty = int(sell_qty)

    price_diff = ((sell_price-stock.current_price)/(stock.current_price))*100
    if price_diff > 2 or price_diff < -2:
        return Response({"detail": "Cannot sell at this price"}, status=status.HTTP_400_BAD_REQUEST)
    
    available_holdings = Holding.objects.filter(portfolio=portfolio, stock=stock).order_by("transaction__transaction_datetime")

    if not available_holdings.exists():
        return Response({"detail": "You don't have any holdings for the requested stock"}, status=status.HTTP_400_BAD_REQUEST)

    available_qty = (available_holdings.aggregate(total_qty=Sum("quantity"))).get("total_qty", 0)

    if sell_qty>available_qty:
        return Response({"detail": "You don't have enough available stocks"}, status=status.HTTP_400_BAD_REQUEST)

    for holding in available_holdings:
        if sell_qty==0:
            break
        diff = min(holding.quantity, sell_qty)
        holding.quantity -= diff
        sell_qty -= diff
        holding.save()
        if holding.quantity == 0:
            holding.delete()

    portfolio.cash += (sell_qty * sell_price)
    portfolio.save

    transaction = Transaction.objects.create(
        user=user,
        stock=stock,
        traded_price=sell_price,
        quantity=sell_qty,
        transaction_type="sell"
    )

    return Response({"detail": "Transaction completed"}, status=status.HTTP_201_CREATED)


class PortfolioApi(APIView):

    def get(self, request):
        user = request.user
        portfolio = Portfolio.objects.get(user=user)
        portfolio_serializer = serializers.PortfolioSerializer(portfolio)
        return Response(portfolio_serializer.data, status=status.HTTP_200_OK)