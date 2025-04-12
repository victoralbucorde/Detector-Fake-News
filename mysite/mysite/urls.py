from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_arquivo_view, name='upload_arquivo'),
    path('chat/<uuid:chat_id>/', views.chat_detail_view, name='chat_detail'),
    path('chat/<uuid:chat_id>/reanalizar/', views.reanalizar_view, name='reanalizar'),
    path('chat/<uuid:chat_id>/opcao/<uuid:opcao_id>/', views.selecionar_opcao_view, name='selecionar_opcao'),
]