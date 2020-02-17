from django.db import models

class ViewCounter(models.Model):
    name = models.CharField(max_length=100)
    counter = models.IntegerField(default=0)

    def __str__(self):
        return self.name + " = " + str(self.counter)
# Create your models here.
