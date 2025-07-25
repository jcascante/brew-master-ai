#!/bin/bash
# Upload files to S3 for processing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"

echo "🍺 Brew Master AI - File Upload"
echo "==============================="

# Function to get S3 bucket name
get_s3_bucket() {
    cd "$TERRAFORM_DIR"
    terraform output -raw s3_bucket_name 2>/dev/null || echo ""
}

# Function to validate file types
validate_files() {
    local files=("$@")
    local valid_extensions=("mp4" "avi" "mov" "mkv" "pptx" "ppt" "wav" "mp3" "m4a")
    local valid_files=()
    local invalid_files=()
    
    echo "📋 Validating file types..."
    
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "   ❌ File not found: $file"
            invalid_files+=("$file")
            continue
        fi
        
        local extension="${file##*.}"
        extension="${extension,,}" # Convert to lowercase
        
        local is_valid=false
        for valid_ext in "${valid_extensions[@]}"; do
            if [ "$extension" = "$valid_ext" ]; then
                is_valid=true
                break
            fi
        done
        
        if [ "$is_valid" = true ]; then
            echo "   ✅ Valid: $file ($extension)"
            valid_files+=("$file")
        else
            echo "   ⚠️  Unknown type: $file ($extension)"
            valid_files+=("$file") # Include anyway, but warn
        fi
    done
    
    if [ ${#invalid_files[@]} -gt 0 ]; then
        echo
        echo "❌ Some files could not be found:"
        printf '   %s\n' "${invalid_files[@]}"
        return 1
    fi
    
    echo
    echo "✅ Found ${#valid_files[@]} files to upload"
    echo "📊 Supported types: ${valid_extensions[*]}"
    
    return 0
}

# Function to calculate upload size and cost estimate
calculate_upload_info() {
    local files=("$@")
    local total_size=0
    
    echo "📊 Upload Analysis:"
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
            total_size=$((total_size + size))
            
            local size_mb=$(echo "scale=2; $size / 1024 / 1024" | bc -l)
            printf "   📁 %s: %.2f MB\n" "$(basename "$file")" "$size_mb"
        fi
    done
    
    local total_gb=$(echo "scale=3; $total_size / 1024 / 1024 / 1024" | bc -l)
    local storage_cost=$(echo "scale=4; $total_gb * 0.023" | bc -l)
    
    printf "\n   📦 Total size: %.3f GB\n" "$total_gb"
    printf "   💰 Monthly storage cost: \$%.4f\n" "$storage_cost"
    
    # Estimate upload time (assuming 10 Mbps average)
    local upload_time_seconds=$(echo "scale=1; $total_size * 8 / (10 * 1024 * 1024)" | bc -l)
    local upload_time_minutes=$(echo "scale=1; $upload_time_seconds / 60" | bc -l)
    
    if [ "$(echo "$upload_time_minutes < 1" | bc -l)" == "1" ]; then
        printf "   ⏱️  Estimated upload time: %.0f seconds\n" "$upload_time_seconds"
    else
        printf "   ⏱️  Estimated upload time: %.1f minutes\n" "$upload_time_minutes"
    fi
    
    return 0
}

# Function to upload files with progress
upload_files() {
    local bucket_name="$1"
    shift
    local files=("$@")
    
    echo
    echo "📤 Uploading files to S3..."
    echo "   Bucket: $bucket_name"
    echo "   Destination: s3://$bucket_name/input/"
    echo
    
    local uploaded_count=0
    local failed_count=0
    
    for file in "${files[@]}"; do
        local filename=$(basename "$file")
        echo "   Uploading: $filename"
        
        if aws s3 cp "$file" "s3://$bucket_name/input/" --progress; then
            echo "   ✅ Success: $filename"
            ((uploaded_count++))
        else
            echo "   ❌ Failed: $filename"
            ((failed_count++))
        fi
        echo
    done
    
    echo "📊 Upload Summary:"
    echo "   ✅ Successful: $uploaded_count files"
    echo "   ❌ Failed: $failed_count files"
    
    if [ $failed_count -gt 0 ]; then
        return 1
    fi
    
    return 0
}

# Function to show upload results
show_upload_results() {
    local bucket_name="$1"
    
    echo
    echo "🎉 Upload Complete!"
    echo "=================="
    
    echo "📁 Files in S3 input directory:"
    aws s3 ls "s3://$bucket_name/input/" --human-readable --recursive | sed 's/^/   /'
    
    echo
    echo "📋 Next Steps:"
    echo "   1. Start processing: ./scripts/start-processing.sh"
    echo "   2. Monitor progress: ./scripts/check-status.sh"
    echo "   3. Check results: aws s3 ls s3://$bucket_name/processed/"
    
    echo
    echo "🔗 Direct S3 Commands:"
    echo "   List files: aws s3 ls s3://$bucket_name/input/"
    echo "   Remove file: aws s3 rm s3://$bucket_name/input/filename"
    echo "   Upload more: aws s3 cp file.mp4 s3://$bucket_name/input/"
    
    return 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] <files...>"
    echo
    echo "Upload files to S3 for Brew Master AI processing"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -d, --dir      Upload entire directory"
    echo "  -r, --recursive Upload directory recursively"
    echo "  --dry-run      Show what would be uploaded without uploading"
    echo
    echo "Supported file types:"
    echo "  Videos: mp4, avi, mov, mkv"
    echo "  Audio: wav, mp3, m4a"
    echo "  Presentations: pptx, ppt"
    echo
    echo "Examples:"
    echo "  $0 video1.mp4 video2.mp4           # Upload specific files"
    echo "  $0 -d /path/to/videos/              # Upload entire directory"
    echo "  $0 -r /path/to/project/             # Upload directory recursively"
    echo "  $0 --dry-run *.mp4                  # Preview upload without doing it"
    echo
    return 0
}

# Function to handle directory upload
upload_directory() {
    local dir="$1"
    local recursive="$2"
    local bucket_name="$3"
    
    echo "📁 Uploading directory: $dir"
    
    local aws_sync_cmd="aws s3 sync \"$dir\" \"s3://$bucket_name/input/\""
    
    if [ "$recursive" != "true" ]; then
        aws_sync_cmd="$aws_sync_cmd --exclude \"*/*\""  # Only top level files
    fi
    
    echo "   Command: $aws_sync_cmd"
    echo
    
    if eval "$aws_sync_cmd"; then
        echo "✅ Directory upload successful"
        return 0
    else
        echo "❌ Directory upload failed"
        return 1
    fi
}

# Main execution
main() {
    local dry_run=false
    local upload_dir=false
    local recursive=false
    local directory=""
    local files=()
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -d|--dir)
                upload_dir=true
                directory="$2"
                shift 2
                ;;
            -r|--recursive)
                recursive=true
                if [ "$upload_dir" = false ]; then
                    upload_dir=true
                    directory="$2"
                    shift 2
                else
                    shift
                fi
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            -*)
                echo "❌ Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                files+=("$1")
                shift
                ;;
        esac
    done
    
    # Check if persistent infrastructure exists
    cd "$TERRAFORM_DIR"
    if ! terraform show -json | jq -e '.values.root_module.child_modules[] | select(.address == "module.persistent")' > /dev/null 2>&1; then
        echo "❌ Persistent infrastructure not found"
        echo "   Run: terraform apply -target=module.persistent"
        exit 1
    fi
    
    # Get S3 bucket name
    bucket_name=$(get_s3_bucket)
    if [ -z "$bucket_name" ]; then
        echo "❌ Could not get S3 bucket name"
        exit 1
    fi
    
    echo "📦 Using S3 bucket: $bucket_name"
    echo
    
    # Handle directory upload
    if [ "$upload_dir" = true ]; then
        if [ -z "$directory" ] && [ ${#files[@]} -gt 0 ]; then
            directory="${files[0]}"
        fi
        
        if [ ! -d "$directory" ]; then
            echo "❌ Directory not found: $directory"
            exit 1
        fi
        
        if [ "$dry_run" = true ]; then
            echo "🔍 Dry run - would upload directory: $directory"
            if [ "$recursive" = true ]; then
                echo "   Mode: Recursive"
            else
                echo "   Mode: Top-level files only"
            fi
            
            echo "   Files that would be uploaded:"
            if [ "$recursive" = true ]; then
                find "$directory" -type f | head -20 | sed 's/^/   /'
            else
                find "$directory" -maxdepth 1 -type f | head -20 | sed 's/^/   /'
            fi
            exit 0
        fi
        
        upload_directory "$directory" "$recursive" "$bucket_name"
        show_upload_results "$bucket_name"
        exit $?
    fi
    
    # Handle file upload
    if [ ${#files[@]} -eq 0 ]; then
        echo "❌ No files specified"
        echo
        show_usage
        exit 1
    fi
    
    # Validate files
    if ! validate_files "${files[@]}"; then
        exit 1
    fi
    
    # Calculate upload info
    calculate_upload_info "${files[@]}"
    
    # Dry run check
    if [ "$dry_run" = true ]; then
        echo
        echo "🔍 Dry run complete - no files uploaded"
        echo "   Remove --dry-run to proceed with upload"
        exit 0
    fi
    
    # Confirm upload
    echo
    read -p "Proceed with upload? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Upload cancelled"
        exit 0
    fi
    
    # Upload files
    if upload_files "$bucket_name" "${files[@]}"; then
        show_upload_results "$bucket_name"
    else
        echo "❌ Upload completed with errors"
        exit 1
    fi
    
    return 0
}

# Run main function
main "$@"