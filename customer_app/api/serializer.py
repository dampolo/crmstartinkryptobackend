from rest_framework import serializers
from customer_app.models import Customer, CustomerComment


class CustomerCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerComment
        fields = ['id', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CustomerSerializer(serializers.ModelSerializer):
    comments = CustomerCommentSerializer(many=True, required=False)

    class Meta:
        model = Customer
        fields = [
            'id',
            'photo',
            'customer_number',
            'title',
            'first_name',
            'last_name',
            'street',
            'number',
            'post_code',
            'city',
            'email',
            'phone',
            'has_portfolio',
            'has_subscription',
            'is_active',
            'created_at',
            'updated_at',
            'comments'
        ]

        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        comments_data = validated_data.pop('comments', [])

        customer = Customer.objects.create(**validated_data)

        for comment in comments_data:
            CustomerComment.objects.create(customer=customer, **comment)

        return customer