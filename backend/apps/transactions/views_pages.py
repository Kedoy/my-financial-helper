from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from apps.transactions.models import Transaction
from apps.categories.models import Category
from apps.transactions.services.sms_parser import parse_sms
from apps.transactions.services.category_suggester import suggest_category


@login_required
def transaction_list(request):
    """Список транзакций"""
    transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('category').order_by('-date')
    
    # Фильтры
    transaction_type = request.GET.get('type')
    category_id = request.GET.get('category')
    
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)
    
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    # Категории для фильтра
    categories = Category.objects.filter(
        Q(is_system=True) | Q(user=request.user)
    ).distinct()
    
    context = {
        'transactions': transactions,
        'categories': categories,
        'current_type': transaction_type,
        'current_category': int(category_id) if category_id else None,
    }
    
    return render(request, 'transactions/transaction_list.html', context)


@login_required
def transaction_create(request):
    """Создание транзакции"""
    categories = Category.objects.filter(
        Q(is_system=True) | Q(user=request.user)
    ).distinct()
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        transaction_type = request.POST.get('type')
        category_id = request.POST.get('category')
        date = request.POST.get('date')
        
        # Получаем категорию
        category = None
        if category_id:
            category = Category.objects.filter(id=category_id).first()
        
        # Создаём транзакцию
        Transaction.objects.create(
            user=request.user,
            amount=amount,
            description=description,
            type=transaction_type,
            category=category,
            date=date,
            source='manual'
        )
        
        messages.success(request, 'Транзакция успешно создана!')
        return redirect('transactions:list')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'transactions/transaction_form.html', context)


@login_required
def transaction_edit(request, pk):
    """Редактирование транзакции"""
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user
    )
    
    categories = Category.objects.filter(
        Q(is_system=True) | Q(user=request.user)
    ).distinct()
    
    if request.method == 'POST':
        transaction.amount = request.POST.get('amount')
        transaction.description = request.POST.get('description')
        transaction.type = request.POST.get('type')
        transaction.date = request.POST.get('date')
        
        category_id = request.POST.get('category')
        if category_id:
            transaction.category = Category.objects.filter(id=category_id).first()
        else:
            transaction.category = None
        
        transaction.save()
        
        messages.success(request, 'Транзакция обновлена!')
        return redirect('transactions:list')
    
    context = {
        'transaction': transaction,
        'categories': categories,
        'editing': True,
    }
    
    return render(request, 'transactions/transaction_form.html', context)


@login_required
def transaction_delete(request, pk):
    """Удаление транзакции"""
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user
    )
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Транзакция удалена!')
        return redirect('transactions:list')
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'transactions/transaction_confirm_delete.html', context)


@login_required
def sms_parse_view(request):
    """Парсинг SMS"""
    if request.method == 'POST':
        sms_text = request.POST.get('sms_text')
        bank_phone = request.POST.get('bank_phone')
        
        # Парсим SMS
        parsed_data = parse_sms(sms_text, bank_phone)
        
        if not parsed_data:
            messages.error(request, 'Не удалось распознать транзакцию в SMS')
            return redirect('transactions:sms_parse')
        
        # Предлагаем категорию
        suggested_category = suggest_category(parsed_data['description'], parsed_data['type'])
        
        # Сохраняем в сессию для подтверждения
        request.session['parsed_transaction'] = {
            'amount': str(parsed_data['amount']),
            'description': parsed_data['description'],
            'type': parsed_data['type'],
            'date': parsed_data['date'].isoformat(),
            'category_id': suggested_category.id if suggested_category else None,
        }
        
        context = {
            'parsed_data': parsed_data,
            'suggested_category': suggested_category,
        }
        
        return render(request, 'transactions/sms_confirm.html', context)
    
    return render(request, 'transactions/sms_parse.html')


@login_required
def sms_confirm(request):
    """Подтверждение транзакции из SMS"""
    if request.method == 'POST':
        parsed = request.session.get('parsed_transaction')
        
        if not parsed:
            messages.error(request, 'Нет данных для сохранения')
            return redirect('transactions:sms_parse')
        
        # Создаём транзакцию
        category = None
        if parsed.get('category_id'):
            category = Category.objects.filter(id=parsed['category_id']).first()
        
        Transaction.objects.create(
            user=request.user,
            amount=parsed['amount'],
            description=parsed['description'],
            type=parsed['type'],
            category=category,
            date=parsed['date'],
            source='sms',
            is_ai_parsed=bool(category)
        )
        
        # Очищаем сессию
        del request.session['parsed_transaction']
        
        messages.success(request, 'Транзакция из SMS сохранена!')
        return redirect('transactions:list')
    
    return redirect('transactions:sms_parse')
