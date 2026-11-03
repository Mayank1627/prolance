from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

# Custom admin titles
admin.site.site_header = "Prolance Administration & Moderation"
admin.site.site_title = "Prolance Portal"
admin.site.index_title = "Academic Platform Operations"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('proposals/', include('proposals.urls')),
    path('workspace/', include('workspace.urls')),
    path('reviews/', include('reviews.urls')),
    path('notifications/', include('notifications.urls')),
]

# Media file serving (works in both development and single-server persistent disk production)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
