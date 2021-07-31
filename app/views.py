from typing import cast
from decouple import config
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .models import AccessPassword, HashTag, Warning
from dateutil.parser import isoparse
from django.db.models import Q
import pytz
import datetime as dt
from django.utils import timezone

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
    zone = config('timezone', cast=str, default='America/New_York')
    past_30 = dt.datetime.now(tz=pytz.utc) - dt.timedelta(minutes=30)
    past_hour = dt.datetime.now(tz=pytz.utc) - dt.timedelta(hours=1)
    past_3hour = dt.datetime.now(tz=pytz.utc) - dt.timedelta(hours=3)
    past_12hour = dt.datetime.now(tz=pytz.utc) - dt.timedelta(hours=12)
    past_24hour = dt.datetime.now(tz=pytz.utc) - dt.timedelta(hours=24)
    suggestions = [
        {
            'local': timezone.localtime(past_30, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M'),
            'utc': past_30.isoformat(),
            'title': 'Past 30 Minutes',
         },
        {
            'local': timezone.localtime(past_hour, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M'),
            'utc': past_hour.isoformat(),
            'title': 'Past Hour',
        },
        {
            'local': timezone.localtime(past_3hour, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M'),
            'utc': past_3hour.isoformat(),
            'title': 'Past 3 Hours',
        },
        {
            'local': timezone.localtime(past_12hour, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M'),
            'utc': past_12hour.isoformat(),
            'title': 'Past 12 Hours',
        },
        {
            'local': timezone.localtime(past_24hour, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M'),
            'utc': past_24hour.isoformat(),
            'title': 'Past 24 Hours',
        },
    ]

    end_local =  dt.datetime.now(tz=pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M')
    end_utc =   dt.datetime.now(tz=pytz.utc).isoformat()

    context = {
        'suggestions': suggestions,
        'end_utc': end_utc,
        'end_local': end_local,
    }

    return render(request, 'authorize.html', context=context)

def activeReport(request):
    start_time = isoparse(request.session['starttime'])
    end_time = isoparse(request.session['endtime'])
    torandoQ = Q(warning_type='TORNADO') & (Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
    tstormQ = Q(warning_type='TSTORM') & (Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
    floodQ = Q(warning_type='FLOOD') & (Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
    context = {
       'amount_tornado_warnings': Warning.objects.filter(torandoQ).count(),
       'amount_tstorm_warnings': Warning.objects.filter(tstormQ).count(),
       'amount_flood_warnings': Warning.objects.filter(floodQ).count()
    }
    if not request.session.get('authenticate'):
        messages.add_message(request, messages.WARNING, 'please provided required info before visit any other page')
        return redirect(reverse('authorize'))
    return render(request, 'active-report.html', context=context)


def warnings(request):
    #get and set up client timezone for future 
    if not request.session.get('authenticate'):
        messages.add_message(request, messages.WARNING, 'please provided required info before visit any other page')
        return redirect(reverse('authorize'))
    if request.method == 'POST' and request.POST.get('type'):
        _type = request.POST.get('type')
        start_time = isoparse(request.session['starttime'])
        end_time = isoparse(request.session['endtime'])
        warning_data = []
        hashes = []
        if _type != 'hashtag':
            q = Q(warning_type=_type.upper()) & (Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
            warning_data = Warning.objects.filter(q)
        else:
            hashes = HashTag.objects.all()

        context = {
            'type': _type, 
            'warnings': warning_data, 
            'hash_tags': hashes,
        }
        return render(request, 'warnings.html', context=context)
    return redirect(reverse('active-report'))