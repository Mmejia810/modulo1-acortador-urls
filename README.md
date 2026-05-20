# Módulo 1 — Servicio de Acortamiento de URLs

## ¿Qué hace?
Recibe una URL larga y devuelve una URL corta con un código de 6 caracteres.
También **crea la tabla DynamoDB `parcial3`** que usan todos los módulos del grupo.

## Endpoint

```
POST /shorten
Content-Type: application/json

Body:
{
  "url": "https://www.google.com"
}

Response 201:
{
  "shortCode": "aB3xYz",
  "shortUrl": "https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/aB3xYz",
  "originalUrl": "https://www.google.com",
  "createdAt": "2025-05-20T03:00:00"
}
```

## Deploy

```bash
# 1. Inicializar Terraform
terraform init

# 2. Ver qué va a crear
terraform plan

# 3. Desplegar
terraform apply

# 4. Ver outputs (URLs importantes para el grupo)
terraform output
```

## Outputs importantes para compartir con el grupo

Después del `terraform apply`, ejecuta `terraform output` y comparte:
- `dynamodb_table_arn` → lo necesitan M2 y M3 para sus políticas IAM
- `endpoint_acortar` → lo necesita M5 (frontend acortador)

## Estructura de archivos

```
modulo1/
├── lambda/
│   └── handler.py       # Lógica de la función
├── main.tf              # Infraestructura (DynamoDB, Lambda, API Gateway, IAM)
├── variables.tf         # Variables configurables
├── outputs.tf           # Valores de salida
└── README.md
```
