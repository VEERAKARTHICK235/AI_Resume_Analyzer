from django.db import models

class Resume(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='resumes/')
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    parsed_data = models.JSONField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
