from django.contrib.auth import get_user_model
User = get_user_model()
try:
    User.objects.create_superuser('root','test@test.ru', 'root123456')
except:
    pass