    @action(detail=True, methods=['post'])
    @transaction.atomic
    def upload_documents(self, request, pk=None):
        """Subir documentos requeridos"""
        application = self.get_object()
        
        # NUEVO: Manejar estado draft con lógica completa de submit
        if application.status == 'draft':
            # Aplicar todas las validaciones de submit()
            if not application.customer.is_profile_complete:
                return Response(
                    {'error': 'Debe completar su perfil antes de enviar la solicitud'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que se están subiendo documentos realmente
            if not any(key in request.FILES for key in ['income_proof', 'id_document', 'address_proof']):
                return Response(
                    {'error': 'Debe subir al menos un documento para enviar la solicitud'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cambiar estado usando la misma lógica de submit()
            old_status = application.status
            application.status = 'submitted'
            application.submitted_at = timezone.now()
            
            # Registrar cambio de estado
            ApplicationStatusHistory.objects.create(
                application=application,
                from_status=old_status,
                to_status='submitted',
                changed_by=request.user,
                notes='Solicitud enviada automáticamente al subir documentos'
            )
            
            # Crear notificación
            EmailNotification.objects.create(
                user=request.user,
                notification_type='application_submitted',
                subject='Solicitud Enviada',
                message=f'Su solicitud {application.application_number} ha sido enviada para revisión con documentos.',
                context={'application_number': application.application_number}
            )
            
        elif application.status not in ['submitted', 'documentation_required']:
            return Response(
                {'error': 'No se pueden subir documentos en este estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar documentos (lógica original)
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
