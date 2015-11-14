from .resources import Resource


class Pagination(object):
    def __init__(self, *args, **kwargs):
        # TODO (howei): possibly extract auto_paginate from kwargs
        # so users can do client = Client(auto_paginate=True)
        self.auto_paginate = False
        super(Pagination, self).__init__(*args, **kwargs)

    def response_callback(self, r, **kwargs):
        # TODO (howei): possibly implement auto pagination logic here
        return super(Pagination, self).response_callback(r, **kwargs)

    def paginate(self, *args, **kwargs):
        params = {}
        if 'per_page' in kwargs:
            params['per_page'] = kwargs['per_page']
            del kwargs['per_page']
        elif self.auto_paginate:
            # if per page is not defined, default to 100 per page
            params['per_page'] = 100

        if 'page' in kwargs:
            params['page'] = kwargs['page']
            del kwargs['page']

        kwargs['params'] = params
        resource = self.get(*args, **kwargs)
        data = list(resource.schema)

        if self.auto_paginate:
            while 'next' in resource.rels and self.rate_limit.remaining > 0:
                resource = resource.rels['next'].get()
                data.extend(list(resource.schema))

        return Resource(self.session, schema=data,
                        url=resource.url, name=resource.name)
