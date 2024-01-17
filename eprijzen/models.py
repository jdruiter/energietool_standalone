from django.db import models
# from django.utils.translation import gettext_lazy as _

GAS_ELECTRA_CHOICES = [
    ('g', 'gas'), 
    ('e', 'electricity')
]


class EnergyPrice(models.Model):
    """ Energieprices 2017 - 2024, mostly NL
    > purchase_price = kale inkoop prijs
    > extra_fee_price is de inkoopprijs met daarbij de door jouw ingesteld (in telegram) inkoopvergoeding en BTW (2022 9% 2022, 2023 21%)
    > all_in_price = inkoopprijs + inkoopvergoeding en ODE + EnergieBelasting (EB) en BTW
    """

    id = models.BigAutoField(primary_key=True)
    country_id = models.CharField("Country (id)", max_length=4)  # NL,EN,DE,..
    # kind = models.CharField("Kind", max_length=255, choices=GAS_ELECTRA_CHOICES, help_text="e,g")
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
    # kind = models.CharField("Kind", max_length=255, choices=GAS_ELECTRA_CHOICES)
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




""" for later
class Country(models.Model):
    # Countries: AT, BE, BG, HR, CZ, DE_LU, DK_1, ES, EE, FI, FR, GR, HU, RO, NO_2, PL, PT, CH, NL, SE_3, IE_SEM, IT_NORD
    
    id = models.AutoField(primary_key=True)
    country_id = models.CharField("Country id", max_length=255, unique=True)
    country_iso = models.CharField("Country ISO", max_length=255, unique=True)
    country_name = models.CharField("Country", max_length=255)
        
    def __str__(self):
        return f"{self.country_name} ({self.country_id})"

    class Meta:
        verbose_name = "Land"
        verbose_name_plural = "Landen"


class BelastingRegels(models.Model):
    id = models.AutoField(primary_key=True, serialize=False, verbose_name='ID')
    kind = models.CharField('Kind', max_length=255, choices=GAS_ELECTRA_CHOICES)
    start_date = models.DateField('Start datum')
    end_date = models.DateField('Eind datum')

    btw = models.FloatField('BTW', null=True, default=None)
    opslag = models.FloatField('Opslag', null=True, default=None)
    ode = models.FloatField('ODE', null=True, default=None)
    eb = models.FloatField('Energiebelasting', null=True, default=None)

    def btw_display(self):
        return f"{self.btw:.0f} %" if self.btw else ''

    btw_display.short_description = 'BTW'

    def opslag_display(self):
        return f"€ {self.opslag:.3f}" if self.opslag else ''

    opslag_display.short_description = 'Opslag'

    def ode_display(self):
        return f"€ {self.ode:.4f}" if self.ode else ''

    ode_display.short_description = "ODE"

    def eb_display(self):
        return f"€ {self.eb:.4f}" if self.eb else ''

    eb_display.short_description = "Energiebelasting"

    def print_line(self):
        return f"{self.start_date}: {self.btw}%"

    class Meta:
        # db_table = 'eprijzen_belastingregels'
        verbose_name = "Belastingregels"
        verbose_name_plural = "Belasting regels"


class BelastingPerDag(models.Model):
    id = models.AutoField(primary_key=True)
    kind = models.CharField('Kind', max_length=255, choices=GAS_ELECTRA_CHOICES)
    datum = models.DateField('Datum')

    btw = models.FloatField('BTW', null=True, default=None)
    opslag = models.FloatField('Opslag', null=True, default=None)
    eb = models.FloatField('Energiebelasting', null=True, default=None)
    ode = models.FloatField('ODE', null=True, default=None)

    def btw_display(self):
        return f"{self.btw:.0f} %" if self.btw else ''

    btw_display.short_description = 'BTW'

    def opslag_display(self):
        return f"€ {self.opslag:.3f}" if self.opslag else ''

    opslag_display.short_description = 'Opslag'

    def ode_display(self):
        return f"€ {self.ode:.4f}" if self.ode else ''

    ode_display.short_description = "ODE"

    def eb_display(self):
        return f"€ {self.eb:.4f}" if self.eb else ''

    eb_display.short_description = "Energiebelasting"

    class Meta:
        ordering = ['kind', '-datum']
        verbose_name = "Belasting per dag"
        verbose_name_plural = "Belastingen per dag"
"""

""" Examples
 poolbuilder = models.ForeignKey(PoolBuilder, on_delete=models.SET_NULL, null=True, related_name='pools')
 logo = models.ImageField(_('Pool picture. Maximum size 10MB'), upload_to='pool/logos', blank=True, null=True)  # validators=[MaxSizeValidator(10000)
"""