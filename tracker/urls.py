from django.urls import path
from django.contrib.auth.views import LoginView
from . import views, views_auth
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Auth-related URLs
    path('', views_auth.redirect_view, name='home'),
    path('signup/', views_auth.signup, name='signup'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views_auth.logout_view, name='logout'),
    
    # Password reset paths 
    path('password_reset/', auth_views.PasswordResetView.as_view(
         template_name='registration/password_reset_form.html'), 
         name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
         template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
         template_name='registration/password_reset_confirm. html'), 
         name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
         template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # Main app URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_expense, name='add_expense'),
    path('list/', views.expense_list, name='expense_list'),
    path('edit/<int:id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:id>/', views.delete_expense, name='delete_expense'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

]

