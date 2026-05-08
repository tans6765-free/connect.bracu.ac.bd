from django.urls import path,include
urlpatterns=[path('',include('portal.urls')), path('accounts/', include('allauth.urls'))]