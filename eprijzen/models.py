from django.db import models


class EnergyPrice(models.Model):
    """ Energieprices 2017 - 2024, mostly NL
    > purchase_price = kale inkoop prijs
    > extra_fee_price is de inkoopprijs met daarbij de door jouw ingesteld (in telegram) inkoopvergoeding en BTW (2022 9% 2022, 2023 21%)
    > all_in_price = inkoopprijs + inkoopvergoeding en ODE + EnergieBelasting (EB) en BTW
    """

    id = models.BigAutoField(primary_key=True)
    country_id = models.CharField("Country (id)", max_length=4)  # NL,EN,DE,..
    objects = models.Manager()

    date = models.DateField("Date")
    time = models.TimeField("Time")
    purchase_price = models.FloatField("Purchase Price", null=True, default=None, help_text="Inkoopprijs")
    extra_fee_price = models.FloatField("Extra Fee Price", blank=True, null=True, default=None, help_text="Inkoopprijs + inkoopvergoeding + BTW")
    all_in_price = models.FloatField("All-in Price", blank=True, null=True, default=None, help_text="Inkoopprijs + inkoopvergoeding + ODE + energiebelasting + BTW")

    class Meta:
        ordering = ['-date']
        verbose_name = "Energyprice"
        verbose_name_plural = "Energy prices"
        index_together = ('date', 'time')

    def print_line(self):
        return f"{self.country_id} {self.date} {self.time}: €{self.purchase_price:.2f}"

    def str(self):
        return "{} {} {}".format(self.country_id, self.date.strftime('%Y-%m-%d'), self.time)


class GasPrice(models.Model):
    """ Gasprices 2018 - 2024, only NL """

    id = models.BigAutoField(primary_key=True, serialize=False)
    country_id = models.CharField("Country (id)", max_length=255)
    objects = models.Manager

    date = models.DateField("Date")
    time = models.TimeField("Time")
    purchase_price = models.FloatField("Purchase Price", null=True, default=None)
    extra_fee_price = models.FloatField("Extra Fee Price", blank=True, null=True, default=None)
    all_in_price = models.FloatField("All-in Price", blank=True, null=True, default=None)

    class Meta:
        ordering = ['-date']
        verbose_name = "Gas prijs"
        verbose_name_plural = "Gas prijzen"
        index_together = ('date', 'time')

    def print_line(self):
        return f"{self.country_id} {self.date} {self.time}: €{self.purchase_price:.2f}"

    def str(self):
        return "{} {} {}".format(self.country_id, self.date.strftime('%Y-%m-%d'), self.time)