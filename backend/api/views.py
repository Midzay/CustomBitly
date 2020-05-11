from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
import secrets
from .short_url import encode_url, decode_url
from .models import LongShortUrl, DataUser, Schedule
from .serializers import *
from backend.settings import DOMAIN
from rest_framework import status
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
import logging
import time


logging.basicConfig(filename='backend.log', filemode='w', level=logging.DEBUG)
logging.debug('Initial')


EXPIRIES_SESSION = getattr(settings, 'EXPIRIES_SESSION', 600)


# Получаем CACHE_TTL для Redis
def get_cache_ttl():
    try:
        shed = Schedule.objects.first()
        CACHE_TTL = shed.ttl_redis
        logging.debug(
            f'Получили данные из таблицы с расписанием CACHE_TTL- {CACHE_TTL}')
    except:
        logging.debug('Пустое расписание или неверные данные')
        CACHE_TTL = getattr(settings, 'CACHE_TTL', 900)
    return CACHE_TTL


# Получаем исходную ссылку для переадресации
# Используем Redis длф кеширования данных
@api_view(['GET'])
def index(request):
    logging.debug('Зашли в запрос по ссылке')
    
   

    try:
        s_url = request.GET['short_url'][1:]
        if s_url in cache:
            logging.debug('Взяли из кеша')
            l_url = cache.get(s_url)
            data = {'long_url': l_url}
            return Response(data, status=status.HTTP_201_CREATED)

        else:
            logging.debug('В кеше нет данных первый запрос')
            CACHE_TTL = get_cache_ttl()
            l_url = LongShortUrl.objects.get(short_url=s_url).long_url
            cache.set(s_url, l_url, timeout=CACHE_TTL)
            data = {'long_url': l_url}
            return Response(data, status=status.HTTP_201_CREATED)
    except:
        logging.exception("Ошибка в обращении по короткой ссылке")


# Получаем из базы все объекты пользователя
# Или возрващаем пустой список если пользователь зашел на сайт первый раз
def get_objects_database(session_id=0):
    logging.debug('Зашли в функцию get_objects_database')
    try:
        obj = LongShortUrl.objects.filter(user_id__session_id=session_id)
        logging.debug(
            f'Получаем все записи пользователя по session_id Кол-во: {len(obj)}')
    except LongShortUrl.DoesNotExist:
        obj = []
    serializer = LongShortUrlSerializer(obj, many=True)
    logging.debug('get_objects_database DONE')
    return serializer.data


# Сохраняем в базе два объекта.
# 1. Сессия пользователя
# 2. Полную и короткую ссылку
def save_to_database(l_url, s_url, session_id):

    logging.debug('Enter save_to_database')
    try:
        data_user = DataUser.objects.get(session_id=session_id)
        logging.debug('Нашли пользователя с такой сессией')
    except DataUser.DoesNotExist:
        logging.debug('Исключение Пользователя с такой сессией нет')
        data_user = []
    if not data_user:
        data_user = DataUser(session_id=session_id)
        data_user.save()
    l_s_u = LongShortUrl(
        long_url=l_url,
        short_url=s_url,
        user_id=data_user
    )
    l_s_u.save()
    logging.debug('save_to_database DONE')


# GET запрос пользователя. Получаем все прошлые запросы
def get_request(request):
    
    try:
        logging.debug('Пытаемся получить записи по номеру сессии ')
        session_id = request.COOKIES['CustomBitly']
        old_request = get_objects_database(session_id)
    except:
        logging.debug('Нет объектов по номеру сессии ')
        old_request = get_objects_database()
    return Response(old_request)


#  Проверяем, что введеный пользователем короткий урл свободен для использования
def check_subart(s_url):
    flag = True
    obj = LongShortUrl.objects.filter(short_url=s_url)
    if obj:
        flag = False
    logging.debug('check_subatr DONE')
    return flag

# для генерации короткой ссылки берем из базы последний элемент. first() так как в модели ordering =['-id]


def post_request(request):

    try:
        #  проверям данные полученные из формы
        if request.data["short_url"]:
            flag = check_subart(request.data["short_url"])
            if flag:
                s_url = request.data["short_url"]
            else:
                return Response({"exist": "True"})
        else:
            s_url = encode_url(int(time.time()))

        serializer = LongShortUrlSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        logging.exception("Ошибка данных с формы")

    l_url = data['long_url']


#  Проверяем есть ли старые сессии, чтобы использовать для получения старых записей
#  Если нет то записываем в cookies нашу сессию
    try:
        logging.debug('Проверяем есть ли наш session_id у клиента')
        response = Response()
        if 'CustomBitly' in request.COOKIES:
            session_id = request.COOKIES['CustomBitly']
            save_to_database(l_url, s_url, session_id)

        else:
            logging.debug('Нету. создаем секретный ключ')
            session_id = secrets.token_hex(16)
            save_to_database(l_url, s_url, session_id)
            response = Response()
            response.set_cookie('CustomBitly', session_id, EXPIRIES_SESSION)
            logging.debug('Все прошло гладко возвращаем данные')
        return response
    except:
         logging.exception("Ошибка сохранения в базу")


@api_view(['GET', 'POST', ])
def get_data(request):
    if request.method == "GET":
        return get_request(request)
    else:
        return post_request(request)
