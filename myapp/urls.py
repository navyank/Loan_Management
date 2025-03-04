from django.urls import path
from .views import *

urlpatterns = [
     path('signup/', UserCreationView.as_view(), name='signup'),
     path('verify_otp/',VerifyOtpView.as_view(),name='verify_otp'),
     path('signin/',UserSignInView.as_view(),name='signin'),
     # path('loans/', LoanView.as_view(), name='loan-list-create'),  # Create & List Loans
     # path('loans/<int:loan_id>/foreclose/', LoanForeclosureView.as_view(), name='loan-foreclose'),  # Foreclose Loan
     # path('payments/', LoanPaymentView.as_view(), name='loan-payment'),  # Make a Payment
     path('loans/<str:loan_id>/', AdminLoanView.as_view(), name='admin-loan-detail'),  # Admin Loan Actions
     path('adminloan/',AdminGetAllLoan.as_view(),name='admin-all-loan'),
     path('loans/', LoanView.as_view(), name='loans'),
     path('loans/<str:loan_id>/foreclose/', LoanForeclosureView.as_view(), name='foreclose-loan'),


]
