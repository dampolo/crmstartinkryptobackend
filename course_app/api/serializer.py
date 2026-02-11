from rest_framework import serializers
from auth_app.models import User
from course_app.models import Course, CourseFeature, Lesson, Purchase, DiscountCode
from django.utils import timezone

class CourseFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFeature
        fields = ['id', 'course', 'text', 'order']

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

class LessonSerializer(serializers.ModelSerializer):
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
        ]


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

class PurchaseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(read_only=True)
    # READ
    course = PurchasedCourseSerializer(read_only=True)

    # WRITE
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source="course",
        write_only=True
    )
    class Meta:
        model = Purchase
        fields = [
            'id',
            'course',
            "course_id",
            'lessons_count',
            'discount',
            'price',
            'created_at',
        ]
        read_only_fields = ['price', 'created_at']

class DiscountCodeSerializer(serializers.ModelSerializer):
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