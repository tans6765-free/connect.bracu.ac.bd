from django.db import models
class Student(models.Model): email=models.EmailField(unique=True)