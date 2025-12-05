# app/serializers.py
from rest_framework import serializers
from app.models import Vendor, UserVendorRole, Product, Order, OrderItem
from accounts.serializers import UserSerializer
from accounts.models import User

class VendorSerializer(serializers.ModelSerializer):
    owner = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Vendor
        fields = ["id", "store_name", "domain", "subdomain", "owner", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        vendor = Vendor.objects.create(user=user, **validated_data)

        UserVendorRole.objects.create(
            user=user,
            vendor=vendor,
            role=UserVendorRole.ROLE_OWNER
        )
        return vendor

class UserVendorRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserVendorRole
        fields = ["id", "user", "vendor", "role"]

    def create(self, validated_data):
        user = self.context["user"]
        vendor = self.context["vendor"]
        role = validated_data["role"]

        return UserVendorRole.objects.get_or_create(
            user=user,
            vendor=vendor,
            defaults={"role": role}
        )[0]

class ProductSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "vendor", "name", "description",
            "price", "stock", "is_active", "created_at"
        ]

    

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]
        read_only_fields = ["price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "vendor",
            "status",
            "total_amount",
            "items",
            "created_at"
        ]
        read_only_fields = ["total_amount", "items", "customer", "vendor"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        first_product = Product.objects.get(id=items_data[0]["product"].id)
        vendor = first_product.vendor

        order = Order.objects.create(
            customer=user,
            vendor=vendor,
            total_amount=0
        )

        total = 0
        for item in items_data:
            product = item["product"]
            quantity = item["quantity"]
            price = product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )

            total += quantity * price

        order.total_amount = total
        order.save()

        return order

class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=UserVendorRole.ROLE_CHOICES)
