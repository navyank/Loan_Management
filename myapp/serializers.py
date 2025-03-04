from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomeUser
        fields='__all__'

class PaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSchedule
        fields = ['installment_no', 'due_date', 'amount', 'status']

class LoanSerializer(serializers.ModelSerializer):
    payment_schedule = serializers.SerializerMethodField()  # Keep this since it's derived

    class Meta:
        model = Loan
        fields = ['loan_id', 'amount', 'tenure', 'interest_rate', 'monthly_installment', 
                  'total_interest', 'total_amount', 'status', 'created_at', 'payment_schedule']

    def get_payment_schedule(self, obj):
        schedule = PaymentSchedule.objects.filter(loan=obj).order_by('installment_no')
        return PaymentScheduleSerializer(schedule, many=True).data
    def get_interest_rate(self, obj):
        return f"{obj.interest_rate}% yearly"
    def validate(self, data):
        """ Validate amount and tenure before saving """
        amount = data.get('amount')
        tenure = data.get('tenure')

        if amount is not None and amount <= 0:
            raise serializers.ValidationError({"amount": "Loan amount must be greater than zero."})
        if amount is not None and amount < 1000:
            raise serializers.ValidationError({"amount": "Minimum loan amount should be 1000."})
        if amount is not None and amount > 100000:
            raise serializers.ValidationError({"amount": "Maximum loan amount should be 100000."})
        if tenure is not None and tenure <= 0:
            raise serializers.ValidationError({"tenure": "Tenure must be a positive integer."})
        if tenure is not None and tenure < 3:
            raise serializers.ValidationError({"tenure": "Tenure should be minimum 3 months."})
        if tenure is not None and tenure > 24:
            raise serializers.ValidationError({"tenure": "Tenure should be maximum 24 months."})

        return data