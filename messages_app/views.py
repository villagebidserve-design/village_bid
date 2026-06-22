from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def chat_room(request, room_name):
    return render(
        request,
        "messages_app/chat.html",
        {
            "room_name": room_name
        }
    )
