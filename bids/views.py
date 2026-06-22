from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Bid
from notifications.models import Notification


@login_required
def my_bids(request):

    bids = Bid.objects.filter(
        bidder=request.user
    ).order_by("-created_at")

    return render(
        request,
        "bids/my_bids.html",
        {
            "bids": bids
        }
    )