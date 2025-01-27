from django.db import models

# Create your models here.
class District(models.Model):
    name = models.CharField(max_length=255)
    manager_email = models.EmailField()

    def __str__(self):
        return self.name

class Store(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    manager_email = models.EmailField()
    team_members_emails = models.TextField()

    def __str__(self):
        return self.name


class QualityResolution(models.Model):
    resolution = models.CharField(max_length=255)

    def __str__(self):
            return self.resolution

class Marketplace(models.Model):
    name = models.CharField(max_length=255)
    to_email = models.EmailField()
    cc_email = models.EmailField()
    case_type = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class DevEmail(models.Model):
    to_email = models.EmailField()
    cc_email = models.EmailField()

class EmailBody(models.Model):
    case_type = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.case_type

class Instructions(models.Model):
    case_type = models.CharField(max_length=255)
    instruction = models.TextField()

    def __str__(self):
        return self.case_type

class Chat(models.Model):
    title = models.CharField(max_length=250)
    arabic = models.TextField()
    english = models.TextField()

    def __str__(self):
        return self.title