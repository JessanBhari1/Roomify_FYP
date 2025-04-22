from django.db import models

class contact(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    type = models.CharField(max_length=20)

    def str(self):
        return f" {self.subject} - {self.email} - {self.type}"
