from django.shortcuts import render
from .models import Category


def category_list(request):

    categories = Category.objects.all()

    return render(
        request,
        "categories/list.html",
        {
            "categories": categories
        }
    )