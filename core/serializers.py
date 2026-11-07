from rest_framework import serializers
from .models import Category,Transaction,Budget
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator

User=get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm=serializers.CharField(
        write_only=True,
        required=True
    )
    class Meta:
        model=User
        fields=['username','email','password','password_confirm']
        extra_kwargs={
            "email":{"required":True},
        }

    def validate(self,attrs):
        if attrs["password"]!=attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_error": "passwords didn't match."
                }
                )
        return attrs
    
    def create(self,validated_data):
        validated_data.pop("password_confirm")
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = fields


class CategorySerializer(serializers.ModelSerializer):
    user=serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Category
        fields = ['id','name','user','type','created_at','updated_at']
        read_only_fields = ['created_at','updated_at']
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['user','name','type'],
                message='You already have a category with the same name and type.',
            )
        ]

class TransactionSerializer(serializers.ModelSerializer):
    category=serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none()
    )
    class Meta:
        model = Transaction
        fields = ["user","category","amount","date","description","created_at","updated_at"]
        read_only_fields = ["user","created_at","updated_at"]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['category'].queryset = Category.objects.filter(user=request.user)

class Budget(serializers.ModelSerializer):
    user = serializers.HiddenField(default = serializers.CurrentUserDefault())
    class Meta :
        model = Budget
        fields = ["id", "user", "category", "month", "limit", "created_at", "updated_at" ]
        read_only_fields = ["id", "created_at", "updated_at"]

        validators = UniqueTogetherValidator(
            queryset = Budget.objects.all(),
            fields = ["user", "category", "month"],
            message = "you already have budget set for the same category this month."
        )

    def __init__(self,*args, **kwargs):
        super().__init__(self,*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated :
            self.fields["category"].queryset = Category.objects.filter(
                user = request.user,
                type = Category.CategoryType.EXPENSE
            )

    def validate(self,value):
        return value.replace(day=1)