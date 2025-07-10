from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django, logout as logout_django
from .models import Nota

def login(request):
    if request.method == "GET":
        return render(request, 'usuarios/login.html')
    else:
        username = request.POST.get('email')
        senha = request.POST.get('senha')

        user = authenticate(username = username, password = senha)

        if user:
            login_django(request, user)
            return render(request, 'usuarios/home.html')
        else:
            return HttpResponse('E-mail ou senha inválidos!')

def logout(request):
    if request.user.is_authenticated:
        logout_django(request)
        return render(request, 'usuarios/login.html')
    else:
        return HttpResponse("Você não acessou sua conta ainda!")

def cadastro(request):
    if request.method == "GET":
        return render(request, 'usuarios/cadastro.html')
    else:
        username = request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('senha')
        first_name = request.POST.get('nome')

        user = User.objects.filter(username=username).first()

        if user:
            return HttpResponse("Usuário já existente!")
        else:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
            user.save()

            return render(request, 'usuarios/login.html')
        
def home(request):
    if request.user.is_authenticated:
        return render(request, 'usuarios/home.html')
    else:
        return HttpResponse("Faça o login para acessar!")

def lancar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, 'usuarios/lancar.html')
        else:
            return HttpResponse("Faça o login para acessar!")
    else:
        nota = Nota()
        nota.nome_aluno = request.user.first_name
        nota.disciplina = request.POST.get('disciplina')
        nota.nota_atividades = request.POST.get('nota_atividades')
        nota.nota_trabalho = request.POST.get('nota_trabalho')
        nota.nota_prova = request.POST.get('nota_prova')
        nota.media = int(nota.nota_atividades) + int(nota.nota_trabalho) + int(nota.nota_prova)

        nota_verificada = Nota.objects.filter(disciplina=nota.disciplina).first()

        if nota_verificada:
            return HttpResponse("Disciplina já possui notas cadastradas!")
        else:
            nota.save()
            return render(request, 'usuarios/home.html')

def alterar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            lista_notas = Nota.objects.all()
            dicionario_notas = {'lista_notas':lista_notas}
            return render(request, 'usuarios/alterar.html', dicionario_notas)
        else:
            return HttpResponse("Faça o login para acessar!")

def visualizar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            lista_notas = Nota.objects.all()
            dicionario_notas = {'lista_notas':lista_notas}
            return render(request, 'usuarios/visualizar.html', dicionario_notas)
        else:
            return HttpResponse("Faça o login para acessar!") 
    else:
        disciplina = request.POST.get('disciplina') 
        if disciplina == "Todas as disciplinas":
            lista_notas = Nota.objects.all()
            dicionario_notas = {'lista_notas':lista_notas}
            return render(request, 'usuarios/visualizar.html', dicionario_notas)
        else:
            lista_notas = Nota.objects.filter(disciplina=disciplina)
            dicionario_notas_filtradas = {'lista_notas':lista_notas}
            return render(request, 'usuarios/visualizar.html', dicionario_notas_filtradas)
        
def excluir_verificacao(request, pk):
    if request.method == "GET":
        if request.user.is_authenticated:
            lista_notas = Nota.objects.get(pk=pk) 
            dicionario_notas = {'lista_notas':lista_notas}     
            return render(request, 'usuarios/excluir.html', dicionario_notas) 
        else:
            return HttpResponse("Faça o login para acessar!")      

def excluir(request, pk):
    if request.method == "GET":
        if request.user.is_authenticated:
            disciplina_selecionada = Nota.objects.get(pk=pk)
            disciplina_selecionada.delete()
            return HttpResponseRedirect(reverse('alterar'))
        else:
            return HttpResponse("Faça o login para acessar!")

def editar_verificacao(request, pk):
    if request.method == "GET":
        if request.user.is_authenticated:
            lista_notas = Nota.objects.get(pk=pk)
            dicionario_notas = {'lista_notas':lista_notas}
            return render(request, 'usuarios/editar.html', dicionario_notas)
        else:
            return HttpResponse("Faça o login para acessar!")

def editar(request, pk):
    if request.method == "POST":
        if request.user.is_authenticated:
            nome_aluno = request.user.first_name
            disciplina = request.POST.get('disciplina')
            nota_atividades = request.POST.get('nota_atividades')
            nota_trabalho = request.POST.get('nota_trabalho')
            nota_prova = request.POST.get('nota_prova')
            media = int(nota_atividades) + int(nota_trabalho) + int(nota_prova)
            
            Nota.objects.filter(pk=pk).update(nome_aluno=nome_aluno,disciplina=disciplina, nota_atividades=nota_atividades, nota_trabalho=nota_trabalho,nota_prova=nota_prova,media=media)
            
            return HttpResponseRedirect(reverse('alterar'))
        else:
            return HttpResponse("Faça o login para acessar!")
        
