# this file is managed by lamb, run
# './lambctl make terraform' to regenerate it
# any changes to this file will be lost

variable "aws_account_id" {}
variable "domain_name" {}
variable "region" {}
variable "role" {}

resource "aws_dynamodb_table" "user" {
  name           = "user"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }
  
  attribute {
    name = "username"
    type = "S"
  }
  global_secondary_index {
    name               = "username_index"
    hash_key           = "username"
    projection_type    = "ALL"
  }
  
}

resource "aws_iam_policy" "policy_user" {
  name        = "${var.domain_name}_user_db_policy"
  description = "${var.domain_name} user_db policy"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Sid": "AllAPIActionsOnBooks",
        "Effect": "Allow",
        "Action": "dynamodb:*",
        "Resource": "arn:aws:dynamodb:${var.region}:${var.aws_account_id}:table/user"
    },
    
      {
          "Sid": "AllQueryOnusername",
          "Effect": "Allow",
          "Action": "dynamodb:Query",
          "Resource": "arn:aws:dynamodb:${var.region}:${var.aws_account_id}:table/user/index/username_index"
      }
    
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "attach_user" {
  name       = "user_attachment"
  roles      = ["${var.role.name}"]
  policy_arn = "${aws_iam_policy.policy_user.arn}"
}
