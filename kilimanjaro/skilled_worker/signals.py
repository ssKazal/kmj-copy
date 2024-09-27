from django.db.models.signals import post_save
from django.dispatch import receiver

from portfolio.models import Portfolio
from skilled_worker.models import SkilledWorker


@receiver(post_save, sender=SkilledWorker)
def create_portfolio(sender, instance, created, **kwargs):

    if created:

        # While creating a 'SkilledWorker' instance, a 'Portfolio' object for that instance also create
        Portfolio.objects.create(skilled_worker=instance)
