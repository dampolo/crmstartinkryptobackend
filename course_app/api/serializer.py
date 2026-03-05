from rest_framework import serializers
from auth_app.models import User
from course_app.models import Course, CourseFeature, Lesson, DiscountCode, LessonPDF
from purchase_app.models import Purchase
from django.utils import timezone

# You can see all features from course, belong to CourseSerializer
class CourseFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFeature
        fields = ['id', 'course', 'text', 'order']


# You can see all courses(not bought)
class CourseSerializer(serializers.ModelSerializer):
    features = CourseFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'description',
            'language',
            'price',
            'image',
            'order',
            'badge',
            'features',
            'status',
        ]

class LessonPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonPDF
        fields = ['id', 'title', 'file']

# If you bought course you can see all leassons from courses
class LessonSerializer(serializers.ModelSerializer):
    # pdfs works because of: related_name='pdfs'
    pdfs = LessonPDFSerializer(
        many= True, read_only= True
        )

    class Meta:
        model = Lesson
        fields = [
            'id',
            'course',
            'title',
            'description',
            'video',
            'description_under_video',
            'order',
            'status',
            'duration',
            'pdfs'
        ]

# Belong to PurchasedSerializer 'course'
class PurchasedCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'description',
            'image',
            'order',
            'language',
        ]

# Show all courses which you bought
class PurchasedSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(read_only=True)
    # READ
    course = PurchasedCourseSerializer(read_only=True)

    # WRITE
    # get id from Course
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source="course",
        write_only=True
    )

    discount = serializers.PrimaryKeyRelatedField(
        queryset=DiscountCode.objects.all(),
        required=False,
        allow_null=True
    )

    total = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        read_only=True
    )
    class Meta:
        model = Purchase
        fields = [
            'id', # id from purchased
            'course',
            "course_id",
            'lessons_count',
            'discount',
            'total',
            'created_at',
        ]
        read_only_fields = ['created_at']

class DiscountCodeSerializer(serializers.ModelSerializer):
    # is_valid exists only in the API response
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = DiscountCode
        fields = [
            "id",
            "code",
            "percent_value",
            "active",
            "expires_at",
            "is_valid",
        ]

    def get_is_valid(self, obj):
        if not obj.active:
            return False
        if obj.expires_at and obj.expires_at < timezone.now():
            return False
        return True