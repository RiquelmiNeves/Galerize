# usuarios/views.py

import os
import datetime
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django, logout as logout_django
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Foto# usuarios/views.py

import os
import datetime
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django, logout as logout_django
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Foto # Certifique-se de que seu modelo Foto está importado

# --- Views de Autenticação ---

def login(request):
    """
    Trata o login de usuários.
    Redireciona para 'home' se o login for bem-sucedido, caso contrário, exibe mensagem de erro.
    """
    if request.method == "GET":
        return render(request, 'usuarios/login.html')
    else: # request.method == "POST"
        username = request.POST.get('email')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            login_django(request, user)
            # Redireciona para 'galeria' após o login bem-sucedido, que é uma página de conteúdo útil.
            return redirect('galeria') 
        else:
            # Melhorar a mensagem de erro para o usuário final
            return render(request, 'usuarios/login.html', {'error_message': 'E-mail ou senha inválidos!'})

def logout(request):
    """
    Realiza o logout do usuário autenticado.
    """
    if request.user.is_authenticated:
        logout_django(request)
    return redirect('login') # Sempre redireciona para a página de login após o logout

def cadastro(request):
    """
    Trata o cadastro de novos usuários.
    """
    if request.method == "GET":
        return render(request, 'usuarios/cadastro.html')
    else: # request.method == "POST"
        username = request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('senha')
        first_name = request.POST.get('nome')

        # Verifica se o nome de usuário (email) já existe
        if User.objects.filter(username=username).exists():
            return render(request, 'usuarios/cadastro.html', {'error_message': "Este e-mail já está cadastrado!"})
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
            user.save()
            # Loga o usuário automaticamente após o cadastro, ou redireciona para login
            login_django(request, user) # Opcional: logar automaticamente após o cadastro
            return redirect('galeria') # Redireciona para a galeria ou home
        except Exception as e:
            # Captura erros gerais no cadastro (ex: problemas no banco de dados)
            print(f"Erro ao cadastrar usuário: {e}")
            return render(request, 'usuarios/cadastro.html', {'error_message': "Ocorreu um erro ao tentar cadastrar. Tente novamente."})

def home(request):
    """
    Redireciona para a página inicial (se autenticado) ou login.
    """
    if request.user.is_authenticated:
        # A página home pode ser apenas um redirecionamento para a galeria se não tiver conteúdo próprio.
        return redirect('galeria') # Ou render('usuarios/home.html') se houver conteúdo único
    else:
        return redirect('login')

# --- Views de Fotos ---

def upload_foto(request):
    """
    Permite aos usuários autenticados fazer upload de novas fotos.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'GET':
        return render(request, 'usuarios/upload_foto.html')
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        tags_input = request.POST.get('tags', '')
        imagem_file = request.FILES.get('imagem')

        if not imagem_file:
            return HttpResponse("Por favor, selecione uma imagem para upload.", status=400) # Bad Request

        # Processamento de tags: garante que sejam formatadas com '#'
        raw_tags = tags_input.replace(' ', ',').split(',')
        formatted_tags_list = []
        for tag in raw_tags:
            tag = tag.strip().lower()
            if tag: # Garante que tags vazias não sejam adicionadas
                if not tag.startswith('#'):
                    tag = '#' + tag
                formatted_tags_list.append(tag)
        formatted_tags_string = ','.join(formatted_tags_list)

        try:
            nova_foto = Foto(
                usuario=request.user,
                titulo=titulo,
                descricao=descricao,
                imagem=imagem_file, # O arquivo de imagem é atribuído aqui
                tags=formatted_tags_string
            )
            nova_foto.save() # O Django salva o arquivo automaticamente quando .save() é chamado no ImageField
            return redirect('galeria')
        except Exception as e:
            # Melhorar a depuração e o feedback para o usuário em caso de erro no salvamento
            print(f"Erro ao salvar foto: {e}")
            return HttpResponse(f"Ocorreu um erro ao fazer upload da foto: {e}", status=500) # Internal Server Error

def galeria(request):
    """
    Exibe a galeria de fotos do usuário logado, com funcionalidades de busca e filtro.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    user_photos_queryset = Foto.objects.filter(usuario=request.user).order_by('-data_upload')

    search_query = request.GET.get('q', '').strip() # Removido .lower() aqui para flexibilidade no icontains
    tag_filter = request.GET.get('tag', '').strip() # Removido .lower()

    if search_query:
        # Filtra por título ou descrição (case-insensitive)
        user_photos_queryset = user_photos_queryset.filter(
            Q(titulo__icontains=search_query) | Q(descricao__icontains=search_query)
        )
    
    if tag_filter:
        # Garante que a tag seja pesquisada com ou sem '#'
        if tag_filter.startswith('#'):
            tag_filter_clean = tag_filter[1:]
        else:
            tag_filter_clean = tag_filter
        
        # Filtra por tags, procurando por #tag ou tag (case-insensitive)
        # Atenção: Esta busca por tag é simples. Para buscas de tags mais complexas (múltiplas tags, exatas),
        # seria melhor usar um campo ManyToManyField ou uma biblioteca de tags.
        user_photos_queryset = user_photos_queryset.filter(
            Q(tags__icontains=f"#{tag_filter_clean}") | Q(tags__icontains=tag_filter_clean)
        )

    processed_photos = []
    all_unique_tags = set()

    for foto_obj in user_photos_queryset:
        # Acesso direto a foto_obj.imagem.url para o template
        photo_data = {
            'id': foto_obj.id,
            'titulo': foto_obj.titulo,
            'descricao': foto_obj.descricao,
            'url_imagem': foto_obj.imagem.url, # <--- Acessando diretamente foto_obj.imagem.url
            'usuario_nome': foto_obj.usuario.first_name if foto_obj.usuario.first_name else foto_obj.usuario.username,
            'data_upload': foto_obj.data_upload,
        }
        
        if foto_obj.tags:
            tags_list_raw = [t.strip().lower() for t in foto_obj.tags.split(',') if t.strip()]
            tags_formatted_for_display = []
            for t in tags_list_raw:
                if not t.startswith('#'): # Garante '#' para exibição
                    t = '#' + t
                tags_formatted_for_display.append(t)
                all_unique_tags.add(t) # Adiciona tags para a lista de tags únicas
            photo_data['tags'] = tags_formatted_for_display # Lista para iteração no template
            photo_data['tags_display'] = ' '.join(tags_formatted_for_display) # String para exibição rápida
        else:
            photo_data['tags'] = []
            photo_data['tags_display'] = ''
        
        processed_photos.append(photo_data)

    sorted_unique_tags = sorted(list(all_unique_tags)) # Tags únicas para o filtro

    return render(request, 'usuarios/galeria.html', {
        'fotos': processed_photos,
        'unique_tags': sorted_unique_tags,
        'current_search_query': search_query,
        'current_tag_filter': tag_filter,
    })


def editar_foto_verificacao(request, id_foto):
    """
    Exibe o formulário para editar os metadados de uma foto específica.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        # Pega a foto do usuário logado pelo ID
        foto = Foto.objects.get(id=id_foto, usuario=request.user)
    except Foto.DoesNotExist:
        return HttpResponse("Foto não encontrada ou você não tem permissão para editá-la.", status=403) # Forbidden
    
    # Prepara a string de tags para o campo de input
    if foto.tags:
        # Remove '#' e espaços extras para que o usuário veja as tags "limpas" no input
        foto.tags_string = ', '.join([t.strip().lstrip('#') for t in foto.tags.split(',') if t.strip()])
    else:
        foto.tags_string = ''

    # Passa o objeto 'foto' diretamente. No template, acessaremos 'foto.imagem.url'
    return render(request, 'usuarios/editar_foto.html', {'foto': foto})

def editar_foto(request, id_foto):
    """
    Processa a submissão do formulário de edição de metadados da foto.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        try:
            foto = Foto.objects.get(id=id_foto, usuario=request.user)
        except Foto.DoesNotExist:
            return HttpResponse("Foto não encontrada ou você não tem permissão para editá-la.", status=403)

        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        tags_input = request.POST.get('tags', '')

        # Processamento de tags
        raw_tags = tags_input.replace(' ', ',').split(',')
        formatted_tags_list = []
        for tag in raw_tags:
            tag = tag.strip().lower()
            if tag:
                if not tag.startswith('#'):
                    tag = '#' + tag
                formatted_tags_list.append(tag)
        formatted_tags_string = ','.join(formatted_tags_list)

        foto.titulo = titulo
        foto.descricao = descricao
        foto.tags = formatted_tags_string
        
        # O campo imagem não é alterado aqui, pois a edição é apenas dos metadados
        foto.save()

        return redirect('galeria')
    else:
        # Se alguém tentar acessar 'editar_foto' com GET, redireciona para a verificação
        return redirect('editar_foto_verificacao', id_foto=id_foto)


def excluir_foto_verificacao(request, id_foto):
    """
    Exibe a página de confirmação para excluir uma foto.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        # Pega a foto do usuário logado pelo ID
        foto = Foto.objects.get(id=id_foto, usuario=request.user)
    except Foto.DoesNotExist:
        return HttpResponse("Foto não encontrada ou você não tem permissão para excluí-la.", status=403)
    
    # Passa o objeto 'foto' diretamente. No template, acessaremos 'foto.imagem.url'
    return render(request, 'usuarios/excluir_foto.html', {'foto': foto})

def excluir_foto(request, id_foto):
    """
    Processa a exclusão de uma foto específica.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        try:
            foto = Foto.objects.get(id=id_foto, usuario=request.user)
        except Foto.DoesNotExist:
            return HttpResponse("Foto não encontrada ou você não tem permissão para excluí-la.", status=403)
        
        # Ao chamar .delete() em um modelo com ImageField,
        # o arquivo físico associado também é excluído por padrão (se o armazenamento for FileSystemStorage)
        foto.delete()

        return redirect('galeria')
    else:
        # Se tentar acessar com GET, redireciona para a página de confirmação
        return redirect('excluir_foto_verificacao', id_foto=id_foto)


def filtrar_fotos(request):
    """
    Filtra fotos do usuário logado com base em título, tags ou data de upload.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    fotos_filtradas = Foto.objects.filter(usuario=request.user).order_by('-data_upload')

    titulo_query = request.GET.get('titulo', '').strip()
    tags_query = request.GET.get('tags', '').strip()
    data_query = request.GET.get('data', '').strip()

    if titulo_query:
        fotos_filtradas = fotos_filtradas.filter(titulo__icontains=titulo_query)
    
    if tags_query:
        # Garante que a tag seja pesquisada com ou sem '#'
        if tags_query.startswith('#'):
            tag_query_clean = tags_query[1:]
        else:
            tag_query_clean = tags_query
        fotos_filtradas = fotos_filtradas.filter(
            Q(tags__icontains=f"#{tag_query_clean}") | Q(tags__icontains=tag_query_clean)
        )
    
    if data_query:
        try:
            # Converte a string de data para um objeto date
            filter_date = datetime.datetime.strptime(data_query, '%Y-%m-%d').date()
            # Filtra pela data de upload (apenas a parte da data, ignorando o tempo)
            fotos_filtradas = fotos_filtradas.filter(data_upload__date=filter_date)
        except ValueError:
            # Se a data não estiver no formato correto, ignora o filtro de data
            pass
    
    # Se nenhum filtro for aplicado, mostra as 15 fotos mais recentes (opcional)
    if not (titulo_query or tags_query or data_query):
        fotos_filtradas = fotos_filtradas[:15]

    processed_photos = []
    for foto_obj in fotos_filtradas:
        photo_data = {
            'id': foto_obj.id,
            'titulo': foto_obj.titulo,
            'url_imagem': foto_obj.imagem.url, # Acessando diretamente .url do ImageField
            'data_upload': foto_obj.data_upload,
        }
        if foto_obj.tags:
            tags_list_raw = [t.strip().lower() for t in foto_obj.tags.split(',') if t.strip()]
            tags_formatted_for_display = []
            for t in tags_list_raw:
                if not t.startswith('#'):
                    t = '#' + t
                tags_formatted_for_display.append(t)
            photo_data['tags'] = ' '.join(tags_formatted_for_display)
        else:
            photo_data['tags'] = ''
        processed_photos.append(photo_data)

    return render(request, 'usuarios/filtrar_fotos.html', {
        'fotos': processed_photos,
        'current_titulo_query': titulo_query,
        'current_tags_query': tags_query,
        'current_data_query': data_query,
    })

def login(request):
    if request.method == "GET":
        return render(request, 'usuarios/login.html')
    else:
        username = request.POST.get('email')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            login_django(request, user)
            return redirect('home') 
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

        if User.objects.filter(username=username).exists():
            return render(request, 'usuarios/cadastro.html', {'error_message': "Este e-mail já está cadastrado!"})
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
            user.save()
            login_django(request, user)
            return redirect('home') 
        except Exception as e:
            print(f"Erro ao cadastrar usuário: {e}")
            return render(request, 'usuarios/cadastro.html', {'error_message': "Ocorreu um erro ao tentar cadastrar. Tente novamente."})

def home(request):
    if request.user.is_authenticated:
        return render(request, 'usuarios/home.html') 
    else:
        return redirect('login')

def upload_foto(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'GET':
        return render(request, 'usuarios/upload_foto.html')
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        tags_input = request.POST.get('tags', '')
        imagem_file = request.FILES.get('imagem')

        if not imagem_file:
            return HttpResponse("Por favor, selecione uma imagem para upload.", status=400)

        raw_tags = tags_input.replace(' ', ',').split(',')
        formatted_tags_list = []
        for tag in raw_tags:
            tag = tag.strip().lower()
            if tag:
                if not tag.startswith('#'):
                    tag = '#' + tag
                formatted_tags_list.append(tag)
        formatted_tags_string = ','.join(formatted_tags_list)

        try:
            nova_foto = Foto(
                usuario=request.user,
                titulo=titulo,
                descricao=descricao,
                imagem=imagem_file,
                tags=formatted_tags_string
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
    tag_filter = request.GET.get('tag', '').strip()

    if search_query:
        user_photos_queryset = user_photos_queryset.filter(
            Q(titulo__icontains=search_query) | Q(descricao__icontains=search_query)
        )
    
    if tag_filter:
        if tag_filter.startswith('#'):
            tag_filter_clean = tag_filter[1:]
        else:
            tag_filter_clean = tag_filter
        
        user_photos_queryset = user_photos_queryset.filter(
            Q(tags__icontains=f"#{tag_filter_clean}") | Q(tags__icontains=tag_filter_clean)
        )

    processed_photos = []
    all_unique_tags = set()

    for foto_obj in user_photos_queryset:
        photo_data = {
            'id': foto_obj.id,
            'titulo': foto_obj.titulo,
            'descricao': foto_obj.descricao,
            'url_imagem': foto_obj.imagem.url,
            'usuario_nome': foto_obj.usuario.first_name if foto_obj.usuario.first_name else foto_obj.usuario.username,
            'data_upload': foto_obj.data_upload,
        }
        
        if foto_obj.tags:
            tags_list_raw = [t.strip().lower() for t in foto_obj.tags.split(',') if t.strip()]
            tags_formatted_for_display = []
            for t in tags_list_raw:
                if not t.startswith('#'):
                    t = '#' + t
                tags_formatted_for_display.append(t)
                all_unique_tags.add(t)
            photo_data['tags'] = tags_formatted_for_display
            photo_data['tags_display'] = ' '.join(tags_formatted_for_display)
        else:
            photo_data['tags'] = []
            photo_data['tags_display'] = ''
        
        processed_photos.append(photo_data)

    sorted_unique_tags = sorted(list(all_unique_tags))

    return render(request, 'usuarios/galeria.html', {
        'fotos': processed_photos,
        'unique_tags': sorted_unique_tags,
        'current_search_query': search_query,
        'current_tag_filter': tag_filter,
    })


def editar_foto_verificacao(request, id_foto):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        foto = Foto.objects.get(id=id_foto, usuario=request.user)
    except Foto.DoesNotExist:
        return HttpResponse("Foto não encontrada ou você não tem permissão para editá-la.", status=403)
    
    if foto.tags:
        foto.tags_string = ', '.join([t.strip().lstrip('#') for t in foto.tags.split(',') if t.strip()])
    else:
        foto.tags_string = ''

    return render(request, 'usuarios/editar_foto.html', {'foto': foto})

def editar_foto(request, id_foto):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        try:
            foto = Foto.objects.get(id=id_foto, usuario=request.user)
        except Foto.DoesNotExist:
            return HttpResponse("Foto não encontrada ou você não tem permissão para editá-la.", status=403)

        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        tags_input = request.POST.get('tags', '')

        raw_tags = tags_input.replace(' ', ',').split(',')
        formatted_tags_list = []
        for tag in raw_tags:
            tag = tag.strip().lower()
            if tag:
                if not tag.startswith('#'):
                    tag = '#' + tag
                formatted_tags_list.append(tag)
        formatted_tags_string = ','.join(formatted_tags_list)

        foto.titulo = titulo
        foto.descricao = descricao
        foto.tags = formatted_tags_string
        
        foto.save()

        return redirect('galeria')
    else:
        return redirect('editar_foto_verificacao', id_foto=id_foto)


def excluir_foto_verificacao(request, id_foto):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        foto = Foto.objects.get(id=id_foto, usuario=request.user)
    except Foto.DoesNotExist:
        return HttpResponse("Foto não encontrada ou você não tem permissão para excluí-la.", status=403)
    
    return render(request, 'usuarios/excluir_foto.html', {'foto': foto})

def excluir_foto(request, id_foto):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        try:
            foto = Foto.objects.get(id=id_foto, usuario=request.user)
        except Foto.DoesNotExist:
            return HttpResponse("Foto não encontrada ou você não tem permissão para excluí-la.", status=403)
        
        foto.delete()

        return redirect('galeria')
    else:
        return redirect('excluir_foto_verificacao', id_foto=id_foto)


def filtrar_fotos(request):
    if not request.user.is_authenticated:
        return redirect('login')

    fotos_filtradas = Foto.objects.filter(usuario=request.user).order_by('-data_upload')

    titulo_query = request.GET.get('titulo', '').strip()
    tags_query = request.GET.get('tags', '').strip()
    data_query = request.GET.get('data', '').strip()

    if titulo_query:
        fotos_filtradas = fotos_filtradas.filter(titulo__icontains=titulo_query)
    
    if tags_query:
        if tags_query.startswith('#'):
            tag_query_clean = tags_query[1:]
        else:
            tag_query_clean = tags_query
        fotos_filtradas = fotos_filtradas.filter(
            Q(tags__icontains=f"#{tag_query_clean}") | Q(tags__icontains=tag_query_clean)
        )
    
    if data_query:
        try:
            filter_date = datetime.datetime.strptime(data_query, '%Y-%m-%d').date()
            fotos_filtradas = fotos_filtradas.filter(data_upload__date=filter_date)
        except ValueError:
            pass
    
    if not (titulo_query or tags_query or data_query):
        fotos_filtradas = fotos_filtradas[:15]

    processed_photos = []
    for foto_obj in fotos_filtradas:
        photo_data = {
            'id': foto_obj.id,
            'titulo': foto_obj.titulo,
            'url_imagem': foto_obj.imagem.url,
            'data_upload': foto_obj.data_upload,
        }
        if foto_obj.tags:
            tags_list_raw = [t.strip().lower() for t in foto_obj.tags.split(',') if t.strip()]
            tags_formatted_for_display = []
            for t in tags_list_raw:
                if not t.startswith('#'):
                    t = '#' + t
                tags_formatted_for_display.append(t)
            photo_data['tags'] = ' '.join(tags_formatted_for_display)
        else:
            photo_data['tags'] = ''
        processed_photos.append(photo_data)

    return render(request, 'usuarios/filtrar_fotos.html', {
        'fotos': processed_photos,
        'current_titulo_query': titulo_query,
        'current_tags_query': tags_query,
        'current_data_query': data_query,
    })