import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def validate_args_and_show_help():
    """Parse and validate arguments before loading heavy dependencies"""
    parser = argparse.ArgumentParser(
        description="🎬 Batch process videos to remove Sora watermarks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process all .mp4 files in input folder
    python batch_process.py -i /path/to/input -o /path/to/output
    # Process all .mov files
    python batch_process.py -i /path/to/input -o /path/to/output --pattern "*.mov"
    # Process all video files (mp4, mov, avi)
    python batch_process.py -i /path/to/input -o /path/to/output --pattern "*.{mp4,mov,avi}"
    # Without displaying the Tqdm bar inside sorawm procrssing.
    python batch_process.py -i /path/to/input -o /path/to/output --quiet
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="📁 Input folder containing video files",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="📁 Output folder for cleaned videos",
    )

    parser.add_argument(
        "-p",
        "--pattern",
        type=str,
        default="*.mp4",
        help="🔍 File pattern to match (default: *.mp4)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Run in quiet mode (suppress tqdm and most logs).",
    )

    args = parser.parse_args()

    # Convert to Path objects
    input_folder = Path(args.input).expanduser().resolve()
    output_folder = Path(args.output).expanduser().resolve()

    # Validate input folder
    if not input_folder.exists():
        print(f"❌ Error: Input folder does not exist: {input_folder}", file=sys.stderr)
        sys.exit(1)

    if not input_folder.is_dir():
        print(
            f"❌ Error: Input path is not a directory: {input_folder}", file=sys.stderr
        )
        sys.exit(1)

    return input_folder, output_folder, args


# Classes are now defined inside main() after imports


def main():
    # Validate arguments BEFORE loading heavy dependencies (ffmpeg, torch, etc.)
    input_folder, output_folder, args = validate_args_and_show_help()

    pattern = args.pattern

    # Only NOW import heavy dependencies after validation passed
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        MofNCompleteColumn,
        Progress,
        ProgressColumn,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    from rich.table import Table
    from rich.text import Text
    from rich.text import Text as RichText

    from sorawm.core import SoraWM

    # Initialize console after importing rich
    console = Console()

    # Make SpeedColumn a proper ProgressColumn subclass now that we've imported it
    global SpeedColumn

    class SpeedColumnImpl(ProgressColumn):
        """Custom column to display processing speed in it/s format (only for video processing)"""

        def render(self, task):
            """Render the speed in it/s format, but only for video processing tasks"""
            # Only show speed for video processing, not for overall batch progress
            if "Overall Progress" in task.description:
                return RichText("", style="")

            speed = task.finished_speed or task.speed
            if speed is None:
                return RichText("-- it/s", style="progress.data.speed")
            return RichText(f"{speed:.2f} it/s", style="cyan")

    SpeedColumn = SpeedColumnImpl

    # Define BatchProcessor here to have access to all imports
    class BatchProcessorImpl:
        """Batch video processor with progress tracking"""

        def __init__(
            self, input_folder: Path, output_folder: Path, pattern: str = "*.mp4"
        ):
            self.input_folder = input_folder
            self.output_folder = output_folder
            self.pattern = pattern
            self.sora_wm = SoraWM()
            self.console = console

            # Statistics
            self.successful: List[str] = []
            self.failed: Dict[str, str] = {}

        def show_banner(self):
            """Display a colorful welcome banner"""
            banner_text = Text()
            banner_text.append("🎬 ", style="bold yellow")
            banner_text.append("Sora Watermark Remover", style="bold cyan")
            banner_text.append(" - Batch Processor", style="bold magenta")

            panel = Panel(
                banner_text,
                box=box.DOUBLE,
                border_style="bright_blue",
                padding=(1, 2),
            )
            console.print(panel)
            console.print()

        def find_videos(self) -> List[Path]:
            """Find all video files matching the pattern"""
            video_files = list(self.input_folder.glob(self.pattern))
            return sorted(video_files)

        def process_batch(self):
            """Process all videos in the batch with progress tracking"""
            # Show banner
            self.show_banner()

            # Find all videos
            video_files = self.find_videos()

            if not video_files:
                console.print(
                    f"[bold red]❌ No files matching '{self.pattern}' found in {self.input_folder}[/bold red]"
                )
                return

            # Display configuration
            config_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
            config_table.add_row(
                "📁 Input folder:", f"[cyan]{self.input_folder}[/cyan]"
            )
            config_table.add_row(
                "📁 Output folder:", f"[green]{self.output_folder}[/green]"
            )
            config_table.add_row("🔍 Pattern:", f"[yellow]{self.pattern}[/yellow]")
            config_table.add_row(
                "🎬 Videos found:", f"[bold magenta]{len(video_files)}[/bold magenta]"
            )
            console.print(config_table)
            console.print()

            # Create output folder
            self.output_folder.mkdir(parents=True, exist_ok=True)

            # Process each video with batch-level progress bar
            start_time = datetime.now()

            # Create rich progress display
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40),
                TaskProgressColumn(),
                MofNCompleteColumn(),
                SpeedColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                # Batch progress task
                batch_task = progress.add_task(
                    "[cyan]Overall Progress", total=len(video_files)
                )

                for idx, input_path in enumerate(video_files, 1):
                    output_path = self.output_folder / f"cleaned_{input_path.name}"

                    # Update batch task description
                    progress.update(
                        batch_task,
                        description=f"[cyan]Overall Progress ({idx}/{len(video_files)})",
                    )

                    # Show current file being processed
                    console.print(
                        f"\n[bold blue]📹 [{idx}/{len(video_files)}][/bold blue] "
                        f"[yellow]{input_path.name}[/yellow]"
                    )

                    try:
                        # Video processing task
                        video_task = progress.add_task(
                            f"  [green]Processing video", total=100
                        )

                        last_progress = [0]

                        def progress_callback(prog: int):
                            """Update the video progress bar"""
                            if prog > last_progress[0]:
                                progress.update(
                                    video_task, advance=prog - last_progress[0]
                                )
                                last_progress[0] = prog

                        # Process the video (quiet=True suppresses internal tqdm bars if enabled)
                        self.sora_wm.run(
                            input_path, output_path, progress_callback, quiet=args.quiet
                        )

                        # Ensure video progress reaches 100%
                        if last_progress[0] < 100:
                            progress.update(video_task, advance=100 - last_progress[0])

                        progress.remove_task(video_task)

                        self.successful.append(input_path.name)
                        console.print(
                            f"  [bold green]✅ Completed:[/bold green] {output_path.name}"
                        )

                    except Exception as e:
                        progress.remove_task(video_task)
                        self.failed[input_path.name] = str(e)
                        console.print(f"  [bold red]❌ Error:[/bold red] {e}")

                    # Update batch progress
                    progress.update(batch_task, advance=1)

            # Print summary
            self._print_summary(start_time)

        def _print_summary(self, start_time: datetime):
            """Print processing summary with rich formatting"""
            end_time = datetime.now()
            duration = end_time - start_time

            console.print()

            # Create summary statistics table
            summary_table = Table(
                show_header=False, box=box.ROUNDED, border_style="cyan"
            )
            summary_table.add_column("Metric", style="bold")
            summary_table.add_column("Value")

            summary_table.add_row("⏱️  Total Time", f"[yellow]{duration}[/yellow]")
            summary_table.add_row(
                "✅ Successful", f"[bold green]{len(self.successful)}[/bold green]"
            )
            summary_table.add_row(
                "❌ Failed", f"[bold red]{len(self.failed)}[/bold red]"
            )
            summary_table.add_row(
                "📊 Total",
                f"[bold magenta]{len(self.successful) + len(self.failed)}[/bold magenta]",
            )

            # Success rate
            total = len(self.successful) + len(self.failed)
            success_rate = (len(self.successful) / total * 100) if total > 0 else 0
            summary_table.add_row(
                "📈 Success Rate", f"[bold cyan]{success_rate:.1f}%[/bold cyan]"
            )

            # Wrap in a panel
            summary_panel = Panel(
                summary_table,
                title="[bold white]📋 BATCH PROCESSING SUMMARY[/bold white]",
                border_style="bright_cyan",
                box=box.DOUBLE,
            )
            console.print(summary_panel)

            # Successful files
            if self.successful:
                console.print()
                success_table = Table(
                    title="[bold green]✅ Successfully Processed[/bold green]",
                    box=box.SIMPLE,
                    show_header=True,
                    header_style="bold green",
                )
                success_table.add_column("#", style="dim", width=4)
                success_table.add_column("Filename", style="green")

                for idx, filename in enumerate(self.successful, 1):
                    success_table.add_row(str(idx), filename)

                console.print(success_table)

            # Failed files
            if self.failed:
                console.print()
                failed_table = Table(
                    title="[bold red]❌ Failed to Process[/bold red]",
                    box=box.SIMPLE,
                    show_header=True,
                    header_style="bold red",
                )
                failed_table.add_column("#", style="dim", width=4)
                failed_table.add_column("Filename", style="red")
                failed_table.add_column("Error", style="dim")

                for idx, (filename, error) in enumerate(self.failed.items(), 1):
                    # Truncate long error messages
                    error_msg = error if len(error) < 60 else error[:57] + "..."
                    failed_table.add_row(str(idx), filename, error_msg)

                console.print(failed_table)

            # Final message
            console.print()
            if len(self.failed) == 0:
                console.print(
                    "[bold green]🎉 All videos processed successfully![/bold green]",
                    justify="center",
                )
            else:
                console.print(
                    "[bold yellow]⚠️  Some videos failed to process. Check errors above.[/bold yellow]",
                    justify="center",
                )
            console.print()

    # Create processor and run
    try:
        processor = BatchProcessorImpl(input_folder, output_folder, pattern)
        processor.process_batch()
    except KeyboardInterrupt:
        console.print()
        console.print(
            "[bold yellow]⚠️  Processing interrupted by user[/bold yellow]",
            justify="center",
        )
        sys.exit(130)
    except Exception as e:
        console.print()
        console.print(f"[bold red]❌ Fatal error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
1
