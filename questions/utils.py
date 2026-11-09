from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def _make_questions(n=30):
    return [
        {'id': i, 'title': f'title {i}', 'text': f'text {i}',
         'tags': ['python', 'django'], 'rating': i % 7}
        for i in range(1, n + 1)
    ]

def paginate(objects_list, request, per_page=10):
    try:
        per_page = int(request.GET.get('per_page', per_page))
        if per_page <= 0 or per_page > 1000:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10

    paginator = Paginator(objects_list, per_page)

    try:
        page_number = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_number = 1

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page