from django.contrib import admin
from .models import (
    Product, ProductVariant, InventoryChange, InventoryReservation,
    PhoneBrand, PhoneModel, RepairService, Accessories
)

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'product_type', 'base_price')
    list_filter = ('brand', 'category', 'product_type')
    search_fields = ('name', 'brand', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline]

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'color', 'storage', 'price', 'count_in_stock', 'reserved_stock', 'available_stock')
    list_filter = ('product__brand', 'color', 'storage')
    search_fields = ('product__name', 'color', 'storage', 'sku')

class InventoryChangeAdmin(admin.ModelAdmin):
    list_display = ('variant', 'quantity', 'reason', 'created_at')
    list_filter = ('reason', 'created_at')
    search_fields = ('variant__product__name', 'notes')
    date_hierarchy = 'created_at'


class InventoryReservationAdmin(admin.ModelAdmin):
    list_display = ('variant', 'quantity', 'session_id', 'expires_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('session_id', 'order_id', 'variant__product__name')
    date_hierarchy = 'created_at'

class PhoneBrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class PhoneModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand')
    list_filter = ('brand',)
    prepopulated_fields = {'slug': ('name',)}

class RepairServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_model', 'price')
    list_filter = ('phone_model__brand',)

class AccessoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'count_in_stock')
    list_filter = ('brand',)
    prepopulated_fields = {'slug': ('name',)}

# Register models
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(InventoryChange, InventoryChangeAdmin)
admin.site.register(InventoryReservation, InventoryReservationAdmin)
admin.site.register(PhoneBrand, PhoneBrandAdmin)
admin.site.register(PhoneModel, PhoneModelAdmin)
admin.site.register(RepairService, RepairServiceAdmin)
admin.site.register(Accessories, AccessoriesAdmin)
