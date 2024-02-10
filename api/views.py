from rest_framework import generics
from core.models import News, Stock
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


class StockDetail(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = serializers.StockDetailSerializer

