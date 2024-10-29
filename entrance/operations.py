from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


def get_unique_username(username, serial=-1) -> User:
    username = username if username < 0 else username + str(serial)
    if not User.objects.filter(
        username=username).exists():
        return username
    serial += 1
    return get_unique_username(username, serial)    

def create_quick_user(email: str) -> User:
    username = get_unique_username(email.split('@')[0])
    user = User(username=username, email=email)
    user.set_password('test1234'); user.save()
    return user 

def login_user(request, username: str, password: str) -> bool:
    if authenticate(username=username, password=password):
        user = User.objects.get(username=username)
        login(request, user)
        return True
    return False
