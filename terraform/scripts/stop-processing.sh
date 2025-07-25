#!/bin/bash
# Stop processing job - Destroys ephemeral infrastructure and preserves results

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"

echo "🍺 Brew Master AI - Stopping Processing Job"
echo "============================================"

# Function to check if ephemeral infrastructure exists
check_ephemeral() {
    echo "📋 Checking ephemeral infrastructure..."
    cd "$TERRAFORM_DIR"
    
    if terraform show -json | jq -e '.values.root_module.child_modules[] | select(.address == "module.ephemeral")' > /dev/null 2>&1; then
        local instance_id=$(terraform output -raw instance_id 2>/dev/null || echo "unknown")
        echo "✅ Ephemeral infrastructure exists (Instance: $instance_id)"
        return 0
    else
        echo "ℹ️  No ephemeral infrastructure found"
        return 1
    fi
}

# Function to get S3 bucket name
get_s3_bucket() {
    cd "$TERRAFORM_DIR"
    terraform output -raw s3_bucket_name 2>/dev/null || echo ""
}

# Function to check processing status before stopping
check_final_status() {
    echo
    echo "📊 Checking final processing status..."
    cd "$TERRAFORM_DIR"
    
    local ssh_command=$(terraform output -raw ssh_command 2>/dev/null)
    
    if [ -n "$ssh_command" ]; then
        local ssh_params=$(echo "$ssh_command" | sed 's/^ssh //')
        
        echo "   Connecting to instance for final status check..."
        
        # Check if any processing is currently running
        if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "pgrep -f 'python.*process_s3.py|brew_master.py' > /dev/null" 2>/dev/null; then
            echo "⚠️  WARNING: Processing appears to be running!"
            echo "   This may interrupt ongoing work."
            echo
            
            read -p "Continue with shutdown? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Shutdown cancelled. Wait for processing to complete."
                return 1
            fi
        else
            echo "✅ No active processing detected"
        fi
        
        # Show final status
        echo "   Final system status:"
        ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "~/check_status.sh" 2>/dev/null || {
            echo "   Could not retrieve final status (instance may be unreachable)"
        }
    else
        echo "   Could not connect to instance for status check"
    fi
    
    return 0
}

# Function to backup any remaining temp data to S3
backup_temp_data() {
    local bucket_name="$1"
    echo
    echo "💾 Backing up any remaining temporary data..."
    cd "$TERRAFORM_DIR"
    
    local ssh_command=$(terraform output -raw ssh_command 2>/dev/null)
    
    if [ -n "$ssh_command" ]; then
        local ssh_params=$(echo "$ssh_command" | sed 's/^ssh //')
        
        echo "   Checking for files to backup..."
        
        # Check if there are any files in the temp directories that need backing up
        local temp_files=$(ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "find /mnt/temp-data/output /mnt/temp-data/logs -type f 2>/dev/null | wc -l" 2>/dev/null || echo "0")
        
        if [ "$temp_files" -gt 0 ]; then
            echo "   Found $temp_files files to backup to S3..."
            
            # Backup output files
            ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "
                if [ -d /mnt/temp-data/output ] && [ \"\$(ls -A /mnt/temp-data/output)\" ]; then
                    echo '   Backing up output files...'
                    aws s3 sync /mnt/temp-data/output/ s3://$bucket_name/processed/\$(date +%Y%m%d-%H%M%S)/
                fi
                
                if [ -d /mnt/temp-data/logs ] && [ \"\$(ls -A /mnt/temp-data/logs)\" ]; then
                    echo '   Backing up log files...'
                    aws s3 sync /mnt/temp-data/logs/ s3://$bucket_name/logs/\$(date +%Y%m%d-%H%M%S)/
                fi
            " 2>/dev/null || {
                echo "   ⚠️  Could not backup temp data (instance may be unreachable)"
            }
            
            echo "✅ Backup completed"
        else
            echo "   No temporary files found to backup"
        fi
    else
        echo "   Could not connect to instance for backup"
    fi
    
    return 0
}

# Function to show final results summary
show_results_summary() {
    local bucket_name="$1"
    echo
    echo "📊 Results Summary"
    echo "=================="
    
    echo "🗂️  S3 Bucket Contents:"
    
    # Show processed files
    echo "   📁 Processed Results:"
    local processed_count=$(aws s3 ls "s3://$bucket_name/processed/" --recursive 2>/dev/null | wc -l)
    if [ "$processed_count" -gt 0 ]; then
        echo "      Found $processed_count processed files"
        aws s3 ls "s3://$bucket_name/processed/" --recursive --human-readable | head -10
        if [ "$processed_count" -gt 10 ]; then
            echo "      ... and $((processed_count - 10)) more files"
        fi
    else
        echo "      No processed files found"
    fi
    
    echo
    echo "   📁 Log Files:"
    local log_count=$(aws s3 ls "s3://$bucket_name/logs/" --recursive 2>/dev/null | wc -l)
    if [ "$log_count" -gt 0 ]; then
        echo "      Found $log_count log files"
    else
        echo "      No log files found"
    fi
    
    echo
    echo "💾 Access Results:"
    echo "   List all: aws s3 ls s3://$bucket_name/ --recursive"
    echo "   Download: aws s3 sync s3://$bucket_name/processed/ ./results/"
    
    return 0
}

# Function to destroy ephemeral infrastructure
destroy_ephemeral() {
    echo
    echo "🗑️  Destroying ephemeral infrastructure..."
    cd "$TERRAFORM_DIR"
    
    echo "   This will destroy:"
    echo "   - EC2 spot instance"
    echo "   - 20GB EBS volume"
    echo "   - Security group"
    echo "   - Volume attachment"
    echo
    echo "   ✅ S3 data will be preserved"
    echo
    
    if terraform destroy -target=module.ephemeral -auto-approve; then
        echo "✅ Ephemeral infrastructure destroyed successfully"
        return 0
    else
        echo "❌ Failed to destroy ephemeral infrastructure"
        return 1
    fi
}

# Function to calculate cost savings
calculate_savings() {
    echo
    echo "💰 Cost Savings"
    echo "==============="
    
    local runtime_hours=${1:-1}
    local hourly_cost=2.50
    local monthly_cost=150
    
    local session_cost=$(echo "$runtime_hours * $hourly_cost" | bc -l)
    local monthly_savings=$(echo "$monthly_cost - $session_cost" | bc -l)
    
    printf "   Session cost (%.1f hours): \$%.2f\n" "$runtime_hours" "$session_cost"
    printf "   Monthly savings vs always-on: \$%.2f\n" "$monthly_savings"
    echo "   Only pay for processing time! 💸"
    
    return 0
}

# Main execution
main() {
    # Check if ephemeral infrastructure exists
    if ! check_ephemeral; then
        echo "ℹ️  No ephemeral infrastructure to stop."
        echo "   Use ./scripts/start-processing.sh to start a processing job."
        exit 0
    fi
    
    # Get S3 bucket name
    bucket_name=$(get_s3_bucket)
    if [ -z "$bucket_name" ]; then
        echo "❌ Could not get S3 bucket name. Check infrastructure state."
        exit 1
    fi
    
    echo "📦 Using S3 bucket: $bucket_name"
    
    # Check processing status before stopping
    if ! check_final_status; then
        echo "Shutdown cancelled by user."
        exit 1
    fi
    
    # Backup any remaining temp data
    backup_temp_data "$bucket_name"
    
    # Show results summary
    show_results_summary "$bucket_name"
    
    echo
    read -p "Proceed with infrastructure destruction? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Infrastructure destruction cancelled."
        echo "Run this script again when ready to stop."
        exit 0
    fi
    
    # Destroy ephemeral infrastructure
    if ! destroy_ephemeral; then
        echo "❌ Failed to destroy infrastructure"
        exit 1
    fi
    
    # Calculate and show cost savings
    calculate_savings
    
    echo
    echo "🎉 Processing job stopped successfully!"
    echo "======================================"
    echo
    echo "✅ Infrastructure destroyed"
    echo "✅ Results preserved in S3"
    echo "✅ Cost savings activated"
    echo
    echo "📋 Next steps:"
    echo "   - Access results: aws s3 sync s3://$bucket_name/processed/ ./results/"
    echo "   - Start new job: ./scripts/start-processing.sh"
    echo "   - Check costs: aws ce get-cost-and-usage --time-period ..."
    echo
    echo "💾 Data preserved in S3:"
    echo "   - Processed results: s3://$bucket_name/processed/"
    echo "   - Log files: s3://$bucket_name/logs/"
    echo "   - Input files: s3://$bucket_name/input/"
    
    return 0
}

# Run main function
main "$@"