from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
	page_size_query_param = 'page_size'  # Name of the query parameter for page size
	max_page_size = 100  # Maximum allowable page size

	def paginate_queryset(self, queryset, request, view=None):

		# Get the page_size query parameter value
		page_size = self.get_page_size(request)
		# If page_size is None, return the entire queryset (disable pagination)
		if page_size is None:
			return None  # Returning None disables pagination

		# Otherwise, use the default pagination logic
		return super().paginate_queryset(queryset, request, view)
