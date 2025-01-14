from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('', views.home, name='home'),
                  path('statistics/', views.statistics, name='statistics'),
                  path('demand/', views.demand, name='demand'),
                  path('geography/', views.geography, name='geography'),
                  path('skills/', views.skills, name='skills'),
                  path('latest_jobs/', views.latest_jobs, name='latest_jobs'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
