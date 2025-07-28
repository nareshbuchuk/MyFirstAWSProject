# S3 File Upload Portal

A FastAPI-based web portal for uploading files to Amazon S3, designed for deployment on AWS Elastic Beanstalk.

## Features
- Async FastAPI backend
- Modular code structure
- Structured logging
- File upload UI
- S3 integration
- CloudFormation for AWS resources
- GitHub Actions CI/CD with OIDC IAM role

## Setup

1. **Clone the repo**
2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure environment**
   - Copy `.env` and fill in AWS credentials, region, and S3 bucket name.

4. **Run locally**
   ```sh
   uvicorn app.main:app --reload
   ```

## Deployment

### 1. AWS Resources
- Deploy `cloudformation.yaml` to create the S3 bucket and IAM role.

### 2. Elastic Beanstalk
- Use the provided `Dockerfile` for containerized deployment.

### 3. GitHub Actions CI/CD
- Configure the following GitHub secrets:
  - `AWS_OIDC_ROLE_ARN`: IAM role ARN for OIDC
  - `AWS_REGION`: AWS region
  - `EB_APP_NAME`: Elastic Beanstalk application name
  - `EB_ENV_NAME`: Elastic Beanstalk environment name

- On push to `main`, the workflow will build and deploy the app.

### 4. OIDC IAM Role
- Create an IAM role with trust policy for GitHub OIDC provider.
- Attach permissions for Elastic Beanstalk and S3.
- Reference the role ARN in your GitHub secrets.

## Testing
- Add unit tests in `app/tests/` and run with pytest.

---

## License
MIT