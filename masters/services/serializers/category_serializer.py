from rest_framework import serializers
from services.models.category_model import Category


class CategorySerializer(serializers.ModelSerializer):  
    class Meta:
        model = Category
        fields = ['id', 'display_name']