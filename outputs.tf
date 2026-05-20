output "api_url" {
  description = "URL base del API — comparte con el grupo para Módulo 5"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "endpoint_acortar" {
  description = "Endpoint POST para acortar URLs"
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}/shorten"
}

output "dynamodb_table_name" {
  description = "Nombre de la tabla DynamoDB — comparte con TODO el grupo"
  value       = aws_dynamodb_table.urls.name
}

output "dynamodb_table_arn" {
  description = "ARN de la tabla DynamoDB — los otros módulos lo necesitan para IAM"
  value       = aws_dynamodb_table.urls.arn
}

output "lambda_function_name" {
  description = "Nombre de la funcion Lambda"
  value       = aws_lambda_function.acortador.function_name
}
