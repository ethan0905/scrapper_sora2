"""
YouTube Title Generator for Sora Remix Videos

Generates catchy, engaging titles for videos based on metadata including
descriptions, comments, and video context.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional


class TitleGenerator:
    """Generates engaging YouTube titles from video metadata."""
    
    # Common patterns to make titles more engaging
    EMOJI_MAP = {
        'gorilla': '🦍',
        'ape': '🦍',
        'monkey': '🐒',
        'glass': '🪟',
        'break': '💥',
        'smash': '💥',
        'robot': '🤖',
        'ai': '🤖',
        'fire': '🔥',
        'explosion': '💥',
        'water': '💧',
        'ocean': '🌊',
        'space': '🚀',
        'funny': '😂',
        'epic': '⚡',
        'crazy': '🤯',
        'amazing': '✨',
    }
    
    POWER_WORDS = [
        'epic', 'insane', 'incredible', 'amazing', 'shocking', 
        'unbelievable', 'hilarious', 'wild', 'crazy', 'ultimate'
    ]
    
    def __init__(self):
        """Initialize the title generator."""
        pass
    
    def generate_title(
        self, 
        metadata: Dict,
        max_length: int = 100,
        include_emoji: bool = True,
        include_hashtag: bool = False
    ) -> str:
        """
        Generate an engaging title from video metadata.
        
        Args:
            metadata: Video metadata dictionary
            max_length: Maximum title length (YouTube limit is 100)
            include_emoji: Whether to add relevant emojis
            include_hashtag: Whether to add #SoraAI hashtag
            
        Returns:
            Generated title string
        """
        # Extract key information
        description = metadata.get('description', '')
        comments = metadata.get('comments', [])
        creator = metadata.get('creator', '')
        
        # Analyze comments for context
        comment_context = self._analyze_comments(comments)
        
        # Generate title based on available information
        if description and description.lower() != 'sora' and not description.startswith('Follow @'):
            title = self._enhance_description(description, comment_context)
        elif comment_context:
            title = self._generate_from_comments(comment_context)
        else:
            title = self._generate_generic_title(creator)
        
        # Add emojis if enabled
        if include_emoji:
            title = self._add_emojis(title)
        
        # Add hashtag if enabled
        if include_hashtag:
            if len(title) + 8 <= max_length:  # " #SoraAI" = 8 chars
                title += " #SoraAI"
        
        # Ensure title doesn't exceed max length
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        return title.strip()
    
    def _analyze_comments(self, comments: List[Dict]) -> Dict:
        """
        Analyze comments to extract context about the video.
        
        Args:
            comments: List of comment dictionaries
            
        Returns:
            Dictionary with extracted context
        """
        context = {
            'reactions': [],
            'subjects': [],
            'actions': [],
            'objects': [],
            'sentiment': 'neutral',
            'raw_text': ''
        }
        
        if not comments:
            return context
        
        # Combine all comment text
        all_text = ' '.join([c.get('comment_text', '').lower() for c in comments])
        context['raw_text'] = all_text
        
        # Detect subjects (what's in the video)
        subjects = ['gorilla', 'ape', 'monkey', 'robot', 'dog', 'cat', 'car', 
                   'person', 'man', 'woman', 'girl', 'boy', 'animal', 'dinosaur',
                   'dragon', 'alien', 'creature']
        context['subjects'] = [s for s in subjects if s in all_text]
        
        # Detect objects/props
        objects = ['glass', 'rope', 'window', 'door', 'wall', 'car', 'building',
                  'tree', 'rock', 'water', 'fire', 'ice']
        context['objects'] = [o for o in objects if o in all_text]
        
        # Detect actions
        actions = ['break', 'smash', 'escape', 'run', 'jump', 'fly', 'dance', 
                  'fight', 'swim', 'crash', 'explode', 'transform', 'swing',
                  'climb', 'fall', 'chase', 'hide']
        context['actions'] = [a for a in actions if a in all_text]
        
        # Detect reactions
        if any(word in all_text for word in ['lol', 'lmao', 'haha', '😂', 'laugh', 'hilarious', 'funny']):
            context['reactions'].append('funny')
        if any(word in all_text for word in ['crazy', 'insane', 'wild', 'wtf', '🤯']):
            context['reactions'].append('crazy')
        if any(word in all_text for word in ['epic', 'amazing', 'awesome', '🔥']):
            context['reactions'].append('epic')
        if any(word in all_text for word in ['shock', 'surprising', 'unexpected', 'wow']):
            context['reactions'].append('shocking')
        
        # Determine overall sentiment
        if context['reactions']:
            context['sentiment'] = context['reactions'][0]
        
        return context
    
    def _enhance_description(self, description: str, context: Dict) -> str:
        """
        Enhance the video description to make it more engaging.
        
        Args:
            description: Original video description
            context: Context extracted from comments
            
        Returns:
            Enhanced title
        """
        title = description
        
        # Add a power word if sentiment is available and not already present
        if context['sentiment'] != 'neutral':
            power_word = context['sentiment'].capitalize()
            if power_word.lower() not in title.lower():
                title = f"{power_word} {title}"
        
        return title
    
    def _generate_from_comments(self, context: Dict) -> str:
        """
        Generate a title based on comment analysis.
        
        Args:
            context: Context extracted from comments
            
        Returns:
            Generated title
        """
        raw_text = context['raw_text']
        
        # Create a more descriptive title based on context
        if 'gorilla' in context['subjects'] or 'ape' in context['subjects']:
            if 'break' in context['actions'] or 'smash' in context['actions']:
                if 'glass' in context['objects'] or 'glass' in raw_text:
                    if 'free' in raw_text:
                        return "Gorilla Breaks Through Glass and Escapes"
                    return "Gorilla Smashes Through Glass Wall"
                if 'rope' in context['objects'] or 'rope' in raw_text:
                    return "Gorilla Breaks Rope During Tug of War"
                return "Gorilla Breaks Free from Enclosure"
            elif 'escape' in context['actions'] or 'free' in raw_text:
                return "Epic Gorilla Escape Caught on Camera"
            elif 'swing' in context['actions'] or 'rope' in context['objects']:
                return "Gorilla Rope Swing Goes Wrong"
        
        # Robot scenarios
        if 'robot' in context['subjects']:
            if 'dance' in context['actions']:
                return "Robot Busts Incredible Dance Moves"
            elif 'transform' in context['actions']:
                return "Robot Transformation Caught on Camera"
            return "Amazing Robot Does the Unexpected"
        
        # Generic construction if no specific scenario
        parts = []
        
        # Add sentiment/power word
        if context['sentiment'] != 'neutral':
            parts.append(context['sentiment'].capitalize())
        
        # Add subject
        if context['subjects']:
            subject = context['subjects'][0].capitalize()
            parts.append(subject)
        else:
            parts.append('Sora AI')
        
        # Add action
        if context['actions']:
            action = context['actions'][0].capitalize() + 's'
            parts.append(action)
        elif context['objects']:
            parts.append('Interacts With')
            parts.append(context['objects'][0].capitalize())
        else:
            parts.append('Does Something')
            parts.append('Unbelievable')
        
        return ' '.join(parts)
    
    def _generate_generic_title(self, creator: str) -> str:
        """
        Generate a generic title when no other context is available.
        
        Args:
            creator: Video creator username
            
        Returns:
            Generic title
        """
        if creator:
            return f"Epic Sora AI Creation by {creator}"
        return "Amazing Sora AI Generated Video"
    
    def _add_emojis(self, title: str) -> str:
        """
        Add relevant emojis to the title.
        
        Args:
            title: Title without emojis
            
        Returns:
            Title with emojis added
        """
        # Don't add if already has emojis
        if any(ord(c) > 127 for c in title):
            return title
        
        title_lower = title.lower()
        
        # Find the first matching keyword and add its emoji
        for keyword, emoji in self.EMOJI_MAP.items():
            if keyword in title_lower:
                # Add emoji at the end
                return f"{title} {emoji}"
        
        # Default emoji for Sora AI content
        return f"{title} ✨"
    
    def generate_title_from_file(
        self, 
        metadata_path: Path,
        **kwargs
    ) -> str:
        """
        Generate title from a metadata JSON file.
        
        Args:
            metadata_path: Path to metadata JSON file
            **kwargs: Additional arguments for generate_title
            
        Returns:
            Generated title
        """
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return self.generate_title(metadata, **kwargs)
    
    def batch_generate_titles(
        self,
        metadata_files: List[Path],
        output_file: Optional[Path] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Generate titles for multiple videos.
        
        Args:
            metadata_files: List of paths to metadata JSON files
            output_file: Optional path to save title mapping JSON
            **kwargs: Additional arguments for generate_title
            
        Returns:
            Dictionary mapping video file paths to generated titles
        """
        titles = {}
        
        for metadata_path in metadata_files:
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Get the video file path from metadata
                video_file = metadata.get('downloaded_file', '')
                if not video_file:
                    # Infer from metadata filename
                    video_file = str(metadata_path).replace('_metadata.json', '.mp4')
                
                # Generate title
                title = self.generate_title(metadata, **kwargs)
                titles[video_file] = title
                
                print(f"✓ {Path(video_file).name}: {title}")
                
            except Exception as e:
                print(f"✗ Error processing {metadata_path}: {e}")
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(titles, f, indent=2, ensure_ascii=False)
            print(f"\n📝 Titles saved to: {output_file}")
        
        return titles


def main():
    """CLI interface for title generation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate YouTube titles for Sora remix videos'
    )
    parser.add_argument(
        'metadata_path',
        type=str,
        help='Path to metadata JSON file or directory containing metadata files'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file for title mapping JSON'
    )
    parser.add_argument(
        '--no-emoji',
        action='store_true',
        help='Disable emoji in titles'
    )
    parser.add_argument(
        '--hashtag',
        action='store_true',
        help='Add #SoraAI hashtag to titles'
    )
    parser.add_argument(
        '--max-length',
        type=int,
        default=100,
        help='Maximum title length (default: 100)'
    )
    
    args = parser.parse_args()
    
    generator = TitleGenerator()
    path = Path(args.metadata_path)
    
    kwargs = {
        'max_length': args.max_length,
        'include_emoji': not args.no_emoji,
        'include_hashtag': args.hashtag
    }
    
    if path.is_file():
        # Single file
        title = generator.generate_title_from_file(path, **kwargs)
        print(f"\nGenerated Title:\n{title}")
        
    elif path.is_dir():
        # Directory - find all metadata files
        metadata_files = list(path.rglob('*_metadata.json'))
        
        if not metadata_files:
            print(f"No metadata files found in {path}")
            return
        
        print(f"\n🎬 Generating titles for {len(metadata_files)} videos...\n")
        
        output_file = Path(args.output) if args.output else path / 'titles.json'
        generator.batch_generate_titles(
            metadata_files,
            output_file=output_file,
            **kwargs
        )
        
    else:
        print(f"Error: {path} is not a valid file or directory")


if __name__ == '__main__':
    main()
