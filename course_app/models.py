from django.db import models
from auth_app.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Language(models.TextChoices):
    DE = "de", _("Deutsch")
    PL = "pl", _("Polnisch")


# -------------------------
# Bonus
# -------------------------

class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    percent_value = models.PositiveIntegerField(help_text="Rabatt % Wert")
    active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} ({self.percent_value}%)"


# -------------------------
# Section
# -------------------------
class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="media/courses/",null=True,blank=True )
    order = models.DecimalField(max_digits=4, decimal_places=2, null=False, blank=False, default=0)
    language = models.CharField(
        max_length=10, 
        choices=Language.choices, 
        default=Language.DE)
    badge = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Example: "Most Popular", "Best Value", "New"'
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

# Short describtion of th coures in points


class CourseFeature(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="features"
    )
    text = models.CharField(max_length=255)
    order = models.DecimalField(max_digits=4, decimal_places=2, null=False, blank=False, default=0)

    class Meta:
        ordering = ['order']
    
class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField()

    # oder URLField bei Verwendung von YouTube/Vimeo
    video = models.FileField(upload_to="videos/")
    description_under_video = models.TextField(blank=True)
    order = models.DecimalField(max_digits=4, decimal_places=2, null=False, blank=False, default=0)
    

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class LessonPDF(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='pdfs')
    file = models.FileField(upload_to='lesson_pdfs/')
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"PDF für {self.lesson.title}"


# -------------------------
# Buy
# -------------------------
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='purchases')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='purchases')

    discount = models.ForeignKey(
        DiscountCode, on_delete=models.SET_NULL, null=True, blank=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} kaufte {self.section.name}"
