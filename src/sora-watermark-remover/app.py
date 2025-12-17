import shutil
import tempfile
from pathlib import Path

import streamlit as st

from sorawm.core import SoraWM
from sorawm.schemas import CleanerType


def main():
    st.set_page_config(
        page_title="Sora Watermark Cleaner", page_icon="🎬", layout="centered"
    )

    # Header section with improved layout
    st.markdown(
        """
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='margin-bottom: 0.5rem;'>
                🎬 Sora Watermark Cleaner
            </h1>
            <p style='font-size: 1.2rem; color: #666; margin-bottom: 1rem;'>
                Remove watermarks from Sora-generated videos with AI-powered precision
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # # Feature badges
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     st.markdown(
    #         """
    #         <div style='text-align: center; padding: 0.8rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    #                     border-radius: 10px; color: white;'>
    #             <div style='font-size: 1.5rem;'>⚡</div>
    #             <div style='font-weight: bold;'>Fast Processing</div>
    #             <div style='font-size: 0.85rem; opacity: 0.9;'>GPU Accelerated</div>
    #         </div>
    #         """,
    #         unsafe_allow_html=True,
    #     )
    # with col2:
    #     st.markdown(
    #         """
    #         <div style='text-align: center; padding: 0.8rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    #                     border-radius: 10px; color: white;'>
    #             <div style='font-size: 1.5rem;'>🎯</div>
    #             <div style='font-weight: bold;'>High Precision</div>
    #             <div style='font-size: 0.85rem; opacity: 0.9;'>AI-Powered</div>
    #         </div>
    #         """,
    #         unsafe_allow_html=True,
    #     )
    # with col3:
    #     st.markdown(
    #         """
    #         <div style='text-align: center; padding: 0.8rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    #                     border-radius: 10px; color: white;'>
    #             <div style='font-size: 1.5rem;'>📦</div>
    #             <div style='font-weight: bold;'>Batch Support</div>
    #             <div style='font-size: 0.85rem; opacity: 0.9;'>Process Multiple</div>
    #         </div>
    #         """,
    #         unsafe_allow_html=True,
    #     )

    # Footer info
    st.markdown(
        """
        <div style='text-align: center; padding: 1rem 0; margin-top: 1rem;'>
            <p style='color: #888; font-size: 0.9rem;'>
                Built with ❤️ using Streamlit and AI | 
                <a href='https://github.com/linkedlist771/SoraWatermarkCleaner' 
                   target='_blank' style='color: #667eea; text-decoration: none;'>
                    ⭐ Star on GitHub
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Model selection
    st.markdown("### ⚙️ Model Settings")

    col1, col2 = st.columns([2, 3])
    with col1:
        model_type = st.selectbox(
            "Select Cleaner Model:",
            options=[CleanerType.LAMA, CleanerType.E2FGVI_HQ],
            format_func=lambda x: {
                CleanerType.LAMA: "🚀 LAMA (Fast, Good Quality)",
                CleanerType.E2FGVI_HQ: "💎 E2FGVI-HQ (Slower when not on GPU, Best Quality with time consistency)",
            }[x],
            help="LAMA: Fast processing with good quality. E2FGVI-HQ: Slower when not on GPU but highest quality results.",
        )

    with col2:
        model_info = {
            CleanerType.LAMA: "⚡ **Fast processing** - Recommended for most videos. Uses LaMa (Large Mask Inpainting) for quick watermark removal.",
            CleanerType.E2FGVI_HQ: "🎯 **Highest quality** - Uses temporal flow-based video inpainting. Best for professional results. Slower when not on GPU. Time consistency is guaranteed.",
        }
        st.info(model_info[model_type])

    # Initialize or reinitialize SoraWM if model changed
    if (
        "sora_wm" not in st.session_state
        or st.session_state.get("current_model") != model_type
    ):
        with st.spinner(f"Loading {model_type.value.upper()} model..."):
            st.session_state.sora_wm = SoraWM(cleaner_type=model_type)
            st.session_state.current_model = model_type
        st.success(f"✅ {model_type.value.upper()} model loaded!")

    st.markdown("---")

    # Mode selection
    mode = st.radio(
        "Select input mode:",
        ["📁 Upload Video File", "🗂️ Process Folder"],
        horizontal=True,
    )

    if mode == "📁 Upload Video File":
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload your video",
            type=["mp4", "avi", "mov", "mkv"],
            accept_multiple_files=False,
            help="Select a video file to remove watermark",
        )

        if uploaded_file:
            # Clear previous processed video if a new file is uploaded
            if (
                "current_file_name" not in st.session_state
                or st.session_state.current_file_name != uploaded_file.name
            ):
                st.session_state.current_file_name = uploaded_file.name
                if "processed_video_data" in st.session_state:
                    del st.session_state.processed_video_data
                if "processed_video_path" in st.session_state:
                    del st.session_state.processed_video_path
                if "processed_video_name" in st.session_state:
                    del st.session_state.processed_video_name

            # Display video info
            st.success(f"✅ Uploaded: {uploaded_file.name}")

            # Create two columns for before/after comparison
            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("### 📥 Original Video")
                st.video(uploaded_file)

            with col_right:
                st.markdown("### 🎬 Processed Video")
                # Placeholder for processed video
                if "processed_video_data" not in st.session_state:
                    st.info("Click 'Remove Watermark' to process the video")
                else:
                    st.video(st.session_state.processed_video_data)

            # Process button
            if st.button(
                "🚀 Remove Watermark", type="primary", use_container_width=True
            ):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_path = Path(tmp_dir)

                    try:
                        # Create progress bar and status text
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        def update_progress(progress: int):
                            progress_bar.progress(progress / 100)
                            if progress < 50:
                                status_text.text(
                                    f"🔍 Detecting watermarks... {progress}%"
                                )
                            elif progress < 95:
                                status_text.text(
                                    f"🧹 Removing watermarks... {progress}%"
                                )
                            else:
                                status_text.text(f"🎵 Merging audio... {progress}%")

                        # Single file processing
                        input_path = tmp_path / uploaded_file.name
                        with open(input_path, "wb") as f:
                            f.write(uploaded_file.read())

                        output_path = tmp_path / f"cleaned_{uploaded_file.name}"

                        st.session_state.sora_wm.run(
                            input_path, output_path, progress_callback=update_progress
                        )

                        progress_bar.progress(100)
                        status_text.text("✅ Processing complete!")
                        st.success("✅ Watermark removed successfully!")

                        # Store processed video path and read video data
                        with open(output_path, "rb") as f:
                            video_data = f.read()

                        st.session_state.processed_video_path = output_path
                        st.session_state.processed_video_data = video_data
                        st.session_state.processed_video_name = (
                            f"cleaned_{uploaded_file.name}"
                        )

                        # Rerun to show the video in the right column
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error processing video: {str(e)}")

            # Download button (show only if video is processed)
            if "processed_video_data" in st.session_state:
                st.download_button(
                    label="⬇️ Download Cleaned Video",
                    data=st.session_state.processed_video_data,
                    file_name=st.session_state.processed_video_name,
                    mime="video/mp4",
                    use_container_width=True,
                )

    else:  # Folder mode
        st.info(
            "💡 Drag and drop your video folder here, or click to browse and select multiple video files"
        )

        # File uploader for multiple files (supports folder drag & drop)
        uploaded_files = st.file_uploader(
            "Upload videos from folder",
            type=["mp4", "avi", "mov", "mkv"],
            accept_multiple_files=True,
            help="You can drag & drop an entire folder here, or select multiple video files",
            key="folder_uploader",
        )

        if uploaded_files:
            # Display uploaded files info
            video_count = len(uploaded_files)
            st.success(f"✅ {video_count} video file(s) uploaded")

            # Show file list in an expander
            with st.expander("📋 View uploaded files", expanded=False):
                for i, file in enumerate(uploaded_files, 1):
                    file_size_mb = file.size / (1024 * 1024)
                    st.text(f"{i}. {file.name} ({file_size_mb:.2f} MB)")

            # Process button
            if st.button(
                "🚀 Process All Videos", type="primary", use_container_width=True
            ):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_path = Path(tmp_dir)
                    input_folder = tmp_path / "input"
                    output_folder = tmp_path / "output"
                    input_folder.mkdir(exist_ok=True)
                    output_folder.mkdir(exist_ok=True)

                    try:
                        # Save all uploaded files to temp folder
                        status_text = st.empty()
                        status_text.text("📥 Saving uploaded files...")

                        for uploaded_file in uploaded_files:
                            # Preserve folder structure if file.name contains subdirectories
                            file_path = input_folder / uploaded_file.name
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.read())

                        # Create progress tracking
                        progress_bar = st.progress(0)
                        current_file_text = st.empty()
                        processed_count = 0

                        def update_progress(progress: int):
                            # Calculate overall progress
                            overall_progress = (
                                (processed_count * 100 + progress) / video_count / 100
                            )
                            progress_bar.progress(overall_progress)

                            if progress < 50:
                                current_file_text.text(
                                    f"🔍 Processing file {processed_count + 1}/{video_count}: Detecting watermarks... {progress}%"
                                )
                            elif progress < 95:
                                current_file_text.text(
                                    f"🧹 Processing file {processed_count + 1}/{video_count}: Removing watermarks... {progress}%"
                                )
                            else:
                                current_file_text.text(
                                    f"🎵 Processing file {processed_count + 1}/{video_count}: Merging audio... {progress}%"
                                )

                        # Process each video file
                        for video_file in input_folder.rglob("*"):
                            if video_file.is_file() and video_file.suffix.lower() in [
                                ".mp4",
                                ".avi",
                                ".mov",
                                ".mkv",
                            ]:
                                # Determine output path maintaining folder structure
                                rel_path = video_file.relative_to(input_folder)
                                output_path = (
                                    output_folder
                                    / rel_path.parent
                                    / f"cleaned_{rel_path.name}"
                                )
                                output_path.parent.mkdir(parents=True, exist_ok=True)

                                # Process the video
                                st.session_state.sora_wm.run(
                                    video_file,
                                    output_path,
                                    progress_callback=update_progress,
                                )
                                processed_count += 1

                        progress_bar.progress(100)
                        current_file_text.text("✅ All videos processed!")
                        st.success(f"✅ {video_count} video(s) processed successfully!")

                        # Create download option for processed videos
                        st.markdown("### 📦 Download Processed Videos")

                        # Store processed files info in session state
                        if "batch_processed_files" not in st.session_state:
                            st.session_state.batch_processed_files = []

                        st.session_state.batch_processed_files.clear()

                        for processed_file in output_folder.rglob("*"):
                            if processed_file.is_file():
                                with open(processed_file, "rb") as f:
                                    video_data = f.read()
                                rel_path = processed_file.relative_to(output_folder)
                                st.session_state.batch_processed_files.append(
                                    {"name": str(rel_path), "data": video_data}
                                )

                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error processing videos: {str(e)}")
                        import traceback

                        st.error(f"Details: {traceback.format_exc()}")

            # Show download buttons for processed files
            if (
                "batch_processed_files" in st.session_state
                and st.session_state.batch_processed_files
            ):
                st.markdown("---")
                st.markdown("### ⬇️ Download Processed Videos")

                for file_info in st.session_state.batch_processed_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(f"📹 {file_info['name']}")
                    with col2:
                        st.download_button(
                            label="⬇️ Download",
                            data=file_info["data"],
                            file_name=file_info["name"],
                            mime="video/mp4",
                            key=f"download_{file_info['name']}",
                            use_container_width=True,
                        )


if __name__ == "__main__":
    main()
