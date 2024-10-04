from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.db import transaction
from rest_framework import status


"""
User Operations
===============

This code manages user data, allowing you to read, update, and delete users.
"""

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, id=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            queryset = User.objects.all()
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def put(self, request, pk):
        # Apply ownership check
        if request.user.pk != pk:
            return Response("Not allowed!", status=status.HTTP_405_METHOD_NOT_ALLOWED)

        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)

        # If validation fails, error is automatically handled by raise_exception=True
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # Apply ownership check
        if request.user.pk != pk:
            return Response("Not allowed!", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        user = get_object_or_404(User, id=pk)
        user.delete()
        return Response("User has been deleted!", status=status.HTTP_204_NO_CONTENT)



"""
Authentication
===============

This code handles user login, signup, and token management, allowing users to 
log in with their credentials or create a new user.
"""

def create_token(user):
    """Create or retrieve a token for the user."""
    token, _ = Token.objects.get_or_create(user=user)
    return token.key

@api_view(['POST'])
def login(request):
    """Handle user login."""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response("Both username and password are required!", status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    
    if user is not None:
        token = create_token(user)
        serializer = UserSerializer(instance=user)
        return Response({"token": token, "user": serializer.data}, status=status.HTTP_200_OK)
    return Response("Invalid username or password!", status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def signup(request):
    """Handle user signup."""
    serializer = UserSerializer(data=request.data)

    # Rollback if either user creation or token generation fails
    try:
        with transaction.atomic():
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token = create_token(user)
    except Exception as e:
        return Response("Signup failed!", status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"token": token, "user": serializer.data}, status=status.HTTP_201_CREATED)
