=====
3. provider.tf
terraform {
required_version = ">= 1.0.0"
required_providers {
aws = {
source  = "hashicorp/aws"
version = "~> 5.0"
}
}
}

provider "aws" {
region = var.aws_region
}

==================================================
4. variables.tf
variable "aws_region" {
description = "The AWS region to deploy resources"
type        = string
default     = "us-east-1"
}

variable "project_name" {
description = "Name prefix for all resources"
type        = string
default     = "project52-ai-pipeline"
}

==================================================
5. main.tf
resource "aws_s3_bucket" "ai_data_bucket" {
bucket        = "project52-ai-data-bucket-azm"
force_destroy = true
}

resource "aws_sqs_queue" "ai_processing_queue" {
name                      = "project52-ai-processing-queue"
delay_seconds             = 0
max_message_size          = 262144
message_retention_seconds = 86400
}

resource "aws_sqs_queue_policy" "sqs_policy" {
queue_url = aws_sqs_queue.ai_processing_queue.id

policy = jsonencode({
Version = "2012-10-17"
Statement = [
{
Sid       = "AllowS3ToSendNotification"
Effect    = "Allow"
Principal = {
Service = "s3.amazonaws.com"
}
Action   = "SQS:SendMessage"
Resource = aws_sqs_queue.ai_processing_queue.arn
Condition = {
ArnEquals = {
"aws:SourceArn" = aws_s3_bucket.ai_data_bucket.arn
}
}
}
]
})
}

resource "aws_s3_bucket_notification" "bucket_notification" {
bucket = aws_s3_bucket.ai_data_bucket.id

queue {
queue_arn     = aws_sqs_queue.ai_processing_queue.arn
events        = ["s3:ObjectCreated:*"]
}

depends_on = [aws_sqs_queue_policy.sqs_policy]
}

resource "aws_dynamodb_table" "ai_results_table" {
name         = "Project52_AI_Results"
billing_mode = "PAY_PER_REQUEST"
hash_key     = "FileId"

attribute {
name = "FileId"
type = "S"
}
}

resource "aws_iam_role" "lambda_exec_role" {
name = "project52_lambda_exec_role"

assume_role_policy = jsonencode({
Version = "2012-10-17"
Statement = [
{
Action = "sts:AssumeRole"
Effect = "Allow"
Principal = {
Service = "lambda.amazonaws.com"
}
}
]
})
}

resource "aws_iam_role_policy" "lambda_policy" {
name = "project52_lambda_policy"
role = aws_iam_role.lambda_exec_role.id

policy = jsonencode({
Version = "2012-10-17"
Statement = [
{
Effect = "Allow"
Action = [
"logs:CreateLogGroup",
"logs:CreateLogStream",
"logs:PutLogEvents"
]
Resource = "arn:aws:logs:::"
},
{
Effect = "Allow"
Action = [
"sqs:ReceiveMessage",
"sqs:DeleteMessage",
"sqs:GetQueueAttributes"
]
Resource = aws_sqs_queue.ai_processing_queue.arn
},
{
Effect = "Allow"
Action = [
"dynamodb:PutItem",
"dynamodb:UpdateItem"
]
Resource = aws_dynamodb_table.ai_results_table.arn
},
{
Effect = "Allow"
Action = [
"bedrock:InvokeModel"
]
Resource = ""
}
]
})
}

data "archive_file" "lambda_zip" {
type        = "zip"
source_file = "lambda_function.py"
output_path = "lambda_function_payload.zip"
}

resource "aws_lambda_function" "ai_processor_lambda" {
filename         = "lambda_function_payload.zip"
function_name    = "project52_ai_processor"
role             = aws_iam_role.lambda_exec_role.arn
handler          = "lambda_function.lambda_handler"
runtime          = "python3.10"
source_code_hash = data.archive_file.lambda_zip.output_base64sha256

environment {
variables = {
TABLE_NAME = aws_dynamodb_table.ai_results_table.name
}
}
}

resource "aws_lambda_event_source_mapping" "sqs_to_lambda" {
event_source_arn = aws_sqs_queue.ai_processing_queue.arn
function_name    = aws_lambda_function.ai_processor_lambda.arn
batch_size       = 5
}

==================================================
6. lambda_function.py
import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'Project52_AI_Results')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
print("Received event: ", json.dumps(event))
for record in event['Records']:
    payload = record['body']
    print(f"Processing message: {payload}")
    
    file_id = record['messageId']
    
    table.put_item(
        Item={
            'FileId': file_id,
            'Status': 'Processed',
            'Payload': payload
        }
    )
    
return {
    'statusCode': 200,
    'body': json.dumps('Successfully processed AI pipeline event!')
}
