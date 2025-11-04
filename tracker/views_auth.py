from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect


# -------------------------
# Redirect on site open (Home route)
# -------------------------
def redirect_view(request):
    """If user is logged in → dashboard, else → login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


# -------------------------
# Sign Up View
# -------------------------
@csrf_exempt
def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "🎉 Account created successfully! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# -------------------------
# Login View
# -------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"👋 Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "❌ Invalid username or password.")
        else:
            messages.error(request, "⚠️ Please check your credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'tracker/login.html', {'form': form})


# -------------------------
# Logout View
# -------------------------
@csrf_exempt
def logout_view(request):
    if request.method in ['GET', 'POST', 'HEAD']:
        logout(request)
        messages.info(request, "👋 You have been logged out successfully.")
        return redirect('login')  # ✅ URL name use kiya
    else:
        return redirect('login')
