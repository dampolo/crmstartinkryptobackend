from django.contrib import admin
from course_app.models import Course, CourseFeature, Lesson, LessonPDF, DiscountCode

admin.site.register(Course)
admin.site.register(CourseFeature)
admin.site.register(Lesson)
admin.site.register(LessonPDF)
admin.site.register(DiscountCode)

# Register your models here.
