from django.contrib import admin
from course_app.models import Course, CourseFeature, Lesson, LessonPDF, DiscountCode, Purchase

admin.site.register(Course)
admin.site.register(CourseFeature)
admin.site.register(Lesson)
admin.site.register(LessonPDF)
admin.site.register(DiscountCode)
admin.site.register(Purchase)


# Register your models here.
