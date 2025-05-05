from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import uuid
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Product(models.Model):
  PRODUCT_TYPES = (
      ('phone', 'Phone'),
      ('accessory', 'Accessory'),
      ('other', 'Other'),
  )
  name = models.CharField(max_length=200)
  slug = models.SlugField(max_length=255, unique=True, blank=True)
  base_image = models.ImageField(upload_to='products/')
  brand = models.CharField(max_length=100)
  category = models.CharField(max_length=100)
  description = models.TextField(blank=True, null=True)
  product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='phone')
  rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
  num_reviews = models.IntegerField(default=0)
  base_price = models.DecimalField(max_digits=10, decimal_places=2)
  stripe_id = models.CharField(max_length=100, null=True, blank=True)
  createdAt = models.DateTimeField(auto_now_add=True)
  updatedAt = models.DateTimeField(auto_now=True)
  def save(self, *args, **kwargs):
      # Generate slug if it doesn't exist
      if not self.slug:
          self.slug = slugify(self.name)
          # Ensure slug is unique
          original_slug = self.slug
          counter = 1
          while Product.objects.filter(slug=self.slug).exclude(id=self.id).exists():
              self.slug = f"{original_slug}-{counter}"
              counter += 1
   
      # Create or update Stripe product
      import stripe
      import os
      from django.conf import settings
     
      # Set Stripe API key safely
      if not stripe.api_key:
          stripe.api_key = settings.STRIPE_SECRET_KEY or os.getenv('STRIPE_SECRET_KEY')
     
      if not self.stripe_id:
          # Create new Stripe product
          try:
              stripe_product = stripe.Product.create(
                  name=self.name,
                  description=self.description or f"{self.brand} {self.name}"
              )
              self.stripe_id = stripe_product.id
          except Exception as e:
              print(f"Error creating Stripe product: {e}")
      else:
          # Update existing Stripe product
          try:
              stripe.Product.modify(
                  self.stripe_id,
                  name=self.name,
                  description=self.description or f"{self.brand} {self.name}"
              )
          except Exception as e:
              print(f"Error updating Stripe product: {e}")
   
      super().save(*args, **kwargs)
  def __str__(self):
      return self.name

class ProductVariant(models.Model):
  product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
  color = models.CharField(max_length=100)
  color_code = models.CharField(max_length=10, blank=True, null=True)  # For hex color codes
  color_image = models.ImageField(upload_to='variants/', null=True, blank=True)
  storage = models.CharField(max_length=50)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  count_in_stock = models.IntegerField(default=0)
  reserved_stock = models.IntegerField(default=0)
  max_purchase_quantity = models.PositiveIntegerField(default=10, help_text="Maximum quantity a customer can purchase in a single order")
  sku = models.CharField(max_length=50, unique=True, blank=True)
  stripe_price_id = models.CharField(max_length=100, null=True, blank=True)
  createdAt = models.DateTimeField(auto_now_add=True)
  updatedAt = models.DateTimeField(auto_now=True)
  class Meta:
      # Ensure each product can only have one variant with a specific color-storage combination
      unique_together = ('product', 'color', 'storage')
  def save(self, *args, **kwargs):
      # Generate SKU if it doesn't exist
      if not self.sku:
          # Get brand abbreviation (first 3 letters)
          brand_abbr = self.product.brand[:3].upper()
       
          # Get product name abbreviation (first 3 letters)
          product_abbr = ''.join([word[0] for word in self.product.name.split()[:3]]).upper()
       
          # Get color abbreviation (first 2 letters)
          color_abbr = self.color[:2].upper()
       
          # Get storage without 'GB' suffix
          storage_num = ''.join(filter(str.isdigit, self.storage))
       
          # Generate a random 4-digit number for uniqueness
          random_digits = str(uuid.uuid4().int)[:4]
       
          # Combine all parts to create the SKU
          self.sku = f"{brand_abbr}-{product_abbr}-{color_abbr}{storage_num}-{random_digits}"
   
      # Create or update Stripe price
      if self.product.stripe_id:
          import stripe
          import os
          from django.conf import settings
         
          # Set Stripe API key safely
          if not stripe.api_key:
              stripe.api_key = settings.STRIPE_SECRET_KEY or os.getenv('STRIPE_SECRET_KEY')
         
          price_in_cents = int(float(self.price) * 100)
       
          if not self.stripe_price_id:
              # Create new price
              try:
                  price = stripe.Price.create(
                      product=self.product.stripe_id,
                      unit_amount=price_in_cents,
                      currency='usd',
                      metadata={
                          'color': self.color,
                          'storage': self.storage,
                          'sku': self.sku
                      }
                  )
                  self.stripe_price_id = price.id
              except Exception as e:
                  print(f"Error creating Stripe price: {e}")
          else:
              # For price updates, create a new price and update the reference
              # (Stripe doesn't allow updating existing prices)
              try:
                  # Check if price needs updating
                  try:
                      current_price = stripe.Price.retrieve(self.stripe_price_id)
                      if current_price.unit_amount != price_in_cents:
                          # Create new price
                          new_price = stripe.Price.create(
                              product=self.product.stripe_id,
                              unit_amount=price_in_cents,
                              currency='usd',
                              metadata={
                                  'color': self.color,
                                  'storage': self.storage,
                                  'sku': self.sku
                              }
                          )
                          # Update to new price ID
                          self.stripe_price_id = new_price.id
                  except stripe.error.StripeError:
                      # If price doesn't exist, create a new one
                      new_price = stripe.Price.create(
                          product=self.product.stripe_id,
                          unit_amount=price_in_cents,
                          currency='usd',
                          metadata={
                              'color': self.color,
                              'storage': self.storage,
                              'sku': self.sku
                          }
                      )
                      self.stripe_price_id = new_price.id
              except Exception as e:
                  print(f"Error updating Stripe price: {e}")
   
      super().save(*args, **kwargs)
  @property
  def available_stock(self):
      return max(0, self.count_in_stock - self.reserved_stock)
  @property
  def is_in_stock(self):
      return self.available_stock > 0
  def __str__(self):
      return f"{self.product.name} - {self.color}, {self.storage}"

class InventoryChange(models.Model):
  REASON_CHOICES = (
      ('purchase', 'Customer Purchase'),
      ('restock', 'Restock'),
      ('adjustment', 'Inventory Adjustment'),
      ('return', 'Customer Return'),
      ('reservation', 'Reservation'),
      ('release', 'Reservation Release'),
  )
  variant = models.ForeignKey(ProductVariant, related_name='inventory_changes', on_delete=models.CASCADE)
  quantity = models.IntegerField()  # Can be positive (increase) or negative (decrease)
  reason = models.CharField(max_length=50, choices=REASON_CHOICES)
  reference_id = models.CharField(max_length=100, blank=True, null=True)  # Order ID, reservation ID, etc.
  notes = models.TextField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
  def __str__(self):
      return f"{self.variant} - {self.quantity} - {self.reason}"

class InventoryReservation(models.Model):
  variant = models.ForeignKey(ProductVariant, related_name='reservations', on_delete=models.CASCADE)
  quantity = models.IntegerField(default=1)
  session_id = models.CharField(max_length=255)
  order_id = models.CharField(max_length=255, null=True, blank=True)
  expires_at = models.DateTimeField()
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  def __str__(self):
      return f"{self.variant} - {self.quantity} - {self.session_id}"

# Phone Repair Service Models
class PhoneBrand(models.Model):
  name = models.CharField(max_length=100)
  slug = models.SlugField(max_length=255, unique=True, blank=True)
  image = models.ImageField(upload_to='brands/', null=True, blank=True)
  def save(self, *args, **kwargs):
      if not self.slug:
          self.slug = slugify(self.name)
          original_slug = self.slug
          counter = 1
          while PhoneBrand.objects.filter(slug=self.slug).exclude(id=self.id).exists():
              self.slug = f"{original_slug}-{counter}"
              counter += 1
      super().save(*args, **kwargs)
  def __str__(self):
      return self.name

class PhoneModel(models.Model):
  brand = models.ForeignKey(PhoneBrand, related_name='models', on_delete=models.CASCADE)
  name = models.CharField(max_length=100)
  slug = models.SlugField(max_length=255, unique=True, blank=True)
  image = models.ImageField(upload_to='models/', null=True, blank=True)
  def save(self, *args, **kwargs):
      if not self.slug:
          self.slug = slugify(self.name)
          original_slug = self.slug
          counter = 1
          while PhoneModel.objects.filter(slug=self.slug).exclude(id=self.id).exists():
              self.slug = f"{original_slug}-{counter}"
              counter += 1
      super().save(*args, **kwargs)
  def __str__(self):
      return f"{self.brand.name} {self.name}"

class RepairService(models.Model):
  phone_model = models.ForeignKey(PhoneModel, related_name='repair_services', on_delete=models.CASCADE)
  name = models.CharField(max_length=200)
  description = models.TextField(blank=True, null=True)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  estimated_time = models.CharField(max_length=100, blank=True, null=True)
  def __str__(self):
      return f"{self.phone_model} - {self.name}"

class Accessories(models.Model):
  name = models.CharField(max_length=200)
  slug = models.SlugField(max_length=255, unique=True, blank=True)
  brand = models.CharField(max_length=100)
  description = models.TextField(blank=True, null=True)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  count_in_stock = models.IntegerField(default=0)
  image = models.ImageField(upload_to='accessories/')
  class Meta:
      verbose_name_plural = "Accessories"
  def save(self, *args, **kwargs):
      if not self.slug:
          self.slug = slugify(self.name)
          original_slug = self.slug
          counter = 1
          while Accessories.objects.filter(slug=self.slug).exclude(id=self.id).exists():
              self.slug = f"{original_slug}-{counter}"
              counter += 1
      super().save(*args, **kwargs)
  def __str__(self):
      return self.name

class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
  phone_number = models.CharField(max_length=15, blank=True, null=True)
  address_line1 = models.CharField(max_length=100, blank=True, null=True)
  address_line2 = models.CharField(max_length=100, blank=True, null=True)
  city = models.CharField(max_length=50, blank=True, null=True)
  state = models.CharField(max_length=50, blank=True, null=True)
  postal_code = models.CharField(max_length=20, blank=True, null=True)
  country = models.CharField(max_length=50, blank=True, null=True)
  is_premium_member = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  def __str__(self):
      return f"{self.user.username}'s Profile"

class Cart(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
  session_id = models.CharField(max_length=255, null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  class Meta:
      constraints = [
          models.UniqueConstraint(
              fields=['user'],
              condition=models.Q(user__isnull=False),
              name='unique_user_cart'
          ),
          models.UniqueConstraint(
              fields=['session_id'],
              condition=models.Q(session_id__isnull=False),
              name='unique_session_cart'
          )
      ]
  def __str__(self):
      if self.user:
          return f"Cart for {self.user.username}"
      return f"Cart for session {self.session_id}"
  @property
  def total_price(self):
      return sum(item.total_price for item in self.items.all())
  @property
  def total_items(self):
      return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
  quantity = models.PositiveIntegerField(default=1)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  class Meta:
      constraints = [
          models.UniqueConstraint(
              fields=['cart', 'variant'],
              condition=models.Q(variant__isnull=False),
              name='unique_variant_cart_item'
          ),
          models.UniqueConstraint(
              fields=['cart', 'product'],
              condition=models.Q(variant__isnull=True),
              name='unique_product_cart_item'
          )
      ]
  def __str__(self):
      if self.variant:
          return f"{self.quantity} x {self.variant} in cart {self.cart.id}"
      return f"{self.quantity} x {self.product.name} in cart {self.cart.id}"
  @property
  def price(self):
      if self.variant:
          return self.variant.price
      return self.product.base_price
  @property
  def total_price(self):
      return self.price * self.quantity

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  """Create a UserProfile when a new User is created"""
  if created:
      UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  """Save the UserProfile when the User is saved"""
  instance.profile.save()

class WebhookEvent(models.Model):
   """
   Model to track processed webhook events for idempotency
   """
   event_id = models.CharField(max_length=255, unique=True)
   event_type = models.CharField(max_length=100)
   data = models.TextField()  # JSON data
   processed_at = models.DateTimeField(auto_now_add=True)
  
   def __str__(self):
       return f"{self.event_type} - {self.event_id}"



