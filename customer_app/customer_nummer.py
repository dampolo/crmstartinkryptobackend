from auth_app.models import User

class GenerateCustomerNumber:
    @staticmethod
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
            User.objects
            .annotate(num=Cast(Substr('customer_number', 3), IntegerField()))
            .aggregate(max_num=Max('num'))['max_num']
        )

        # If at least one number exists, increment it; otherwise start at 1
        next_number = (last_number + 1) if last_number else 1
        
        # Format result as SK + 6-digit zero-padded number
        return f"SK{next_number:06d}"