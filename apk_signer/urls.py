from django.conf import settings
from django.conf.urls import patterns, include, url
from django import http


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'sign', include('apk_signer.sign.urls')),
    url(r'system/', include('apk_signer.system.urls')),
    url(r'', include('apk_signer.base.urls')),

    # Generate a robots.txt
    (r'^robots\.txt$',
        lambda r: http.HttpResponse(
            "User-agent: *\n{0}: /".format('Allow' if settings.ENGAGE_ROBOTS
                                           else 'Disallow'),
            mimetype="text/plain"
        )
    )

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
