from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .pagination import ProductPagination
from .models import Product, Message
from .serializers import MessageSerializer, ProductSerializer
from core.models import Farmer  # adjust if located elsewhere
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from .serializers import OrderSerializer
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


@extend_schema(
    request=ProductSerializer,
    responses={201: ProductSerializer},
    description="Allows a farmer to create a product listing. Only users with a farmer profile can create products."
)
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            farmer = self.request.user.farmer
        except Farmer.DoesNotExist:
            raise PermissionDenied(_("Only farmers can create products."))
        serializer.save(farmer=farmer)

# ✅ List all products (anyone can view)
@extend_schema(
    parameters=[
        OpenApiParameter(name='name', location='query', required=False, description='Filter by product name'),
        OpenApiParameter(name='farmer__id', location='query', required=False, description='Filter by farmer ID'),
        OpenApiParameter(name='search', location='query', required=False, description='Search in name or description'),
    ],
    responses={200: ProductSerializer(many=True)},
    description="List all products. Supports filtering by name and farmer ID, and search in name/description."
)
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ProductPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_fields = ['name', 'farmer__id']  # Existing filters
    search_fields = ['name', 'description']   # 🔍 New search fields


# ✅ Retrieve a single product by ID
@extend_schema(
    responses={200: ProductSerializer},
    description="Retrieve detailed information about a product by its ID."
)
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny]

# ✅ Update product (Farmer can only update their own product)
@extend_schema(
    request=ProductSerializer,
    responses={200: ProductSerializer},
    description="Update a product. Only the farmer who created the product can update it."
)
class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        product = self.get_object()
        if not hasattr(self.request.user, 'farmer') or product.farmer != self.request.user.farmer:
            raise PermissionDenied(_("You are not allowed to update this product."))
        serializer.save()


# ✅ Delete a product (only if it belongs to the authenticated farmer)
@extend_schema(
    responses={204: OpenApiExample("Product deleted", value={"detail": "Product deleted successfully."})},
    description="Delete a product. Only the owning farmer is allowed to delete."
)
class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if not hasattr(self.request.user, 'farmer') or instance.farmer != self.request.user.farmer:
            raise PermissionDenied(_("You are not allowed to delete this product."))
        instance.delete()


@extend_schema(
    request=MessageSerializer,
    responses={201: MessageSerializer},
    description="Send a message to a product owner. An email is also sent to the receiver."
)
class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)

        # Email notification
        subject = _(f'New message from {message.sender.get_full_name()} on AgriSmart')
        body = _(f'''
Hi {message.receiver.get_full_name()},

You have received a new message regarding the product: {message.product.name}.

Message:
"{message.content}"

Please log in to your account to reply.

AgriSmart Team
        ''')
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [message.receiver.email],
            fail_silently=True
        )


@extend_schema(
    responses={200: MessageSerializer(many=True)},
    description="List all messages received by the authenticated user. Only non-deleted messages are shown."
)
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Only show non-deleted messages
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(receiver=user, is_deleted=False)

    # Soft delete
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user == instance.receiver or request.user == instance.sender:
            instance.is_deleted = True
            instance.save()
            return Response({"detail": _("Message deleted successfully.")}, status=204)
        return Response({"detail": _("Not authorized to delete this message.")}, status=403)



@extend_schema(
    request=MessageSerializer,
    responses={200: MessageSerializer},
    description="View or mark a message as read. Automatically marks the message as read on update."
)
class MessageDetailView(generics.RetrieveUpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(is_read=True)



@extend_schema(
    request=OrderSerializer,
    responses={201: OrderSerializer},
    description="Place a new order for a product. Total price is calculated automatically."
)
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        total_price = product.price * quantity
        serializer.save(buyer=self.request.user, total_price=total_price)


@extend_schema(
    responses={200: OrderSerializer(many=True)},
    description="List all orders made by the currently authenticated user (as buyer)."
)
class BuyerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)


@extend_schema(
    responses={200: OrderSerializer(many=True)},
    description="List all orders received by the authenticated farmer (as seller)."
)
class SellerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(product__farmer=self.request.user)


@extend_schema(
    request=OrderSerializer,
    responses={200: OrderSerializer},
    description="Update the status of an order. Only the farmer who owns the product can perform this action."
)
class OrderUpdateStatusView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if order.product.farmer != request.user:
            return Response({'detail': 'Unauthorized'}, status=403)
        order.status = request.data.get('status', order.status)
        order.save()
        return Response(OrderSerializer(order).data)
    


@extend_schema(
    responses={200: OpenApiExample(
        name="Notification Summary",
        value={
            "unread_messages": 3,
            "pending_orders": 2
        }
    )},
    description="Returns a count of unread messages and pending orders for the current user (buyer or seller)."
)
class DashboardNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        unread_messages = Message.objects.filter(receiver=user, is_read=False, is_deleted=False).count()

        if hasattr(user, 'farmer'):
            pending_orders = Order.objects.filter(product__farmer=user, status='pending').count()
        else:
            pending_orders = Order.objects.filter(buyer=user, status='pending').count()

        return Response({
            'unread_messages': unread_messages,
            'pending_orders': pending_orders
        })
