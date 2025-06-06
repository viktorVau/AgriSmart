from rest_framework import serializers
from .models import Product
from .models import Message
from .models import Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['farmer']


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.get_full_name', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'product', 'content',
            'timestamp', 'is_read', 'parent', 'replies',
            'sender_name', 'receiver_name', 'is_deleted'
        ]
        read_only_fields = ['sender', 'timestamp', 'is_read', 'replies', 'is_deleted']

    def get_replies(self, obj):
        return MessageSerializer(obj.replies.filter(is_deleted=False), many=True).data


class OrderSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'product', 'quantity', 'total_price',
            'status', 'timestamp', 'buyer_name', 'product_name'
        ]
        read_only_fields = ['buyer', 'total_price', 'status', 'timestamp']
