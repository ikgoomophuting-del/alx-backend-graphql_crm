#!/usr/bin/env python3
"""
CRM GraphQL Schema for Customers, Products, and Orders.
Defines GraphQL types, queries, and mutations for the CRM system.
"""

import re
import graphene
from decimal import Decimal
from datetime import datetime
from django.db import transaction
from graphene_django import DjangoObjectType
from django.core.exceptions import ValidationError
from .models import Customer, Product, Order


# ============================================================
#  Object Types (GraphQL Types)
# ============================================================

class CustomerType(DjangoObjectType):
    """GraphQL type for Customer model."""

    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    """GraphQL type for Product model."""

    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    """GraphQL type for Order model."""

    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# ============================================================
#  Mutations
# ============================================================

class CreateCustomer(graphene.Mutation):
    """Mutation to create a single customer."""
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, email, phone=None):
        errors = []
        phone_regex = r"^\+?\d[\d\-]{7,14}$"

        if Customer.objects.filter(email=email).exists():
            errors.append("Email already exists.")

        if phone and not re.match(phone_regex, phone):
            errors.append("Invalid phone format. Use +1234567890 or 123-456-7890.")

        if errors:
            return CreateCustomer(errors=errors, message="Customer creation failed.")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully!")


class CustomerInput(graphene.InputObjectType):
    """Input object for bulk customer creation."""
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class BulkCreateCustomers(graphene.Mutation):
    """Mutation for bulk creating customers."""
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        customers = []
        errors = []
        phone_regex = r"^\+?\d[\d\-]{7,14}$"

        for data in input:
            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")

            if Customer.objects.filter(email=email).exists():
                errors.append(f"Email already exists: {email}")
                continue

            if phone and not re.match(phone_regex, phone):
                errors.append(f"Invalid phone for {name}: {phone}")
                continue

            customer = Customer.objects.create(name=name, email=email, phone=phone)
            customers.append(customer)

        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    """Mutation to create a product."""
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, price, stock=0):
        errors = []
        if price <= 0:
            errors.append("Price must be positive.")
        if stock < 0:
            errors.append("Stock cannot be negative.")

        if errors:
            return CreateProduct(errors=errors)

        product = Product.objects.create(name=name, price=Decimal(price), stock=stock)
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    """Mutation to create an order."""
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        errors = []
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID.")
            return CreateOrder(errors=errors)

        if not product_ids:
            errors.append("At least one product must be selected.")

        products = Product.objects.filter(pk__in=product_ids)
        if products.count() != len(product_ids):
            errors.append("One or more product IDs are invalid.")

        if errors:
            return CreateOrder(errors=errors)

        total_amount = sum([p.price for p in products])
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date or datetime.now()
        )
        order.products.set(products)
        order.save()
        return CreateOrder(order=order)


# ============================================================
#  Root Mutation and Query Registration
# ============================================================

class Mutation(graphene.ObjectType):
    """Root mutation class for CRM schema."""
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


class Query(graphene.ObjectType):
    """Root query class for CRM schema."""
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.select_related("customer").prefetch_related("products")


schema = graphene.Schema(query=Query, mutation=Mutation)
