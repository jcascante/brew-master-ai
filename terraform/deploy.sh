#!/bin/bash

# Brew Master AI Infrastructure Deployment Script
# This script automates the deployment of the Brew Master AI infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Terraform is installed
    if ! command_exists terraform; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create S3 backend infrastructure
create_backend() {
    print_status "Creating S3 backend infrastructure..."
    
    BUCKET_NAME="brew-master-ai-terraform-state"
    TABLE_NAME="brew-master-ai-terraform-locks"
    REGION=$(aws configure get region)
    
    # Create S3 bucket if it doesn't exist
    if ! aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
        print_status "Creating S3 bucket: $BUCKET_NAME"
        aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "$BUCKET_NAME" \
            --versioning-configuration Status=Enabled
        
        # Enable encryption
        aws s3api put-bucket-encryption \
            --bucket "$BUCKET_NAME" \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
        
        print_success "S3 bucket created and configured"
    else
        print_warning "S3 bucket $BUCKET_NAME already exists"
    fi
    
    # Create DynamoDB table if it doesn't exist
    if ! aws dynamodb describe-table --table-name "$TABLE_NAME" >/dev/null 2>&1; then
        print_status "Creating DynamoDB table: $TABLE_NAME"
        aws dynamodb create-table \
            --table-name "$TABLE_NAME" \
            --attribute-definitions AttributeName=LockID,AttributeType=S \
            --key-schema AttributeName=LockID,KeyType=HASH \
            --billing-mode PAY_PER_REQUEST \
            --region "$REGION"
        
        # Wait for table to be active
        print_status "Waiting for DynamoDB table to be active..."
        aws dynamodb wait table-exists --table-name "$TABLE_NAME"
        
        print_success "DynamoDB table created"
    else
        print_warning "DynamoDB table $TABLE_NAME already exists"
    fi
}

# Function to create EC2 key pair
create_key_pair() {
    print_status "Creating EC2 key pair..."
    
    ENVIRONMENT=$1
    KEY_NAME="brew-master-ai-${ENVIRONMENT}-key"
    KEY_FILE="${KEY_NAME}.pem"
    
    # Check if key pair already exists
    if aws ec2 describe-key-pairs --key-names "$KEY_NAME" >/dev/null 2>&1; then
        print_warning "Key pair $KEY_NAME already exists"
        return 0
    fi
    
    # Create key pair
    print_status "Creating key pair: $KEY_NAME"
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --query 'KeyMaterial' \
        --output text > "$KEY_FILE"
    
    # Set proper permissions
    chmod 400 "$KEY_FILE"
    
    print_success "Key pair created: $KEY_FILE"
    print_warning "Keep this key file secure and don't commit it to version control"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    print_status "Deploying infrastructure..."
    
    ENVIRONMENT=$1
    VAR_FILE="environments/${ENVIRONMENT}.tfvars"
    
    # Check if var file exists
    if [ ! -f "$VAR_FILE" ]; then
        print_error "Environment file $VAR_FILE not found"
        exit 1
    fi
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_status "Planning deployment..."
    terraform plan -var-file="$VAR_FILE" -out=tfplan
    
    # Ask for confirmation
    echo
    print_warning "Review the plan above. Do you want to proceed with the deployment? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled"
        exit 0
    fi
    
    # Apply deployment
    print_status "Applying deployment..."
    terraform apply tfplan
    
    # Clean up plan file
    rm -f tfplan
    
    print_success "Infrastructure deployment completed"
}

# Function to show outputs
show_outputs() {
    print_status "Infrastructure outputs:"
    terraform output
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [ENVIRONMENT]"
    echo
    echo "Commands:"
    echo "  deploy    Deploy infrastructure for the specified environment"
    echo "  destroy   Destroy infrastructure for the specified environment"
    echo "  plan      Plan infrastructure changes for the specified environment"
    echo "  outputs   Show infrastructure outputs"
    echo "  setup     Setup prerequisites (S3 backend, key pair)"
    echo
    echo "Environments:"
    echo "  dev       Development environment"
    echo "  prod      Production environment"
    echo
    echo "Examples:"
    echo "  $0 setup dev"
    echo "  $0 deploy dev"
    echo "  $0 plan prod"
    echo "  $0 destroy dev"
}

# Function to destroy infrastructure
destroy_infrastructure() {
    print_status "Destroying infrastructure..."
    
    ENVIRONMENT=$1
    VAR_FILE="environments/${ENVIRONMENT}.tfvars"
    
    # Check if var file exists
    if [ ! -f "$VAR_FILE" ]; then
        print_error "Environment file $VAR_FILE not found"
        exit 1
    fi
    
    # Ask for confirmation
    echo
    print_warning "This will destroy ALL infrastructure for the $ENVIRONMENT environment."
    print_warning "This action cannot be undone. Are you sure? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Destruction cancelled"
        exit 0
    fi
    
    # Destroy infrastructure
    terraform destroy -var-file="$VAR_FILE"
    
    print_success "Infrastructure destruction completed"
}

# Function to plan infrastructure
plan_infrastructure() {
    print_status "Planning infrastructure changes..."
    
    ENVIRONMENT=$1
    VAR_FILE="environments/${ENVIRONMENT}.tfvars"
    
    # Check if var file exists
    if [ ! -f "$VAR_FILE" ]; then
        print_error "Environment file $VAR_FILE not found"
        exit 1
    fi
    
    # Initialize Terraform
    terraform init
    
    # Plan changes
    terraform plan -var-file="$VAR_FILE"
}

# Main script logic
main() {
    COMMAND=$1
    ENVIRONMENT=$2
    
    # Check if command is provided
    if [ -z "$COMMAND" ]; then
        show_usage
        exit 1
    fi
    
    # Check prerequisites for all commands except setup
    if [ "$COMMAND" != "setup" ]; then
        check_prerequisites
    fi
    
    case $COMMAND in
        "setup")
            if [ -z "$ENVIRONMENT" ]; then
                print_error "Environment is required for setup command"
                show_usage
                exit 1
            fi
            create_backend
            create_key_pair "$ENVIRONMENT"
            print_success "Setup completed for $ENVIRONMENT environment"
            ;;
        "deploy")
            if [ -z "$ENVIRONMENT" ]; then
                print_error "Environment is required for deploy command"
                show_usage
                exit 1
            fi
            deploy_infrastructure "$ENVIRONMENT"
            show_outputs
            ;;
        "destroy")
            if [ -z "$ENVIRONMENT" ]; then
                print_error "Environment is required for destroy command"
                show_usage
                exit 1
            fi
            destroy_infrastructure "$ENVIRONMENT"
            ;;
        "plan")
            if [ -z "$ENVIRONMENT" ]; then
                print_error "Environment is required for plan command"
                show_usage
                exit 1
            fi
            plan_infrastructure "$ENVIRONMENT"
            ;;
        "outputs")
            show_outputs
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 