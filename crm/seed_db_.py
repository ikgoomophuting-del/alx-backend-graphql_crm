from .models import Customer, Product

def seed_data():
    Customer.objects.get_or_create(name="Alice", email="alice@example.com", phone="+1234567890")
    Customer.objects.get_or_create(name="Bob", email="bob@example.com", phone="123-456-7890")
    Product.objects.get_or_create(name="Laptop", price=999.99, stock=5)
    Product.objects.get_or_create(name="Phone", price=499.99, stock=10)

    print("✅ Database seeded successfully!")
  
