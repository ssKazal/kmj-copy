from rest_framework import pagination
from rest_framework.response import Response
from django.shortcuts import reverse


class ResultSetPagination(pagination.PageNumberPagination):
	page_size = 10
	page_size_query_param = 'page_size'

	def get_paginated_response(self, data):
		return Response({
				'pagination': {
				'total_value': self.page.paginator.count,
				'this_page_start_index_no': self.page.start_index(),
				'this_page_end_index_no': self.page.end_index(),
				'num_of_pages': self.page.paginator.num_pages,
				'current_page': self.page.number,
				'next_page_number': self.page.number+1 if self.get_next_link() else None,
				'page_range': list(self.page.paginator.page_range),
				'next_page': self.get_next_link()
			},
			'results': data,
		})