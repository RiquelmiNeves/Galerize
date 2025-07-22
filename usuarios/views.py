import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django, logout as logout_django
from django.contrib.auth.models import User
from django.db.models import Q

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

def cadastro(request):
    if request.method == "GET":
        return render(request, 'usuarios/cadastro.html')
    else:
        username = request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('senha')
        first_name = request.POST.get('nome')

        user_exists = User.objects.filter(username=username).first() 

        if user_exists:
            return render(request, 'usuarios/cadastro.html', {'error_message': "Este e-mail já está cadastrado!"}) 
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
                user.save()
                return redirect('login') 
            except Exception as e:
                print(f"Erro ao cadastrar usuário: {e}")
                return render(request, 'usuarios/cadastro.html', {'error_message': "Ocorreu um erro ao tentar cadastrar. Tente novamente."})

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'usuarios/base.html') 

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
    data_query = request.GET.get('data', '').strip()

    if titulo_query:
        fotos_filtradas = fotos_filtradas.filter(titulo__icontains=titulo_query)
    
    if data_query:
        try:
            filter_date = datetime.datetime.strptime(data_query, '%Y-%m-%d').date()
            fotos_filtradas = fotos_filtradas.filter(data_upload__date=filter_date)
        except ValueError:
            pass
    
    if not (titulo_query or data_query):
        fotos_filtradas = fotos_filtradas.order_by('-data_upload')[:15]
    else:
        fotos_filtradas = fotos_filtradas.order_by('-data_upload')

    return render(request, 'usuarios/filtrar_fotos.html', {
        'fotos': fotos_filtradas,
        'current_titulo_query': titulo_query,
        'current_data_query': data_query,
    })