"""
Vision-Based YouTube Title Generator using OpenAI GPT-4o mini

Analyzes video frames using GPT-4o vision to generate accurate,
engaging titles based on what's actually happening in the video.
"""

import json
import base64
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import cv2
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# SYSTEM PROMPT - EDIT THIS TO CUSTOMIZE TITLE GENERATION STYLE
# ============================================================================

TITLE_GENERATION_PROMPT = """You are an expert YouTube title writer specializing in AI-generated video content.

Your task is to analyze video frames and create compelling, click-worthy titles that accurately describe what's happening while being engaging and SEO-optimized.

Guidelines:
- Be SPECIFIC about what's actually happening in the video
- Use action words and power phrases (Epic, Amazing, Incredible, Wild, Crazy)
- Make it intriguing - hint at what happens without spoiling everything
- Include visual details that make the title descriptive
- Keep it concise and punchy
- Use title case (Capitalize Important Words)
- Be authentic - don't exaggerate or mislead

Examples of GOOD titles:
- "Gorilla Smashes Through Glass Wall and Escapes Zoo 🦍"
- "Robot Dog Does Backflip Over Moving Car 🤖"
- "Time-Lapse: City Transforms Into Futuristic Metropolis ✨"
- "Epic Chase Scene: Drone vs. Sports Car Through City 🚁"

Examples of BAD titles:
- "Video" (too generic)
- "You Won't BELIEVE What Happens Next!!!" (clickbait)
- "sora video" (not descriptive)
- "Cool stuff" (vague)
"""

# Style-specific instructions (you can customize these too)
STYLE_PROMPTS = {
    'engaging': """
    Make it catchy and intriguing. Use action words and create curiosity.
    Perfect for viral content and entertainment.
    """,
    
    'descriptive': """
    Be clear, accurate, and straightforward. Focus on describing exactly what happens.
    Perfect for educational or documentary-style content.
    """,
    
    'clickbait': """
    Create maximum curiosity with emotional triggers and cliffhangers.
    Use phrases like "You Won't Believe", "What Happens Next", "Shocking".
    Perfect for maximizing clicks (use responsibly).
    """,
    
    'professional': """
    Keep it professional, informative, and suitable for business or educational contexts.
    Avoid slang, emojis (unless requested), and overly casual language.
    """,
    
    'viral': """
    Optimize for virality: short, punchy, with strong emotional hooks.
    Use trending language and relatable scenarios.
    Perfect for TikTok/YouTube Shorts style content.
    """
}

# ============================================================================


class VisionTitleGenerator:
    """Generates YouTube titles by analyzing video frames with GPT-4o vision."""
    
    def __init__(self, api_key: Optional[str] = None, rate_limit_rpm: int = 20):
        """
        Initialize the vision title generator.
        
        Args:
            api_key: OpenAI API key (or uses OPENAI_API_KEY env var)
            rate_limit_rpm: Max requests per minute (default: 20 for safety)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Rate limiting configuration
        self.rate_limit_rpm = rate_limit_rpm
        self.min_delay_seconds = 2.0  # Minimum delay between calls
        self.last_call_time = None
        self.call_times = []  # Track recent API calls
        
        print(f"⚡ Rate limit: {rate_limit_rpm} requests/minute")
    
    def _rate_limit_wait(self):
        """
        Enforce rate limiting to prevent OpenAI API bans.
        
        - Ensures minimum delay between calls
        - Limits requests per minute
        - Logs when rate limit is hit
        """
        now = datetime.now()
        
        # Remove calls older than 1 minute
        self.call_times = [
            t for t in self.call_times 
            if now - t < timedelta(minutes=1)
        ]
        
        # If we've hit the per-minute limit, wait
        if len(self.call_times) >= self.rate_limit_rpm:
            oldest_call = self.call_times[0]
            wait_until = oldest_call + timedelta(minutes=1)
            sleep_seconds = (wait_until - now).total_seconds()
            
            if sleep_seconds > 0:
                print(f"⏳ Rate limit reached ({self.rate_limit_rpm} RPM), waiting {sleep_seconds:.1f}s...")
                time.sleep(sleep_seconds)
                # Clean up old calls after waiting
                now = datetime.now()
                self.call_times = [
                    t for t in self.call_times 
                    if now - t < timedelta(minutes=1)
                ]
        
        # Enforce minimum delay between consecutive calls
        if self.last_call_time:
            elapsed = (now - self.last_call_time).total_seconds()
            if elapsed < self.min_delay_seconds:
                sleep_time = self.min_delay_seconds - elapsed
                time.sleep(sleep_time)
        
        # Record this call
        self.last_call_time = datetime.now()
        self.call_times.append(self.last_call_time)
    
    def extract_frames(
        self,
        video_path: str,
        num_frames: int = 4,
        method: str = 'uniform'
    ) -> List[str]:
        """
        Extract frames from video for analysis.
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract
            method: 'uniform' (evenly spaced) or 'key' (detect scene changes)
            
        Returns:
            List of base64-encoded frame images
        """
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video info
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"📹 Video info: {duration:.1f}s, {total_frames} frames, {fps:.1f} fps")
        
        frames = []
        
        if method == 'uniform':
            # Extract evenly spaced frames
            frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
        else:
            # For now, use uniform - can implement scene detection later
            frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
        
        for idx in frame_indices:
            video.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = video.read()
            
            if ret:
                # Resize to reduce token usage
                height, width = frame.shape[:2]
                max_size = 512
                if max(height, width) > max_size:
                    scale = max_size / max(height, width)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Convert to JPEG and encode to base64
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_b64 = base64.b64encode(buffer).decode('utf-8')
                frames.append(frame_b64)
                
                print(f"  ✓ Extracted frame {idx}/{total_frames} ({idx/fps:.1f}s)")
        
        video.release()
        
        print(f"✅ Extracted {len(frames)} frames\n")
        return frames
    
    def generate_title(
        self,
        video_path: str,
        metadata: Optional[Dict] = None,
        num_frames: int = 4,
        max_length: int = 100,
        include_emoji: bool = True,
        include_hashtag: bool = True,
        style: str = 'engaging'
    ) -> str:
        """
        Generate a title by analyzing video frames with GPT-4o vision.
        
        Args:
            video_path: Path to video file
            metadata: Optional metadata for additional context
            num_frames: Number of frames to analyze
            max_length: Maximum title length
            include_emoji: Whether to include emojis
            include_hashtag: Whether to add #SoraAI hashtag
            style: 'engaging', 'descriptive', 'clickbait', 'professional'
            
        Returns:
            Generated title string
        """
        print(f"🎬 Analyzing video: {Path(video_path).name}")
        
        # Extract frames
        frames = self.extract_frames(video_path, num_frames=num_frames)
        
        # Build the prompt
        prompt = self._build_prompt(metadata, max_length, include_emoji, include_hashtag, style)
        
        # Prepare messages with frames
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        # Add frames as images
        for i, frame_b64 in enumerate(frames):
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_b64}",
                    "detail": "low"  # Use low detail to save tokens
                }
            })
        
        # Call GPT-4o vision (with rate limiting)
        print("🤖 Generating title with GPT-4o mini vision...\n")
        
        # Enforce rate limiting before API call
        self._rate_limit_wait()
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )
        
        title = response.choices[0].message.content.strip()
        
        # Remove quotes if present
        if title.startswith('"') and title.endswith('"'):
            title = title[1:-1]
        if title.startswith("'") and title.endswith("'"):
            title = title[1:-1]
        
        # Ensure it fits max length
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        return title
    
    def _build_prompt(
        self,
        metadata: Optional[Dict],
        max_length: int,
        include_emoji: bool,
        include_hashtag: bool,
        style: str
    ) -> str:
        """
        Build the GPT-4o prompt for title generation.
        
        Args:
            metadata: Video metadata
            max_length: Maximum title length
            include_emoji: Whether to include emojis
            include_hashtag: Whether to include hashtags
            style: Title style
            
        Returns:
            Prompt string
        """
        # Start with the system prompt
        prompt_parts = [
            TITLE_GENERATION_PROMPT,
            "",
            "===== VIDEO ANALYSIS =====",
            "",
            "Analyze the provided video frames (showing different moments throughout the video).",
        ]
        
        # Add metadata context if available
        if metadata:
            prompt_parts.append("\n📊 Additional Context:")
            
            if metadata.get('description'):
                desc = metadata['description']
                if not desc.startswith('Follow @'):
                    prompt_parts.append(f"  • Original description: {desc}")
            
            if metadata.get('creator'):
                prompt_parts.append(f"  • Creator: {metadata['creator']}")
            
            if metadata.get('likes'):
                prompt_parts.append(f"  • Likes: {metadata['likes']}")
            
            # Add some top comments for context
            comments = metadata.get('comments', [])
            if comments:
                top_comments = [c.get('comment_text', '') for c in comments[:3] if c.get('comment_text')]
                if top_comments:
                    prompt_parts.append(f"  • Top viewer reactions: {'; '.join(top_comments)}")
        
        # Add style-specific instructions
        style_instruction = STYLE_PROMPTS.get(style, STYLE_PROMPTS['engaging'])
        prompt_parts.extend([
            "",
            "🎨 Style:",
            style_instruction.strip(),
        ])
        
        # Add requirements
        prompt_parts.extend([
            "",
            "📋 Requirements:",
            f"  • Maximum {max_length} characters (including emojis/hashtags)",
        ])
        
        if include_emoji:
            prompt_parts.append("  • Include 1-2 relevant emojis that enhance the title")
        else:
            prompt_parts.append("  • NO emojis")
        
        if include_hashtag:
            prompt_parts.append("  • End with #SoraAI hashtag")
        else:
            prompt_parts.append("  • NO hashtags")
        
        prompt_parts.extend([
            "  • Use title case (Capitalize Important Words)",
            "  • Be specific and descriptive based on what you see",
            "  • Make it SEO-friendly with relevant keywords",
            "",
            "⚡ Output ONLY the title - no quotes, no explanation, just the title:"
        ])
        
        return "\n".join(prompt_parts)
    
    def batch_generate_titles(
        self,
        video_files: List[str],
        metadata_dir: Optional[str] = None,
        output_file: Optional[str] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Generate titles for multiple videos.
        
        Args:
            video_files: List of video file paths
            metadata_dir: Directory containing metadata JSON files
            output_file: Optional path to save title mapping
            **kwargs: Additional arguments for generate_title
            
        Returns:
            Dictionary mapping video paths to titles
        """
        titles = {}
        
        for i, video_path in enumerate(video_files, 1):
            print(f"\n{'='*60}")
            print(f"Video {i}/{len(video_files)}")
            print(f"{'='*60}\n")
            
            try:
                # Load metadata if available
                metadata = None
                if metadata_dir:
                    video_name = Path(video_path).stem
                    metadata_path = Path(metadata_dir) / f"{video_name}_metadata.json"
                    if metadata_path.exists():
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                
                # Generate title
                title = self.generate_title(video_path, metadata=metadata, **kwargs)
                titles[video_path] = title
                
                print(f"✅ Generated: {title}\n")
                
            except Exception as e:
                print(f"❌ Error processing {video_path}: {e}\n")
                titles[video_path] = f"Sora AI Video - {Path(video_path).stem}"
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(titles, f, indent=2, ensure_ascii=False)
            print(f"\n📝 Titles saved to: {output_file}")
        
        return titles
    
    def generate_title_from_file(
        self,
        video_path: str,
        **kwargs
    ) -> str:
        """
        Generate title from a video file (with auto-detected metadata).
        
        Args:
            video_path: Path to video file
            **kwargs: Additional arguments for generate_title
            
        Returns:
            Generated title
        """
        # Try to find metadata file
        video_p = Path(video_path)
        metadata_path = video_p.parent / f"{video_p.stem}_metadata.json"
        
        metadata = None
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        return self.generate_title(video_path, metadata=metadata, **kwargs)


def main():
    """CLI interface for vision-based title generation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate YouTube titles using GPT-4o vision analysis'
    )
    parser.add_argument(
        'video_path',
        type=str,
        help='Path to video file or directory containing videos'
    )
    parser.add_argument(
        '-k', '--api-key',
        type=str,
        help='OpenAI API key (or set OPENAI_API_KEY env var)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file for title mapping JSON'
    )
    parser.add_argument(
        '-n', '--num-frames',
        type=int,
        default=4,
        help='Number of frames to analyze (default: 4)'
    )
    parser.add_argument(
        '--no-emoji',
        action='store_true',
        help='Disable emoji in titles'
    )
    parser.add_argument(
        '--no-hashtag',
        action='store_true',
        help='Disable #SoraAI hashtag'
    )
    parser.add_argument(
        '--style',
        type=str,
        choices=['engaging', 'descriptive', 'clickbait', 'professional', 'viral'],
        default='engaging',
        help='Title style (default: engaging)'
    )
    parser.add_argument(
        '--max-length',
        type=int,
        default=100,
        help='Maximum title length (default: 100)'
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    try:
        generator = VisionTitleGenerator(api_key=args.api_key)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nSet your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("Or pass it with --api-key flag")
        return
    
    path = Path(args.video_path)
    
    kwargs = {
        'num_frames': args.num_frames,
        'max_length': args.max_length,
        'include_emoji': not args.no_emoji,
        'include_hashtag': not args.no_hashtag,
        'style': args.style
    }
    
    if path.is_file():
        # Single file
        title = generator.generate_title_from_file(str(path), **kwargs)
        print(f"\n{'='*60}")
        print("GENERATED TITLE:")
        print(f"{'='*60}")
        print(title)
        print(f"{'='*60}\n")
        
    elif path.is_dir():
        # Directory - find all video files
        video_files = []
        for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
            video_files.extend(path.rglob(f'*{ext}'))
        
        # Filter out _start files and duplicates
        video_files = [
            str(v) for v in video_files 
            if '_start' not in v.stem and 'all_remixes' not in v.stem
        ]
        
        if not video_files:
            print(f"❌ No video files found in {path}")
            return
        
        print(f"🎬 Found {len(video_files)} videos to analyze\n")
        
        output_file = args.output or path / 'vision_titles.json'
        generator.batch_generate_titles(
            video_files,
            metadata_dir=str(path),
            output_file=str(output_file),
            **kwargs
        )
        
    else:
        print(f"❌ Error: {path} is not a valid file or directory")


if __name__ == '__main__':
    main()
