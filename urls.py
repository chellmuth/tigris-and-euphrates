from django.conf.urls.defaults import *
from tigris.views import current_datetime, hours_ahead

urlpatterns = patterns('',
    (r'^time/$', current_datetime),
    (r'^time/plus/(\d{1,2})/$', hours_ahead),
    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
