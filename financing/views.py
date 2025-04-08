from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import FinancingPlan, Simulation
from .serializers.financing_serializers import (
    FinancingPlanSerializer, 
    SimulationSerializer,
    SimulationCreateSerializer
)

# Create your views here.

class FinancingPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancingPlan.objects.filter(is_active=True)
    serializer_class = FinancingPlanSerializer
    lookup_field = 'slug'

class SimulationListView(generics.ListAPIView):
    serializer_class = SimulationSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Simulation.objects.filter(user=self.request.user)
        return Simulation.objects.none()

class SaveSimulationView(generics.CreateAPIView):
    serializer_class = SimulationCreateSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        
class SimulateFinancingView(APIView):
    """
    Vista para simular financiamiento sin guardar en base de datos
    """
    def post(self, request, format=None):
        # Obtenemos los datos básicos
        product_value = float(request.data.get('product_value', 0))
        plan_type = request.data.get('plan_type', 'programada')
        initial_percentage = float(request.data.get('initial_percentage', 0))
        term = int(request.data.get('term', 12))
        
        # Realizamos cálculos básicos según el tipo de plan
        if plan_type == 'programada':
            # Para Compra Programada
            initial_amount = product_value * (initial_percentage / 100)
            adjudication_percentage = 45  # Porcentaje para adjudicación
            
            # Calculamos cuota mensual promedio para alcanzar el porcentaje de adjudicación
            remaining_percentage = adjudication_percentage - initial_percentage
            remaining_amount = product_value * (remaining_percentage / 100)
            monthly_payment = remaining_amount / term
            
            # Preparamos resultado
            simulation_result = {
                'plan_type': 'programada',
                'product_value': product_value,
                'initial_percentage': initial_percentage,
                'initial_amount': initial_amount,
                'adjudication_percentage': adjudication_percentage,
                'remaining_percentage': remaining_percentage,
                'remaining_amount': remaining_amount,
                'monthly_payment': monthly_payment,
                'term': term,
                'post_adjudication_amount': product_value * ((100 - adjudication_percentage) / 100),
                'estimated_adjudication_date': term  # En meses
            }
        else:
            # Para Crédito Inmediato
            initial_amount = product_value * (initial_percentage / 100)
            remaining_amount = product_value - initial_amount
            
            # Calcular tasa de interés mensual (asumiendo 12% anual)
            annual_interest = 12.0
            monthly_interest = annual_interest / 12 / 100
            
            # Calcular cuota mensual con interés compuesto
            monthly_payment = remaining_amount * (monthly_interest * (1 + monthly_interest) ** term) / ((1 + monthly_interest) ** term - 1)
            
            total_payment = monthly_payment * term
            total_interest = total_payment - remaining_amount
            
            # Preparamos resultado
            simulation_result = {
                'plan_type': 'credito',
                'product_value': product_value,
                'initial_percentage': initial_percentage,
                'initial_amount': initial_amount,
                'remaining_amount': remaining_amount,
                'annual_interest_rate': annual_interest,
                'monthly_interest_rate': monthly_interest * 100,
                'monthly_payment': monthly_payment,
                'term': term,
                'total_payment': total_payment,
                'total_interest': total_interest,
                'total_cost': initial_amount + total_payment
            }
        
        return Response(simulation_result, status=status.HTTP_200_OK)
