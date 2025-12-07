#!/usr/bin/env python3
"""
Interactive Sora Scraper Interface
Guides users through scraping options with a friendly menu system.
"""

import os
import sys
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a colored header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_section(text):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'-'*len(text)}{Colors.END}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def get_choice(prompt, options, default=None):
    """Get user choice from a list of options"""
    while True:
        if default:
            choice = input(f"{prompt} [{default}]: ").strip() or default
        else:
            choice = input(f"{prompt}: ").strip()
        
        if choice.lower() in [str(i) for i in range(1, len(options) + 1)] + options:
            return choice
        
        print_error(f"Invalid choice. Please choose from: {', '.join(options)}")


def get_yes_no(prompt, default='y'):
    """Get yes/no input from user"""
    while True:
        choice = input(f"{prompt} [y/n, default={default}]: ").strip().lower() or default
        if choice in ['y', 'yes', 'n', 'no']:
            return choice in ['y', 'yes']
        print_error("Please enter 'y' or 'n'")


def get_number(prompt, default=None, min_val=1, max_val=None):
    """Get a number from user"""
    while True:
        if default:
            value = input(f"{prompt} [{default}]: ").strip() or str(default)
        else:
            value = input(f"{prompt}: ").strip()
        
        try:
            num = int(value)
            if num < min_val:
                print_error(f"Please enter a number >= {min_val}")
                continue
            if max_val and num > max_val:
                print_error(f"Please enter a number <= {max_val}")
                continue
            return num
        except ValueError:
            print_error("Please enter a valid number")


def get_url(prompt):
    """Get URL from user"""
    while True:
        url = input(f"{prompt}: ").strip()
        if url:
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        print_error("URL cannot be empty")


def show_welcome():
    """Show welcome screen"""
    print_header("🎬 SORA VIDEO SCRAPER - Interactive Mode")
    print(f"{Colors.BOLD}Welcome!{Colors.END} This interactive tool will guide you through")
    print("extracting videos or metadata from Sora.\n")
    print_info("At any time, press Ctrl+C to exit")


def choose_mode():
    """Let user choose scraping mode"""
    print_section("Step 1: Choose Scraping Source")
    print("\nWhere do you want to scrape from?\n")
    print(f"  {Colors.BOLD}1.{Colors.END} Home Page (Sora explore/top feed)")
    print(f"     {Colors.CYAN}→ Get trending videos from the homepage{Colors.END}")
    print()
    print(f"  {Colors.BOLD}2.{Colors.END} User Profile (specific creator)")
    print(f"     {Colors.CYAN}→ Get videos from a specific user's profile{Colors.END}")
    print()
    
    choice = get_choice("Choose an option", ['1', '2', 'home', 'profile'], default='2')
    
    if choice in ['1', 'home']:
        return 'home', None
    else:
        print()
        print_info("Example: https://sora.chatgpt.com/user/johndoe")
        profile_url = get_url("Enter the profile URL")
        return 'profile', profile_url


def choose_output_mode():
    """Let user choose output mode"""
    print_section("Step 2: Choose Output Mode")
    print("\nWhat do you want to extract?\n")
    print(f"  {Colors.BOLD}1.{Colors.END} {Colors.GREEN}Metadata (JSON){Colors.END} - {Colors.BOLD}RECOMMENDED{Colors.END}")
    print(f"     {Colors.CYAN}→ Extract video info: creator, description, comments, likes{Colors.END}")
    print(f"     {Colors.CYAN}→ Perfect for building TikTok-like apps{Colors.END}")
    print(f"     {Colors.CYAN}→ Fast, small files (KB){Colors.END}")
    print()
    print(f"  {Colors.BOLD}2.{Colors.END} Video Files (MP4)")
    print(f"     {Colors.CYAN}→ Download actual video files{Colors.END}")
    print(f"     {Colors.CYAN}→ For archiving purposes{Colors.END}")
    print(f"     {Colors.CYAN}→ Slow, large files (GB){Colors.END}")
    print()
    
    choice = get_choice("Choose an option", ['1', '2', 'metadata', 'video'], default='1')
    return choice in ['1', 'metadata']


def choose_metadata_format():
    """Let user choose metadata output format"""
    print_section("Step 2b: Metadata Format")
    print("\nHow do you want to save the metadata?\n")
    print(f"  {Colors.BOLD}1.{Colors.END} Single JSON file (all videos together)")
    print(f"     {Colors.CYAN}→ Output: metadata.json{Colors.END}")
    print(f"     {Colors.CYAN}→ Good for: Small datasets, simple import{Colors.END}")
    print()
    print(f"  {Colors.BOLD}2.{Colors.END} Multiple JSON files (one per video)")
    print(f"     {Colors.CYAN}→ Output: metadata/ folder with separate files{Colors.END}")
    print(f"     {Colors.CYAN}→ Good for: Large datasets, incremental processing{Colors.END}")
    print()
    
    choice = get_choice("Choose an option", ['1', '2', 'single', 'multiple'], default='1')
    return choice in ['2', 'multiple']


def choose_quantity():
    """Let user choose how many videos to scrape"""
    print_section("Step 3: Choose Quantity")
    print("\nHow many videos do you want to scrape?\n")
    print(f"  {Colors.BOLD}1.{Colors.END} Specific number (e.g., 20 videos)")
    print(f"  {Colors.BOLD}2.{Colors.END} ALL videos (scrape everything available)")
    print()
    
    choice = get_choice("Choose an option", ['1', '2', 'specific', 'all'], default='1')
    
    if choice in ['1', 'specific']:
        print()
        num_videos = get_number("Enter number of videos", default=20, min_val=1)
        return False, num_videos
    else:
        print_warning("This may take a long time for profiles with many videos!")
        confirm = get_yes_no("Are you sure you want to scrape ALL videos?", default='n')
        if confirm:
            return True, None
        else:
            num_videos = get_number("Enter number of videos instead", default=20, min_val=1)
            return False, num_videos


def choose_advanced_options():
    """Let user choose advanced options"""
    print_section("Step 4: Advanced Options")
    print()
    
    # Slow mode
    print(f"{Colors.BOLD}Slow Mode:{Colors.END}")
    print("  Use slower scrolling and random pauses to avoid detection")
    print("  Recommended for large extractions (--all flag)")
    use_slow = get_yes_no("Enable slow mode?", default='n')
    print()
    
    # Existing Chrome
    print(f"{Colors.BOLD}Existing Chrome Session:{Colors.END}")
    print("  Connect to an existing Chrome session (no re-login needed)")
    print("  You must launch Chrome first with: ./launch_chrome.sh")
    use_existing = get_yes_no("Use existing Chrome session?", default='n')
    print()
    
    # Delay
    if not use_slow:
        print(f"{Colors.BOLD}Scroll Delay:{Colors.END}")
        print("  Time to wait between scrolls (seconds)")
        delay = get_number("Enter delay", default=2, min_val=1, max_val=10)
    else:
        delay = 5  # Default for slow mode
    
    return {
        'slow': use_slow,
        'existing_chrome': use_existing,
        'delay': delay
    }


def show_documentation_links(metadata_mode):
    """Show relevant documentation links"""
    print_section("📚 Helpful Documentation")
    print()
    
    if metadata_mode:
        print(f"  📖 {Colors.UNDERLINE}GETTING_STARTED.md{Colors.END} - Step-by-step tutorial")
        print(f"  ⚡ {Colors.UNDERLINE}METADATA_QUICK_REF.md{Colors.END} - Quick reference")
        print(f"  📖 {Colors.UNDERLINE}METADATA_MODE.md{Colors.END} - Complete guide")
        print(f"  🎯 {Colors.UNDERLINE}AT_A_GLANCE.md{Colors.END} - Visual guide")
        print(f"  💻 {Colors.UNDERLINE}example_metadata_usage.py{Colors.END} - Code examples")
    else:
        print(f"  📖 {Colors.UNDERLINE}USAGE_GUIDE.md{Colors.END} - Complete usage guide")
        print(f"  📖 {Colors.UNDERLINE}USE_EXISTING_CHROME.md{Colors.END} - Chrome setup")
        print(f"  📖 {Colors.UNDERLINE}VIRTUAL_SCROLLING_FIX.md{Colors.END} - Technical details")
    
    print(f"\n  📚 {Colors.UNDERLINE}DOCS_INDEX.md{Colors.END} - All documentation")
    print()


def build_command(config):
    """Build the command to execute"""
    cmd = ['python3', 'scraper_sora_advanced.py']
    
    # Mode
    cmd.extend(['--mode', config['mode']])
    
    # Profile URL
    if config['profile_url']:
        cmd.extend(['--profile-url', config['profile_url']])
    
    # Quantity
    if config['all_videos']:
        cmd.append('--all')
    else:
        cmd.extend(['--num-videos', str(config['num_videos'])])
    
    # Metadata mode
    if config['metadata_mode']:
        cmd.append('--metadata-mode')
        if config['metadata_per_file']:
            cmd.append('--metadata-per-file')
    
    # Advanced options
    if config['slow']:
        cmd.append('--slow')
    
    if config['existing_chrome']:
        cmd.append('--use-existing-chrome')
    
    cmd.extend(['--delay', str(config['delay'])])
    
    return cmd


def show_command_summary(cmd, config):
    """Show summary of what will be executed"""
    print_section("📋 Summary")
    print()
    
    # What will happen
    print(f"{Colors.BOLD}Configuration:{Colors.END}")
    print(f"  Source: {Colors.GREEN}{config['mode'].upper()}{Colors.END}", end='')
    if config['profile_url']:
        print(f" ({config['profile_url'][:50]}...)")
    else:
        print()
    
    if config['metadata_mode']:
        print(f"  Output: {Colors.GREEN}Metadata (JSON){Colors.END}")
        if config['metadata_per_file']:
            print(f"  Format: {Colors.GREEN}Multiple files{Colors.END} (metadata/ folder)")
        else:
            print(f"  Format: {Colors.GREEN}Single file{Colors.END} (metadata.json)")
    else:
        print(f"  Output: {Colors.GREEN}Video files (MP4){Colors.END}")
    
    if config['all_videos']:
        print(f"  Quantity: {Colors.YELLOW}ALL videos{Colors.END}")
    else:
        print(f"  Quantity: {Colors.GREEN}{config['num_videos']} videos{Colors.END}")
    
    print(f"  Delay: {Colors.GREEN}{config['delay']}s{Colors.END} between scrolls")
    
    if config['slow']:
        print(f"  Mode: {Colors.YELLOW}SLOW{Colors.END} (safer, avoids detection)")
    
    if config['existing_chrome']:
        print(f"  Chrome: {Colors.GREEN}Use existing session{Colors.END}")
    
    print()
    
    # Command
    print(f"{Colors.BOLD}Command that will be executed:{Colors.END}")
    print(f"{Colors.CYAN}{' '.join(cmd)}{Colors.END}")
    print()
    
    # Warnings
    if config['all_videos']:
        print_warning("This may take a LONG time for profiles with many videos!")
    
    if config['existing_chrome'] and not check_chrome_running():
        print_warning("Chrome doesn't seem to be running with remote debugging!")
        print_info("Run './launch_chrome.sh' in another terminal first")
        print()


def check_chrome_running():
    """Check if Chrome is running with remote debugging"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9222))
        sock.close()
        return result == 0
    except:
        return False


def run_command(cmd):
    """Execute the scraper command"""
    print_section("🚀 Running Scraper")
    print()
    
    try:
        # Run the command
        result = subprocess.run(cmd, cwd=os.getcwd())
        
        if result.returncode == 0:
            print()
            print_success("Scraping completed successfully!")
            return True
        else:
            print()
            print_error(f"Scraping failed with exit code {result.returncode}")
            return False
            
    except KeyboardInterrupt:
        print()
        print_warning("Scraping interrupted by user")
        return False
    except Exception as e:
        print()
        print_error(f"Error running scraper: {e}")
        return False


def show_next_steps(config):
    """Show what to do next"""
    print_section("✨ Next Steps")
    print()
    
    if config['metadata_mode']:
        if config['metadata_per_file']:
            print_success("Metadata saved in metadata/ folder")
            print()
            print("View the files:")
            print(f"  {Colors.CYAN}ls -lh metadata/{Colors.END}")
            print(f"  {Colors.CYAN}cat metadata/*.json | head -50{Colors.END}")
        else:
            print_success("Metadata saved in metadata.json")
            print()
            print("View the file:")
            print(f"  {Colors.CYAN}cat metadata.json | head -100{Colors.END}")
            print(f"  {Colors.CYAN}cat metadata.json | python -m json.tool | less{Colors.END}")
        
        print()
        print("Run usage examples:")
        print(f"  {Colors.CYAN}python example_metadata_usage.py{Colors.END}")
        
        print()
        print("Import to MongoDB:")
        print(f"  {Colors.CYAN}mongoimport --db tiktok --collection videos --file metadata.json --jsonArray{Colors.END}")
        
    else:
        print_success("Videos saved in videos/ folder")
        print()
        print("View downloaded videos:")
        print(f"  {Colors.CYAN}ls -lh videos/{Colors.END}")
        print(f"  {Colors.CYAN}open videos/{Colors.END}")
    
    print()
    print_info("Check page_backup.html for the raw HTML if you need to debug")
    print()


def main():
    """Main interactive flow"""
    try:
        show_welcome()
        
        # Step 1: Choose mode (home or profile)
        mode, profile_url = choose_mode()
        
        # Step 2: Choose output mode (metadata or video)
        metadata_mode = choose_output_mode()
        
        # Step 2b: If metadata, choose format
        metadata_per_file = False
        if metadata_mode:
            metadata_per_file = choose_metadata_format()
        
        # Step 3: Choose quantity
        all_videos, num_videos = choose_quantity()
        
        # Step 4: Advanced options
        advanced = choose_advanced_options()
        
        # Build config
        config = {
            'mode': mode,
            'profile_url': profile_url,
            'metadata_mode': metadata_mode,
            'metadata_per_file': metadata_per_file,
            'all_videos': all_videos,
            'num_videos': num_videos,
            'slow': advanced['slow'],
            'existing_chrome': advanced['existing_chrome'],
            'delay': advanced['delay']
        }
        
        # Build command
        cmd = build_command(config)
        
        # Show summary
        show_command_summary(cmd, config)
        
        # Show documentation links
        show_documentation_links(metadata_mode)
        
        # Confirm
        print()
        if not get_yes_no(f"{Colors.BOLD}Ready to start scraping?{Colors.END}", default='y'):
            print_warning("Scraping cancelled")
            return
        
        # Run
        success = run_command(cmd)
        
        # Show next steps
        if success:
            show_next_steps(config)
        
    except KeyboardInterrupt:
        print()
        print_warning("\nInteractive mode cancelled by user")
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
