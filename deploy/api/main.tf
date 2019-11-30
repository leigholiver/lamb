# this file is managed by lamb, any changes to it will be lost
# edit 'main.tf.j2' and run'./lambctl make terraform' to regenerate it

variable "cloudflare_zone" {}
variable "domain_name" {}
variable "api_path" {}
variable "region" {}
variable "source_dir" { default = "./api" }
variable "lambda_zip" { default = "./deploy/api_lambda.zip" }
variable "log_retention_days" {}
variable "jwt_secret" {}
variable "lambda_name" {}

# increase these if you start getting internal server error responses
variable "lambda_memory" { default = 256 } # in mb
variable "lambda_timeout" { default = 4 } # in seconds

# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = "${var.domain_name}_api_endpoints"
}

resource "aws_api_gateway_resource" "endpoint" {
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  parent_id   = "${aws_api_gateway_rest_api.api.root_resource_id}"
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = "${aws_api_gateway_rest_api.api.id}"
  resource_id   = "${aws_api_gateway_resource.endpoint.id}"
  http_method   = "ANY"
  authorization = "NONE"
  request_parameters = {
    "method.request.path.proxy" = true
  }
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.api.id}"
  resource_id             = "${aws_api_gateway_resource.endpoint.id}"
  http_method             = "${aws_api_gateway_method.method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.lambda.invoke_arn}"
  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

# Lambda
data "archive_file" "lambda_zip" {
    type        = "zip"
    source_dir  = "${var.source_dir}"
    output_path = "${var.lambda_zip}"
}

resource "aws_lambda_function" "lambda" {
  filename      = "${var.lambda_zip}"
  function_name = "${var.lambda_name}"
  role          = "${aws_iam_role.role.arn}"
  handler       = "router.lambda_handler"
  runtime       = "python3.7"
  source_code_hash = "${filebase64sha256("${var.lambda_zip}")}"
  memory_size = "${var.lambda_memory}"
  timeout = "${var.lambda_timeout}"
  environment {
    variables = {
      JWT_SECRET = "${var.jwt_secret}"
    }
  }
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda.function_name}"
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/*"
}

resource "aws_api_gateway_deployment" "deployment" {
  depends_on = ["aws_api_gateway_integration.integration"]
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  stage_name  = "${var.api_path}"
}


# Cloudflare forwarding
# Worker rule to use 307 redirects, retaining POST body
resource "cloudflare_worker_route" "cf_route_307" {
  zone_id = "${var.cloudflare_zone}"
  pattern = "${var.domain_name}/${var.api_path}/*"
  script_name = "${cloudflare_worker_script.cf_script_307.name}"
}

resource "cloudflare_worker_script" "cf_script_307" {
  name = "api_redirects_307"
  content = <<EOF
addEventListener('fetch', event => {
  event.respondWith(bulkRedirects(event.request))
})

async function bulkRedirects(request) {
  
  // redirect api requests with a 307 to retain post body 
  if(request.url.startsWith("https://${var.domain_name}/${var.api_path}/") ||
      request.url.startsWith("https://www.${var.domain_name}/${var.api_path}/")) {
    location = request.url.replace("https://${var.domain_name}/", 
      "https://${aws_api_gateway_rest_api.api.id}.execute-api.${var.region}.amazonaws.com/")
    return Response.redirect(location, 307)
  }

  return fetch(request)
}
EOF
}

# IAM lambda role
resource "aws_iam_role" "role" {
  name = "${var.domain_name}_lambda_role"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }    
  ]
}
POLICY
}

# logging
resource "aws_cloudwatch_log_group" "example" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = "${var.log_retention_days}"
}

resource "aws_iam_policy" "lambda_logging" {
  name = "lambda_logging"
  path = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "lambda_logs" {
  name       = "lambda_logs_attachment"
  roles      = ["${aws_iam_role.role.name}"]
  policy_arn = "${aws_iam_policy.lambda_logging.arn}"
}

# output for the role so that the db module can provide access
output "role" {
  value = "${aws_iam_role.role}"
}