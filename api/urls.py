from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.NewsList.as_view(), name='news-list'),
    path('news/<int:pk>', views.NewsDetail.as_view(), name='news-detail'),
    path('stocks/', views.StockList.as_view(), name='stocks-list'),
    path('stocks/<int:pk>', views.StockDetail.as_view(), name='stocks-detail'),
    path('stocks/buy/<int:id>', views.BuyStockApi.as_view(), name='buy-stock'),
    path('stocks/sell/<int:id>', views.SellStockApi.as_view(), name='sell-stock'),
    path('portfolio/', views.PortfolioApi.as_view(), name='portfolio'),
    path('cash/', views.UserCashApi.as_view(), name='cash'),
    path('availablequantity/<int:id>', views.UserStocksApi.as_view(), name='available-qty')
]
