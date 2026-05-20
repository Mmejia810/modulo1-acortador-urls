import json
import pytest
import sys
import os

# Agregar el directorio lambda al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Variables de entorno para las pruebas
os.environ['TABLE_NAME'] = 'parcial3-test'
os.environ['BASE_URL'] = 'https://test.execute-api.us-east-1.amazonaws.com'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

import boto3
from moto import mock_aws
from handler import lambda_handler, generate_short_code


# ─────────────────────────────────────────
# Fixture: DynamoDB simulada con moto
# ─────────────────────────────────────────
@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='parcial3-test',
            KeySchema=[{'AttributeName': 'shortCode', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'shortCode', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        yield table


# ─────────────────────────────────────────
# Pruebas unitarias
# ─────────────────────────────────────────
def test_generate_short_code_length():
    """El código generado debe tener 6 caracteres"""
    code = generate_short_code()
    assert len(code) == 6


def test_generate_short_code_is_alphanumeric():
    """El código debe ser alfanumérico"""
    code = generate_short_code()
    assert code.isalnum()


def test_generate_short_code_custom_length():
    """El código debe respetar la longitud personalizada"""
    code = generate_short_code(length=10)
    assert len(code) == 10


@mock_aws
def test_shorten_url_success():
    """Acortar una URL válida debe retornar 201 con shortCode"""
    # Crear tabla simulada
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    dynamodb.create_table(
        TableName='parcial3-test',
        KeySchema=[{'AttributeName': 'shortCode', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'shortCode', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    event = {
        'body': json.dumps({'url': 'https://google.com'}),
        'httpMethod': 'POST'
    }

    response = lambda_handler(event, {})
    body = json.loads(response['body'])

    assert response['statusCode'] == 201
    assert 'shortCode' in body
    assert 'shortUrl' in body
    assert body['originalUrl'] == 'https://google.com'
    assert len(body['shortCode']) == 6


@mock_aws
def test_shorten_url_missing_url():
    """Debe retornar 400 si no se envía el campo url"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    dynamodb.create_table(
        TableName='parcial3-test',
        KeySchema=[{'AttributeName': 'shortCode', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'shortCode', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    event = {
        'body': json.dumps({}),
        'httpMethod': 'POST'
    }

    response = lambda_handler(event, {})
    body = json.loads(response['body'])

    assert response['statusCode'] == 400
    assert 'error' in body


@mock_aws
def test_shorten_url_invalid_url():
    """Debe retornar 400 si la URL no comienza con http:// o https://"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    dynamodb.create_table(
        TableName='parcial3-test',
        KeySchema=[{'AttributeName': 'shortCode', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'shortCode', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    event = {
        'body': json.dumps({'url': 'google.com'}),
        'httpMethod': 'POST'
    }

    response = lambda_handler(event, {})
    body = json.loads(response['body'])

    assert response['statusCode'] == 400
    assert 'error' in body


def test_cors_options_preflight():
    """Debe retornar 200 para peticiones OPTIONS (CORS preflight)"""
    event = {'httpMethod': 'OPTIONS'}
    response = lambda_handler(event, {})
    assert response['statusCode'] == 200


def test_cors_headers_present():
    """La respuesta debe incluir headers CORS"""
    event = {'httpMethod': 'OPTIONS'}
    response = lambda_handler(event, {})
    assert 'Access-Control-Allow-Origin' in response['headers']