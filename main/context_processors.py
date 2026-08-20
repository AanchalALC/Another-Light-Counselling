from .models import Service


def service_categories(request):
    """
    Groups published services by category, in the fixed CATEGORY_ORDER, for the
    nav dropdown and any other template that wants the same grouping the
    Services hub uses. Available on every template render.
    """
    services = Service.objects.filter(is_published=True).order_by('id')

    by_category = {}
    uncategorized = []
    for service in services:
        if service.category:
            by_category.setdefault(service.category, []).append(service)
        else:
            uncategorized.append(service)

    category_labels = dict(Service.CATEGORY_CHOICES)
    groups = []
    for key in Service.CATEGORY_ORDER:
        items = by_category.get(key, [])
        if items:
            groups.append({'key': key, 'label': category_labels.get(key, key), 'services': items})

    return {
        'service_categories': groups,
        'uncategorized_services': uncategorized,
    }
