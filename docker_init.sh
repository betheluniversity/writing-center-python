#!/bin/sh

appServerProd="wlp-ttr.its.bethel.edu"

# Check if DEV environment set
if [ "${ENVIRON}" = "dev" ]; then

    # Check if SSH Key already present
    if ! [ -f "/root/.ssh/id_rsa" ]; then
        # Check if docker secret present
        if [ -f "/run/secrets/docker_ssh_key" ]; then
            # Set up SSH key
            mkdir -p /root/.ssh
            cp /run/secrets/docker_ssh_key /root/.ssh/id_rsa
            chmod 700 /root/.ssh
            chmod 600 /root/.ssh/id_rsa

            # Check if MYSQL_DATABASE_SERVER is not blank
            if ! [ -z "${MYSQL_DATABASE_SERVER}" ]; then
                ssh-keyscan -t rsa ${appServerProd} >> ~/.ssh/known_hosts
            elif ! [ -z "${DEV_SSH_TUNNEL_SQL_SERVER}" ]; then
                ssh-keyscan -t rsa ${DEV_SSH_TUNNEL_SERVER} >> ~/.ssh/known_hosts
            fi
        fi
    fi

    # For using local mysql server
    # Check if MYSQL_DATABASE_SERVER is not blank
    if ! [ -z "${MYSQL_DATABASE_SERVER}" ]; then
        if ! [ -d "/databases/${MYSQL_DATABASE_NAME}/active" ]; then
            echo "Downloading ${MYSQL_DATABASE_NAME}_prod..."
            sh /get_database.sh -r /srv/flask_app -k "${MYSQL_SSH_USER}" -m prod -d "${MYSQL_DATABASE_NAME}" -o "/databases/${MYSQL_DATABASE_NAME}/import"
        fi

        until [ -d "/databases/${MYSQL_DATABASE_NAME}/active" ]; do
            sleep 10
        done
    else
        # For using SSH Tunnel to connect to mysql server
        # Check if Dev Tunnel Server is not blank
        if ! [ -z "${DEV_SSH_TUNNEL_SQL_SERVER}" ]; then
            # Set up SSH Tunnel to DB
            ssh ${DEV_SSH_TUNNEL_USER}@${DEV_SSH_TUNNEL_SERVER} -L 0.0.0.0:3306:${DEV_SSH_TUNNEL_SQL_SERVER}:${DEV_SSH_TUNNEL_SQL_SERVER_PORT} -fN
        fi
    fi
fi
