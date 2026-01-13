from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role="customer", **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password, role="admin")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def active(self):
        return self.filter(is_active=True)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("vendor", "Vendor"),
        ("admin", "Admin"),
    )

    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return f"{self.get_username()}"
    
    def get_full_name(self):
        if self.first_name and not self.last_name:
            return self.first_name
        return f"{self.first_name} {self.last_name}"
        
    


