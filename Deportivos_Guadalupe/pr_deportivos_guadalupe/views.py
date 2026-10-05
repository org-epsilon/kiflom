# pr_deportivos_guadalupe/views.py

from django.shortcuts import render, redirect

def home_view(request):
    """
    Página de Bienvenida (http://127.0.0.1:8000/)
    """
    return render(request, 'pr_deportivos_guadalupe/home.html')

def login_view(request):
    """
    Página de Login (http://127.0.0.1:8000/login/)
    """
    if request.method == 'POST':
        # Redirige a la URL '/guadalupe/garaje/' en la app
        return redirect('app_deportivos_guadalupe:garaje')
        
    return render(request, 'pr_deportivos_guadalupe/login.html')