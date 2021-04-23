from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib import messages

from .models import AccessPassword
from .utils.get_locations import get_locations, location_url
from .utils.parse_datetime import get_parsed_time
from .utils.data import hash_tags, hash_url

def authorize(request):
    if request.method == 'POST':
        defaultPassword = AccessPassword.objects.first().password
        userpassword = request.POST.get('password')
        starttime = request.POST.get('starttime')
        endtime = request.POST.get('endtime')
        if defaultPassword == userpassword and starttime and endtime:
            request.session['starttime'] = starttime
            request.session['endtime'] = endtime
            request.session['authenticate'] = True
            return redirect(reverse('active-report'))
        else:
            messages.add_message(request, messages.WARNING, 'invalid info provided, please provide correct data')
            return redirect(reverse('authorize'))
    return render(request, 'authorize.html')

def activeReport(request):
    context = {
       'amount_tornado_warnings': 4,
       'amount_tstorm_warnings': 22,
       'amount_flood_warnings': 6
    }
    if not request.session.get('authenticate'):
        messages.add_message(request, messages.WARNING, 'please provided required info before visit any other page')
        return redirect(reverse('authorize'))
    return render(request, 'active-report.html', context=context)


def location(request):
    if not request.session.get('authenticate'):
        messages.add_message(request, messages.WARNING, 'please provided required info before visit any other page')
        return redirect(reverse('authorize'))
    if request.method == 'POST' and request.POST.get('type'):
        _type = request.POST.get('type')
        context = {
            'type': _type, 
            'locationData': get_locations(), 
            'location_url': location_url,
            'start_time': get_parsed_time(request.session.get('starttime')),
            'end_time': get_parsed_time(request.session.get('endtime')),
            'hash_tags': hash_tags,
            'hash_url': hash_url
        }
        return render(request, 'location.html', context=context)
    return redirect(reverse('active-report'))