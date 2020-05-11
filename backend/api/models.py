from django.db import models


# Create your models here.



class DataUser(models.Model):
    session_id = models.UUIDField()

class LongShortUrl(models.Model):
    long_url = models.URLField(max_length=2048)
    short_url = models.CharField(max_length=15, blank=True,default="",unique=True)
    user_id = models.ForeignKey('DataUser', on_delete=models.CASCADE)

    class Meta:
        ordering =['-id'] 

class Schedule(models.Model): 
     ttl_redis = models.IntegerField(verbose_name='Время жизни Redis (default=900)', default=900)
     def __str__(self):
         return ("Установка значений")

     class Meta:
         verbose_name = 'Настройки расписания Redid '
         verbose_name_plural = 'Настройки расписания Redid '
         ordering =['-id'] 



