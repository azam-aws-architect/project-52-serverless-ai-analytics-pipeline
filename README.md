# Project 52: Serverless AI Analytics Pipeline on AWS using Terraform

A fully automated, event-driven serverless pipeline built on Amazon Web Services (AWS) utilizing Infrastructure as Code (IaC) with Terraform.

## 🏗️ Architecture Overview

This project implements a cloud-native serverless architecture to process data events securely and efficiently:

1. **Amazon S3**: Acts as the entry point for raw data uploads. Whenever a new file is uploaded, an S3 event notification is triggered.
2. **Amazon SQS**: Receives the event notifications from S3 securely using a dedicated SQS Queue Policy, ensuring reliable message decoupling.
3. **AWS Lambda**: Automatically triggered by the SQS queue using event source mapping. It processes the payloads via Python and handles execution securely.
4. **Amazon DynamoDB**: A NoSQL database that stores the final metadata and processing status for each pipeline run.
5. **Terraform**: Manages the entire lifecycle of all AWS resources as Code.

---

## 🛠️ Tech Stack & Services Used

- **Cloud Provider**: AWS (Amazon Web Services)
- **Infrastructure as Code**: Terraform (AWS & Archive Providers)
- **Compute**: AWS Lambda (Python 3.10)
- **Storage**: Amazon S3
- **Messaging**: Amazon SQS
- **Database**: Amazon DynamoDB
- **Security & IAM**: Custom IAM Roles and SQS/S3 Bucket Policies

---

## 📂 Project File Structure

- `provider.tf`: Defines the AWS provider and required versions.
- `variables.tf`: Configuration variables for region and project naming.
- `main.tf`: Core infrastructure definitions (S3, SQS, DynamoDB, IAM Roles, Lambda, and Event Mappings).
- `lambda_function.py`: Python code executed by the Lambda function to handle events and save records to DynamoDB.

---

## 🚀 Deployment Instructions

1. Clone the repository and navigate to the project folder.
2. Initialize Terraform providers:
   ```bash
   terraform init -upgrade
