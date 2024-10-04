from django.urls import path
from .views import UserView, login, signup

urlpatterns = [
    # Authentication
    path('login/', login, name="Login"),
    path('signup/', signup, name="Signup"),

    # For GET (all users)
    path('', UserView.as_view(), name="UserList"),
    # For GET (single user), PUT (update), DELETE (remove user)
    path('<int:pk>/', UserView.as_view(), name="UserDetailUpdateDelete"),
]
