from django.urls import path
from .views import VehicleView

urlpatterns = [
    # Methods: GET (all vehicles), Post (create)
    path('', VehicleView.as_view(), name="VehicleList"),
    # Methods: GET (single vehicle), PUT (update), DELETE (remove vehicle)
    path('<int:pk>/', VehicleView.as_view(), name="VehicleDetailUpdateDelete"),
]
