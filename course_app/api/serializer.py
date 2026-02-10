from rest_framework import serializers
from auth_app.models import User
from course_app.models import Course, CourseFeature

class CourseFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFeature
        fields = ["id", "course", "text", "order"]

class CourseSerializer(serializers.ModelSerializer):
    features = CourseFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'description',
            'price',
            'image',
            'order',
            'badge',
            'features'
        ]