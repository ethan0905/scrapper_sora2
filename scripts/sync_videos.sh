#!/bin/bash
# sync_videos.sh - Sync videos from cloud VM to local machine
# Usage: ./scripts/sync_videos.sh YOUR_DROPLET_IP

set -e

if [ -z "$1" ]; then
    echo "❌ Error: Please provide your VM IP address"
    echo ""
    echo "Usage: ./scripts/sync_videos.sh YOUR_VM_IP"
    echo ""
    echo "Example:"
    echo "  ./scripts/sync_videos.sh 123.456.789.012"
    exit 1
fi

VM_IP="$1"
REMOTE_PATH="/root/scrapper_sora2/videos_batch"
LOCAL_PATH="./videos_synced"

echo "🔄 Syncing videos from cloud VM..."
echo "========================================"
echo "VM IP: $VM_IP"
echo "Remote path: $REMOTE_PATH"
echo "Local path: $LOCAL_PATH"
echo ""

# Create local directory if it doesn't exist
mkdir -p "$LOCAL_PATH"

# Sync videos
echo "📥 Starting sync..."
rsync -avz --progress \
    --include="*/" \
    --include="*.mp4" \
    --include="*.mov" \
    --include="*.avi" \
    --include="*.json" \
    --include="*.txt" \
    --exclude="*" \
    "root@$VM_IP:$REMOTE_PATH/" \
    "$LOCAL_PATH/"

echo ""
echo "✅ Sync complete!"
echo ""
echo "📊 Local videos:"
ls -lh "$LOCAL_PATH" | wc -l | xargs -I {} echo "   {} files"
du -sh "$LOCAL_PATH" | awk '{print "   Total size: " $1}'
echo ""
echo "💡 Tip: Run this script regularly to backup videos from VM"
