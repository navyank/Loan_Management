from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import date, timedelta

# Create your models here.

class CustomeUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin','Admin'),
        ('user','User')
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    email_verifield=models.BooleanField(default=False)   

    
class OTPVerification(models.Model):
    user = models.OneToOneField(CustomeUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)    
    
class Loan(models.Model):    
    loan_id = models.CharField(max_length=10, unique=True, editable=False)
    user = models.ForeignKey(CustomeUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField()  
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2) 
    total_interest = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('CLOSED', 'Closed')], default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.loan_id:
            last_loan = Loan.objects.order_by('-id').first()
            if last_loan and last_loan.loan_id.startswith("LOAN"):
                last_number = int(last_loan.loan_id[4:])
                self.loan_id = f"LOAN{last_number + 1:03d}"
            else:
                self.loan_id = "LOAN001"
        
        monthly_rate = (self.interest_rate / 100) / 12
        self.monthly_installment = round(
            (self.amount * monthly_rate) / (1 - (1 + monthly_rate) ** -self.tenure), 2
        )
        self.total_interest = round(self.monthly_installment * self.tenure - self.amount, 2)
        self.total_amount = round(self.amount + self.total_interest, 2)

        super().save(*args, **kwargs)

class PaymentSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Pending', 'Pending')], default='Pending')
    installment_no = models.IntegerField()
    def save(self, *args, **kwargs):
        if not self.id:
            self.due_date = date.today() + timedelta(days=30 * (self.installment_no - 1))
        super().save(*args, **kwargs)
