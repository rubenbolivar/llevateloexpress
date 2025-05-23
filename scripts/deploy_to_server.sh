#!/bin/bash
# Script para automatizar el despliegue y la ejecución de comandos en el servidor remoto

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

# Configuración
SERVER_USER="root"
SERVER_IP="203.161.55.87"
SERVER_PATH="/var/www/llevateloexpress"
SSH_OPTIONS="-o StrictHostKeyChecking=no"

# Función para mostrar el uso del script
show_usage() {
    echo -e "Uso: $0 [opción]"
    echo -e "Opciones:"
    echo -e "  --sync-code\t\tSincronizar código con el servidor"
    echo -e "  --sync-from-server\tSincronizar archivos desde el servidor hacia el entorno local"
    echo -e "  --verify-local\t\tVerificar integridad de los archivos locales antes del despliegue"
    echo -e "  --verify-remote\t\tVerificar integridad del sitio web después del despliegue"
    echo -e "  --update-deps\t\tActualizar dependencias en el servidor"
    echo -e "  --migrate\t\tEjecutar migraciones en el servidor"
    echo -e "  --collect-static\tRecolectar archivos estáticos"
    echo -e "  --restart-server\tReiniciar servicios en el servidor"
    echo -e "  --fix-db\t\tCorregir configuración de la base de datos"
    echo -e "  --check-status\tVerificar estado de los servicios"
    echo -e "  --execute \"comando\"\tEjecutar un comando personalizado en el servidor"
    echo -e "  --shell\t\tAbrir una shell interactiva en el servidor"
    echo -e "  --full-deploy\t\tEjecutar un despliegue completo (sync + deps + migrate + static + restart)"
    echo -e "  --safe-deploy\t\tEjecutar un despliegue con verificaciones de integridad (verify + sync + restart + verify)"
}

# Función para sincronizar el código con el servidor
sync_code() {
    echo -e "${YELLOW}Sincronizando código con el servidor...${NC}"
    # Crear un archivo tar para la transferencia
    tar -czf deploy_tmp.tar.gz \
        --exclude="backend_env" \
        --exclude=".git" \
        --exclude="node_modules" \
        --exclude="*.pyc" \
        --exclude="__pycache__" \
        --exclude="staticfiles" \
        --exclude="media" \
        --exclude="deploy_tmp.tar.gz" \
        .
    
    # Transferir el archivo al servidor
    scp $SSH_OPTIONS deploy_tmp.tar.gz $SERVER_USER@$SERVER_IP:/tmp/
    
    # Extraer el archivo en el servidor
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        echo -e "${YELLOW}Extrayendo archivos en el servidor...${NC}"
        mkdir -p $SERVER_PATH
        tar -xzf /tmp/deploy_tmp.tar.gz -C $SERVER_PATH
        rm /tmp/deploy_tmp.tar.gz
        echo -e "${GREEN}Código sincronizado correctamente.${NC}"
EOF
    
    # Limpiar archivo temporal local
    rm deploy_tmp.tar.gz
    echo -e "${GREEN}Sincronización completada.${NC}"
}

# Función para actualizar dependencias en el servidor
update_dependencies() {
    echo -e "${YELLOW}Actualizando dependencias en el servidor...${NC}"
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        cd $SERVER_PATH
        source backend_env/bin/activate || python3 -m venv backend_env && source backend_env/bin/activate
        pip install -r requirements.txt
        pip install gunicorn gevent
        echo -e "${GREEN}Dependencias actualizadas correctamente.${NC}"
EOF
}

# Función para ejecutar migraciones en el servidor
run_migrations() {
    echo -e "${YELLOW}Ejecutando migraciones en el servidor...${NC}"
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        cd $SERVER_PATH
        source backend_env/bin/activate
        python manage.py migrate
        echo -e "${GREEN}Migraciones ejecutadas correctamente.${NC}"
EOF
}

# Función para recolectar archivos estáticos
collect_static() {
    echo -e "${YELLOW}Recolectando archivos estáticos en el servidor...${NC}"
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        cd $SERVER_PATH
        source backend_env/bin/activate
        python manage.py collectstatic --noinput
        echo -e "${GREEN}Archivos estáticos recolectados correctamente.${NC}"
EOF
}

# Función para reiniciar servicios en el servidor
restart_services() {
    echo -e "${YELLOW}Reiniciando servicios en el servidor...${NC}"
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        # Asegurarse de que los directorios tienen los permisos correctos
        chown -R llevateloexpress:www-data $SERVER_PATH || echo "No existe el usuario 'llevateloexpress', usando 'www-data'"
        chown -R www-data:www-data $SERVER_PATH/staticfiles $SERVER_PATH/media
        chmod -R 755 $SERVER_PATH
        
        # Reiniciar servicios
        systemctl daemon-reload
        systemctl restart llevateloexpress || echo "El servicio llevateloexpress no está disponible"
        systemctl restart nginx || echo "El servicio nginx no está disponible"
        echo -e "${GREEN}Servicios reiniciados correctamente.${NC}"
EOF
}

# Función para corregir la configuración de la base de datos
fix_database() {
    echo -e "${YELLOW}Corrigiendo configuración de la base de datos en el servidor...${NC}"
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
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
        cd $SERVER_PATH
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
}

# Función para verificar el estado de los servicios
check_status() {
    echo -e "${YELLOW}Verificando el estado de los servicios en el servidor...${NC}"
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        echo -e "\n${YELLOW}===== Estado de PostgreSQL =====${NC}"
        systemctl status postgresql --no-pager
        
        echo -e "\n${YELLOW}===== Estado de Nginx =====${NC}"
        systemctl status nginx --no-pager
        
        echo -e "\n${YELLOW}===== Estado del Servicio de Django =====${NC}"
        systemctl status llevateloexpress --no-pager || echo "El servicio llevateloexpress no está configurado aún"
        
        echo -e "\n${YELLOW}===== Verificación de puertos =====${NC}"
        echo "Verificando el puerto 80 (HTTP):"
        ss -tulpn | grep ":80" || echo "Ningún servicio en el puerto 80"
        
        echo -e "\nVerificando el puerto 443 (HTTPS):"
        ss -tulpn | grep ":443" || echo "Ningún servicio en el puerto 443"
        
        echo -e "\nVerificando el puerto 5432 (PostgreSQL):"
        ss -tulpn | grep ":5432" || echo "PostgreSQL no está escuchando en el puerto 5432"
        
        echo -e "\n${YELLOW}===== Espacio en disco =====${NC}"
        df -h
        
        echo -e "\n${YELLOW}===== Memoria disponible =====${NC}"
        free -h
        
        echo -e "\n${YELLOW}===== Directorio de la aplicación =====${NC}"
        ls -la $SERVER_PATH
        
        echo -e "\n${YELLOW}===== Verificación de Nginx =====${NC}"
        nginx -t
        
        echo -e "\n${YELLOW}===== Logs de errores de Nginx =====${NC}"
        tail -n 20 /var/log/nginx/error.log || echo "No hay archivo de logs de error"
        
        echo -e "\n${YELLOW}===== Logs de errores de Django =====${NC}"
        tail -n 20 $SERVER_PATH/logs/error.log || echo "No hay archivo de logs de error para Django"
EOF
}

# Función para ejecutar un comando personalizado en el servidor
execute_command() {
    local command=$1
    echo -e "${YELLOW}Ejecutando comando en el servidor: ${command}${NC}"
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP "${command}"
}

# Función para abrir una shell interactiva en el servidor
open_shell() {
    echo -e "${YELLOW}Abriendo shell interactiva en el servidor...${NC}"
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP
}

# Función para ejecutar un despliegue completo
full_deploy() {
    sync_code
    update_dependencies
    fix_database
    run_migrations
    collect_static
    restart_services
    check_status
}

# Función para verificar integridad local
verify_local_integrity() {
    echo -e "${YELLOW}Verificando integridad de archivos locales...${NC}"
    if [ -f "./scripts/verificar_integridad.sh" ]; then
        chmod +x ./scripts/verificar_integridad.sh
        ./scripts/verificar_integridad.sh
        RESULT=$?
        if [ $RESULT -ne 0 ]; then
            echo -e "${RED}La verificación de integridad local falló. Abortando despliegue.${NC}"
            exit 1
        else
            echo -e "${GREEN}Verificación de integridad local exitosa.${NC}"
        fi
    else
        echo -e "${RED}No se encontró el script de verificación. Crea scripts/verificar_integridad.sh primero.${NC}"
        exit 1
    fi
}

# Función para verificar integridad remota
verify_remote_integrity() {
    echo -e "${YELLOW}Verificando integridad del sitio web después del despliegue...${NC}"
    if [ -f "./scripts/verificar_despliegue.sh" ]; then
        chmod +x ./scripts/verificar_despliegue.sh
        ./scripts/verificar_despliegue.sh
        RESULT=$?
        if [ $RESULT -ne 0 ]; then
            echo -e "${RED}La verificación post-despliegue falló. Revisa los errores reportados.${NC}"
            return 1
        else
            echo -e "${GREEN}Verificación post-despliegue exitosa.${NC}"
            return 0
        fi
    else
        echo -e "${RED}No se encontró el script de verificación. Crea scripts/verificar_despliegue.sh primero.${NC}"
        return 1
    fi
}

# Función para sincronizar desde el servidor
sync_from_server() {
    echo -e "${YELLOW}Sincronizando archivos desde el servidor hacia el entorno local...${NC}"
    if [ -f "./scripts/sync_from_server.sh" ]; then
        chmod +x ./scripts/sync_from_server.sh
        ./scripts/sync_from_server.sh
        RESULT=$?
        if [ $RESULT -ne 0 ]; then
            echo -e "${RED}La sincronización desde el servidor falló.${NC}"
            exit 1
        else
            echo -e "${GREEN}Sincronización desde el servidor completada.${NC}"
        fi
    else
        echo -e "${RED}No se encontró el script de sincronización. Crea scripts/sync_from_server.sh primero.${NC}"
        exit 1
    fi
}

# Función para ejecutar un despliegue seguro
safe_deploy() {
    echo -e "${YELLOW}Iniciando despliegue seguro con verificaciones...${NC}"
    
    # Paso 1: Verificar integridad local
    verify_local_integrity
    
    # Paso 2: Sincronizar código
    sync_code
    
    # Paso 3: Reiniciar servicios
    restart_services
    
    # Paso 4: Verificar integridad remota
    verify_remote_integrity
    RESULT=$?
    
    if [ $RESULT -eq 0 ]; then
        echo -e "${GREEN}¡Despliegue seguro completado con éxito!${NC}"
    else
        echo -e "${RED}El despliegue presenta algunos problemas. Revisa los errores reportados.${NC}"
    fi
}

# Verificar si se proporcionaron argumentos
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Procesar argumentos
case "$1" in
    --sync-code)
        sync_code
        ;;
    --sync-from-server)
        sync_from_server
        ;;
    --verify-local)
        verify_local_integrity
        ;;
    --verify-remote)
        verify_remote_integrity
        ;;
    --update-deps)
        update_dependencies
        ;;
    --migrate)
        run_migrations
        ;;
    --collect-static)
        collect_static
        ;;
    --restart-server)
        restart_services
        ;;
    --fix-db)
        fix_database
        ;;
    --check-status)
        check_status
        ;;
    --execute)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Debes proporcionar un comando para ejecutar.${NC}"
            exit 1
        fi
        execute_command "$2"
        ;;
    --shell)
        open_shell
        ;;
    --full-deploy)
        full_deploy
        ;;
    --safe-deploy)
        safe_deploy
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

exit 0 