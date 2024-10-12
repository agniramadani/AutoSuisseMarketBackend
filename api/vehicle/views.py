from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status
from .models import Vehicle, VehicleImage


"""
Vehicle Operations
==================

This code manages vehicle data, allowing you to read, create, update, and delete vehicles.
Only the owner is allowed to make changes or delete the vehicle.
Anyone can get all or a single vehicle, no authentication needed for that.
"""

class VehicleView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Allow anyone to access the GET method
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request, pk=None):
        if pk:
            vehicle = get_object_or_404(Vehicle, id=pk)
            serializer = VehicleDetailSerializer(vehicle)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            queryset = Vehicle.objects.all()
            serializer = VehicleSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):        
        # Create a new Vehicle instance with the provided data
        request.data["owner"] = request.user.pk
        serializer = VehicleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        # Check if vehicle exists
        vehicle = get_object_or_404(Vehicle, id=pk)

        # Apply ownership check
        if request.user.pk != vehicle.owner.pk:
            return Response("Not allowed!", status=status.HTTP_405_METHOD_NOT_ALLOWED)

        # If the request user is the owner, allow the vehicle to be modified
        serializer = VehicleSerializer(vehicle, data=request.data, partial=True)
        # If validation fails, error is automatically handled by raise_exception=True
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # Check if vehicle exists
        vehicle = get_object_or_404(Vehicle, id=pk)

        # Apply ownership check
        if request.user.pk != vehicle.owner.pk:
            return Response("Not allowed!", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # If the request user is the owner, allow the vehicle to be deleted
        vehicle.delete()
        return Response("Vehicle has been deleted!", status=status.HTTP_204_NO_CONTENT)


"""
Vehicle Image
=============

This code manages vehicle image data, allowing to create or delete vehicle image.
Only the owner is allowed to execute.
"""

class VehicleImageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):     
        # Images can only be added to a vehicle after the vehicle has been created
        vehicle = get_object_or_404(Vehicle, id=request.data["vehicle"])

        # Apply ownership check
        if request.user.pk != vehicle.owner.pk:
            return Response("Not allowed!", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        serializer = VehicleImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        # To proceed the request user has to be the vehicle owner
        # Check if vehicle image exists
        vehicle_image = get_object_or_404(VehicleImage, id=pk)
        # Get vehicle because we need owner pk 
        vehicle = get_object_or_404(Vehicle, id=vehicle_image.vehicle.pk)

        # Apply ownership check
        if request.user.pk != vehicle.owner.pk:
            return Response("Not allowed!", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # If the request user is the owner, allow the vehicle to be deleted
        vehicle_image.delete()
        return Response("Vehicle image has been deleted!", status=status.HTTP_204_NO_CONTENT)


"""
Vehicle Search
==============

# This code helps search for vehicle makes, models, and filters by year and price.
# No authentication is needed!
"""

@api_view(["GET"])
def get_vehicle_by_query(request):
    make = request.query_params.get('make', None)
    model = request.query_params.get('model', None)
    year = request.query_params.get('year', None)
    price = request.query_params.get('price', None)

    # Start with all vehicles
    queryset = Vehicle.objects.all()

    # Filter by make if provided
    if make:
        queryset = queryset.filter(make__iexact=make)

    # Filter by model if provided
    if model:
        queryset = queryset.filter(model__iexact=model)

    # Filter by year (from that year onwards) if provided
    if year:
        queryset = queryset.filter(year__gte=year)

    # Filter by price (from that price onwards) if provided
    if price:
        queryset = queryset.filter(price__gte=price)

    # Finally sort by lowest price
    queryset = queryset.order_by('price')

    serializer = VehicleSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_vehicle_makes(request):
    queryset = Vehicle.objects.values('make').distinct().order_by('make')
    serializer = VehicleMakeSerializer(queryset, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_vehicle_models(request, requested_make):
    # Convert the make to uppercase since all makes are saved in uppercase.
    requested_make = requested_make.upper()
    queryset = Vehicle.objects.filter(make=requested_make).values("model").distinct().order_by("model")
    serializer = VehicleModelSerializer(queryset, many=True)

    if not queryset.exists():
        return Response("No models found for the specified make.", status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
