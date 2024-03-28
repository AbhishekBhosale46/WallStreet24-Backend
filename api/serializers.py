from rest_framework import serializers
from core.models import News, Stock, Portfolio, Holding
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
        transaction__transaction_type="buy").values("stock","stock__name", "stock__ticker").annotate(
        avg_price = (Sum( F("transaction__traded_price") * F("transaction__quantity") ) / Sum("transaction__quantity")),
        total_quantity=Sum("transaction__quantity")
        )
        return list(holdings)