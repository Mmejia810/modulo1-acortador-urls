terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.31.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "2.4.2"
    }
  }
  required_version = ">= 1.6.0"
}

provider "aws" {
  region = var.aws_region
}

# ─────────────────────────────────────────
# DynamoDB — tabla compartida con todos los módulos
# SOLO este módulo la crea; los demás la usan por nombre
# ─────────────────────────────────────────
resource "aws_dynamodb_table" "urls" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "shortCode"

  attribute {
    name = "shortCode"
    type = "S"
  }

  tags = {
    Project = "parcial3"
    Module  = "modulo1"
  }
}

# ─────────────────────────────────────────
# IAM Role para la Lambda
# ─────────────────────────────────────────
resource "aws_iam_role" "lambda_role" {
  name = "${var.lambda_function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_dynamodb_policy" {
  name = "${var.lambda_function_name}-dynamo-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem"
        ]
        Resource = aws_dynamodb_table.urls.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# ─────────────────────────────────────────
# Empaquetar el código Lambda en zip
# ─────────────────────────────────────────
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda_function.zip"
}

# ─────────────────────────────────────────
# Lambda Function
# ─────────────────────────────────────────
resource "aws_lambda_function" "acortador" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 10

  environment {
    variables = {
      TABLE_NAME = var.table_name
      BASE_URL   = "https://${aws_apigatewayv2_api.http_api.id}.execute-api.${var.aws_region}.amazonaws.com"
    }
  }

  depends_on = [aws_iam_role_policy.lambda_dynamodb_policy]
}

# ─────────────────────────────────────────
# API Gateway v2 — HTTP API (más rápido y simple que REST API)
# ─────────────────────────────────────────
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.lambda_function_name}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["Content-Type"]
  }
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.acortador.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "post_shorten" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /shorten"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# Permiso para que API Gateway invoque la Lambda
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.acortador.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
