import asyncio
import json
import uuid
from decouple import config
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.core.cache import cache

from .utils.big_map import big_map
from .utils.download_media import download_media
from .utils.generate_map import generate_map
from .models import AccessPassword, HashTag, Util, Warning
from dateutil.parser import isoparse
import pytz
import datetime as dt
from django.utils import timezone

def authorize(request):
    if request.method == 'POST':
        userpassword = request.POST.get('password')
        current_user = None
        try:
            current_user = AccessPassword.objects.filter(password=userpassword).first()
            starttime = request.POST.get('starttime')
            endtime = request.POST.get('endtime')
            if current_user.password == userpassword and starttime and endtime:
                request.session['starttime'] = starttime
                request.session['endtime'] = endtime
                request.session['authenticate'] = True
                request.session['access_id'] = current_user.id
                return redirect(reverse('active-report'))
            else:
                messages.add_message(request, messages.WARNING, 'invalid info provided, please provide correct data')
                return redirect(reverse('authorize'))
        except Exception as e:
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
            'local': timezone.localtime(past_30, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M %p'),
            'utc': past_30.isoformat(),
            'title': 'Past 30 Minutes',
         },
        {
            'local': timezone.localtime(past_hour, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M %p'),
            'utc': past_hour.isoformat(),
            'title': 'Past Hour',
        },
        {
            'local': timezone.localtime(past_3hour, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M %p'),
            'utc': past_3hour.isoformat(),
            'title': 'Past 3 Hours',
        },
        {
            'local': timezone.localtime(past_12hour, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M %p'),
            'utc': past_12hour.isoformat(),
            'title': 'Past 12 Hours',
        },
        {
            'local': timezone.localtime(past_24hour, pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M %p'),
            'utc': past_24hour.isoformat(),
            'title': 'Past 24 Hours',
        },
    ]

    end_local =  dt.datetime.now(tz=pytz.timezone(zone)).strftime('%Y-%m-%d %I:%M %p')
    end_utc =   dt.datetime.now(tz=pytz.utc).isoformat()

    context = {
        'suggestions': suggestions,
        'end_utc': end_utc,
        'end_local': end_local,
    }

    return render(request, 'authorize.html', context=context)

def activeReport(request):
    if not request.session.get('authenticate'):
        messages.add_message(request, messages.WARNING, 'please provided required info before visit any other page')
        return redirect(reverse('authorize'))

    access_id = request.session.get('access_id')
    start_time = isoparse(request.session.get('starttime'))
    end_time = isoparse(request.session.get('endtime')) + dt.timedelta(hours=12)
    user = AccessPassword.objects.filter(id=access_id).first()
    context = {
       'amount_tornado_warnings': len(Warning.get_warnings('TORNADO', start_time, end_time, user)),
       'amount_tstorm_warnings': len(Warning.get_warnings('TSTORM', start_time, end_time, user)),
       'amount_flood_warnings': len(Warning.get_warnings('FLOOD', start_time, end_time, user)),
       'last_update': cache.get('tornado_last_update')
    }
    # context['map_path'] = generate_map(lats=user.lat, lons=user.long, withMarker=False, width=user.width or 3, height=user.height or 5)
    if not user.lats_bounds or not user.lats_bounds:
        messages.add_message(request, messages.WARNING, 'You have not set lats_bounds and lons_bounds for this user, please update these fields from admin panel to access this page')
        return redirect(reverse('authorize'))
    
    lats, lons = user.location_coordinate
    lats_bounds = user.lats_bounds.split(',')
    lons_bounds = user.lons_bounds.split(',')
    context['map_path'] = big_map(lats_bounds=lats_bounds,lons_bounds=lons_bounds, lats=lats, lons=lons, place_name=user.place_name, force=user.generate_new_big_map)
    return render(request, 'active-report.html', context=context)


def hashtags(request):
    access_id = request.session.get('access_id')
    user = AccessPassword.objects.filter(id=access_id).first()
    hashes = user.hashtag_set.all()
    return render(request, 'hashtags.html', context={'hash_tags': hashes})

def warning_update(request):
    # zone = config('timezone', cast=str, default='America/New_York')
    # end_time =  dt.datetime.now(tz=pytz.timezone(zone))
    start_time = isoparse(request.session.get('starttime'))
    end_time = isoparse(request.session.get('endtime')) + dt.timedelta(hours=12)
    access_id = request.session.get('access_id')
    user = AccessPassword.objects.filter(id=access_id).first()

    context = {
        'amount_tornado_warnings': len(Warning.get_warnings('TORNADO', start_time, end_time, user)),
        'amount_tstorm_warnings': len(Warning.get_warnings('TSTORM', start_time, end_time, user)),
        'amount_flood_warnings': len(Warning.get_warnings('FLOOD', start_time, end_time, user)),
        'last_update': cache.get("tornado_last_update")
    }
    return JsonResponse(context)


def warningList(request):
    access_id = request.session.get('access_id')
    start_time = isoparse(request.session.get('starttime'))
    end_time = isoparse(request.session.get('endtime')) + dt.timedelta(hours=12)
    user = AccessPassword.objects.filter(id=access_id).first()

    warnings = Warning.get_warnings(request.GET.get('type').upper(), start_time, end_time, user)
    lats = [warning.location.lat for warning in warnings]
    lons = [warning.location.lng for warning in warnings]
    warnings = [warning.formated for warning in warnings]
    key = f"{request.GET.get('type')}_last_update"
    last_update = cache.get(key) or dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    context = {
        'warnings': warnings,
        # 'map_path': generate_map(lats=user.lat, lons=user.long, points=[lats, longs]),
        'last_update': last_update,
    }

    lats_bounds = user.lats_bounds.split(',')
    lons_bounds = user.lons_bounds.split(',')
    coordinate = lats + lons
    map_name = str(str(coordinate).__hash__())
    context['map_path'] = big_map(lats_bounds=lats_bounds,lons_bounds=lons_bounds, lats=lats, lons=lons, place_name=map_name, marker=True, force=user.generate_new_big_map)

    return JsonResponse(context, safe=False)

def about(request):
    return render(request, 'about.html')

def download(request):
    if not request.session.get('authenticate'):
        messages.add_message(request, messages.WARNING, 'you are not authorized to visit the download media page')
        return redirect(reverse('authorize'))
    
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        url = body['url']
        if url:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
            links = loop.run_until_complete(download_media(url))
            return JsonResponse({'links': links, 'status': "success"})
        return JsonResponse({'status': "error"})
    return render(request, 'download.html')