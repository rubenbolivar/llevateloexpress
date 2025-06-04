from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal
import math

from .models import (
    FinancingPlan, FinancingRequest, Payment, 
    PaymentSchedule, ApplicationStatusHistory,
    FinancingConfiguration, ProductCategory, SimulatorProduct, HelpText,
    CalculatorMode
)
from .serializers.financing_serializers import (
    FinancingPlanSerializer,
    FinancingRequestListSerializer,
    FinancingRequestDetailSerializer,
    FinancingRequestCreateSerializer,
    FinancingRequestUpdateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentScheduleSerializer,
    FinancingCalculatorSerializer
)
from notifications.models import EmailNotification
from products.models import Product, Category


class FinancingPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para planes de financiamiento"""
    queryset = FinancingPlan.objects.filter(is_active=True)
    serializer_class = FinancingPlanSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class FinancingRequestViewSet(viewsets.ModelViewSet):
    """ViewSet para solicitudes de financiamiento"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar solicitudes por usuario"""
        user = self.request.user
        if user.is_staff:
            return FinancingRequest.objects.all()
        return FinancingRequest.objects.filter(customer__user=user)
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'list':
            return FinancingRequestListSerializer
        elif self.action == 'create':
            return FinancingRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FinancingRequestUpdateSerializer
        return FinancingRequestDetailSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Crear nueva solicitud de financiamiento"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Obtener el serializer detallado para la respuesta
        detail_serializer = FinancingRequestDetailSerializer(
            serializer.instance,
            context={'request': request}
        )
        
        headers = self.get_success_headers(detail_serializer.data)
        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def submit(self, request, pk=None):
        """Enviar solicitud para revisión"""
        application = self.get_object()
        
        if application.status != 'draft':
            return Response(
                {'error': 'Solo se pueden enviar solicitudes en estado borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el perfil esté completo
        if not application.customer.is_profile_complete:
            return Response(
                {'error': 'Debe completar su perfil antes de enviar la solicitud'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar estado
        old_status = application.status
        application.status = 'submitted'
        application.submitted_at = timezone.now()
        application.save()
        
        # Registrar cambio de estado
        ApplicationStatusHistory.objects.create(
            application=application,
            from_status=old_status,
            to_status='submitted',
            changed_by=request.user,
            notes='Solicitud enviada para revisión'
        )
        
        # Crear notificación
        EmailNotification.objects.create(
            user=request.user,
            notification_type='application_submitted',
            subject='Solicitud Enviada',
            message=f'Su solicitud {application.application_number} ha sido enviada para revisión.',
            context={'application_number': application.application_number}
        )
        
        serializer = FinancingRequestDetailSerializer(
            application,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_documents(self, request, pk=None):
        """Subir documentos requeridos"""
        application = self.get_object()
        
        if application.status not in ['submitted', 'documentation_required']:
            return Response(
                {'error': 'No se pueden subir documentos en este estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar documentos
        if 'income_proof' in request.FILES:
            application.income_proof = request.FILES['income_proof']
        if 'id_document' in request.FILES:
            application.id_document = request.FILES['id_document']
        if 'address_proof' in request.FILES:
            application.address_proof = request.FILES['address_proof']
        
        application.save()
        
        serializer = FinancingRequestDetailSerializer(
            application,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payment_schedule(self, request, pk=None):
        """Obtener calendario de pagos"""
        application = self.get_object()
        schedules = application.payment_schedule.all()
        serializer = PaymentScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Obtener historial de pagos"""
        application = self.get_object()
        payments = application.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet para pagos"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar pagos por usuario"""
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(application__customer__user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Registrar nuevo pago"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar que el usuario puede registrar pagos para esta solicitud
        application = serializer.validated_data['application']
        if not request.user.is_staff and application.customer.user != request.user:
            return Response(
                {'error': 'No tiene permisos para registrar pagos en esta solicitud'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_create(serializer)
        
        # Crear notificación
        EmailNotification.objects.create(
            user=application.customer.user,
            notification_type='payment_registered',
            subject='Pago Registrado',
            message=f'Se ha registrado un pago de ${serializer.instance.amount} para su solicitud {application.application_number}',
            context={
                'amount': str(serializer.instance.amount),
                'application_number': application.application_number
            }
        )
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            PaymentSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class FinancingCalculatorView(APIView):
    """Vista para calcular financiamiento"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Calcular plan de financiamiento"""
        serializer = FinancingCalculatorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtener datos validados
        product = serializer.validated_data['product']
        plan = serializer.validated_data['financing_plan']
        down_payment_percentage = serializer.validated_data['down_payment_percentage']
        payment_frequency = serializer.validated_data['payment_frequency']
        term_months = serializer.validated_data['term_months']
        
        # Calcular montos
        product_price = Decimal(str(product.price))
        down_payment_amount = product_price * Decimal(str(down_payment_percentage)) / 100
        financed_amount = product_price - down_payment_amount
        
        # Calcular interés
        annual_rate = Decimal(str(plan.interest_rate))
        monthly_rate = annual_rate / 12 / 100
        
        # Calcular número de pagos según frecuencia
        if payment_frequency == 'weekly':
            number_of_payments = term_months * 4
            period_rate = monthly_rate / 4
        elif payment_frequency == 'biweekly':
            number_of_payments = term_months * 2
            period_rate = monthly_rate / 2
        else:  # monthly
            number_of_payments = term_months
            period_rate = monthly_rate
        
        # Calcular cuota usando la fórmula de amortización
        if period_rate > 0:
            payment_amount = financed_amount * (
                period_rate * (1 + period_rate) ** number_of_payments
            ) / ((1 + period_rate) ** number_of_payments - 1)
        else:
            payment_amount = financed_amount / number_of_payments
        
        # Calcular totales
        total_amount = down_payment_amount + (payment_amount * number_of_payments)
        total_interest = total_amount - product_price
        
        # Preparar respuesta
        result = {
            'product': {
                'id': product.id,
                'name': product.name,
                'price': float(product_price),
                'image': product.image.url if product.image else None
            },
            'financing_plan': {
                'id': plan.id,
                'name': plan.name,
                'interest_rate': float(annual_rate)
            },
            'calculation': {
                'product_price': float(product_price),
                'down_payment_percentage': down_payment_percentage,
                'down_payment_amount': float(down_payment_amount),
                'financed_amount': float(financed_amount),
                'payment_frequency': payment_frequency,
                'payment_frequency_display': dict(FinancingRequest.PAYMENT_FREQUENCIES)[payment_frequency],
                'term_months': term_months,
                'number_of_payments': number_of_payments,
                'payment_amount': float(payment_amount),
                'total_interest': float(total_interest),
                'total_amount': float(total_amount)
            }
        }
        
        return Response(result, status=status.HTTP_200_OK)


class CustomerApplicationsView(generics.ListAPIView):
    """Vista para listar solicitudes del cliente actual"""
    serializer_class = FinancingRequestListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FinancingRequest.objects.filter(
            customer__user=self.request.user
        ).order_by('-created_at')


class PaymentScheduleListView(generics.ListAPIView):
    """Vista para listar calendario de pagos del cliente"""
    serializer_class = PaymentScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentSchedule.objects.filter(
            application__customer__user=self.request.user,
            is_paid=False
        ).order_by('due_date')


class SimulatorConfigurationView(APIView):
    """Vista para obtener la configuración del simulador"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            # Obtener configuración activa
            config = FinancingConfiguration.objects.filter(is_active=True).first()
            if not config:
                return Response({
                    'error': 'No hay configuración activa'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Obtener opciones de inicial
            down_payments = config.down_payment_options.filter(is_active=True).values(
                'percentage', 'order'
            )
            
            # Obtener plazos
            terms = config.financing_terms.filter(is_active=True).values(
                'months', 'order'
            )
            
            # Obtener frecuencias
            frequencies = []
            for freq in config.payment_frequencies.filter(is_active=True):
                frequencies.append({
                    'value': freq.frequency,
                    'label': freq.get_frequency_display(),
                    'order': freq.order
                })
            
            # Obtener productos reales del catálogo
            categories = []
            for category in Category.objects.all():
                products = Product.objects.filter(
                    category=category,
                    stock__gt=0  # Solo productos con stock
                ).values('id', 'name', 'price', 'description', 'brand')
                
                if products:
                    categories.append({
                        'id': category.id,
                        'name': category.name,
                        'slug': category.slug,
                        'products': list(products)
                    })
            
            # Obtener textos de ayuda
            help_texts = {}
            for help_text in HelpText.objects.filter(is_active=True):
                help_texts[help_text.section] = {
                    'title': help_text.title,
                    'content': help_text.content
                }
            
            return Response({
                'down_payment_options': list(down_payments),
                'financing_terms': list(terms),
                'payment_frequencies': frequencies,
                'categories': categories,
                'help_texts': help_texts
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimulatorCalculateView(APIView):
    """Vista para calcular financiamiento con la nueva configuración"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            # Obtener datos
            product_id = request.data.get('product_id')
            product_price = Decimal(str(request.data.get('product_price', 0)))
            down_payment_percentage = Decimal(str(request.data.get('down_payment_percentage', 0)))
            term_months = int(request.data.get('term_months', 12))
            payment_frequency = request.data.get('payment_frequency', 'monthly')
            
            # Si hay product_id, obtener el producto real
            product_data = None
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    product_data = {
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'brand': product.brand,
                        'category': product.category.name
                    }
                    product_price = product.price
                except Product.DoesNotExist:
                    pass
            
            # Calcular montos
            down_payment_amount = product_price * down_payment_percentage / 100
            financed_amount = product_price - down_payment_amount
            
            # Calcular número de pagos según frecuencia
            if payment_frequency == 'weekly':
                payments_per_month = Decimal('4.33')  # 52/12
                number_of_payments = int(term_months * payments_per_month)
            elif payment_frequency == 'biweekly':
                payments_per_month = Decimal('2.17')  # 26/12
                number_of_payments = int(term_months * payments_per_month)
            else:  # monthly
                payments_per_month = 1
                number_of_payments = term_months
            
            # Calcular monto por pago (sin intereses)
            if number_of_payments > 0:
                payment_amount = financed_amount / number_of_payments
            else:
                payment_amount = 0
            
            # Preparar respuesta
            calculation = {
                'product': product_data,
                'calculation': {
                    'product_price': float(product_price),
                    'down_payment_percentage': float(down_payment_percentage),
                    'down_payment_amount': float(down_payment_amount),
                    'financed_amount': float(financed_amount),
                    'term_months': term_months,
                    'payment_frequency': payment_frequency,
                    'payment_frequency_display': dict(PaymentFrequency.FREQUENCY_CHOICES).get(payment_frequency, payment_frequency),
                    'number_of_payments': number_of_payments,
                    'payment_amount': float(payment_amount),
                    'total_interest': 0,  # Sin intereses
                    'total_amount': float(product_price)
                }
            }
            
            return Response(calculation)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CalculatorConfigurationView(APIView):
    """Vista para obtener la configuración de la calculadora actual"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            # Obtener modalidades activas
            modes = CalculatorMode.objects.filter(is_active=True).order_by('order')
            
            # Obtener productos del catálogo real agrupados por categoría
            categories = []
            for category in Category.objects.all():
                products = Product.objects.filter(
                    category=category,
                    stock__gt=0  # Solo productos con stock
                ).values('id', 'name', 'price', 'description', 'brand')
                
                if products:
                    categories.append({
                        'id': category.id,
                        'name': category.name,
                        'slug': category.slug,
                        'products': list(products)
                    })
            
            # Preparar configuración de modalidades
            modes_config = []
            for mode in modes:
                mode_data = {
                    'id': mode.id,
                    'name': mode.name,
                    'mode_type': mode.mode_type,
                    'description': mode.description,
                    'order': mode.order
                }
                
                if mode.mode_type == 'programada':
                    mode_data.update({
                        'adjudication_percentage': float(mode.adjudication_percentage),
                        'initial_fee_percentage': float(mode.initial_fee_percentage),
                        'min_initial_contribution': float(mode.min_initial_contribution),
                        'max_initial_contribution': float(mode.max_initial_contribution)
                    })
                elif mode.mode_type == 'credito':
                    mode_data.update({
                        'down_payment_options': mode.get_down_payment_options(),
                        'term_options': mode.get_term_options(),
                        'interest_rate': float(mode.interest_rate)
                    })
                
                modes_config.append(mode_data)
            
            return Response({
                'modes': modes_config,
                'categories': categories
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CalculatorCalculateView(APIView):
    """Vista para calcular financiamiento con las modalidades configurables"""
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            # Obtener datos del request
            mode_type = request.data.get('mode_type')  # 'programada' o 'credito'
            product_id = request.data.get('product_id')
            product_price = Decimal(str(request.data.get('product_price', 0)))
            
            # Obtener configuración de la modalidad
            try:
                mode = CalculatorMode.objects.get(mode_type=mode_type, is_active=True)
            except CalculatorMode.DoesNotExist:
                return Response({
                    'error': f'Modalidad {mode_type} no encontrada o inactiva'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Si hay product_id, obtener el producto real
            product_data = None
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    product_data = {
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'brand': product.brand,
                        'category': product.category.name
                    }
                    product_price = product.price
                except Product.DoesNotExist:
                    pass
            
            # Calcular según la modalidad
            if mode_type == 'programada':
                return self._calculate_programada(mode, product_data, product_price, request.data)
            elif mode_type == 'credito':
                return self._calculate_credito(mode, product_data, product_price, request.data)
            else:
                return Response({
                    'error': 'Modalidad no soportada'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _calculate_programada(self, mode, product_data, product_price, data):
        """Calcular modalidad Compra Programada"""
        initial_contribution_percentage = Decimal(str(data.get('initial_contribution_percentage', mode.min_initial_contribution)))
        monthly_payment = Decimal(str(data.get('monthly_payment', 300)))
        punctuality = data.get('punctuality', 'always')
        
        # Validar rango de aporte inicial
        if initial_contribution_percentage < mode.min_initial_contribution or initial_contribution_percentage > mode.max_initial_contribution:
            return Response({
                'error': f'El aporte inicial debe estar entre {mode.min_initial_contribution}% y {mode.max_initial_contribution}%'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calcular valores
        initial_fee = product_price * mode.initial_fee_percentage / 100  # Cuota inicial fija (5%)
        initial_contribution = product_price * initial_contribution_percentage / 100  # Aporte inicial variable
        
        # Monto hasta adjudicación (45% del valor)
        adjudication_amount = product_price * mode.adjudication_percentage / 100
        amount_to_finance = adjudication_amount - initial_fee - initial_contribution
        
        # Calcular meses hasta adjudicación
        if monthly_payment > 0:
            months_to_adjudication = math.ceil(amount_to_finance / monthly_payment)
        else:
            months_to_adjudication = 0
        
        # Monto post-adjudicación (55% restante)
        post_adjudication_amount = product_price - adjudication_amount
        
        # Calcular puntos por puntualidad
        punctuality_points = {
            'always': 3,
            'mostly': 2,
            'sometimes': 1
        }.get(punctuality, 1)
        
        # Reducción de meses por puntos (ejemplo: 1 mes por cada 10 puntos)
        total_points = punctuality_points * months_to_adjudication
        reduced_months = total_points // 10
        final_months = max(1, months_to_adjudication - reduced_months)
        
        # Fechas estimadas
        from datetime import date, timedelta
        try:
            from dateutil.relativedelta import relativedelta
        except ImportError:
            # Fallback si dateutil no está disponible
            def relativedelta(months=0):
                return timedelta(days=months * 30)
        
        today = date.today()
        estimated_adjudication = today + relativedelta(months=months_to_adjudication)
        final_adjudication = today + relativedelta(months=final_months)
        
        return Response({
            'mode': {
                'name': mode.name,
                'type': mode.mode_type
            },
            'product': product_data,
            'calculation': {
                'vehicle_value': float(product_price),
                'initial_fee': float(initial_fee),
                'initial_contribution': float(initial_contribution),
                'amount_to_finance': float(amount_to_finance),
                'monthly_payment': float(monthly_payment),
                'post_adjudication_amount': float(post_adjudication_amount),
                'months_to_adjudication': months_to_adjudication,
                'estimated_adjudication_date': estimated_adjudication.strftime('%d/%m/%Y'),
                'accumulated_points': total_points,
                'reduced_months': reduced_months,
                'final_adjudication_date': final_adjudication.strftime('%d/%m/%Y'),
                'adjudication_percentage': float(mode.adjudication_percentage)
            }
        })
    
    def _calculate_credito(self, mode, product_data, product_price, data):
        """Calcular modalidad Crédito Inmediato"""
        down_payment_percentage = Decimal(str(data.get('down_payment_percentage', 30)))
        term_months = int(data.get('term_months', 12))
        payment_frequency = data.get('payment_frequency', 'monthly')
        
        # Validar que las opciones estén disponibles
        available_down_payments = mode.get_down_payment_options()
        available_terms = mode.get_term_options()
        
        if available_down_payments and float(down_payment_percentage) not in available_down_payments:
            return Response({
                'error': f'Porcentaje de inicial no disponible. Opciones: {available_down_payments}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if available_terms and term_months not in available_terms:
            return Response({
                'error': f'Plazo no disponible. Opciones: {available_terms}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calcular valores
        down_payment_amount = product_price * down_payment_percentage / 100
        financed_amount = product_price - down_payment_amount
        
        # Calcular número de pagos según frecuencia
        if payment_frequency == 'weekly':
            payments_per_month = Decimal('4.33')  # 52 semanas / 12 meses
            number_of_payments = int(term_months * payments_per_month)
            period_rate_divisor = 52  # 52 semanas por año
        elif payment_frequency == 'biweekly':
            payments_per_month = Decimal('2.17')  # 26 quincenas / 12 meses
            number_of_payments = int(term_months * payments_per_month)
            period_rate_divisor = 26  # 26 quincenas por año
        else:  # monthly
            payments_per_month = 1
            number_of_payments = term_months
            period_rate_divisor = 12  # 12 meses por año
        
        # Calcular cuota según frecuencia
        annual_rate = mode.interest_rate / 100
        if annual_rate > 0:
            period_rate = annual_rate / period_rate_divisor
            payment_amount = financed_amount * (
                period_rate * (1 + period_rate) ** number_of_payments
            ) / ((1 + period_rate) ** number_of_payments - 1)
        else:
            payment_amount = financed_amount / number_of_payments
        
        # Calcular totales
        total_payments = payment_amount * number_of_payments
        total_cost = down_payment_amount + total_payments
        total_interest = total_cost - product_price
        
        # Fechas
        from datetime import date, timedelta
        try:
            from dateutil.relativedelta import relativedelta
        except ImportError:
            # Fallback si dateutil no está disponible
            def relativedelta(months=0):
                return timedelta(days=months * 30)
        
        today = date.today()
        
        # Calcular fecha del primer pago según frecuencia
        if payment_frequency == 'weekly':
            first_payment_date = today + timedelta(weeks=1)
        elif payment_frequency == 'biweekly':
            first_payment_date = today + timedelta(weeks=2)
        else:  # monthly
            first_payment_date = today + relativedelta(months=1)
        
        payoff_date = today + relativedelta(months=term_months)
        
        # Nombres de frecuencia para mostrar
        frequency_names = {
            'weekly': 'semanal',
            'biweekly': 'quincenal',
            'monthly': 'mensual'
        }
        
        return Response({
            'mode': {
                'name': mode.name,
                'type': mode.mode_type
            },
            'product': product_data,
            'calculation': {
                'vehicle_value': float(product_price),
                'down_payment_amount': float(down_payment_amount),
                'down_payment_percentage': float(down_payment_percentage),
                'financed_amount': float(financed_amount),
                'term_months': term_months,
                'payment_frequency': payment_frequency,
                'payment_frequency_display': frequency_names.get(payment_frequency, 'mensual'),
                'number_of_payments': number_of_payments,
                'payment_amount': float(payment_amount),
                'monthly_payment': float(payment_amount),  # Para compatibilidad con frontend
                'total_cost': float(total_cost),
                'total_interest': float(total_interest),
                'interest_rate': float(mode.interest_rate),
                'first_payment_date': first_payment_date.strftime('%d/%m/%Y'),
                'payoff_date': payoff_date.strftime('%d/%m/%Y')
            }
        })

# DEBUGGING ENDPOINT - TEMPORAL
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Customer
from django.utils import timezone
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_financing_request(request):
    """
    Endpoint temporal para debugging del problema de solicitudes.
    CERO RIESGO - Solo recolecta información.
    """
    debug_info = {
        'timestamp': str(timezone.now()),
        'user_info': {
            'user_id': request.user.id,
            'username': request.user.username,
            'is_authenticated': request.user.is_authenticated,
            'has_customer_attr': hasattr(request.user, 'customer'),
        },
        'customer_info': {
            'customer_count': Customer.objects.filter(user=request.user).count(),
            'customer_exists': Customer.objects.filter(user=request.user).exists(),
        },
        'request_data': dict(request.data),
        'request_method': request.method,
        'content_type': request.content_type,
    }
    
    # Intentar acceder a customer de diferentes maneras
    try:
        customer_direct = Customer.objects.get(user=request.user)
        debug_info['customer_direct'] = {
            'success': True,
            'customer_id': customer_direct.id,
            'verified': customer_direct.verified,
            'is_profile_complete': customer_direct.is_profile_complete,
        }
    except Customer.DoesNotExist:
        debug_info['customer_direct'] = {
            'success': False,
            'error': 'Customer.DoesNotExist'
        }
    except Exception as e:
        debug_info['customer_direct'] = {
            'success': False,
            'error': str(e)
        }
    
    # Intentar el método problemático
    try:
        customer_property = request.user.customer
        debug_info['customer_property'] = {
            'success': True,
            'result': str(customer_property)
        }
    except Exception as e:
        debug_info['customer_property'] = {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }
    
    return Response({
        'status': 'debug_success',
        'message': 'Información de debugging recolectada',
        'debug_data': debug_info
    }) 