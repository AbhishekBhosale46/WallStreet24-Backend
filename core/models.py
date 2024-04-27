from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from decimal import Decimal
import random
from datetime import datetime
from tinymce import models as tinymce_models

class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        user_portfolio = Portfolio.objects.create(
            user=user,
            cash=1000000
        )
        return user

    def create_superuser(self, name, password):
        email = f"{name}@wallstreet.com"
        user = self.create_user(email=email, password=password, name=name)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    contact_no = models.CharField(max_length=10)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'name'

    def __str__(self):
        return f"{self.email}"


class Stock(models.Model):
    name = models.CharField(max_length=50)
    ticker = models.CharField(max_length=10)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_history = models.JSONField(default=list, blank=True)
    is_listed = models.BooleanField()
    details = tinymce_models.HTMLField(default='')
    total_shares = models.IntegerField()
    remaining_shares = models.IntegerField()

    def __str__(self):
        return f"{self.name}-{self.ticker}"

    def price_change(self):
        last_traded_price = Decimal((self.price_history[-2]).get("price"))
        return str(((self.current_price-last_traded_price)/last_traded_price)*100)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.price_history.append({'price': str(self.current_price), 'datetime': str(datetime.now())})
            self.price_history.append({'price': str(self.current_price), 'datetime': str(datetime.now())})
        super().save(*args, **kwargs)


class News(models.Model):
    title = models.TextField()
    description = models.TextField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=10, choices=[('positive', 'positive'), ('negative', 'negative')])
    impact = models.FloatField()
    impact_no = models.IntegerField(default=1)
    impacts = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.title}"
        
    def divide_number_into_5_parts(self, number):
        parts = []
        for _ in range(4):
            max_part = max(5, number / (5 - len(parts)))
            part = random.uniform(5, max_part)
            parts.append(round(part,2))
            number -= part
        parts.append(round(number,2))
        random.shuffle(parts)
        return parts

    def save(self, *args, **kwargs):
        if not self.pk:
            number = self.impact
            parts = self.divide_number_into_5_parts(100)
            self.impacts = parts
        super().save(*args, **kwargs)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    traded_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=5, choices=[('buy', 'buy'), ('sell', 'sell')])
    transaction_datetime = models.DateTimeField(auto_now_add=True)


class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cash = models.IntegerField()
    # networth = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.user.email}"


class Holding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    quantity = models.IntegerField()    

    def __str__(self) -> str:
        return f"{self.stock.name}-{self.quantity}"


class Market(models.Model):
    is_open = models.BooleanField(default=False)


class Ipo(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    issue_size = models.IntegerField()
    floor_price = models.IntegerField()
    ceil_price = models.IntegerField()
    lot_size = models.IntegerField()
    red_herring_prospectus = models.TextField()
    listing_price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.stock.name}"


class IpoSubscription(models.Model):
    ipo = models.ForeignKey(Ipo, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_price = models.IntegerField()
    bid_quantity = models.IntegerField()
    transaction_datetime = models.DateTimeField(auto_now_add=True)