from django.urls import path
from . import views
from usuarios import views as usuarios_views

urlpatterns = [
    path('login/', views.login, name = 'login'),
    path('cadastro/', views.cadastro, name = 'cadastro'),
    path('home/', views.home, name = 'home'),
    path('logout/', views.logout, name = 'logout'),
    
    # URLs para Fotos
    path('upload_foto/', views.upload_foto, name='upload_foto'),
    path('galeria/', views.galeria, name='galeria'),
    path('editar_foto_verificacao/<int:id_foto>/', views.editar_foto_verificacao, name='editar_foto_verificacao'),
    path('editar_foto/<int:id_foto>/', views.editar_foto, name='editar_foto'),
    path('excluir_foto_verificacao/<int:id_foto>/', views.excluir_foto_verificacao, name='excluir_foto_verificacao'),
    path('excluir_foto/<int:id_foto>/', views.excluir_foto, name='excluir_foto'),
    path('filtrar_fotos/', views.filtrar_fotos, name='filtrar_fotos'),
    path('editar-foto/', usuarios_views.editar_foto_perfil, name='editar_foto'),
    path('sobre/', views.sobre, name='sobre'),
    path('contato/', views.contato, name='contato'),
]