from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Product, ProductVariant, PhoneBrand, PhoneModel, RepairService, Accessories
from .serializers import (
    ProductSerializer, ProductDetailSerializer, ProductVariantSerializer,
    PhoneBrandSerializer, PhoneModelSerializer, RepairServiceSerializer,
    AccessoriesSerializer
)
from rest_framework.pagination import PageNumberPagination

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    """
    Home page view that returns a welcome message
    """
    return Response({
        "message": "Welcome to ZainWireless API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/myapp/products/",
            "product_detail": "/myapp/products/<id>/",
            "product_by_slug": "/myapp/products/slug/<slug>/",
            "brands": "/myapp/brands/",
            "categories": "/myapp/categories/",
            "phone_brands": "/myapp/phone-brands/",
            "phone_models": "/myapp/phone-models/<brand_slug>/",
            "repair_services": "/myapp/repair-services/<model_slug>/",
            "accessories": "/myapp/accessories/"
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    """
    Get all products or filter by query params
    """
    try:
        # Get query parameters
        brand = request.query_params.get('brand')
        category = request.query_params.get('category')
        product_type = request.query_params.get('type')
        search = request.query_params.get('search')
       
        # Start with all products
        products = Product.objects.all()
       
        # Apply filters if provided
        if brand:
            products = products.filter(brand__iexact=brand)
        if category:
            products = products.filter(category__iexact=category)
        if product_type:
            products = products.filter(product_type=product_type)
        if search:
            products = products.filter(name__icontains=search)
       
        # Paginate the results
        page = request.query_params.get('page', 1)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_products = paginator.paginate_queryset(products, request)
       
        # Serialize and return
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_detail(request, pk):
    """
    Get detailed information for a specific product
    """
    try:
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_by_slug(request, slug):
    """
    Get detailed information for a product by its slug
    """
    try:
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_brands(request):
    """
    Get all unique brands
    """
    try:
        brands = Product.objects.values_list('brand', flat=True).distinct()
        return Response(list(brands))
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    """
    Get all unique categories
    """
    try:
        categories = Product.objects.values_list('category', flat=True).distinct()
        return Response(list(categories))
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Phone Repair Service views
@api_view(['GET'])
@permission_classes([AllowAny])
def get_phone_brands(request):
    """
    Get all phone brands for repair service
    """
    try:
        brands = PhoneBrand.objects.all()
        serializer = PhoneBrandSerializer(brands, many=True)
        return Response(serializer.data)
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_phone_models(request, brand_slug=None):
    """
    Get phone models for a specific brand or all models
    """
    try:
        if brand_slug:
            brand = get_object_or_404(PhoneBrand, slug=brand_slug)
            models = PhoneModel.objects.filter(brand=brand)
        else:
            models = PhoneModel.objects.all()
       
        serializer = PhoneModelSerializer(models, many=True)
        return Response(serializer.data)
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_repair_services(request, model_slug=None):
    """
    Get repair services for a specific phone model or all services
    """
    try:
        if model_slug:
            model = get_object_or_404(PhoneModel, slug=model_slug)
            services = RepairService.objects.filter(phone_model=model)
        else:
            services = RepairService.objects.all()
       
        serializer = RepairServiceSerializer(services, many=True)
        return Response(serializer.data)
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_accessories(request):
    """
    Get all accessories
    """
    try:
        accessories = Accessories.objects.all()
        serializer = AccessoriesSerializer(accessories, many=True)
        return Response(serializer.data)
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
