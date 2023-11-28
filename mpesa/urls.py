from django.urls import path
from . import views

urlpatterns = [
    path('get-token', views.get_auth_token, name='get_auth_token'),
    path('stk-push', views.stk_push_view, name='stk_push'),
    path('register-url', views.register_url_view, name='register_url'),
    path('b2c', views.b2c_view, name='b2c'),
    path('b2c/result', views.b2c_callback_view, name='b2c_callback'),
    path('b2c/queue', views.b2c_queue_view, name='b2c_queue'),
    path('c2b/result', views.register_url_view, name='c2b_result'),  # Assuming it's the same as register_url
    path('express/callback/url', views.express_callback_view, name='express_callback')
]
