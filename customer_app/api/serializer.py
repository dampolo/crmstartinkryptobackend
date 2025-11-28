from rest_framework import serializers
from customer_app.models import Customer, CustomerComment


class CustomerCommentSerializer(serializers.ModelSerializer):
    text = serializers.CharField(allow_blank=True)
    
    class Meta:
        model = CustomerComment
        fields = ['id', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_text(self, value):
        # Strip whitespace and check for empty result
        if not value.strip():
            raise serializers.ValidationError("Comment text cannot be empty.")
        return value

class CustomerSerializer(serializers.ModelSerializer):
    comments = CustomerCommentSerializer(many=True, required=False)

    class Meta:
        model = Customer
        fields = [
            'id',
            'user',
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

        read_only_fields = ['created_at', 'updated_at', 'user']
    
    def create(self, validated_data):
        comments_data = validated_data.pop('comments', [])
        
        validated_data['customer_number'] = generate_customer_number()

        customer = Customer.objects.create(**validated_data)

        for comment in comments_data:
            CustomerComment.objects.create(customer=customer, **comment)

        return customer
    
    def update(self, instance, validated_data):
        # Extract nested comments if provided
        validated_data.pop('comments', [])

        # Extract customer_number if client tries to send it
        validated_data.pop('customer_number', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


def generate_customer_number():
    """
    Generate a new sequential customer number with the format: SK000001
    
    The function:
    - Extracts the numeric part from existing customer numbers (after 'SK')
    - Finds the highest existing number
    - Increments it by 1
    - Returns the new number formatted with leading zeros
    """
    from django.db.models import Max
    from django.db.models.functions import Substr, Cast
    from django.db.models import IntegerField

    # Annotate each customer with the numeric portion of customer_number
    # Example: "SK000123" → 123
    last_number = (
        Customer.objects
        .annotate(num=Cast(Substr('customer_number', 3), IntegerField()))
        .aggregate(max_num=Max('num'))['max_num']
    )

    # If at least one number exists, increment it; otherwise start at 1
    next_number = (last_number + 1) if last_number else 1
    
    # Format result as SK + 6-digit zero-padded number
    return f"SK{next_number:06d}"
