from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db.models import Sum
from core.models import News, Stock, Portfolio, Transaction, Holding, Market, Ipo, IpoSubscription, User
from . import serializers
from rest_framework.views import APIView
from datetime import date
from django.db.models import Sum, F


class NewsList(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = News.objects.all()
    serializer_class = serializers.NewsSerializer

    def get_queryset(self):
        return self.queryset.filter(is_published=True).order_by('-published_at')


class NewsDetail(generics.RetrieveAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = News.objects.all()
    serializer_class = serializers.NewsDetailSerializer

    def get_queryset(self):
        return self.queryset.filter(is_published=True)


class StockList(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = serializers.StockSerializer

    def get_queryset(self):
        return self.queryset.filter(is_listed=True).order_by("name")


class StockDetail(generics.RetrieveAPIView):
    queryset = Stock.objects.all()
    serializer_class = serializers.StockDetailSerializer


class BuyStockApi(APIView):

    def post(self, request, id):

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


class SellStockApi(APIView):

    def post(self, request, id):

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

        portfolio.cash += (temp_qty * sell_price)
        portfolio.save

        transaction = Transaction.objects.create(
            user=user,
            stock=stock,
            traded_price=sell_price,
            quantity=temp_qty,
            transaction_type="sell"
        )

        return Response({"detail": "Transaction completed"}, status=status.HTTP_201_CREATED)


class PortfolioApi(APIView):

    def get(self, request):

        user = request.user
        portfolio = Portfolio.objects.get(user=user)
        portfolio_serializer = serializers.PortfolioSerializer(portfolio)

        return Response(portfolio_serializer.data, status=status.HTTP_200_OK)


class UserCashApi(APIView):

    def get(self, request):
        user = request.user
        portfolio = Portfolio.objects.get(user=user)
        return Response({'cash': portfolio.cash}, status=status.HTTP_200_OK)


class UserStocksApi(APIView):

    def get(self, request, id):
        user = request.user
        stock = get_object_or_404(Stock, id=id)
        portfolio = Portfolio.objects.get(user=user)
        available_holdings = Holding.objects.filter(portfolio=portfolio, stock=stock).order_by("transaction__transaction_datetime")
        available_qty = (available_holdings.aggregate(total_qty=Sum("quantity"))).get("total_qty", 0)
        if not available_holdings.exists():
            available_qty = 0
        return Response({'available_quantity': available_qty}, status=status.HTTP_200_OK)


class TransactionList(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-transaction_datetime")


class IpoList(generics.ListAPIView):
    queryset = Ipo.objects.all()
    serializer_class = serializers.IpoSerializer


class IpoDetail(generics.RetrieveAPIView):
    queryset = Ipo.objects.all()
    serializer_class = serializers.IpoSerializer


class IpoSubscriptionApi(APIView):

    def post(self, request, id):
        
        user = request.user
        ipo = get_object_or_404(Ipo, id=id)
        portfolio = Portfolio.objects.get(user=user)

        bid_price = request.data.get("bid_price", None)
        bid_qty = request.data.get("bid_quantity", None)

        if date.today()<ipo.start_date:
            return Response({"detail": "IPO subscription has not started yet"}, status=status.HTTP_400_BAD_REQUEST)

        if date.today()>ipo.end_date:
            return Response({"detail": "IPO subscription has been closed"}, status=status.HTTP_400_BAD_REQUEST)

        if not bid_price:
            return Response({"detail": "Bid price not given"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not bid_qty:
            return Response({"detail": "Bid Quantity not given"}, status=status.HTTP_400_BAD_REQUEST)

        if IpoSubscription.objects.filter(user=user, ipo=ipo).exists():
            return Response({"detail": "You have already subscribed the ipo"}, status=status.HTTP_400_BAD_REQUEST)

        bid_price = int(bid_price)
        bid_qty = int(bid_qty)

        if bid_price < ipo.floor_price or bid_price > ipo.ceil_price:
            return Response({"detail": "Bid price must be within the range"}, status=status.HTTP_400_BAD_REQUEST)

        required_cash = bid_price * bid_qty * ipo.lot_size

        if required_cash > 200000:
            return Response({"detail": "You cannot place order more than 2,00,000"}, status=status.HTTP_400_BAD_REQUEST)
        
        subscription = IpoSubscription.objects.create(
            ipo=ipo,
            user=user,
            bid_price=bid_price,
            bid_quantity=bid_qty,
        )

        subscription.save()

        portfolio.cash = portfolio.cash - required_cash
        portfolio.save()

        return Response({"detail": "Ipo subscribed successfully"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def market_status(request):
    market = Market.objects.get(id=1)
    return Response({"is_open": market.is_open}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def get_rankings(request):
    users = User.objects.all()
    ranks = []
    for user in users:
        portfolio = Portfolio.objects.get(user=user)
        user_id = portfolio.user.id
        holdings = Holding.objects.filter(portfolio__user__id=user_id,
        transaction__transaction_type="buy").values("stock","stock__name", "stock__ticker", "stock__current_price").annotate(
        avg_price = (Sum( F("transaction__traded_price") * F("quantity") ) / Sum("quantity")),
        total_quantity=Sum("quantity")
        )
        holdings = list(holdings)
        user_cash = portfolio.cash
        user_portfolio_value = 0
        for holding in holdings:
            user_portfolio_value += int(holding.get('total_quantity',0)) * int(holding.get('stock__current_price',0))
        ranks.append({
            "user_id": user_id,
            "name": user.name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "contact": user.contact_no,
            "networth": int(user_cash*0.4) + int(user_portfolio_value*0.6)
        })
    ranks = sorted(ranks, key=lambda rank: rank["networth"], reverse=True)
    return Response(ranks, status=status.HTTP_200_OK)