from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.NewsList.as_view(), name='news-list'),
    path('news/<int:pk>', views.NewsDetail.as_view(), name='news-detail'),
    path('stocks/', views.StockList.as_view(), name='stocks-list'),
    path('stocks/<int:pk>', views.StockDetail.as_view(), name='stocks-detail'),
    path('stocks/buy/<int:id>', views.buy_stock, name='buy-stock'),
    path('stocks/sell/<int:id>', views.sell_stock, name='sell-stock'),
]
