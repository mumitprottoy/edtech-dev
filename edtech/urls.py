from django.contrib import admin
from django.urls import path
from home import views as home_views
from tests import views as test_views, api as test_api
from entrance import views as entrance_views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    #home
    path('', home_views._home, name='home'),
    
    # test api
    path('test/submit-answer/<str:key>/<int:answer_id>/<int:option_id>', test_api.post_answer),
    
    # test
    path('test/<str:key>', test_views.test_handler),
    path('quick-test', test_views.quick_test, name='quick-test'),
    
    #entrance
    path('login/', entrance_views.login, name='login'),
    path('logout/', entrance_views.logout, name='logout'),
]
