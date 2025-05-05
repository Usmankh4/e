import requests
import json
import sys

def test_product_api(product_slug):
    # Test the product by slug endpoint
    url = f"http://127.0.0.1:8000/myapp/api/products/by-slug/{product_slug}/"
    print(f"Testing URL: {url}")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("\n=== Product Data Structure ===")
            print(json.dumps(data, indent=2))
            
            # Check if variants exist
            if 'variants' in data and data['variants']:
                print("\n=== Variants Found ===")
                print(f"Number of variants: {len(data['variants'])}")
                
                # Display the first variant
                print("\nFirst variant structure:")
                print(json.dumps(data['variants'][0], indent=2))
                
                # Check for color_image
                if 'color_image' in data['variants'][0]:
                    print(f"\nColor image URL: {data['variants'][0]['color_image']}")
                else:
                    print("\nWARNING: 'color_image' field is missing from variants!")
            else:
                print("\nWARNING: No variants found in the product data!")
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    # Use command line argument or default to 'iphone-15'
    product_slug = sys.argv[1] if len(sys.argv) > 1 else "iphone-15"
    test_product_api(product_slug)
