
# from flask import abort


# def get_paginated_list(results, url, start, limit, with_params):
#     start = int(start)
#     limit = int(limit)
#     count = len(results)
#     if count < start or limit < 0:
#         abort(404)
#     # make response
#     obj = {}
#     obj['start'] = start
#     obj['limit'] = limit
#     obj['count'] = count
#     # make URLs
#     # make previous url
#     if start == 1:
#         obj['previous'] = ''
#     else:
#         start_copy = max(1, start - limit)
#         limit_copy = limit
#         if with_params:
#             obj['previous'] = url + '&start=%d&limit=%d' % (start_copy, limit_copy)
#         else:
#             obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
#     # make next url
#     if start + limit > count:
#         obj['next'] = ''
#     else:
#         start_copy = start + limit
#         if with_params:
#             obj['next'] = url + '&start=%d&limit=%d' % (start_copy, limit)
#         else:
#             obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)

#     # finally extract result according to bounds
#     obj['results'] = results[(start - 1):(start - 1 + limit)]
#     return obj

from flask import abort
from urllib.parse import urlencode

def get_paginated_list(results, url, start=1, limit=10, with_params=False):
    try:
        start = int(start)
        limit = int(limit)
    except ValueError:
        abort(400, description="Invalid pagination parameters. 'start' and 'limit' must be integers.")

    count = len(results)
    if count == 0:  # Handle empty results
        return {
            'start': start,
            'limit': limit,
            'count': 0,
            'results': [],
            'previous': '',
            'next': ''
        }

    if start < 1 or start > count:
        abort(404, description="Pagination parameters are out of range.")

    # Build the pagination response
    obj = {
        'start': start,
        'limit': limit,
        'count': count,
        'results': results[(start - 1):(start - 1 + limit)]
    }

    # Previous URL
    if start > 1:
        prev_start = max(1, start - limit)
        prev_limit = limit
        params = {'start': prev_start, 'limit': prev_limit}
        obj['previous'] = f"{url}&{urlencode(params)}" if with_params else f"{url}?{urlencode(params)}"
    else:
        obj['previous'] = ''

    # Next URL
    if start + limit <= count:
        next_start = start + limit
        params = {'start': next_start, 'limit': limit}
        obj['next'] = f"{url}&{urlencode(params)}" if with_params else f"{url}?{urlencode(params)}"
    else:
        obj['next'] = ''

    return obj
