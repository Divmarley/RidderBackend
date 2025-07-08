from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.exceptions import ValidationError

class PharmacyAPIView(APIView):
 
    def get(self, request):
        restaurants = Pharmacy.objects.all()
        # print("Getting",restaurants )
    
        serializer = PharmacySerializer(restaurants, many=True)
        # print("Serializing",serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request): 
        serializer = PharmacySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        print('serializer.errors',serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PharmacyDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PharmacySerializer

    def get_queryset(self):
        return Pharmacy.objects.all()

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return Pharmacy.objects.get(user__id=user_id)
        except Pharmacy.DoesNotExist:
            # Manually return a 404 Response
            self.response = Response(
                {"error": "Pharmacy not found for the given user ID."},
                status=status.HTTP_404_NOT_FOUND
            )
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return self.response
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return self.response
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return self.response
        return super().destroy(request, *args, **kwargs)

class PharmacyProductListCreateView(generics.ListCreateAPIView):
    """
    API view to create and list pharmacy products
    """
    serializer_class = PharmacyProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter products by pharmacy user"""
        return PharmacyProduct.objects.filter(
            pharmacy__user=self.request.user
        ).select_related('pharmacy', )

    def perform_create(self, serializer):
        # Get the pharmacy associated with the user
        pharmacy = self.request.user.pharmacy.first()
        print("Pharmacy for user:", pharmacy)
        if not pharmacy:
            raise ValidationError("No pharmacy found for this user")
        serializer.save(pharmacy=pharmacy)

class PharmacyProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete pharmacy product
    """
    serializer_class = PharmacyProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return PharmacyProduct.objects.filter(
            pharmacy__user=self.request.user
        ).select_related('pharmacy', 'category')


class PharmacyProductsByPharmacyView(generics.ListAPIView):
    """
    API view to list all products for a specific pharmacy
    """
    serializer_class = PharmacyProductSerializer
    permission_classes = [AllowAny]  # Allow public access to view products

    def get_queryset(self):
        pharmacy_id = self.kwargs.get('pharmacy_id')
        return PharmacyProduct.objects.filter(
            pharmacy_id=pharmacy_id,
            inStock=True  # Only show in-stock items
        ).select_related('pharmacy', 'category')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response(
                    {"detail": "No products found for this pharmacy"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "pharmacy_id": self.kwargs.get('pharmacy_id'),
                "products_count": queryset.count(),
                "products": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )