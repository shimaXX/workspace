from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django_socketio import broadcast, broadcast_channel, NoSocket
from django.db.models import Count

from showtweet.models import ChatRoom

@user_passes_test(lambda user: user.is_staff)
def system_message(request, template="system_message.html"):
    # timeの取得
    from datetime import datetime
    ymdt = datetime.now()
    year = ymdt.year
    month = ymdt.month
    day = ymdt.day
    hour = ymdt.hour
    minute = ymdt.minute
    filtered = ChatRoom.objects.filter(create_time>=datetime(year, month, day,hour,minute))
    cnt = filtered.annotate(Count('tweet'))
    data = {"action": "system", "message": cnt}
    try:
        broadcast(data)
    except NoSocket, e:
        context["message"] = e
    else:
        context["message"] = "Message sent"
    return render(request, template, context)
