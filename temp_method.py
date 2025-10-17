
    def update_profile_completeness(self):
        """
        Actualiza automáticamente el campo is_profile_complete basado en si todos
        los campos requeridos para financiamiento están completos.
        """
        required_fields_complete = all([
            self.address,  # Dirección
            self.date_of_birth,  # Fecha de nacimiento
            self.occupation,  # Ocupación
            self.monthly_income,  # Ingreso mensual
        ])
        
        # Solo actualizar si el estado cambió
        if self.is_profile_complete != required_fields_complete:
            self.is_profile_complete = required_fields_complete
            self.save(update_fields=['is_profile_complete'])
        
        return self.is_profile_complete
