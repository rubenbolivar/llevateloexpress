from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.services import notification_service
import logging

logger = logging.getLogger('notifications')


class Command(BaseCommand):
    help = 'Procesa la cola de emails pendientes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Cantidad de emails a procesar en cada lote (default: 10)'
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Ejecutar en modo continuo (procesar indefinidamente)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Intervalo en segundos entre procesamiento en modo continuo (default: 60)'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        continuous = options['continuous']
        interval = options['interval']
        
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando procesamiento de cola de emails...')
        )
        
        if continuous:
            self.stdout.write(
                self.style.WARNING(f'Modo continuo activado. Intervalo: {interval}s')
            )
            self.process_continuously(batch_size, interval)
        else:
            self.process_once(batch_size)
    
    def process_once(self, batch_size):
        """Procesa la cola una sola vez"""
        start_time = timezone.now()
        
        try:
            processed_count = notification_service.process_email_queue(batch_size)
            
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            if processed_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Procesados {processed_count} emails en {duration:.2f} segundos'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No hay emails pendientes en la cola')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error procesando cola: {str(e)}')
            )
            logger.error(f'Error en command process_email_queue: {str(e)}')
    
    def process_continuously(self, batch_size, interval):
        """Procesa la cola continuamente"""
        import time
        
        try:
            while True:
                self.process_once(batch_size)
                self.stdout.write(f'Esperando {interval} segundos...')
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\nProcesamiento interrumpido por el usuario')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error en modo continuo: {str(e)}')
            )
            logger.error(f'Error en modo continuo: {str(e)}') 