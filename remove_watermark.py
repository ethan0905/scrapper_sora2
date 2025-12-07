#!/usr/bin/env python3
"""
Simple script to remove Sora watermarks from downloaded videos.
Usage: python remove_watermark.py [video_number]
Example: python remove_watermark.py 1  (processes video_001.mp4)
"""

import sys
from pathlib import Path

# Add the sora-watermark-remover to the path
sys.path.insert(0, str(Path(__file__).parent / "sora-watermark-remover"))

from sorawm.core import SoraWM
from sorawm.schemas import CleanerType


def remove_watermark(video_number: int, use_fast_mode: bool = False):
    """
    Remove watermark from a specific video.
    
    Args:
        video_number: The video number (e.g., 1 for video_001.mp4)
        use_fast_mode: If True, uses LAMA (fast but may flicker). 
                      If False, uses E2FGVI_HQ (slow but time-consistent and better quality)
    """
    # Setup paths
    base_dir = Path(__file__).parent
    videos_dir = base_dir / "videos"
    output_dir = base_dir / "videos_cleaned"
    output_dir.mkdir(exist_ok=True)
    
    # Format video filename
    video_filename = f"video_{video_number:03d}.mp4"
    input_path = videos_dir / video_filename
    output_filename = f"video_{video_number:03d}_cleaned.mp4"
    output_path = output_dir / output_filename
    
    # Check if input exists
    if not input_path.exists():
        print(f"❌ Error: Video not found at {input_path}")
        print(f"Available videos: {sorted([f.name for f in videos_dir.glob('*.mp4')])[:5]}...")
        return False
    
    print(f"🎬 Processing: {video_filename}")
    print(f"📂 Input: {input_path}")
    print(f"💾 Output: {output_path}")
    
    # Choose cleaner type
    if use_fast_mode:
        print(f"⚡ Mode: LAMA (Fast, may have slight flicker)")
        cleaner_type = CleanerType.LAMA
    else:
        print(f"✨ Mode: E2FGVI_HQ (High Quality, time-consistent)")
        cleaner_type = CleanerType.E2FGVI_HQ
    
    print("\n🔧 Initializing watermark remover...")
    
    try:
        # Initialize SoraWM
        sora_wm = SoraWM(cleaner_type=cleaner_type)
        
        print("🚀 Starting watermark removal...")
        print("⏳ This may take a few minutes depending on video length...\n")
        
        # Process the video
        sora_wm.run(input_path, output_path)
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Watermark removed!")
        print("="*60)
        print(f"📁 Cleaned video saved to: {output_path}")
        print(f"📊 Original size: {input_path.stat().st_size / (1024*1024):.2f} MB")
        print(f"📊 Cleaned size: {output_path.stat().st_size / (1024*1024):.2f} MB")
        print("\n💡 Tip: Use 'open videos_cleaned/' to view the result!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("🎨 Sora Watermark Remover")
    print("="*60)
    print()
    
    # Check if video number is provided
    if len(sys.argv) < 2:
        print("Usage: python remove_watermark.py <video_number> [mode]")
        print("\nExamples:")
        print("  python remove_watermark.py 1        # Remove watermark from video_001.mp4 (fast mode)")
        print("  python remove_watermark.py 5 slow   # Remove from video_005.mp4 (slow but better quality)")
        print("\nAvailable modes:")
        print("  fast (default) - Uses LAMA: Quick processing, may have slight flicker")
        print("  slow          - Uses E2FGVI_HQ: Slow but time-consistent, no flicker")
        
        # List some available videos
        videos_dir = Path(__file__).parent / "videos"
        if videos_dir.exists():
            videos = sorted(videos_dir.glob("video_*.mp4"))
            if videos:
                print(f"\n📹 You have {len(videos)} videos available (showing first 10):")
                for i, video in enumerate(videos[:10], 1):
                    size_mb = video.stat().st_size / (1024*1024)
                    print(f"  {i}. {video.name} ({size_mb:.2f} MB)")
        sys.exit(1)
    
    # Parse arguments
    try:
        video_number = int(sys.argv[1])
    except ValueError:
        print(f"❌ Error: '{sys.argv[1]}' is not a valid number")
        print("Please provide a video number (e.g., 1 for video_001.mp4)")
        sys.exit(1)
    
    # Check mode
    use_fast_mode = True
    if len(sys.argv) >= 3:
        mode = sys.argv[2].lower()
        if mode in ['slow', 'hq', 'quality']:
            use_fast_mode = False
            print("ℹ️  Slow mode selected - better quality but takes longer")
        elif mode not in ['fast', 'quick']:
            print(f"⚠️  Unknown mode '{mode}', using fast mode")
    
    # Remove watermark
    success = remove_watermark(video_number, use_fast_mode)
    
    if success:
        print("\n✨ Done! Enjoy your watermark-free video!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
