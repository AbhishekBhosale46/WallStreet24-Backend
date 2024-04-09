from rest_framework import serializers
from core.models import News, Stock, Portfolio, Holding, Transaction, Ipo, IpoSubscription
from django.db.models import Sum, F


class NewsSerializer(serializers.ModelSerializer):
    short_description = serializers.SerializerMethodField();
    
    class Meta:
        model = News
        fields = ["id", "title", "short_description", "published_at"]

    def get_short_description(self, news):
        return news.description[0:200]


class NewsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["id", "title", "description", "published_at"]


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["id", "name", "ticker", "current_price", "price_change"]


class StockDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["id", "name", "ticker", "current_price", "price_change", "price_history"]


class PortfolioSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    holdings = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ["id", "username", "cash", "holdings"]

    def get_username(self, portfolio):
        return portfolio.user.name

    def get_holdings(self, portfolio):
        user = portfolio.user.id
        holdings = Holding.objects.filter(portfolio__user__id=user,
        transaction__transaction_type="buy").values("stock","stock__name", "stock__ticker", "stock__current_price").annotate(
        avg_price = (Sum( F("transaction__traded_price") * F("quantity") ) / Sum("quantity")),
        total_quantity=Sum("quantity")
        )
        return list(holdings)


class TransactionSerializer(serializers.ModelSerializer):
    ticker = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ["id", "ticker", "traded_price", "quantity", "transaction_type", "transaction_datetime"]

    def get_ticker(self, transaction):
        return transaction.stock.ticker
    

class IpoSerializer(serializers.ModelSerializer):
    stock_name = serializers.SerializerMethodField()
    stock_ticker = serializers.SerializerMethodField()

    class Meta:
        model = Ipo
        fields = ["id", "stock_name", "stock_ticker", "start_date", "end_date", "issue_size",\
                  "floor_price", "ceil_price", "lot_size", "red_herring_prospectus"]

    def get_stock_name(self, ipo):
        return ipo.stock.name

    def get_stock_ticker(self, ipo):
        return ipo.stock.ticker