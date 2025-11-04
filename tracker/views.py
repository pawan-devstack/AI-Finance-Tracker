from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.db.models import Sum
from decimal import Decimal
from .models import Expense, Category
import calendar
from django.db.models.functions import TruncMonth

# -------------------------
# login required
# -------------------------
@login_required(login_url='login')
def dashboard(request):
    # Total calculations
    total_expense = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_income = 25000
    savings = total_income - total_expense
    transactions = Expense.objects.count()

    # Monthly expenses data for chart
    monthly_data = (
        Expense.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    months = [calendar.month_name[item['month'].month] for item in monthly_data if item['month']]
    totals = [float(item['total']) for item in monthly_data if item['total']]

    # Category-wise chart data
    category_data = (
        Expense.objects.values('category__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')
    )

    categories = [item['category__name'] or 'Uncategorized' for item in category_data]
    amounts = [float(item['total_amount']) for item in category_data]

    # Simple AI-style suggestions
    suggestions = []
    if total_expense > 0:
        top_category = max(category_data, key=lambda x: x['total_amount'])['category__name']
        suggestions.append(f"You spent the most on '{top_category}'. Try limiting it next month!")
        if total_expense > 10000:
            suggestions.append("You're spending quite a lot — maybe review your monthly goals.")
    else:
        suggestions.append("No expenses added yet. Start tracking to get insights!")

    context = {
        'total_expense': total_expense,
        'total_income': total_income,
        'savings': savings,
        'transactions': transactions,
        'months': months,
        'totals': totals,
        'categories': categories,
        'amounts': amounts,
        'suggestions': suggestions,
        'recent_expenses': Expense.objects.order_by('-date')[:5],
    }

    return render(request, 'tracker/dashboard.html', context)
# -------------------------
# Home Page
# -------------------------
@login_required(login_url='login')
def home(request):
    labels = ['Food', 'Travel', 'Bills']
    data = [1200, 800, 4500]
    total_expenses = sum(data)
    monthly_limit = 20000
    remaining = monthly_limit - total_expenses

    return render(request, 'tracker/dashboard.html', {
        'labels': labels,
        'data': data,
        'total_expenses': total_expenses,
        'monthly_limit': monthly_limit,
        'remaining': remaining,
    })


# -------------------------
# Register (User Signup)
# -------------------------
@login_required(login_url='login')
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "🎉 Registration successful! Welcome!")
            return redirect('expense_list')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})


# -------------------------
# Add Expense
# -------------------------
@login_required(login_url='login')
def add_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category_name = request.POST.get('category')
        description = request.POST.get('description')

        # Fetch or create category
        category_obj, created = Category.objects.get_or_create(name=category_name)

        # Save expense
        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            category=category_obj,
            description=description,
            date=timezone.now().date()
        )

        messages.success(request, "✅ Expense added successfully!")
        return redirect('expense_list')

    return render(request, 'tracker/add_expense.html')


# -------------------------
# Expense List
# -------------------------
@login_required(login_url='login')
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    total = sum(exp.amount for exp in expenses)

    # Category-wise data
    category_data = (
        Expense.objects.filter(user=request.user)
        .values('category__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')
    )

    categories = [item['category__name'] for item in category_data]
    totals = [float(item['total_amount']) for item in category_data]

    # ----- AI Suggestion Logic -----
    suggestions = []

    if category_data:
        highest = max(category_data, key=lambda x: x['total_amount'])
        lowest = min(category_data, key=lambda x: x['total_amount'])
        avg = sum(item['total_amount'] for item in category_data) / Decimal(len(category_data))

        # Suggestion 1: Highest spending
        suggestions.append(
            f"Your highest spending category is '{highest['category__name']}' (₹{highest['total_amount']}). Try to reduce this by 10–15% next month."
        )

        # Suggestion 2: Lowest spending
        suggestions.append(
            f"You're managing '{lowest['category__name']}' expenses well — only ₹{lowest['total_amount']} spent. Keep it up!"
        )

        # Suggestion 3: Above-average spending
        for item in category_data:
            if item['total_amount'] > avg * Decimal('1.2'):
                suggestions.append(
                    f"You're spending more than average on '{item['category__name']}'. Maybe set a smaller budget next time."
                )
    else:
        suggestions.append("No expense data yet. Add some expenses to get insights!")

    return render(request, 'tracker/expense_list.html', {
        'expenses': expenses,
        'total': total,
        'categories': categories,
        'totals': totals,
        'suggestions': suggestions,
    })


# -------------------------
# Edit Expense
# -------------------------
@login_required(login_url='login')
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category_name = request.POST.get('category')
        category_obj, created = Category.objects.get_or_create(name=category_name)

        expense.title = title
        expense.amount = amount
        expense.category = category_obj
        expense.save()

        messages.success(request, "✏️ Expense updated successfully!")
        return redirect('expense_list')

    return render(request, 'tracker/add_expense.html', {'expense': expense})


# -------------------------
# Delete Expense
# -------------------------
@login_required(login_url='login')
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    messages.success(request, "🗑️ Expense deleted successfully!")
    return redirect('expense_list')

@login_required(login_url='login')
def logout_view(request):
   if request.method in ["POST", "GET"]:
        logout(request)
        return render(request, 'registration/logout.html')
   else:
        return redirect('dashboard')
    
# -------------------------
# profile view
# -------------------------
@login_required
def profile_view(request):
    return render(request, 'tracker/profile.html')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'tracker/profile_edit.html')    