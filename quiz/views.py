from django.shortcuts import render, redirect
from django.contrib import messages
import hashlib
from quiz.models import User


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def home_view(request):
    if request.session.get('user_id'):
        return redirect('afterlogin')
    return render(request, 'quiz/home.html')


def signup_view(request):
    if request.session.get('user_id'):
        return redirect('afterlogin')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', '')

        if not all([name, email, password, role]):
            messages.error(request, 'All fields are required.')
            return render(request, 'quiz/signup.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'quiz/signup.html')

        if User.objects(email=email).first():
            messages.error(request, 'Email already registered.')
            return render(request, 'quiz/signup.html')

        User(
            name=name,
            email=email,
            password=hash_password(password),
            role=role
        ).save()
        messages.success(request, 'Account created! Please login.')
        return redirect('login')

    return render(request, 'quiz/signup.html')


def login_view(request):
    if request.session.get('user_id'):
        return redirect('afterlogin')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        user = User.objects(email=email, password=hash_password(password)).first()
        if user:
            request.session['user_id'] = str(user.id)
            request.session['user_name'] = user.name
            request.session['user_role'] = user.role
            request.session['user_email'] = user.email
            return redirect('afterlogin')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'quiz/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('home')


def afterlogin_view(request):
    role = request.session.get('user_role')
    if role == 'student':
        return redirect('student-dashboard')
    elif role == 'teacher':
        return redirect('teacher-dashboard')
    return redirect('login')
