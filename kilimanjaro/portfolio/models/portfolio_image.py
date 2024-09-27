import datetime
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from model_utils.models import TimeStampedModel

from core.utils.general_data import MAX_PORTFOLIO_IMAGE_NUMBER
from core.utils.general_func import generate_uids
from portfolio.models import Portfolio


class PortfolioImage(TimeStampedModel):
    def _upload_to_portfolio_picture(self, filename):
        """Using filename returns "picture" field file saving path"""

        uid = generate_uids()  # Custom function to generate unique id
        now_time = datetime.datetime.now()
        return (
            "portfolio-picture/id-"
            + uid
            + "/"
            + str(now_time.strftime("%Y-%m-%d"))
            + "/"
            + filename
        )

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    picture = models.ImageField(
        upload_to=_upload_to_portfolio_picture, max_length=1000, null=True
    )  # _upload_to_portfolio_picture() has called here
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, verbose_name="portfolio"
    )

    def __str__(self):
        return str(self.id)

    def clean(self):

        # Can not add more images than MAX_PORTFOLIO_IMAGE_NUMBER
        if not self.pk and PortfolioImage.objects.filter(
            portfolio=self.portfolio
        ).count() >= int(MAX_PORTFOLIO_IMAGE_NUMBER):
            raise ValidationError(
                f"Up to {MAX_PORTFOLIO_IMAGE_NUMBER} pictures can be added to one portfolio."
            )
