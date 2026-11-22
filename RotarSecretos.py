import boto3
import pymysql
import os
import random
import string

def lambda_handler(event, context):
    host_param = os.environ['DB_HOST']
    user = os.environ['DB_USER']
    secret_name = os.environ['DB_PASSWORD']
    database = os.environ['DB_NAME']
    
    ssm = boto3.client('ssm')
    secrets_client = boto3.client('secretsmanager')

    # 2. Obtener host y contraseña actual
    host = ssm.get_parameter(Name=host_param, WithDecryption=True)['Parameter']['Value']
    current_password = secrets_client.get_secret_value(SecretId=secret_name)['SecretString']

    # 3. Generar nueva contraseña aleatoria (12 caracteres)
    caracteres = string.ascii_letters + string.digits
    new_password = ''.join(random.choice(caracteres) for i in range(12)) + "#1aA"

    connection = None
    try:
        # 4. Conectarse a MySQL con la contraseña actual
        connection = pymysql.connect(host=host, user=user, password=current_password, db=database)
        
        with connection.cursor() as cursor:
            # 5. Actualizar la contraseña en la base de datos
            cursor.execute(f"ALTER USER '{user}'@'%' IDENTIFIED BY '{new_password}';")
            connection.commit()
        
        # 6. Guardar la nueva contraseña en Secrets Manager
        secrets_client.put_secret_value(SecretId=secret_name, SecretString=new_password)
        
        print(f"Contraseña rotada exitosamente para el usuario {user}")
        return {"statusCode": 200, "body": "Rotación exitosa"}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "error": str(e)}

    finally:
        if connection:
            connection.close()
