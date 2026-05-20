import json
import boto3
import random
import string
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'parcial3')
BASE_URL = os.environ.get('BASE_URL', '')  # Se llena con el API Gateway URL

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def lambda_handler(event, context):
    # Headers CORS para que el frontend pueda consumir la API
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }

    # Preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        # Parsear el body
        body = json.loads(event.get('body', '{}'))
        original_url = body.get('url', '').strip()

        if not original_url:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'El campo "url" es requerido'})
            }

        # Validacion basica de URL
        if not original_url.startswith(('http://', 'https://')):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'La URL debe comenzar con http:// o https://'})
            }

        table = dynamodb.Table(TABLE_NAME)

        # Generar codigo unico (reintenta si ya existe)
        max_attempts = 5
        short_code = None
        for _ in range(max_attempts):
            candidate = generate_short_code()
            response = table.get_item(Key={'shortCode': candidate})
            if 'Item' not in response:
                short_code = candidate
                break

        if not short_code:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'No se pudo generar un codigo unico, intenta de nuevo'})
            }

        # Guardar en DynamoDB
        item = {
            'shortCode': short_code,
            'originalUrl': original_url,
            'createdAt': datetime.utcnow().isoformat(),
            'visits': 0,
            'visitDates': []
        }
        table.put_item(Item=item)

        # Construir URL corta
        short_url = f"{BASE_URL}/{short_code}" if BASE_URL else short_code

        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({
                'shortCode': short_code,
                'shortUrl': short_url,
                'originalUrl': original_url,
                'createdAt': item['createdAt']
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Error interno del servidor'})
        }