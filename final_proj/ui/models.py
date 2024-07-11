from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Sector(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Stock(models.Model):
    name = models.CharField(max_length=255)
    ticker = models.CharField(max_length=25, unique=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sectors = models.ManyToManyField(Sector, blank=True)
    stocks = models.ManyToManyField(Stock, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Define a function to create a UserProfile instance whenever a new User is created


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Check if the User instance is newly created
    if created:
        # Create a new UserProfile instance associated with the User instance
        UserProfile.objects.create(user=instance)

# Define a function to save the UserProfile instance whenever a User instance is saved


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Access the UserProfile instance associated with the User instance and save it
    instance.userprofile.save()


class NiftyData(models.Model):
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    adj_close = models.FloatField()
    daily_return = models.FloatField()
    cumulative_return = models.FloatField()
    sma_50 = models.FloatField()
    sma_200 = models.FloatField()
    rsi = models.FloatField()
    upper_bb = models.FloatField()
    lower_bb = models.FloatField()
    obv = models.FloatField()
    force_index = models.FloatField()
    standard_deviation = models.FloatField()
    final_decision = models.CharField(max_length=10)
    market_condition = models.CharField(max_length=10)

    def __str__(self):
        return f"NiftyData ({self.date})"


class StockData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    daily_return = models.FloatField()
    cumulative_return = models.FloatField()
    sma_50 = models.FloatField()
    sma_200 = models.FloatField()
    rsi = models.FloatField()
    upper_bb = models.FloatField()
    lower_bb = models.FloatField()
    obv = models.FloatField()
    force_index = models.FloatField()
    standard_deviation = models.FloatField()
    final_decision = models.CharField(max_length=10)
    market_condition = models.CharField(max_length=10)

    class Meta:
        unique_together = ('stock', 'date')

    def __str__(self):
        return f"{self.stock.name} - {self.date}"
