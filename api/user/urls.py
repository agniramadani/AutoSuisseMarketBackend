from django.urls import path
from .views import UserView, login, signup

urlpatterns = [
    # Authentication
    path('login/', login, name="Login"),
    path('signup/', signup, name="Signup"),

    # Method: GET (all users)
    path('', UserView.as_view(), name="UserList"),
    # Methods: GET (single user), PUT (update), DELETE (remove user)
    path('<int:pk>/', UserView.as_view(), name="UserDetailUpdateDelete"),
]
