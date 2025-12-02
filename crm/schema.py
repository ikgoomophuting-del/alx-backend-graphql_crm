import re
from decimal import Decimal
from datetime import datetime

import graphene
from graphene_django import DjangoObjectType
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Customer, Product, Order


# ---------------------------------------------------------
# Relay Node Types (for filtering + checker requirements)
# ---------------------------------------------------------

class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "email": ["exact", "icontains"],
            "phone": ["exact", "icontains"],
        }


# ---------------------------------------------------------
# Regular GraphQL Types (non-Relay)
# ---------------------------------------------------------

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# ---------------------------------------------------------
# Mutations
# ---------------------------------------------------------

# Create Customer
class CreateCustomer(graphene.Mutation):
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


# Bulk Create Customers
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class BulkCreateCustomers(graphene.Mutation):
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


# Create Product
class CreateProduct(graphene.Mutation):
    class Arguments:
