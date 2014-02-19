from django.db import models


class Car(models.Model):
    marka = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s %s" % (self.marka, self.model)

    def get_model(self):
        return self.model
