from django.core.management.base import BaseCommand
from django.utils import timezone
from financing.models import FinancingRequest, PaymentSchedule

class Command(BaseCommand):
    help = 'Genera cronogramas de pago para solicitudes aprobadas que no los tengan'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerar cronogramas existentes',
        )
        parser.add_argument(
            '--application-id',
            type=int,
            help='Generar cronograma solo para una solicitud específica',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando generación de cronogramas de pago...')
        )

        # Filtrar solicitudes aprobadas
        queryset = FinancingRequest.objects.filter(status='approved')
        
        if options['application_id']:
            queryset = queryset.filter(id=options['application_id'])
            
        total_requests = queryset.count()
        self.stdout.write(f"📋 Encontradas {total_requests} solicitudes aprobadas")
        
        processed = 0
        skipped = 0
        errors = 0
        
        for request in queryset:
            try:
                # Verificar si ya tiene cronograma
                existing_schedule = request.payment_schedule.count()
                
                if existing_schedule > 0 and not options['force']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⏭️  Solicitud {request.application_number} ya tiene cronograma ({existing_schedule} cuotas)"
                        )
                    )
                    skipped += 1
                    continue
                
                # Generar cronograma
                self.stdout.write(f"🔄 Procesando solicitud {request.application_number}...")
                
                # Si force=True, eliminar cronograma existente
                if options['force'] and existing_schedule > 0:
                    request.payment_schedule.all().delete()
                    self.stdout.write(
                        self.style.WARNING(f"🗑️  Eliminado cronograma existente")
                    )
                
                request.calculate_payment_schedule()
                new_schedule_count = request.payment_schedule.count()
                
                if new_schedule_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Generado cronograma para {request.application_number}: "
                            f"{new_schedule_count} cuotas de ${request.payment_amount}"
                        )
                    )
                    processed += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Error: No se generaron cuotas para {request.application_number}"
                        )
                    )
                    errors += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"💥 Error procesando solicitud {request.application_number}: {str(e)}"
                    )
                )
                errors += 1
        
        # Resumen final
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"📊 RESUMEN DE PROCESAMIENTO:"))
        self.stdout.write(f"   📝 Total de solicitudes: {total_requests}")
        self.stdout.write(self.style.SUCCESS(f"   ✅ Procesadas exitosamente: {processed}"))
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f"   ⏭️  Saltadas (ya tenían cronograma): {skipped}"))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"   ❌ Errores: {errors}"))
        
        # Mostrar estadísticas del sistema
        total_schedules = PaymentSchedule.objects.count()
        total_applications = FinancingRequest.objects.count()
        approved_applications = FinancingRequest.objects.filter(status='approved').count()
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"📈 ESTADÍSTICAS DEL SISTEMA:"))
        self.stdout.write(f"   🔢 Total de solicitudes: {total_applications}")
        self.stdout.write(f"   ✅ Solicitudes aprobadas: {approved_applications}")
        self.stdout.write(f"   📅 Total cuotas programadas: {total_schedules}")
        
        if processed > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 ¡Proceso completado! {processed} cronogramas generados correctamente."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  No se generaron nuevos cronogramas."
                )
            ) 