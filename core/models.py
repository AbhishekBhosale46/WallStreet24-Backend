from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        user_portfolio = Portfolio.objects.create(
            user=user,
            cash=9999999
        )
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.email}"


class Stock(models.Model):
    name = models.CharField(max_length=50)
    ticker = models.CharField(max_length=10)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_history = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.name}-{self.ticker}"

    def get_price_change(self):
        last_traded_price = (self.price_history[-1]).get("price")
        return ((self.current_price-last_traded_price)/last_traded_price)*100


class News(models.Model):
    title = models.TextField()
    description = models.TextField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=10, choices=[('positive', 'positive'), ('negative', 'negative')])
    impact = models.FloatField()
    decay_factor = models.DecimalField(max_digits=6, decimal_places=2)
    decay_rate = models.DecimalField(max_digits=6, decimal_places=2)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.title}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    traded_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=5, choices=[('buy', 'sell'), ('buy', 'sell')])
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