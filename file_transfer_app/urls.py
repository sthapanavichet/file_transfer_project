from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('download/', views.download_page, name='download_page'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('upload/share/<int:file_id>/', views.share_file, name='share'),
    path('upload/remove/<int:file_id>/', views.remove_file, name='remove'),
]

# Include static files serving during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
