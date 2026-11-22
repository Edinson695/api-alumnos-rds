import boto3
import pymysql
import os

def lambda_handler(event, context):
    SSM_host = os.environ['DB_HOST']
    user = os.environ['DB_USER']
    Secret_password = os.environ['DB_PASSWORD']
    database = os.environ['DB_NAME']

    # 1. Recuperar el host desde Parameter Store (SSM)
    ssm = boto3.client('ssm')
    response_host = ssm.get_parameter(
        Name=SSM_host,
        WithDecryption=True
    )
    host = response_host['Parameter']['Value']

    # 2. Recuperar el password desde Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    response_pass = secrets_client.get_secret_value(
        SecretId=Secret_password
    )
    password = response_pass['SecretString']

    connection = None
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alumnos;")
            results = cursor.fetchall()

        return {
            "statusCode": 200,
            "body": results
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }

    finally:
        if connection:
            connection.close()
