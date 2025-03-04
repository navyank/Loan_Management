from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
import random
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser
from rest_framework.permissions import AllowAny
from decimal import Decimal
from .permissions import IsNormalUser
from rest_framework_simplejwt.authentication import JWTAuthentication



 
# Create your views here.
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role  # Add role to token

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
class UserCreationView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = UserSerializer(data=request.data)
        role=request.data.get('role') 
        if not role:
            return Response({
                "success": False,
                "data": None,
                "message": "User role is required",
                "error": "User role is missing"
            },status=status.HTTP_400_BAD_REQUEST)
        try:
            if role == "user":
                username = request.data.get('username')    
                email = request.data.get('email')
                if not username or not email:
                    return Response({
                        "success": False,
                        "data": None,
                        "message": "user signup failed",
                        "error": "Username and email are required"
                    },status=status.HTTP_200_OK)
                user=CustomeUser.objects.filter(email=email).first()  
                if user:
                    return Response({
                        "success": False,
                        "data": None,
                        "message": "User with this email is already registered",
                        "error": None
                    },status=status.HTTP_400_BAD_REQUEST)
                otp = str(random.randint(100000, 999999))
                new_user = CustomeUser.objects.create_user( 
                     first_name=username, 
                     email=email,
                     role="user",
                     username=email                                 
                )
                otpcode = OTPVerification.objects.create(
                    otp_code=otp,
                    user=new_user
                )
                subject = "Welcome and Your OTP"
                message = f"Hello {username},\n\nWelcome to our platform! Your OTP is: {otp}.\n\nBest regards,\nYour Team"
                send_mail(subject, message, 'no-reply@yourdomain.com', [email])
                return Response({
                    "success": True,
                     "data": {"email": new_user.email, "username": new_user.first_name,"otp":otp},
                     "message": "user signed up successfully",
                     "error": None
                },status=status.HTTP_200_OK)
            elif role == "admin" :
                username = request.data.get('username')    
                email = request.data.get('email')
                if not username or not email:
                    return Response({
                        "success": False,
                        "data": None,
                        "message": "admin signup failed",
                        "error": "Username and email are required"
                    },status=status.HTTP_200_OK)
                user=CustomeUser.objects.filter(email=email).first()  
                if user:
                    return Response({
                        "success": False,
                        "data": None,
                        "message": "admin with this email is already registered",
                        "error": None
                    },status=status.HTTP_400_BAD_REQUEST)
                otp = str(random.randint(100000, 999999))
                new_user = CustomeUser.objects.create_user( 
                     username=email, 
                     email=email,
                     role="admin",
                     first_name=username                                       
                )
                otpcode = OTPVerification.objects.create(
                    otp_code=otp,
                    user=new_user
                )
                subject = "Welcome and Your OTP"
                message = f"Hello {username},\n\nWelcome to our platform! Your OTP is: {otp}.\n\nBest regards,\nYour Team"
                send_mail(subject, message, 'no-reply@yourdomain.com', [email])
                return Response({
                    "success": True,
                     "data": {"email": new_user.email, "username": new_user.first_name,"otp":otp},
                     "message": "admin signed up successfully",
                     "error": None
                },status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "success": False,
                        "data": None,
                        "message": "Invalid user type",
                        "error": "User type is invalid"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )    
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "data": None,
                    "message": "An unexpected error occurred",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class VerifyOtpView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            email = request.data.get('email')
            otp = request.data.get('otp')  
            if not email or not otp:
               return Response({
                   "success":False,
                   "error": "email and OTP are required"
               }, status=status.HTTP_400_BAD_REQUEST)  
            user=CustomeUser.objects.filter(email=email).first()   
            if not user:
                return Response({
                    "success": False,
                    "error": "User not found"
                }, status=status.HTTP_404_NOT_FOUND)
            otp_record = OTPVerification.objects.filter(user=user, otp_code=otp).first()
            if not otp_record:
                return Response({
                    "success": False,
                    "error": "Invalid OTP"
                }, status=status.HTTP_400_BAD_REQUEST)
            user.email_verifield = True
            user.save()
            otp_record.delete()
            tokens = get_tokens_for_user(user)
            return Response({
                "success": True,
                "tokens": tokens,
                "message": "OTP verified successfully"
            }, status=status.HTTP_200_OK)
       
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)                   
class UserSignInView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        email = request.data.get('email')
        if not email:
            return Response({
                "success": False,
                "message": "Email is required",
                "error": "Email missing"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = CustomeUser.objects.filter(email=email).first()

        if not user:
            return Response({
                "success": False,
                "message": "User not found",
                "error": "Invalid email"
            }, status=status.HTTP_404_NOT_FOUND)

        otp = str(random.randint(100000, 999999))

        # Save OTP in the database
        otp_record, created = OTPVerification.objects.update_or_create(
            user=user, defaults={"otp_code": otp}
        )

        # Send OTP via email
        subject = "Your Login OTP"
        message = f"Hello {user.first_name},\n\nYour OTP for login is: {otp}.\n\nBest regards,\nYour Team"
        send_mail(subject, message, 'no-reply@yourdomain.com', [email])

        return Response({
            "success": True,
            "otp":otp,
            "message": "OTP sent successfully to your email"
        }, status=status.HTTP_200_OK)



# # Admin Loan Actions (View, Update, Delete)
class AdminLoanView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
            serializer = LoanSerializer(loan)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': "Loan details fetched",
                'error': None
            }, status=status.HTTP_200_OK)
        except Loan.DoesNotExist:
            return Response({
                'success': False,
                'data': None,
                'message': "Loan not found",
                'error': "Invalid loan ID"
            }, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
            serializer = LoanSerializer(loan, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'message': "Loan updated successfully",
                    'error': None
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'data': serializer.errors,
                'message': "Loan update failed",
                'error': "Validation error"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Loan.DoesNotExist:
            return Response({
                'success': False,
                'data': None,
                'message': "Loan not found",
                'error': "Invalid loan ID"
            }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
            loan.delete()
            return Response({
                'success': True,
                'data': None,
                'message': "Loan deleted successfully",
                'error': None
            }, status=status.HTTP_204_NO_CONTENT)
        except Loan.DoesNotExist:
            return Response({
                'success': False,
                'data': None,
                'message': "Loan not found",
                'error': "Invalid loan ID"
            }, status=status.HTTP_404_NOT_FOUND)
class AdminGetAllLoan(APIView):
      authentication_classes = [JWTAuthentication]
      permission_classes = [IsAuthenticated, IsAdminUser]
      def get(self, request):
        loans = Loan.objects.all()
        loan_data = []

        for loan in loans:
            paid_amount = sum(ps.amount for ps in PaymentSchedule.objects.filter(loan=loan, status='Paid'))
            remaining_amount = loan.total_amount - paid_amount
            next_due = PaymentSchedule.objects.filter(loan=loan, status='Pending').order_by('due_date').first()
            next_due_date = next_due.due_date if next_due else None

            loan_data.append({
                "loan_id": loan.loan_id,
                "amount": loan.amount,
                "tenure": loan.tenure,
                "monthly_installment": loan.monthly_installment,
                "total_amount": loan.total_amount,
                "amount_paid": paid_amount,
                "amount_remaining": remaining_amount,
                "next_due_date": next_due_date,
                "status": loan.status,
                "created_at": loan.created_at
            })

        return Response({
            "success":False,
            "data": {"loans": loan_data}
        }, status=status.HTTP_200_OK)
              
class LoanView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsNormalUser]
    # permission_classes = [AllowAny]
    def post(self, request):
        print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")

        if not request.user.is_authenticated:
            return Response({
                'success':False,
                'error': "User not authenticated"
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = LoanSerializer(data=request.data)

        if serializer.is_valid():
            with transaction.atomic():
                loan = Loan.objects.create(
                    user=request.user,  # Ensure user is set
                    amount=serializer.validated_data['amount'],
                    tenure=serializer.validated_data['tenure'],
                    interest_rate=serializer.validated_data.get('interest_rate')
                )

                for i in range(1, loan.tenure + 1):
                    PaymentSchedule.objects.create(
                        loan=loan,
                        installment_no=i,
                        amount=loan.monthly_installment
                    )

                return Response({
                    "success":True,
                    "data": LoanSerializer(loan).data
                }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        loans = Loan.objects.all()
        loan_data = []

        for loan in loans:
            paid_amount = sum(ps.amount for ps in PaymentSchedule.objects.filter(loan=loan, status='Paid'))
            remaining_amount = loan.total_amount - paid_amount
            next_due = PaymentSchedule.objects.filter(loan=loan, status='Pending').order_by('due_date').first()
            next_due_date = next_due.due_date if next_due else None

            loan_data.append({
                "loan_id": loan.loan_id,
                "amount": loan.amount,
                "tenure": loan.tenure,
                "monthly_installment": loan.monthly_installment,
                "total_amount": loan.total_amount,
                "amount_paid": paid_amount,
                "amount_remaining": remaining_amount,
                "next_due_date": next_due_date,
                "status": loan.status,
                "created_at": loan.created_at
            })

        return Response({
            "success":False,
            "data": {"loans": loan_data}
        }, status=status.HTTP_200_OK)

class LoanForeclosureView(APIView):    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsNormalUser]
    def post(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
            if loan.status == "CLOSED":
                return Response({
                    "success":False,
                    "message": "Loan is already closed."
                }, status=status.HTTP_400_BAD_REQUEST)

            paid_amount = sum(ps.amount for ps in PaymentSchedule.objects.filter(loan=loan, status='Paid'))
            remaining_amount = loan.total_amount - paid_amount

            # Convert float to Decimal
            foreclosure_discount = round(remaining_amount * Decimal("0.05"), 2)
            final_settlement_amount = round(remaining_amount - foreclosure_discount, 2)

            loan.status = "CLOSED"
            loan.save()

            return Response({
                "success": True,
                "message": "Loan foreclosed successfully.",
                "data": {
                    "loan_id": loan.loan_id,
                    "amount_paid": paid_amount,
                    "foreclosure_discount": foreclosure_discount,
                    "final_settlement_amount": final_settlement_amount,
                    "status": "CLOSED"
                }
            }, status=status.HTTP_200_OK)

        except Loan.DoesNotExist:
            return Response({
                "success": False,
                "message": "Loan not found."
            }, status=status.HTTP_404_NOT_FOUND)