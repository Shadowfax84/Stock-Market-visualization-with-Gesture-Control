from django.db import models


class NiftyData(models.Model):
    date = models.DateField()
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
        return f"StockData({self.date})"
