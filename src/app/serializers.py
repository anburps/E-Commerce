from rest_framework import serializers
from accounts.models import User
from .models import Vendor, UserVendorRole, Product, Order, OrderItem


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["vendor", "created_at", "id"]

    def create(self, validated_data):
        request = self.context.get("request") 
        user = request.user

        vendor = Vendor.objects.filter(
            vendor_users__user=user,
            vendor_users__role__in=["owner", "staff"]
        ).first()

        if not vendor:
            raise serializers.ValidationError("You are not allowed to create products.")

        validated_data["vendor"] = vendor
        
        return Product.objects.create(**validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price",
            "created_at"
        ]
        read_only_fields = ["id", "price", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=True)

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
        read_only_fields = ["id", "customer", "vendor", "total_amount", "created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        request = self.context.get("request")
        user = request.user

        # Vendor and role must come from your logic (your view handles assignment)
        vendor = validated_data.get("vendor")

        # Create order with placeholder amount (will update later)
        order = Order.objects.create(
            customer=user,
            vendor=vendor,
            total_amount=0  # will update after items processing
        )

        total_amount = 0

        # Create order items
        for item in items_data:
            product = item["product"]
            quantity = item["quantity"]

            # Ensure stock available
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {product.name}. Available: {product.stock}"
                )

            # Deduct stock
            product.stock -= quantity
            product.save()

            price = product.price
            item_price_total = price * quantity
            total_amount += item_price_total

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )

        # Update total amount
        order.total_amount = total_amount
        order.save()

        return order

    def update(self, instance, validated_data):
        """
        Vendors may update status.
        Customers cannot modify items or totals.
        """

        # Only update fields DRF allows
        status_value = validated_data.get("status", None)
        if status_value:
            instance.status = status_value
            instance.save()

        return instance
