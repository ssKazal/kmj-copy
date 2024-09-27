from django_filters import Filter
from django_filters import rest_framework as rest_framework_filter

from user.models import User


class OccupationFilter(Filter):
    """Returns filtered queryset

    Methods
    -------
    filter(qs=Queryset, value=""):
        Returns queryset
    """

    def filter(self, qs, value):
        """Returns queryset
        User model has no "occupation" field, so to search a User(skilled worker)
        by it's "occupation", this custom filte will use

        Parameters
        ----------
        qs : QuerySet
            Users SkilledWorker objects QuerySet
        value : str
            Name of the occupation

        Returns
        -------
        QuerySet
        """

        if not value:  # No 'occupation name' inserted
            return qs

        qs = qs.filter(skilledworker__occupation__name__icontains=value)
        return qs


class SkilledWorkerFilterSet(rest_framework_filter.FilterSet):
    """To filter users(skilled worker) by 'country','city','occupation name'"""

    occupation = OccupationFilter(field_name="occupation")  # Custome field

    class Meta:
        model = User
        fields = {"country": ["exact"], "city": ["icontains"]}
