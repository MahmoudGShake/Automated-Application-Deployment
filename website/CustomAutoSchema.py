from typing import List

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import _SchemaType


class CustomAutoSchema(AutoSchema):
    def _get_parameters(self):
        params = super()._get_parameters()
        for param in params:
            for key,value in param.items():
                if key == "description" and value == 'A search term.':
                    # Get search fields
                    search_fields = getattr(self.view, 'search_fields', [])

                    # Flatten in case search_fields contains nested lists
                    flat_search_fields = []
                    for field in search_fields:
                        if isinstance(field, list):  # If field is a list, extend the result
                            flat_search_fields.extend(field)
                        else:
                            flat_search_fields.append(field)

                    # Convert all fields to strings and join them for description
                    param[key] = f"Search by: {', '.join(map(str, flat_search_fields))}"
                elif key == "description" and value == 'Which field to use when ordering the results.':
                    # Get ordering fields
                    ordering_fields = getattr(self.view, 'ordering_fields', [])

                    # Flatten in case search_fields contains nested lists
                    flat_ordering_fields = []
                    for field in ordering_fields:
                        if isinstance(field, list):  # If field is a list, extend the result
                            flat_ordering_fields.extend(field)
                        else:
                            flat_ordering_fields.append(field)

                    # Convert all fields to strings and join them for description
                    param[key] = f"Order by Ascending: {', '.join(map(str, flat_ordering_fields))} OR Order by Descending: {', '.join([f'-{f}' for f in flat_ordering_fields])}"

        return params
