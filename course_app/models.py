from django.db import models
from auth_app.models import User
from django.utils.translation import gettext_lazy as _
from invoice_app.models import Invoice

import subprocess
import json
from django.db import models


class Status(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")


class Language(models.TextChoices):
    DE = "Deutsch", _("Deutsch")
    PL = "Polnisch", _("Polnisch")


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
    image = models.ImageField(
        upload_to="media/lessons/", null=True, blank=True)
    order = models.DecimalField(
        max_digits=4, decimal_places=2, null=False, blank=False, default=0)
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

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
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
    order = models.DecimalField(
        max_digits=4, decimal_places=2, null=False, blank=False, default=0)

    class Meta:
        ordering = ['order']


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField()

    # oder URLField bei Verwendung von YouTube/Vimeo
    video = models.FileField(upload_to="media/videos/",  null=True, blank=True)
    description_under_video = models.TextField(blank=True)
    order = models.DecimalField(
        max_digits=4, decimal_places=2, null=False, blank=False, default=0)
    duration = models.PositiveIntegerField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # save file first

        if self.video and not self.duration:
            video_path = self.video.path

            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "format=duration",
                    "-of", "json",
                    video_path,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            output = json.loads(result.stdout)
            duration = float(output["format"]["duration"])

            self.duration = int(duration)
            super().save(update_fields=["duration"])
            
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

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
        return f"{self.title} für {self.lesson.title}"
