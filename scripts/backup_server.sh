#!/bin/bash

# Script para realizar backups completos del servidor LlévateloExpress
# Incluye archivos web y base de datos PostgreSQL
# Mantiene los últimos 10 días de backups

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

# Configuración
SERVER_USER="root"
SERVER_IP="203.161.55.87"
SERVER_PATH="/var/www/llevateloexpress"
BACKUP_PATH="/var/backups/llevateloexpress"
DB_NAME="llevateloexpress"
DB_USER="llevateloexpress_user"
DB_PASSWORD="llevateloexpress_pass"  # Password para la DB
MAX_BACKUPS=10  # Número de backups diarios a mantener
SSH_OPTIONS="-o StrictHostKeyChecking=no"

# Fecha actual para el nombre del backup
DATE=$(date +"%Y%m%d")

# Mostrar ayuda
show_usage() {
    echo -e "Uso: $0 [opción]"
    echo -e "Opciones:"
    echo -e "  --remote\t\tEjecutar backup en el servidor remoto (recomendado)"
    echo -e "  --local\t\tDescargar backup al entorno local"
    echo -e "  --status\t\tVer el estado de los backups"
    echo -e "  --restore FECHA\tRestaurar un backup específico (formato: YYYYMMDD)"
    echo -e "  --setup-cron\t\tConfigurar backup automático diario"
    echo -e "  --help\t\tMostrar esta ayuda"
}

# Función para ejecutar el backup en el servidor remoto
remote_backup() {
    echo -e "${YELLOW}Ejecutando backup completo en el servidor remoto...${NC}"
    
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        # Crear directorio de backups si no existe
        mkdir -p $BACKUP_PATH
        
        # Crear directorio para el backup del día actual
        BACKUP_DIR="$BACKUP_PATH/backup_$DATE"
        mkdir -p \$BACKUP_DIR
        
        echo -e "${YELLOW}Realizando backup de archivos web...${NC}"
        # Backup de archivos del sitio web
        tar -czf \$BACKUP_DIR/web_files_$DATE.tar.gz -C $(dirname $SERVER_PATH) $(basename $SERVER_PATH)
        
        echo -e "${YELLOW}Realizando backup de la base de datos PostgreSQL...${NC}"
        # Backup de la base de datos PostgreSQL usando PGPASSWORD para autenticación no interactiva
        export PGPASSWORD="$DB_PASSWORD"
        pg_dump -h localhost -U $DB_USER $DB_NAME > \$BACKUP_DIR/db_$DATE.sql
        unset PGPASSWORD
        
        # Comprimir el dump de la base de datos
        gzip \$BACKUP_DIR/db_$DATE.sql
        
        echo -e "${YELLOW}Ajustando permisos...${NC}"
        # Ajustar permisos
        chmod 600 \$BACKUP_DIR/*.gz
        
        echo -e "${YELLOW}Eliminando backups antiguos...${NC}"
        # Mantener solo los últimos MAX_BACKUPS backups
        ls -t $BACKUP_PATH | grep 'backup_' | tail -n +$(($MAX_BACKUPS + 1)) | xargs -I {} rm -rf $BACKUP_PATH/{}
        
        echo -e "${GREEN}Backup completado: \$BACKUP_DIR${NC}"
        echo -e "${YELLOW}Listado de backups disponibles:${NC}"
        du -sh $BACKUP_PATH/backup_* 2>/dev/null || echo "No hay backups disponibles todavía"
EOF
}

# Función para descargar el backup más reciente al entorno local
local_backup() {
    echo -e "${YELLOW}Descargando el backup más reciente al entorno local...${NC}"
    
    # Crear directorio local para backups
    LOCAL_BACKUP_DIR="./backups"
    mkdir -p $LOCAL_BACKUP_DIR
    
    # Obtener el directorio de backup más reciente en el servidor
    LATEST_BACKUP=$(ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP "ls -t $BACKUP_PATH | grep 'backup_' | head -1")
    
    if [ -z "$LATEST_BACKUP" ]; then
        echo -e "${RED}No se encontraron backups en el servidor.${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Descargando el backup: $LATEST_BACKUP${NC}"
    # Descargar los archivos de backup
    scp $SSH_OPTIONS -r $SERVER_USER@$SERVER_IP:$BACKUP_PATH/$LATEST_BACKUP $LOCAL_BACKUP_DIR/
    
    echo -e "${GREEN}Backup descargado: $LOCAL_BACKUP_DIR/$LATEST_BACKUP${NC}"
    du -sh $LOCAL_BACKUP_DIR/$LATEST_BACKUP
}

# Función para ver el estado de los backups
backup_status() {
    echo -e "${YELLOW}Verificando estado de los backups en el servidor...${NC}"
    
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        echo -e "${YELLOW}Backups disponibles:${NC}"
        if [ -d "$BACKUP_PATH" ]; then
            if [ -n "\$(ls -A $BACKUP_PATH 2>/dev/null)" ]; then
                echo -e "Espacio total utilizado por backups:"
                du -sh $BACKUP_PATH
                
                echo -e "\nListado de backups (del más reciente al más antiguo):"
                ls -lt $BACKUP_PATH | grep 'backup_' | awk '{print \$9, \$6, \$7, \$8}'
                
                echo -e "\nTamaño de cada backup:"
                for backup in \$(ls -t $BACKUP_PATH | grep 'backup_'); do
                    echo -n "\$backup: "
                    du -sh "$BACKUP_PATH/\$backup"
                done
            else
                echo -e "${YELLOW}El directorio de backups existe pero está vacío.${NC}"
            fi
        else
            echo -e "${RED}No se encontró el directorio de backups.${NC}"
        fi
EOF
}

# Función para restaurar un backup específico
restore_backup() {
    RESTORE_DATE=$1
    
    if [ -z "$RESTORE_DATE" ]; then
        echo -e "${RED}Debe especificar una fecha para restaurar (formato: YYYYMMDD).${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Restaurando backup del $RESTORE_DATE...${NC}"
    
    # Preguntar al usuario para confirmar
    read -p "¿Está seguro de que desea restaurar el backup del $RESTORE_DATE? Esto sobrescribirá los datos actuales. (s/n): " CONFIRM
    if [[ "$CONFIRM" != "s" && "$CONFIRM" != "S" ]]; then
        echo -e "Operación cancelada."
        exit 0
    fi
    
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        BACKUP_DIR="$BACKUP_PATH/backup_$RESTORE_DATE"
        
        if [ ! -d "\$BACKUP_DIR" ]; then
            echo -e "${RED}No se encontró el backup para la fecha $RESTORE_DATE.${NC}"
            exit 1
        fi
        
        # Detener servicios
        echo -e "${YELLOW}Deteniendo servicios...${NC}"
        systemctl stop llevateloexpress
        systemctl stop nginx
        
        # Restaurar archivos
        echo -e "${YELLOW}Restaurando archivos web...${NC}"
        rm -rf $SERVER_PATH.bak
        mv $SERVER_PATH $SERVER_PATH.bak  # Backup de seguridad antes de restaurar
        mkdir -p $(dirname $SERVER_PATH)
        tar -xzf \$BACKUP_DIR/web_files_$RESTORE_DATE.tar.gz -C $(dirname $SERVER_PATH)
        
        # Restaurar base de datos
        echo -e "${YELLOW}Restaurando base de datos...${NC}"
        gunzip -c \$BACKUP_DIR/db_$RESTORE_DATE.sql.gz > /tmp/restore_db.sql
        
        # Usar PGPASSWORD para autenticación no interactiva
        export PGPASSWORD="$DB_PASSWORD"
        psql -h localhost -U $DB_USER -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" $DB_NAME
        psql -h localhost -U $DB_USER -d $DB_NAME -f /tmp/restore_db.sql
        unset PGPASSWORD
        
        rm /tmp/restore_db.sql
        
        # Ajustar permisos
        echo -e "${YELLOW}Ajustando permisos...${NC}"
        chown -R llevateloexpress:www-data $SERVER_PATH
        chmod -R 755 $SERVER_PATH
        
        # Reiniciar servicios
        echo -e "${YELLOW}Iniciando servicios...${NC}"
        systemctl start llevateloexpress
        systemctl start nginx
        
        echo -e "${GREEN}Restauración completada exitosamente.${NC}"
EOF
}

# Configurar cron para backups diarios automáticos
setup_cron() {
    echo -e "${YELLOW}Configurando cron para backups diarios automáticos...${NC}"
    
    ssh $SSH_OPTIONS $SERVER_USER@$SERVER_IP << EOF
        # Crear directorio de scripts si no existe
        mkdir -p /root/scripts
        
        # Crear el script de backup
        cat > /root/scripts/daily_backup.sh << 'EOFSCRIPT'
#!/bin/bash
# Backup diario automático de LlévateloExpress
DATE=\$(date +"%Y%m%d")
BACKUP_PATH="$BACKUP_PATH"
SERVER_PATH="$SERVER_PATH"
DB_NAME="$DB_NAME"
DB_USER="$DB_USER"
DB_PASSWORD="$DB_PASSWORD"
MAX_BACKUPS=$MAX_BACKUPS

# Crear directorio de backups si no existe
mkdir -p \$BACKUP_PATH

# Crear directorio para el backup del día actual
BACKUP_DIR="\$BACKUP_PATH/backup_\$DATE"
mkdir -p \$BACKUP_DIR

# Backup de archivos del sitio web
tar -czf \$BACKUP_DIR/web_files_\$DATE.tar.gz -C \$(dirname \$SERVER_PATH) \$(basename \$SERVER_PATH)

# Backup de la base de datos PostgreSQL usando PGPASSWORD para autenticación no interactiva
export PGPASSWORD="\$DB_PASSWORD"
pg_dump -h localhost -U \$DB_USER \$DB_NAME > \$BACKUP_DIR/db_\$DATE.sql
unset PGPASSWORD

# Comprimir dump
gzip \$BACKUP_DIR/db_\$DATE.sql

# Ajustar permisos
chmod 600 \$BACKUP_DIR/*.gz

# Mantener solo los últimos MAX_BACKUPS backups
ls -t \$BACKUP_PATH | grep 'backup_' | tail -n +\$((\$MAX_BACKUPS + 1)) | xargs -I {} rm -rf \$BACKUP_PATH/{}

# Registrar la finalización
echo "Backup completo realizado el \$(date)" >> /var/log/llevateloexpress/backup.log
EOFSCRIPT
        
        # Hacer el script ejecutable
        chmod +x /root/scripts/daily_backup.sh
        
        # Añadir tarea cron para ejecutar el backup todos los días a las 2:00 AM
        (crontab -l 2>/dev/null || echo "") | grep -v "daily_backup.sh" | { cat; echo "0 2 * * * /root/scripts/daily_backup.sh"; } | crontab -
        
        # Crear directorio de logs si no existe
        mkdir -p /var/log/llevateloexpress
        
        echo -e "${GREEN}Configuración de cron completada. Backup automático programado para ejecutarse todos los días a las 2:00 AM.${NC}"
EOF
}

# Procesar argumentos
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

case "$1" in
    --remote)
        remote_backup
        ;;
    --local)
        local_backup
        ;;
    --status)
        backup_status
        ;;
    --restore)
        if [ -z "$2" ]; then
            echo -e "${RED}Debe especificar una fecha para restaurar (formato: YYYYMMDD).${NC}"
            exit 1
        fi
        restore_backup "$2"
        ;;
    --setup-cron)
        setup_cron
        ;;
    --help)
        show_usage
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

exit 0 