variable "aws_region" {
  description = "Region de AWS"
  type        = string
  default     = "us-east-1"
}

variable "table_name" {
  description = "Nombre de la tabla DynamoDB compartida"
  type        = string
  default     = "parcial3"
}

variable "lambda_function_name" {
  description = "Nombre de la funcion Lambda"
  type        = string
  default     = "modulo1-acortador"
}
