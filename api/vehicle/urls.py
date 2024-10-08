from django.urls import path
from .views import VehicleView, VehicleImageView, get_vehicle_makes, get_vehicle_models

urlpatterns = [
    # Methods: GET (all vehicles), Post (create)
    path('', VehicleView.as_view(), name="VehicleList"),
    # Methods: GET (single vehicle), PUT (update), DELETE (remove vehicle)
    path('<int:pk>/', VehicleView.as_view(), name="VehicleDetailUpdateDelete"),

    # Method: Post (create vehicle image)
    path('image/', VehicleImageView.as_view(), name="VehicleImageCreate"),
    # Method: DELETE (remove vehicle image)
    path('image/<int:pk>/', VehicleImageView.as_view(), name="VehicleImageDelete"),

    # Method: Get (Vehicles make, model, filter by year or price)
    path('make/', get_vehicle_makes, name='GetVehicleMakes'),
    path('model/<str:requested_make>/', get_vehicle_models, name='GetVehicleModels'),
]
