from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from apps.transactions.models import Transaction
from apps.categories.models import Category


def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Аутентификация по email
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.email}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверный email или пароль')
    
    return render(request, 'login.html')


def register_view(request):
    """Страница регистрации"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Проверка паролей
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'register.html')
        
        # Проверка email
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email уже зарегистрирован')
            return render(request, 'register.html')
        
        # Создание пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        login(request, user)
        messages.success(request, 'Аккаунт успешно создан!')
        return redirect('dashboard')
    
    return render(request, 'register.html')


def logout_view(request):
    """Выход"""
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('login')


@login_required
def profile_view(request):
    """Страница профиля"""
    if request.method == 'POST':
        # Обновление профиля
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        
        # Обновляем или создаём профиль
        from apps.accounts.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.bio = request.POST.get('bio', '')
        profile.currency = request.POST.get('currency', 'RUB')
        profile.save()
        
        user.save()
        messages.success(request, 'Профиль обновлён!')
        return redirect('profile')
    
    return render(request, 'profile.html')


@login_required
def dashboard_view(request):
    """Главная страница (dashboard)"""
    # Получаем текущий месяц
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Транзакции за месяц
    monthly_transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=month_start
    )
    
    # Считаем расходы и доходы
    expenses = monthly_transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    income = monthly_transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    
    # Общий баланс (все доходы - все расходы)
    total_income = Transaction.objects.filter(user=request.user, type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Transaction.objects.filter(user=request.user, type='expense').aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expenses
    
    # Последние транзакции
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('category').order_by('-date')[:5]
    
    # Категории
    categories = Category.objects.filter(is_system=True)[:10]
    
    context = {
        'balance': balance,
        'expenses': expenses,
        'income': income,
        'recent_transactions': recent_transactions,
        'categories': categories,
    }
    
    return render(request, 'dashboard.html', context)
