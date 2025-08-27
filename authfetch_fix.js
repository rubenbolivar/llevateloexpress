        async authFetch(url, options = {}) {
            const token = localStorage.getItem('access_token');
            if (\!token) return { error: true, message: 'No autenticado' };
            
            // Preparar headers base
            const headers = {
                ...options.headers,
                'Authorization': 'Bearer ' + token
            };
            
            // Solo agregar Content-Type si no es FormData
            if (\!(options.body instanceof FormData)) {
                headers['Content-Type'] = 'application/json';
            }
            
            const authOptions = {
                ...options,
                headers
            };
            
            try {
                let response = await fetch(url, authOptions);
                
                // Si el token expiró, intentar refrescarlo
