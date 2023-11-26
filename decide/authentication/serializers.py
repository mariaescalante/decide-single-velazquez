from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.CharField(source='get_absoluto_url' , read_only=True)
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'token' ,'email', 'is_staff', 'url')