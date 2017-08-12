# Copyright 2015-2017 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

