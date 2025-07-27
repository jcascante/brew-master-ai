#!/bin/bash
# Check processing status - Monitor jobs without creating/destroying infrastructure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"

echo "🍺 Brew Master AI - Status Check"
echo "================================="

# Function to check infrastructure status
check_infrastructure() {
    echo "🏗️  Infrastructure Status:"
    cd "$TERRAFORM_DIR"
    
    # Check persistent infrastructure
    if terraform show -json | jq -e '.values.root_module.child_modules[] | select(.address == "module.persistent")' > /dev/null 2>&1; then
        echo "   ✅ Persistent infrastructure: Active"
        
        local bucket_name=$(terraform output -raw s3_bucket_name 2>/dev/null || echo "unknown")
        echo "   📦 S3 Bucket: $bucket_name"
    else
        echo "   ❌ Persistent infrastructure: Not found"
        echo "   Run: terraform apply -target=module.persistent"
        return 1
    fi
    
    # Check ephemeral infrastructure
    if terraform show -json | jq -e '.values.root_module.child_modules[] | select(.address == "module.ephemeral")' > /dev/null 2>&1; then
        echo "   ✅ Ephemeral infrastructure: Active"
        
        local instance_id=$(terraform output -raw instance_id 2>/dev/null || echo "unknown")
        local public_ip=$(terraform output -raw public_ip 2>/dev/null || echo "unknown")
        
        echo "   🖥️  Instance ID: $instance_id"
        echo "   🌐 Public IP: $public_ip"
        
        # Check instance state
        if [ "$instance_id" != "unknown" ]; then
            local instance_state=$(aws ec2 describe-instances --instance-ids "$instance_id" --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null || echo "unknown")
            echo "   📊 Instance State: $instance_state"
        fi
    else
        echo "   ⚪ Ephemeral infrastructure: Not deployed"
        echo "   Run: ./scripts/start-processing.sh"
    fi
    
    return 0
}

# Function to check S3 status
check_s3_status() {
    echo
    echo "☁️  S3 Storage Status:"
    cd "$TERRAFORM_DIR"
    
    local bucket_name=$(terraform output -raw s3_bucket_name 2>/dev/null)
    
    if [ -z "$bucket_name" ]; then
        echo "   ❌ Cannot get S3 bucket name"
        return 1
    fi
    
    # Check input files
    local input_count=$(aws s3 ls "s3://$bucket_name/input/" --recursive 2>/dev/null | wc -l)
    echo "   📥 Input files: $input_count"
    
    if [ "$input_count" -gt 0 ]; then
        echo "      Recent uploads:"
        aws s3 ls "s3://$bucket_name/input/" --recursive --human-readable | tail -5 | sed 's/^/      /'
    fi
    
    # Check processed files
    local processed_count=$(aws s3 ls "s3://$bucket_name/processed/" --recursive 2>/dev/null | wc -l)
    echo "   📤 Processed files: $processed_count"
    
    if [ "$processed_count" -gt 0 ]; then
        echo "      Recent results:"
        aws s3 ls "s3://$bucket_name/processed/" --recursive --human-readable | tail -5 | sed 's/^/      /'
    fi
    
    # Check temp files
    local temp_count=$(aws s3 ls "s3://$bucket_name/temp/" --recursive 2>/dev/null | wc -l)
    if [ "$temp_count" -gt 0 ]; then
        echo "   🗂️  Temp files: $temp_count (will auto-delete after 7 days)"
    fi
    
    # Check logs
    local log_count=$(aws s3 ls "s3://$bucket_name/logs/" --recursive 2>/dev/null | wc -l)
    echo "   📋 Log files: $log_count"
    
    return 0
}

# Function to check EC2 processing status
check_ec2_status() {
    echo
    echo "🖥️  EC2 Processing Status:"
    cd "$TERRAFORM_DIR"
    
    local ssh_command=$(terraform output -raw ssh_command 2>/dev/null)
    
    if [ -z "$ssh_command" ]; then
        echo "   ⚪ No EC2 instance deployed"
        return 0
    fi
    
    local ssh_params=$(echo "$ssh_command" | sed 's/^ssh //')
    local public_ip=$(terraform output -raw public_ip 2>/dev/null)
    
    # Test SSH connectivity
    if timeout 5 bash -c "echo > ssh -o ConnectTimeout=5$public_ip/22" 2>/dev/null; then
        echo "   ✅ SSH connectivity: Available"
        
        # Check if setup is complete
        if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "test -f /home/ubuntu/setup_complete.flag" 2>/dev/null; then
            echo "   ✅ Instance setup: Complete"
            
            # Check system status
            echo "   📊 System Status:"
            ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "
                echo '      CPU Usage:' \$(top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{print 100 - \$1\"%\"}')
                echo '      Memory:' \$(free -h | awk '/^Mem:/ {print \$3\"/\"\$2}')
                echo '      Disk:' \$(df -h /mnt/temp-data | awk 'NR==2 {print \$3\"/\"\$2\" (\"\$5\" used)\"}')
            " 2>/dev/null || echo "      Could not retrieve system metrics"
            
            # Check active processes
            echo "   🔄 Active Processes:"
            local active_processes=$(ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "pgrep -f 'python.*process_s3.py|brew_master.py|whisper' | wc -l" 2>/dev/null || echo "0")
            
            if [ "$active_processes" -gt 0 ]; then
                echo "      ✅ Processing active ($active_processes processes)"
                ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "ps aux | grep -E 'python.*process_s3.py|brew_master.py|whisper' | grep -v grep | head -3" 2>/dev/null | sed 's/^/      /' || true
            else
                echo "      ⚪ No active processing"
            fi
            
            # Check recent logs
            echo "   📋 Recent Activity:"
            if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "test -f /mnt/temp-data/logs/brew_master.log" 2>/dev/null; then
                ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ssh_params "tail -3 /mnt/temp-data/logs/brew_master.log" 2>/dev/null | sed 's/^/      /' || true
            else
                echo "      No recent log activity"
            fi
            
        else
            echo "   ⏳ Instance setup: In progress (5-10 minutes typical)"
            echo "      System is installing packages and setting up environment"
        fi
        
    else
        echo "   ❌ SSH connectivity: Not available"
        echo "      Instance may be starting up or stopped"
    fi
    
    return 0
}

# Function to show cost information
show_cost_info() {
    echo
    echo "💰 Cost Information:"
    cd "$TERRAFORM_DIR"
    
    # Check if ephemeral infrastructure is running
    if terraform show -json | jq -e '.values.root_module.child_modules[] | select(.address == "module.ephemeral")' > /dev/null 2>&1; then
        local instance_id=$(terraform output -raw instance_id 2>/dev/null)
        
        if [ -n "$instance_id" ] && [ "$instance_id" != "unknown" ]; then
            # Get instance launch time
            local launch_time=$(aws ec2 describe-instances --instance-ids "$instance_id" --query 'Reservations[0].Instances[0].LaunchTime' --output text 2>/dev/null || echo "")
            
            if [ -n "$launch_time" ]; then
                local current_time=$(date -u +%s)
                local launch_timestamp=$(date -d "$launch_time" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "${launch_time%.*}" +%s 2>/dev/null || echo "0")
                local runtime_hours=$(echo "scale=2; ($current_time - $launch_timestamp) / 3600" | bc -l 2>/dev/null || echo "0")
                
                if [ "$(echo "$runtime_hours > 0" | bc -l)" == "1" ]; then
                    local estimated_cost=$(echo "scale=2; $runtime_hours * 2.50" | bc -l)
                    printf "   ⏱️  Runtime: %.1f hours\n" "$runtime_hours"
                    printf "   💵 Estimated cost: \$%.2f\n" "$estimated_cost"
                    echo "   📊 Hourly rate: ~\$2.50 (spot pricing)"
                else
                    echo "   ⏱️  Runtime: Just started"
                    echo "   💵 Estimated cost: <\$1.00"
                fi
            fi
        fi
        
        echo "   💡 Cost optimization: Infrastructure destroys automatically when not needed"
    else
        echo "   ✅ Current cost: \$0.00 (no ephemeral infrastructure running)"
        echo "   📦 S3 storage: ~\$0.023/GB/month (pay for actual usage)"
    fi
    
    return 0
}

# Function to show recommended actions
show_recommendations() {
    echo
    echo "🎯 Recommended Actions:"
    cd "$TERRAFORM_DIR"
    
    # Check if persistent infrastructure exists
    if ! terraform show -json | jq -e '.values.root_module.child_modules[] | select(.address == "module.persistent")' > /dev/null 2>&1; then
        echo "   🔧 Deploy persistent infrastructure: terraform apply -target=module.persistent"
        return 0
    fi
    
    # Check if ephemeral infrastructure exists
    if ! terraform show -json | jq -e '.values.root_module.child_modules[] | select(.address == "module.ephemeral")' > /dev/null 2>&1; then
        echo "   🚀 Start processing job: ./scripts/start-processing.sh"
        return 0
    fi
    
    # Check for input files
    local bucket_name=$(terraform output -raw s3_bucket_name 2>/dev/null)
    local input_count=$(aws s3 ls "s3://$bucket_name/input/" --recursive 2>/dev/null | wc -l)
    
    if [ "$input_count" -eq 0 ]; then
        echo "   📥 Upload files: aws s3 cp your-files s3://$bucket_name/input/ --recursive"
    fi
    
    # Check if processing is active
    local ssh_command=$(terraform output -raw ssh_command 2>/dev/null)
    if [ -n "$ssh_command" ]; then
        local ssh_params=$(echo "$ssh_command" | sed 's/^ssh //')
        local active_processes=$(ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $ssh_params "pgrep -f 'python.*process_s3.py|brew_master.py' | wc -l" 2>/dev/null || echo "0")
        
        if [ "$active_processes" -eq 0 ]; then
            echo "   ▶️  Start processing: ssh to instance and run ~/start_processing.sh"
        fi
    fi
    
    echo "   📊 Monitor progress: ./scripts/check-status.sh"
    echo "   🛑 Stop when done: ./scripts/stop-processing.sh"
    
    return 0
}

# Main execution
main() {
    # Check infrastructure status
    if ! check_infrastructure; then
        echo
        echo "❌ Infrastructure not properly deployed"
        echo "   Run: terraform apply -target=module.persistent"
        exit 1
    fi
    
    # Check S3 status
    check_s3_status
    
    # Check EC2 status
    check_ec2_status
    
    # Show cost information
    show_cost_info
    
    # Show recommendations
    show_recommendations
    
    echo
    echo "🔄 Status check complete!"
    echo
    echo "📋 Quick Commands:"
    echo "   SSH to instance: $(terraform output -raw ssh_command 2>/dev/null || echo 'No instance running')"
    echo "   View logs: tail -f /mnt/temp-data/logs/brew_master.log"
    echo "   List S3 files: aws s3 ls s3://$(terraform output -raw s3_bucket_name 2>/dev/null || echo 'BUCKET')/ --recursive"
    
    return 0
}

# Handle script arguments
case "${1:-}" in
    --watch|-w)
        echo "🔄 Watching status (press Ctrl+C to stop)..."
        while true; do
            clear
            main
            echo
            echo "Next update in 30 seconds..."
            sleep 30
        done
        ;;
    --help|-h)
        echo "Usage: $0 [--watch|--help]"
        echo "  --watch, -w    Watch status continuously"
        echo "  --help, -h     Show this help"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac