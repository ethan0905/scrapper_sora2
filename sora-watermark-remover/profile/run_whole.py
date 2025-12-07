from pathlib import Path
from sorawm.core import SoraWM
from sorawm.schemas import CleanerType
from pathlib import Path
from typing import Callable
import numpy as np
from loguru import logger
from tqdm import tqdm
import ffmpeg
from sorawm.schemas import CleanerType
from sorawm.utils.imputation_utils import (
    find_2d_data_bkps,
    find_idxs_interval,
    get_interval_average_bbox,
)
from sorawm.utils.video_utils import VideoLoader, merge_frames_with_overlap
from sorawm.watermark_cleaner import WaterMarkCleaner
from sorawm.watermark_detector import SoraWaterMarkDetector
from torch.cuda.nvtx import range_pop, range_push


from pathlib import Path
from sorawm.core import SoraWM
from sorawm.schemas import CleanerType
from pathlib import Path
from typing import Callable
import numpy as np
from loguru import logger
from tqdm import tqdm
import ffmpeg
from sorawm.schemas import CleanerType
from sorawm.utils.imputation_utils import (
    find_2d_data_bkps,
    find_idxs_interval,
    get_interval_average_bbox,
)
from sorawm.utils.video_utils import VideoLoader, merge_frames_with_overlap
from sorawm.watermark_cleaner import WaterMarkCleaner
from sorawm.watermark_detector import SoraWaterMarkDetector
from torch.cuda.nvtx import range_pop, range_push
from contextlib import contextmanager
from torch.cuda.nvtx import range_pop, range_push


@contextmanager
def nvtx(msg: str):
    range_push(msg)
    try:
        yield
    finally:
        range_pop()


class ProfileSoraWM(SoraWM):
    def run(
        self,
        input_video_path: Path,
        output_video_path: Path,
        progress_callback: Callable[[int], None] | None = None,
        quiet: bool = False,
    ):
        with nvtx("ProfileSoraWM.run"):
            with nvtx("init video loader"):
                input_video_loader = VideoLoader(input_video_path)
                width = input_video_loader.width
                height = input_video_loader.height
                fps = input_video_loader.fps
                total_frames = input_video_loader.total_frames

                temp_output_path = (
                    output_video_path.parent / f"temp_{output_video_path.name}"
                )
                output_options = {
                    "pix_fmt": "yuv420p",
                    "vcodec": "libx264",
                    "preset": "slow",
                }

                if input_video_loader.original_bitrate:
                    output_options["video_bitrate"] = str(
                        int(int(input_video_loader.original_bitrate) * 1.2)
                    )
                else:
                    output_options["crf"] = "18"

                process_out = (
                    ffmpeg.input(
                        "pipe:",
                        format="rawvideo",
                        pix_fmt="bgr24",
                        s=f"{width}x{height}",
                        r=fps,
                    )
                    .output(str(temp_output_path), **output_options)
                    .overwrite_output()
                    .global_args("-loglevel", "error")
                    .run_async(pipe_stdin=True)
                )
            range_push("detect watermarks")
            frame_bboxes = {}
            detect_missed = []
            bbox_centers = []
            bboxes = []

            if not quiet:
                logger.debug(
                    f"total frames: {total_frames}, fps: {fps}, width: {width}, height: {height}"
                )

                for idx, frame in enumerate(
                    tqdm(
                        input_video_loader,
                        total=total_frames,
                        desc="Detect watermarks",
                        disable=quiet,
                    )
                ):
                    detection_result = self.detector.detect(frame)
                    if detection_result["detected"]:
                        frame_bboxes[idx] = {"bbox": detection_result["bbox"]}
                        x1, y1, x2, y2 = detection_result["bbox"]
                        bbox_centers.append((int((x1 + x2) / 2), int((y1 + y2) / 2)))
                        bboxes.append((x1, y1, x2, y2))
                    else:
                        frame_bboxes[idx] = {"bbox": None}
                        detect_missed.append(idx)
                        bbox_centers.append(None)
                        bboxes.append(None)

                    if progress_callback and idx % 10 == 0:
                        progress = 10 + int((idx / total_frames) * 40)
                        progress_callback(progress)

            if not quiet:
                logger.debug(f"detect missed frames: {detect_missed}")

            range_pop()
            range_push("find bkps")
            bkps_full = [0, total_frames]
            if detect_missed:
                bkps = find_2d_data_bkps(bbox_centers)
                bkps_full = [0] + bkps + [total_frames]

                interval_bboxes = get_interval_average_bbox(bboxes, bkps_full)
                missed_intervals = find_idxs_interval(detect_missed, bkps_full)

                for missed_idx, interval_idx in zip(detect_missed, missed_intervals):
                    if (
                        interval_idx < len(interval_bboxes)
                        and interval_bboxes[interval_idx] is not None
                    ):
                        frame_bboxes[missed_idx]["bbox"] = interval_bboxes[interval_idx]
                        if not quiet:
                            logger.debug(
                                f"Filled missed frame {missed_idx} with bbox:\n"
                                f" {interval_bboxes[interval_idx]}"
                            )
                    else:
                        before = max(missed_idx - 1, 0)
                        after = min(missed_idx + 1, total_frames - 1)
                        before_box = frame_bboxes[before]["bbox"]
                        after_box = frame_bboxes[after]["bbox"]
                        if before_box:
                            frame_bboxes[missed_idx]["bbox"] = before_box
                        elif after_box:
                            frame_bboxes[missed_idx]["bbox"] = after_box
            else:
                del bboxes, bbox_centers, detect_missed
            range_pop()
            range_push("remove watermarks")

            if self.cleaner_type == CleanerType.LAMA:
                raise NotImplementedError("Lama cleaner is not implemented yet.")

            elif self.cleaner_type == CleanerType.E2FGVI_HQ:
                input_video_loader = VideoLoader(input_video_path)
                frame_counter = 0
                overlap_ratio = self.cleaner.config.overlap_ratio
                all_cleaned_frames = None
                num_segments = len(bkps_full) - 1

                for segment_idx in range(num_segments):
                    # with nvtx(f"process segment {segment_idx}"):
                    range_push(f"process segment {segment_idx}")
                    seg_start = bkps_full[segment_idx]
                    seg_end = bkps_full[segment_idx + 1]
                    seg_length = seg_end - seg_start
                    segment_overlap = max(1, int(overlap_ratio * seg_length))
                    start = seg_start
                    end = seg_end

                    if segment_idx > 0:
                        start = max(
                            seg_start - segment_overlap,
                            bkps_full[segment_idx - 1],
                        )
                    if segment_idx < num_segments - 1:
                        end = min(
                            seg_end + segment_overlap,
                            bkps_full[segment_idx + 2],
                        )

                    if not quiet:
                        logger.debug(
                            f"Segment {segment_idx}: original=[{seg_start}, {seg_end}), "
                            f"with_overlap=[{start}, {end}), overlap={segment_overlap}"
                        )

                    frames = np.array(input_video_loader.get_slice(start, end))
                    frames = frames[:, :, :, ::-1].copy()

                    masks = np.zeros((len(frames), height, width), dtype=np.uint8)
                    for idx in range(start, end):
                        bbox = frame_bboxes[idx]["bbox"]
                        if bbox is not None:
                            x1, y1, x2, y2 = bbox
                            idx_offset = idx - start
                            masks[idx_offset][y1:y2, x1:x2] = 255

                    # with nvtx(f"clean frames [{start},{end})"):
                    range_push(f"clean frames [{start},{end})")
                    # masks_npy_path = Path("masks.npy")
                    # frames_np_path = Path("frames.npy")
                    # np.save(masks_npy_path, masks)
                    # np.save(frames_np_path, frames)
                    # raise Exception("Stop here")
                    cleaned_frames = self.cleaner.clean(frames, masks)
                    range_pop()
                    # with nvtx("merge frames"):
                    range_push("merge frames")
                    all_cleaned_frames = merge_frames_with_overlap(
                        result_frames=all_cleaned_frames,
                        chunk_frames=cleaned_frames,
                        start_idx=start,
                        overlap_size=segment_overlap,
                        is_first_chunk=(segment_idx == 0),
                    )
                    range_pop()

                    # with nvtx("write frames"):
                    range_push("write frames")
                    write_start = seg_start
                    write_end = seg_end
                    for write_idx in range(write_start, write_end):
                        if (
                            write_idx < len(all_cleaned_frames)
                            and all_cleaned_frames[write_idx] is not None
                        ):
                            cleaned_frame = all_cleaned_frames[write_idx]
                            cleaned_frame_bgr = cleaned_frame[:, :, ::-1]
                            process_out.stdin.write(
                                cleaned_frame_bgr.astype(np.uint8).tobytes()
                            )
                            frame_counter += 1
                            if progress_callback and frame_counter % 10 == 0:
                                progress = 50 + int((frame_counter / total_frames) * 45)
                                progress_callback(progress)

                    range_pop()
                    range_pop()
            range_pop()
            range_push("finalize ffmpeg")
            process_out.stdin.close()
            process_out.wait()

            if progress_callback:
                progress_callback(95)

            range_pop()
            range_push("merge audio track")
            self.merge_audio_track(
                input_video_path, temp_output_path, output_video_path
            )
            range_pop()


if __name__ == "__main__":
    input_video_path = Path("resources/dog_vs_sam.mp4")
    output_stem = Path("outputs/sora_watermark_removed")

    sora_wm = ProfileSoraWM(cleaner_type=CleanerType.E2FGVI_HQ)
    sora_wm.run(
        input_video_path, output_stem.parent / (output_stem.name + "_e2fgvi_hq.mp4")
    )
