# crm/schema.py
import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
import re
from decimal import Decimal

# ========== TYPES ==========

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


# crm/schema.py (continued)

# ========== MUTATIONS ==========

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    def validate_phone(self, phone):
        if phone and not re.match(r"^\+?\d[\d\-\s]{7,}$", phone):
            raise ValidationError("Invalid phone format. Use +1234567890 or 123-456-7890.")

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(success=False, message="Email already exists.", customer=None)

        try:
            self.validate_phone(phone)
            customer = Customer.objects.create(name=name, email=email, phone=phone)
            return CreateCustomer(success=True, message="Customer created successfully.", customer=customer)
        except ValidationError as e:
            return CreateCustomer(success=False, message=str(e), customer=None)


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(
            graphene.NonNull(
                graphene.InputObjectType(
                    "CustomerInput",
                    name=graphene.String(required=True),
                    email=graphene.String(required=True),
                    phone=graphene.String()
                )
            )
        )

    created_customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, customers):
        created = []
        errors = []

        for data in customers:
            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")

            if Customer.objects.filter(email=email).exists():
                errors.append(f"Duplicate email: {email}")
                continue

            if phone and not re.match(r"^\+?\d[\d\-\s]{7,}$", phone):
                errors.append(f"Invalid phone format for {email}")
                continue

            c = Customer(name=name, email=email, phone=phone)
            c.save()
            created.append(c)

        return BulkCreateCustomers(created_customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, price, stock=0):
        if price <= 0:
            return cls(success=False, message="Price must be positive.", product=None)
        if stock < 0:
            return cls(success=False, message="Stock cannot be negative.", product=None)

        product = Product.objects.create(name=name, price=price, stock=stock)
        return cls(success=True, message="Product created successfully.", product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return cls(success=False, message="Invalid customer ID.", order=None)

        if not product_ids:
            return cls(success=False, message="At least one product must be selected.", order=None)

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            return cls(success=False, message="Invalid product IDs.", order=None)

        total = sum(Decimal(p.price) for p in products)

        order = Order.objects.create(customer=customer, order_date=order_date or None, total_amount=total)
        order.products.set(products)

        return cls(success=True, message="Order created successfully.", order=order)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
