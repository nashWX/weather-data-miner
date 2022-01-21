from app.models import Util

def util(request):
    prev_url = request.META.get('HTTP_REFERER')
    if request.path == '/active-reports':
        prev_url = '/'

    return {'util': Util.objects.first(), 'prev_url': prev_url}