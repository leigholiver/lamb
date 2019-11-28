# this file is managed by lamb, run
# './lambctl make terraform' to regenerate it
# any changes to this file will be lost
# changes can be made in util/templater/templates/main.tf.j2

terraform {
  backend "local" {
    path = "./.tfdata/terraform.tfstate"
  }
}

variable "cloudflare_email" {}
variable "cloudflare_apikey" {}
variable "cloudflare_zone" {}
variable "cloudflare_account_id" {}
variable "aws_account_id" {}
variable "domain_name" {}
variable "static_domain_name" {}
variable "api_path" {}
variable "region" {}
variable "log_retention_days" {}
variable "jwt_secret" {}

provider "cloudflare" {
  email   = "${var.cloudflare_email}"
  api_key   = "${var.cloudflare_apikey}"
  account_id = "${var.cloudflare_account_id}"
}

# aws lambda json api
module "api" {
  source = "./deploy/api"
  cloudflare_zone = "${var.cloudflare_zone}"
  domain_name = "${var.domain_name}"
  api_path = "${var.api_path}"
  region = "${var.region}"
  log_retention_days = "${var.log_retention_days}"
  jwt_secret = "${var.jwt_secret}"
  lambda_name = replace("lamb_${var.domain_name}", ".", "_")
}

# dynamodb models
module "db" {
  source = "./deploy/db"
  region = "${var.region}"
  aws_account_id = "${var.aws_account_id}"
  domain_name = "${var.domain_name}"
  role = "${module.api.role}"
}

# public s3 bucket with cloudflare naming
module "static" {
  source = "./deploy/static"
  static_domain_name = "${var.static_domain_name}"
  cloudflare_zone = "${var.cloudflare_zone}"
}

# s3 backed single page site
module "public" {
  source = "./deploy/public"
  domain_name = "${var.domain_name}"
  cloudflare_zone = "${var.cloudflare_zone}"
}