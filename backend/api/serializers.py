
from rest_framework import serializers
from .models import *


class LongShortUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = LongShortUrl
        fields = ['long_url', 'short_url',]
