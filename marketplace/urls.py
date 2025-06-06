from django.urls import path
from .views import BuyerOrderListView, MessageCreateView, MessageDetailView, MessageListView, OrderCreateView, OrderUpdateStatusView, ProductCreateView, ProductDeleteView, ProductDetailView, ProductListView, ProductUpdateView, SellerOrderListView

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:id>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('<int:id>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('messages/send/', MessageCreateView.as_view(), name='send-message'),
    path('messages/inbox/', MessageListView.as_view(), name='inbox'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
    path('orders/create/', OrderCreateView.as_view()),
    path('orders/buyer/', BuyerOrderListView.as_view()),
    path('orders/seller/', SellerOrderListView.as_view()),
    path('orders/<int:pk>/update-status/', OrderUpdateStatusView.as_view()),
]