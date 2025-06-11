from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class LoginManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# Create your models here.
class login_tbl(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=50)
    fullname=models.CharField(max_length=200)
    firstname=models.CharField(max_length=200)
    lastname=models.CharField(max_length=25)
    username=models.CharField(max_length=25)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=100)
    mobile=models.BigIntegerField(null=True,blank=True)
    image=models.ImageField(upload_to='images/')
    is_superuser = models.BooleanField(default=False)
    is_admin=models.BooleanField(default=False)
    block = models.BooleanField(default=False)  # False = not blocked, True = blocked

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = LoginManager()
class UploadedCSV(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class Insurance(models.Model):
    uploaded_csv=models.ForeignKey(UploadedCSV, on_delete=models.CASCADE)
    entry_date = models.DateField(default=timezone.now,null=True, blank=True)
    client_name = models.CharField(max_length=255,null=True,blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    lob_product = models.CharField("LOB (PRODUCT)", max_length=100, null=True, blank=True)
    insurance_company = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    risk_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    own_damage = models.CharField(max_length=50, null=True, blank=True)
    third_party = models.CharField(max_length=50, null=True, blank=True)
    terrorism_premium = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_premium = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    booking_code = models.CharField(max_length=100, null=True, blank=True)
    agent_name = models.CharField(max_length=255, null=True, blank=True)
    policy_number = models.CharField(max_length=100, null=True, blank=True)
    registered_number = models.CharField(max_length=100, null=True, blank=True)
    fuel_type = models.CharField(max_length=50, null=True, blank=True)
    vehicle_cc = models.IntegerField(null=True, blank=True)
    gvw = models.CharField(max_length=100, null=True, blank=True)
    idv_of_vehicle = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    manufacture_year = models.IntegerField(null=True, blank=True)
    ncb = models.CharField(max_length=50, null=True, blank=True)
    type_of_vehicle = models.CharField(max_length=100, null=True, blank=True)
    policy_type = models.CharField(max_length=100, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    email_id = models.CharField(max_length=255,null=True, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)
    payment_mode = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    cheque_no = models.CharField(max_length=50, null=True, blank=True)
    od_brok_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tp_terr_brok_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_grid = models.CharField(max_length=100, null=True, blank=True)
    od_brok_amt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tp_terr_brok_amt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    agency_comm_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    agency_comm_amt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deduction_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    less_amt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tibpl_share = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    receivable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
   

    def __str__(self):
        return f"{self.client_name} - {self.policy_number or 'N/A'} - {self.agent_name}"


class PolicyReport(models.Model):
    policy_number = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    data = models.TextField()

    def __str__(self):
        return self.policy_number
class Location(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)  # or any additional field

    def __str__(self):
        return self.name  # Only return name, not full string with code


class Permission(models.Model):
    section_name = models.CharField(max_length=100)
    
    allowed = models.BooleanField(default=False)
    block=models.BooleanField(default=False)  # False = not blocked, True = blocked

    user = models.ForeignKey('login_tbl', on_delete=models.CASCADE, related_name='permissions')  # Adjust if you have a custom user

    def __str__(self):
        return f"{self.user.username} - {self.section_name}"