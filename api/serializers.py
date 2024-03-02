from rest_framework import serializers
from core.models import News, Stock, Portfolio, Holding
from django.db.models import Sum, F


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["id", "title", "published_at"]


class NewsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["id", "title", "description", "published_at"]


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["id", "name", "ticker", "current_price", "get_price_change"]


class StockDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["id", "name", "ticker", "current_price", "get_price_change", "price_history"]


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
        transaction__transaction_type="buy").values("stock","stock__name", "stock__ticker").annotate(
        avg_price = (Sum( F("transaction__traded_price") * F("transaction__quantity") ) / Sum("transaction__quantity")),
        total_quantity=Sum("transaction__quantity")
        )
        return list(holdings)