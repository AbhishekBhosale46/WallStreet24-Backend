from rest_framework import serializers
from core.models import News, Stock


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