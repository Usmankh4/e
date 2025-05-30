from rest_framework import serializers
from .models import (
    Product, ProductVariant, InventoryChange, InventoryReservation,
    PhoneBrand, PhoneModel, RepairService, Accessories, UserProfile, Cart, CartItem
)
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class ProductVariantSerializer(serializers.ModelSerializer):
    available_stock = serializers.ReadOnlyField()
    total_available_stock = serializers.ReadOnlyField()
    has_physical_stock = serializers.ReadOnlyField()
   
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'color', 'color_image', 'storage', 'price',
            'count_in_stock', 'reserved_stock', 'available_stock',
            'total_available_stock', 'has_physical_stock',
            'sku', 'stripe_price_id', 'max_purchase_quantity'
        ]
        def get_formatted_price(self, obj):
            return "${:,.2f}".format(obj.price)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'base_image', 'brand', 'category',
            'product_type', 'rating', 'num_reviews', 'base_price'
        ]

class ProductDetailSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
   
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'base_image', 'brand', 'category',
            'description', 'product_type', 'rating', 'num_reviews',
            'base_price', 'variants'
        ]

class InventoryChangeSerializer(serializers.ModelSerializer):
    variant_name = serializers.SerializerMethodField()
   
    class Meta:
        model = InventoryChange
        fields = [
            'id', 'variant', 'variant_name', 'quantity', 'reason',
            'notes', 'timestamp'
        ]
   
    def get_variant_name(self, obj):
        return str(obj.variant)

class InventoryReservationSerializer(serializers.ModelSerializer):
    variant_name = serializers.SerializerMethodField()
   
    class Meta:
        model = InventoryReservation
        fields = [
            'id', 'variant', 'variant_name', 'quantity', 'session_id',
            'order_id', 'expires_at', 'is_active', 'created_at'
        ]
   
    def get_variant_name(self, obj):
        return str(obj.variant)

# Phone Repair Service Serializers
class PhoneBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneBrand
        fields = ['id', 'name', 'slug', 'image']

class PhoneModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.SerializerMethodField()
   
    class Meta:
        model = PhoneModel
        fields = ['id', 'brand', 'brand_name', 'name', 'slug', 'image']
   
    def get_brand_name(self, obj):
        return obj.brand.name

class RepairServiceSerializer(serializers.ModelSerializer):
    phone_model_name = serializers.SerializerMethodField()
   
    class Meta:
        model = RepairService
        fields = [
            'id', 'phone_model', 'phone_model_name', 'name',
            'description', 'price', 'estimated_time'
        ]
   
    def get_phone_model_name(self, obj):
        return str(obj.phone_model)

class AccessoriesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Accessories
        fields = [
            'id', 'name', 'slug', 'brand', 'description',
            'price', 'count_in_stock', 'image'
        ]
    
    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception as e:
                # Return None if image URL can't be generated
                print(f"Error getting image URL for {obj.name}: {str(e)}")
                return None
        return None

# Cart Serializers
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    variant_details = serializers.SerializerMethodField()
    price = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'product_image', 'variant', 
                  'variant_details', 'quantity', 'price', 'total_price')
    
    def get_product_name(self, obj):
        return obj.product.name
    
    def get_product_image(self, obj):
        if obj.variant and obj.variant.color_image:
            return obj.variant.color_image.url
        return obj.product.base_image.url if obj.product.base_image else None
    
    def get_variant_details(self, obj):
        if obj.variant:
            return {
                'color': obj.variant.color,
                'storage': obj.variant.storage,
                'sku': obj.variant.sku
            }
        return None

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price', 'total_items', 'created_at', 'updated_at')

# User Authentication Serializers
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        
        return token

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address_line1', 'address_line2', 'city', 
                  'state', 'postal_code', 'country', 'is_premium_member')

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile')
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update UserProfile fields
        if profile_data and hasattr(instance, 'profile'):
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()
            
        return instance
