from django.contrib import admin
from django.urls import path, include
from home import views as home_views
from tests import views as test_views, api as test_api
from entrance import views as entrance_views
from library import views as lib_views, api as lib_api
from dashboard import views as dash_views
from profiles import views as profile_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    
    #home
    path('', home_views._home, name='home'),
    path('nope/', home_views.nope, name='nope'),
    
    # test api
    path('test/submit-answer/<str:key>/<int:answer_id>/<int:option_id>', test_api.post_answer),
    
    # test
    path('test/<str:key>', test_views.test_handler),
    path('quick-test', test_views.quick_test, name='quick-test'),
    path('all-tests', test_views.all_tests, name='all-tests'),
    
    # library
    path('library/', lib_views.chapter_library, name='library'), 
    path('study/<int:chapter_id>', lib_views.study), 
    path('all-topics/<int:chapter_id>', lib_views.all_topics),
    path('topic/<int:level_id>', lib_views.study_topic),
    
    # library api 
    path('amar-onek-buddhi/<str:gibberish>', lib_api.amar_onek_buddhi), 
    
    # dashbaord
    path('dashboard/', dash_views.dashboard, name='dashboard'),
    path('solved-answer-sheet/<str:key>', dash_views.detailed_report),
    
    # profiles
    path('add-phone-number', profile_views.add_phone_number, name='add-phone-number'),
    
    # entrance
    path('login/', entrance_views.login, name='login'),
    path('logout/', entrance_views.logout, name='logout'),
]
