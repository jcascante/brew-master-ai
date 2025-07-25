#!/bin/bash
# Start processing job - Creates ephemeral infrastructure and begins processing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"

echo "🍺 Brew Master AI - Starting Processing Job"
echo "============================================"

# Function to check if persistent infrastructure exists
check_persistent() {
    echo "📋 Checking persistent infrastructure..."
    cd "$TERRAFORM_DIR"
    
    if terraform show -json | jq -e '.values.root_module.child_modules[] | select(.address == "module.persistent")' > /dev/null 2>&1; then
        echo "✅ Persistent infrastructure exists"
        return 0
    else
        echo "❌ Persistent infrastructure not found"
        return 1
    fi
}

# Function to get S3 bucket name
get_s3_bucket() {
    cd "$TERRAFORM_DIR"
    terraform output -raw s3_bucket_name 2>/dev/null || echo ""
}

# Function to list files in S3 input directory
check_input_files() {
    local bucket_name="$1"
    echo "📁 Checking for input files in S3..."
    
    file_count=$(aws s3 ls "s3://$bucket_name/input/" --recursive | wc -l)
    
    if [ "$file_count" -gt 0 ]; then
        echo "✅ Found $file_count files in S3 input directory:"
        aws s3 ls "s3://$bucket_name/input/" --recursive --human-readable
        return 0
    else
        echo "⚠️  No files found in S3 input directory"
        echo "   Upload files with: aws s3 cp your-files s3://$bucket_name/input/"
        return 1
    fi
}

# Function to deploy ephemeral infrastructure
deploy_ephemeral() {
    echo
    echo "🚀 Deploying ephemeral processing infrastructure..."
    cd "$TERRAFORM_DIR"
    
    echo "   - Creating EC2 spot instance (c5.2xlarge)"
    echo "   - Attaching 20GB EBS volume"
    echo "   - Setting up security group"
    echo "   - Installing data-extraction pipeline"
    
    if terraform apply -target=module.ephemeral -auto-approve; then
        echo "✅ Ephemeral infrastructure deployed successfully"
        return 0
    else
        echo "❌ Failed to deploy ephemeral infrastructure"
        return 1
    fi
}

# Function to get instance connection info
get_connection_info() {
    cd "$TERRAFORM_DIR"
    
    local instance_id=$(terraform output -raw instance_id 2>/dev/null)
    local public_ip=$(terraform output -raw public_ip 2>/dev/null)
    local ssh_command=$(terraform output -raw ssh_command 2>/dev/null)
    
    echo
    echo "🔗 Connection Information:"
    echo "   Instance ID: $instance_id"
    echo "   Public IP: $public_ip"
    echo "   SSH Command: $ssh_command"
    
    return 0
}

# Function to wait for instance to be ready
wait_for_instance() {
    echo
    echo "⏳ Waiting for instance to be ready..."
    cd "$TERRAFORM_DIR"
    
    local instance_id=$(terraform output -raw instance_id 2>/dev/null)
    local public_ip=$(terraform output -raw public_ip 2>/dev/null)
    
    # Wait for instance to be running
    echo "   Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids "$instance_id"
    
    # Wait for SSH to be available
    echo "   Waiting for SSH to be available..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if timeout 5 bash -c "echo > /dev/tcp/$public_ip/22" 2>/dev/null; then
            echo "✅ Instance is ready for SSH"
            break
        fi
        
        echo "   Attempt $attempt/$max_attempts - SSH not ready yet..."
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ Timeout waiting for SSH to be available"
        return 1
    fi
    
    return 0
}

# Function to check processing status
check_processing_status() {
    echo
    echo "📊 Checking processing status..."
    cd "$TERRAFORM_DIR"
    
    local ssh_command=$(terraform output -raw ssh_command 2>/dev/null)
    
    # Remove the 'ssh' part and extract connection details
    local ssh_params=$(echo "$ssh_command" | sed 's/^ssh //')
    
    echo "   Connecting to instance to check status..."
    
    # Check if setup is complete
    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "test -f /home/ubuntu/setup_complete.flag" 2>/dev/null; then
        echo "✅ Instance setup is complete"
        
        # Run status check
        echo "   Running status check..."
        ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "~/check_status.sh" 2>/dev/null || {
            echo "⚠️  Could not run status check (instance may still be initializing)"
        }
    else
        echo "⏳ Instance is still setting up (this can take 5-10 minutes)"
        echo "   Setup includes: system updates, Python packages, git clone, etc."
    fi
    
    return 0
}

# Main execution
main() {
    # Check if persistent infrastructure exists
    if ! check_persistent; then
        echo
        echo "🔧 Deploying persistent infrastructure first..."
        cd "$TERRAFORM_DIR"
        terraform apply -target=module.persistent -auto-approve
        echo "✅ Persistent infrastructure deployed"
    fi
    
    # Get S3 bucket name
    bucket_name=$(get_s3_bucket)
    if [ -z "$bucket_name" ]; then
        echo "❌ Could not get S3 bucket name. Check persistent infrastructure."
        exit 1
    fi
    
    echo "📦 Using S3 bucket: $bucket_name"
    
    # Check for input files (optional - continue even if none found)
    if ! check_input_files "$bucket_name"; then
        echo
        read -p "Continue without input files? Processing will wait for files to be uploaded. (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Upload files first, then run this script again."
            echo "Example: aws s3 cp your-video.mp4 s3://$bucket_name/input/"
            exit 1
        fi
    fi
    
    # Deploy ephemeral infrastructure
    if ! deploy_ephemeral; then
        echo "❌ Failed to deploy infrastructure"
        exit 1
    fi
    
    # Get connection information
    get_connection_info
    
    # Wait for instance to be ready
    if ! wait_for_instance; then
        echo "❌ Instance setup failed"
        exit 1
    fi
    
    # Check processing status
    check_processing_status
    
    echo
    echo "🎉 Processing job started successfully!"
    echo "========================================"
    echo
    echo "📋 Next steps:"
    echo "   1. Upload files: aws s3 cp files/ s3://$bucket_name/input/ --recursive"
    echo "   2. Monitor status: ./scripts/check-status.sh"
    echo "   3. View results: aws s3 ls s3://$bucket_name/processed/"
    echo "   4. Stop when done: ./scripts/stop-processing.sh"
    echo
    echo "🔗 SSH Access:"
    echo "   $(terraform output -raw ssh_command)"
    echo "   Then run: ~/start_processing.sh"
    echo
    echo "📊 Monitor processing:"
    echo "   tail -f /mnt/temp-data/logs/brew_master.log"
    
    return 0
}

# Run main function
main "$@"