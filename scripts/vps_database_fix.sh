#!/bin/bash
# Script para corregir la configuración de la base de datos en el VPS

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

SERVER_USER="root"
SERVER_IP="203.161.55.87"
SSH_OPTS="-o StrictHostKeyChecking=no"

echo -e "${YELLOW}Iniciando corrección de la configuración de la base de datos...${NC}"

# Conectarse al servidor y ejecutar los comandos
ssh $SSH_OPTS $SERVER_USER@$SERVER_IP << EOF
    echo -e "Configurando PostgreSQL..."

    # Reiniciar PostgreSQL
    systemctl restart postgresql

    # Verificar si PostgreSQL está en ejecución
    systemctl status postgresql --no-pager

    # Corregir la autenticación para PostgreSQL
    echo -e "Configurando método de autenticación..."
    su - postgres -c "psql -c \"ALTER USER llevateloexpress_user WITH PASSWORD 'llevateloexpress_pass';\""
    
    # Comprobar si el archivo pg_hba.conf existe
    if [ -f /etc/postgresql/12/main/pg_hba.conf ]; then
        # Hacer una copia de seguridad del archivo original
        cp /etc/postgresql/12/main/pg_hba.conf /etc/postgresql/12/main/pg_hba.conf.bak
        
        # Modificar el método de autenticación
        sed -i 's/local   all             postgres                                peer/local   all             postgres                                md5/g' /etc/postgresql/12/main/pg_hba.conf
        sed -i 's/local   all             all                                     peer/local   all             all                                     md5/g' /etc/postgresql/12/main/pg_hba.conf
        
        # Reiniciar PostgreSQL
        systemctl restart postgresql
        
        echo -e "Configuración de autenticación actualizada."
    else
        echo -e "No se encontró el archivo pg_hba.conf. Es posible que la instalación de PostgreSQL sea diferente."
    fi

    # Verificar la conexión a la base de datos
    echo -e "Verificando conexión a la base de datos..."
    cd /var/www/llevateloexpress
    source backend_env/bin/activate
    python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        dbname='llevateloexpress',
        user='llevateloexpress_user',
        password='llevateloexpress_pass',
        host='localhost'
    )
    print('Conexión exitosa!')
    conn.close()
except Exception as e:
    print(f'Error de conexión: {e}')
"
EOF

echo -e "${GREEN}Script de corrección completado.${NC}"
echo -e "Si la conexión a la base de datos fue exitosa, ahora podrás realizar las migraciones."
echo -e "Si aún hay problemas, verifica los mensajes de error mostrados arriba." 