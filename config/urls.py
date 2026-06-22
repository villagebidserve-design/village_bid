from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path("accounts/", include("accounts.urls")),
    path('dashboard/', include('dashboard.urls')),
    path("products/", include("products.urls")),
    path("auctions/",include("auctions.urls")),
    path("bids/",include("bids.urls")),
    path("favorites/",include("favorites.urls")),
    path("categories/",include("categories.urls")),
    path("reviews/",include("reviews.urls")),
    path("notifications/",include("notifications.urls")),
    path("messages/", include("messages_app.urls")),
    path("livebidding/", include("livebidding.urls")),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )