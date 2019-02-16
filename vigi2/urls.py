from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.searchRoom, name='home'),
    url(r'^register/$', views.register, name='register'),
    url(r'^pay/(?P<reservationid>[0-9]+)/$', views.pay, name='pay'),
    url(r'^applycoupon/(?P<reservationid>[0-9]+)/coupon/(?P<couponid>[0-9]+)$', views.apply_coupons, name='apply_coupon'),
    url(r'^edit_reservation/(?P<reservationid>[0-9]+)/$', views.edit_reservation, name='edit_reservation'),
    url(r'^mypage/$', views.mypage, name='mypage'),
    url(r'^editroom/(?P<roomid>[0-9]+)$', views.editroom, name='editroom'),
    url(r'^confirm/(?P<token>.+)$', views.confirm, name='confirm'),
    url(r'^retrieverooms/$', views.retrieverooms, name='retrieverooms'),
    url(r'^approve/$', views.approve, name='approve'),
    url(r'^approve_user/(?P<id>[0-9]+)$', views.approve_user, name='approve_user'),
    url(r'^deny_user/(?P<id>[0-9]+)$', views.deny_user, name='deny_user'),
    url(r'^delete/(?P<reservationid>[0-9]+)/$', views.delete, name='delete'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'', include('social_django.urls', namespace='social')),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html'}, name='logout'),
    url(r'^reserve/(?P<roomid>[0-9]+)/checkin/(?P<checkin>[0-9|-]+)/checkout/(?P<checkout>[0-9|-]+)/number/(?P<number>[0-9]+)/$', views.reserve,  name='reserve'),
]
