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
            "accessories": "/myapp/accessories/",
            "accessory_by_slug": "/myapp/accessories/slug/<slug>/",
            "debug_accessories": "/myapp/debug-accessories/"
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
    import logging
    logger = logging.getLogger(__name__)
    logger.info("get_accessories endpoint called")
    
    try:
        logger.info("Attempting to fetch accessories...")
        
        # First, check if the Accessories model has any records
        count = Accessories.objects.count()
        logger.info(f"Found {count} accessories in the database")
        
        # Get all accessories
        accessories = Accessories.objects.all()
        
        # Log the first few accessories for debugging
        if count > 0:
            sample = list(accessories[:3])
            logger.info(f"Sample accessories: {[str(a) for a in sample]}")
        
        # Serialize the data
        serializer = AccessoriesSerializer(accessories, many=True)
        
        # Log serialized data for debugging
        serialized_data = serializer.data
        logger.info(f"Serialized {len(serialized_data)} accessories")
        
        # Check for image field issues (common source of serialization errors)
        for item in serialized_data[:3] if serialized_data else []:
            if 'image' in item:
                logger.info(f"Image URL for {item.get('name', 'unknown')}: {item.get('image')}")
        
        return Response(serialized_data)
   
    except Exception as e:
        # Log the full error with traceback
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in get_accessories: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        
        # Return a more detailed error response
        return Response(
            {
                "error": "Failed to fetch accessories",
                "details": str(e),
                "type": type(e).__name__
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_accessory_by_slug(request, slug):
    """
    Get detailed information for an accessory by its slug
    """
    try:
        accessory = get_object_or_404(Accessories, slug=slug)
        serializer = AccessoriesSerializer(accessory)
        return Response(serializer.data)
   
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_accessories(request):
    """
    Debug endpoint for accessories
    """
    import logging
    import traceback
    from django.conf import settings
    
    logger = logging.getLogger(__name__)
    logger.info("debug_accessories endpoint called")
    
    response_data = {
        "debug_info": {},
        "accessories": []
    }
    
    try:
        # Check Django settings
        response_data["debug_info"]["media_url"] = settings.MEDIA_URL
        response_data["debug_info"]["media_root"] = settings.MEDIA_ROOT
        response_data["debug_info"]["static_url"] = settings.STATIC_URL
        
        # Check if Accessories model exists
        from django.apps import apps
        model_exists = apps.is_installed("myapp") and apps.get_model("myapp", "Accessories") is not None
        response_data["debug_info"]["model_exists"] = model_exists
        
        # Count accessories
        count = Accessories.objects.count()
        response_data["debug_info"]["count"] = count
        
        # Get sample accessories (limit to 3)
        accessories = Accessories.objects.all()[:3]
        
        # Manually serialize to avoid serialization issues
        for acc in accessories:
            acc_data = {
                "id": acc.id,
                "name": acc.name,
                "slug": acc.slug,
                "brand": acc.brand,
                "description": acc.description,
                "price": str(acc.price),
                "count_in_stock": acc.count_in_stock,
            }
            
            # Safely get image URL
            try:
                if acc.image and hasattr(acc.image, 'url'):
                    acc_data["image"] = acc.image.url
                else:
                    acc_data["image"] = None
                    acc_data["image_error"] = "No image or no URL attribute"
            except Exception as e:
                acc_data["image"] = None
                acc_data["image_error"] = str(e)
            
            response_data["accessories"].append(acc_data)
        
        return Response(response_data)
    
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Error in debug_accessories: {str(e)}")
        logger.error(f"Traceback: {tb}")
        
        response_data["error"] = str(e)
        response_data["traceback"] = tb
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
