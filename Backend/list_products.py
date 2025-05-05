import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# Import models after Django setup
from myapp.models import Product, ProductVariant

def list_all_products():
    print("\n=== All Products ===")
    products = Product.objects.all()
    
    if not products:
        print("No products found in the database!")
        return
    
    print(f"Total products: {products.count()}")
    
    for product in products:
        print(f"\nProduct ID: {product.id}")
        print(f"Name: {product.name}")
        print(f"Slug: {product.slug}")
        print(f"Brand: {product.brand}")
        print(f"Category: {product.category}")
        print(f"Base Price: ${product.base_price}")
        
        # Check variants
        variants = ProductVariant.objects.filter(product=product)
        if variants:
            print(f"Variants: {variants.count()}")
            for i, variant in enumerate(variants, 1):
                print(f"  {i}. Color: {variant.color}, Storage: {variant.storage}, Price: ${variant.price}")
        else:
            print("No variants for this product")

if __name__ == "__main__":
    list_all_products()
