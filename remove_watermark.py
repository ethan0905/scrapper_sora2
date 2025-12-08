#!/usr/bin/env python3
"""
Simple script to remove Sora watermarks from downloaded videos.
Usage: 
  python remove_watermark.py <video_number>           # Process video_001.mp4
  python remove_watermark.py <path/to/video.mp4>      # Process specific video file
  python remove_watermark.py <path/to/folder>         # Process all videos in folder
"""

import sys
from pathlib import Path
from typing import List, Union

# Add the sora-watermark-remover to the path
sys.path.insert(0, str(Path(__file__).parent / "sora-watermark-remover"))

from sorawm.core import SoraWM
from sorawm.schemas import CleanerType


def process_single_video(input_path: Path, output_path: Path, use_fast_mode: bool = False) -> bool:
    """
    Remove watermark from a specific video file.
    
    Args:
        input_path: Path to the input video file
        output_path: Path where the cleaned video will be saved
        use_fast_mode: If True, uses LAMA (fast but may flicker). 
                      If False, uses E2FGVI_HQ (slow but time-consistent and better quality)
    """
    # Check if input exists
    if not input_path.exists():
        print(f"❌ Error: Video not found at {input_path}")
        return False
    
    if not input_path.is_file():
        print(f"❌ Error: {input_path} is not a file")
        return False
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"🎬 Processing: {input_path.name}")
    print(f"📂 Input: {input_path}")
    print(f"💾 Output: {output_path}")
    
    # Check if on Mac and using high-quality mode
    import platform
    if platform.system() == "Darwin" and not use_fast_mode:
        print("\n⚠️  WARNING: You're on macOS using high-quality mode!")
        print("   E2FGVI_HQ doesn't support Apple Silicon GPU (MPS).")
        print("   This will run on CPU and be EXTREMELY SLOW (could take hours).")
        print("\n💡 RECOMMENDATION: Use fast mode instead!")
        print("   Run with: ./quick_remove.sh <input> fast")
        print("   or: python remove_watermark.py <input> fast")
        print("\n   Fast mode (LAMA) works great on Mac and is much quicker!")
        print("\n⏱️  Continuing with CPU processing (this will take a while)...")
    
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


def process_folder(input_folder: Path, output_folder: Path, use_fast_mode: bool = False) -> tuple:
    """
    Process all video files in a folder.
    
    Args:
        input_folder: Path to folder containing videos
        output_folder: Path to folder where cleaned videos will be saved
        use_fast_mode: Processing mode
        
    Returns:
        Tuple of (success_count, failed_count, total_count)
    """
    # Find all video files
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    video_files = []
    for ext in video_extensions:
        video_files.extend(input_folder.glob(f'*{ext}'))
        video_files.extend(input_folder.glob(f'*{ext.upper()}'))
    
    video_files = sorted(set(video_files))
    
    if not video_files:
        print(f"❌ No video files found in {input_folder}")
        return (0, 0, 0)
    
    print(f"\n📁 Found {len(video_files)} video(s) to process")
    print("="*60)
    
    success_count = 0
    failed_count = 0
    
    for i, video_path in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Processing: {video_path.name}")
        print("-"*60)
        
        # Create output path with _cleaned suffix
        output_name = video_path.stem + "_cleaned" + video_path.suffix
        output_path = output_folder / output_name
        
        # Process the video
        success = process_single_video(video_path, output_path, use_fast_mode)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
        
        print("-"*60)
    
    return (success_count, failed_count, len(video_files))


def get_video_path_from_number(video_number: int, base_dir: Path) -> tuple:
    """
    Convert video number to input/output paths.
    
    Returns:
        Tuple of (input_path, output_path)
    """
    videos_dir = base_dir / "videos"
    output_dir = base_dir / "videos_cleaned"
    
    video_filename = f"video_{video_number:03d}.mp4"
    input_path = videos_dir / video_filename
    output_filename = f"video_{video_number:03d}_cleaned.mp4"
    output_path = output_dir / output_filename
    
    return (input_path, output_path)


def main():
    print("="*60)
    print("🎨 Sora Watermark Remover - High Quality Mode")
    print("="*60)
    print()
    
    # Check if input is provided
    if len(sys.argv) < 2:
        import platform
        is_mac = platform.system() == "Darwin"
        
        print("Usage: python remove_watermark.py <input> [mode]")
        print("\nInput Options:")
        print("  <number>           - Video number (e.g., 1 for video_001.mp4)")
        print("  <path/to/video>    - Path to a specific video file")
        print("  <path/to/folder>   - Path to a folder of videos")
        print("\nExamples:")
        print("  python remove_watermark.py 1")
        print("  python remove_watermark.py videos/my_video.mp4")
        print("  python remove_watermark.py /path/to/videos/")
        print("  python remove_watermark.py videos/  # Process entire videos folder")
        print("\nMode (optional):")
        if is_mac:
            print("  Default: Fast mode (LAMA) - GPU accelerated, recommended for Mac")
            print("  hq    : High quality (E2FGVI_HQ) - CPU only on Mac, VERY SLOW")
        else:
            print("  Default: High quality (E2FGVI_HQ) - time-consistent, no flicker")
            print("  fast  : Fast mode (LAMA) - quicker but may have slight flicker")
        
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
    
    base_dir = Path(__file__).parent
    input_arg = sys.argv[1]
    
    # Determine mode (default depends on platform)
    import platform
    is_mac = platform.system() == "Darwin"
    
    # Default to fast mode on Mac (since E2FGVI_HQ doesn't support MPS)
    use_fast_mode = is_mac
    
    if len(sys.argv) >= 3:
        mode = sys.argv[2].lower()
        if mode in ['fast', 'quick', 'lama']:
            use_fast_mode = True
            print("⚡ Fast mode selected - quicker processing")
        elif mode in ['slow', 'hq', 'quality', 'e2fgvi']:
            use_fast_mode = False
            print("✨ High quality mode - time-consistent output")
            if is_mac:
                print("⚠️  Note: Running on CPU (very slow on Mac)")
        else:
            print("✨ Using default mode for your platform")
    else:
        if is_mac:
            print("⚡ Fast mode (default for macOS) - GPU accelerated")
            print("💡 Tip: E2FGVI_HQ mode not recommended on Mac (CPU only, very slow)")
        else:
            print("✨ High quality mode (default) - time-consistent output")
    
    # Determine input type: number, file, or folder
    input_path = Path(input_arg)
    
    # Case 1: Input is a number (e.g., "1" for video_001.mp4)
    if input_arg.isdigit():
        video_number = int(input_arg)
        input_path, output_path = get_video_path_from_number(video_number, base_dir)
        
        success = process_single_video(input_path, output_path, use_fast_mode)
        
        if success:
            print("\n✨ Done! Enjoy your watermark-free video!")
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Case 2: Input is a folder
    elif input_path.is_dir():
        output_folder = base_dir / "videos_cleaned"
        
        print(f"📁 Processing all videos in: {input_path}")
        print(f"💾 Output folder: {output_folder}\n")
        
        success_count, failed_count, total = process_folder(input_path, output_folder, use_fast_mode)
        
        print("\n" + "="*60)
        print("📊 BATCH PROCESSING COMPLETE")
        print("="*60)
        print(f"✅ Successful: {success_count}/{total}")
        print(f"❌ Failed: {failed_count}/{total}")
        print(f"💾 Output location: {output_folder}")
        print("\n✨ Done!")
        
        sys.exit(0 if failed_count == 0 else 1)
    
    # Case 3: Input is a file path
    elif input_path.is_file():
        # Create output path with _cleaned suffix
        output_folder = base_dir / "videos_cleaned"
        output_name = input_path.stem + "_cleaned" + input_path.suffix
        output_path = output_folder / output_name
        
        success = process_single_video(input_path, output_path, use_fast_mode)
        
        if success:
            print("\n✨ Done! Enjoy your watermark-free video!")
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Case 4: Input doesn't exist
    else:
        print(f"❌ Error: '{input_arg}' is not a valid number, file, or folder")
        print("\nPlease provide:")
        print("  - A video number (e.g., 1)")
        print("  - A path to a video file")
        print("  - A path to a folder containing videos")
        sys.exit(1)


if __name__ == "__main__":
    main()
