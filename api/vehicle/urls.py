from django.urls import path
from .views import VehicleView, VehicleImageView

urlpatterns = [
    # Methods: GET (all vehicles), Post (create)
    path('', VehicleView.as_view(), name="VehicleList"),
    # Methods: GET (single vehicle), PUT (update), DELETE (remove vehicle)
    path('<int:pk>/', VehicleView.as_view(), name="VehicleDetailUpdateDelete"),

    # Method: Post (create vehicle image)
    path('image/', VehicleImageView.as_view(), name="VehicleImageCreate"),
    # Method: DELETE (remove vehicle image)
    path('image/<int:pk>/', VehicleImageView.as_view(), name="VehicleImageDelete"),
]
