# from django.contrib.auth import get_user_model

# User = get_user_model()


# def signup_user(data):

#     if User.objects.filter(username=data.get("username", None)).exists():
#         raise ValueError("username already exists")
#     user = User.objects.create_user(**data)
#     return user
