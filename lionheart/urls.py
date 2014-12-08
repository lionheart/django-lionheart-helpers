try:
    from django.conf.urls.defaults import patterns
except ImportError:
    from django.conf.urls import patterns

from utils import simple_url, template_url

urlpatterns = patterns('lionheart.views',
    simple_url('auth/password/reset'),
    simple_url('auth/password/reset/request'),
    template_url('auth/password/reset/sent'),
)

