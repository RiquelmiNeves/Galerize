import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django, logout as logout_django
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Profile
import random
from .models import Foto

def login(request):
    if request.method == "GET":
        return render(request, 'usuarios/login.html')
    else:
        username = request.POST.get('email')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            login_django(request, user)
            return redirect('galeria') 
        else:
            return render(request, 'usuarios/login.html', {'error_message': 'E-mail ou senha inválidos!'})

def logout(request):
    if request.user.is_authenticated:
        logout_django(request)
    return redirect('login') 

import shutil
import os
from django.conf import settings
from django.core.files import File

import os
from django.conf import settings
from django.core.files import File

def cadastro(request):
    if request.method == "GET":
        return render(request, 'usuarios/cadastro.html')
    else:
        username = request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('senha')
        first_name = request.POST.get('nome')
        foto_perfil = request.FILES.get('foto_perfil')

        if User.objects.filter(username=username).exists():
            return render(request, 'usuarios/cadastro.html', {'error_message': "Este e-mail já está cadastrado!"})
        
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
        user.save()

        profile = Profile(user=user)
        if foto_perfil:
            profile.foto_perfil = foto_perfil
        else:
            caminho_padrao = os.path.join(settings.BASE_DIR, 'static', 'perfil', 'perfil.png')
            with open(caminho_padrao, 'rb') as f:
                profile.foto_perfil.save(f'perfil_padrao_user_{user.id}.png', File(f), save=False)
        profile.save()

        return redirect('login')


def home(request):
    return dashboard(request)

def upload_foto(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'GET':
        return render(request, 'usuarios/upload_foto.html')
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        imagem_file = request.FILES.get('imagem')

        if not imagem_file:
            return HttpResponse("Por favor, selecione uma imagem para upload.", status=400)

        try:
            nova_foto = Foto(
                usuario=request.user,
                titulo=titulo,
                descricao=descricao,
                imagem=imagem_file,
            )
            nova_foto.save()
            return redirect('galeria') 
        except Exception as e:
            print(f"Erro ao salvar foto: {e}")
            return HttpResponse(f"Ocorreu um erro ao fazer upload da foto: {e}", status=500)

def galeria(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_photos_queryset = Foto.objects.filter(usuario=request.user).order_by('-data_upload')

    search_query = request.GET.get('q', '').strip()

    if search_query:
        user_photos_queryset = user_photos_queryset.filter(
            Q(titulo__icontains=search_query) | Q(descricao__icontains=search_query)
        )
    
    return render(request, 'usuarios/galeria.html', {
        'fotos': user_photos_queryset,
        'current_search_query': search_query,
    })

def editar_foto_verificacao(request, id_foto):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        foto = get_object_or_404(Foto, id=id_foto, usuario=request.user)
    except Exception: 
        return HttpResponse("Foto não encontrada ou você não tem permissão para editá-la.", status=403)
    
    return render(request, 'usuarios/editar_foto.html', {'foto': foto})

def editar_foto(request, id_foto):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        try:
            foto = get_object_or_404(Foto, id=id_foto, usuario=request.user)
        except Exception:
            return HttpResponse("Foto não encontrada ou você não tem permissão para editá-la.", status=403)

        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')

        foto.titulo = titulo
        foto.descricao = descricao     
        foto.save()

        return redirect('galeria') 
    else:
        return redirect('editar_foto_verificacao', id_foto=id_foto) 

def excluir_foto_verificacao(request, id_foto):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        foto = get_object_or_404(Foto, id=id_foto, usuario=request.user)
    except Exception:
        return HttpResponse("Foto não encontrada ou você não tem permissão para excluí-la.", status=403)
    
    return render(request, 'usuarios/excluir_foto.html', {'foto': foto})

def excluir_foto(request, id_foto):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        try:
            foto = get_object_or_404(Foto, id=id_foto, usuario=request.user)
        except Exception:
            return HttpResponse("Foto não encontrada ou você não tem permissão para excluí-la.", status=403)
        
        foto.delete()

        return redirect('galeria') 
    else:
        return redirect('excluir_foto_verificacao', id_foto=id_foto)

def filtrar_fotos(request):
    if not request.user.is_authenticated:
        return redirect('login')

    fotos_filtradas = Foto.objects.filter(usuario=request.user)

    titulo_query = request.GET.get('titulo', '').strip()
    ordem_query = request.GET.get('ordem', '').strip()  # Nova variável

    if titulo_query:
        fotos_filtradas = fotos_filtradas.filter(titulo__icontains=titulo_query)

    # Aplicar ordenação com base na opção selecionada
    if ordem_query == 'mais_recente':
        fotos_filtradas = fotos_filtradas.order_by('-data_upload')
    elif ordem_query == 'mais_antigo':
        fotos_filtradas = fotos_filtradas.order_by('data_upload')
    elif ordem_query == 'az':
        fotos_filtradas = fotos_filtradas.order_by('titulo')
    elif ordem_query == 'za':
        fotos_filtradas = fotos_filtradas.order_by('-titulo')
    else:
        fotos_filtradas = fotos_filtradas.order_by('-data_upload')[:15]  # padrão

    return render(request, 'usuarios/filtrar_fotos.html', {
        'fotos': fotos_filtradas,
        'current_titulo_query': titulo_query,
        'current_ordem_query': ordem_query,  # para manter a opção selecionada no formulário
    })


def editar_foto_perfil(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = request.user.profile

    if request.method == 'POST':
        nova_foto = request.FILES.get('foto_perfil')
        if nova_foto:
            profile.foto_perfil = nova_foto
            profile.save()
            return redirect('home')  
    return render(request, 'usuarios/editar_perfil.html', {'profile': profile})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user

    fotos_usuario_logado = list(Foto.objects.filter(usuario=user).order_by('-data_upload')[:4])

    total_fotos_necessarias = 15
    faltando_para_15 = max(total_fotos_necessarias - len(fotos_usuario_logado), 0)


    usuarios_aleatorios = list(User.objects.exclude(id=user.id))
    random.shuffle(usuarios_aleatorios)

    galeria_mista = []
    for u in usuarios_aleatorios:
        if len(galeria_mista) >= faltando_para_15:
            break
        fotos = list(Foto.objects.filter(usuario=u).order_by('-data_upload')[:3])
        galeria_mista.extend(fotos)

    return render(request, 'usuarios/base.html', {
        'fotos_usuario_logado': fotos_usuario_logado,
        'galeria_mista': galeria_mista[:faltando_para_15],  # Garante que só adiciona o necessário
    })

def sobre(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'usuarios/sobre.html')

def contato(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'usuarios/Contato.html')

