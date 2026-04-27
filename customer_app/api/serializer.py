from rest_framework import serializers
from customer_app.models import UserComment
from auth_app.models import User
from customer_app.customer_nummer import GenerateCustomerNumber

class CustomerCommentSerializer(serializers.ModelSerializer):
    # With allow_blank=True you give decision to the validation method validate_text.
    text = serializers.CharField(allow_blank=True)
    
    class Meta:
        model = UserComment
        fields = ['id', 'user', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_text(self, value):
        # Strip whitespace and check for empty result
        if not value.strip():
            raise serializers.ValidationError("Comment text cannot be empty.")
        return value

class CustomerSerializer(serializers.ModelSerializer):
    comments = CustomerCommentSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'role',
            'username',
            'image',
            'customer_number',
            'title',
            'first_name',
            'last_name',
            'street',
            'street_number',
            'postcode',
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

        read_only_fields = ['created_at', 'updated_at', 'user', 'customer_number']
    
    def validate_post_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Post code must contain numbers only.")
        return value

    def create(self, validated_data):
        request = self.context['request']
        user = request.user           
        
        comments_data = validated_data.pop('comments', [])
        validated_data['customer_number'] = GenerateCustomerNumber.generate_customer_number()

        customer = User.objects.create(**validated_data)


        for comment in comments_data:
            UserComment.objects.create(
                customer=customer,
                user=user,
                **comment
            )
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


# Serializer only for Customer
class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'image',
            'customer_number',
            'title',
            'first_name',
            'last_name',
            'street',
            'street_number',
            'postcode',
            'city',
            'email',
            'phone',
            'has_portfolio',
            'has_subscription',
            'is_active',
        ]

        read_only_fields = ['created_at', 'updated_at', 'user', 'customer_number']
    
    def validate_post_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Post code must contain numbers only.")
        return value

    def create(self, validated_data):
        request = self.context['request']   # <-- get request here
        user = request.user                 # <-- authenticated user
        
        comments_data = validated_data.pop('comments', [])
        validated_data['customer_number'] = GenerateCustomerNumber.generate_customer_number()

        customer = User.objects.create(**validated_data)


        for comment in comments_data:
            UserComment.objects.create(
                customer=customer,
                user=user,      # <-- ADD THIS
                **comment
            )
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