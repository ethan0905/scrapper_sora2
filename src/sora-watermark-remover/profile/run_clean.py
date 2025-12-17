import numpy as np
from pathlib import Path
from contextlib import contextmanager
from typing import List

import torch
from torch.cuda.nvtx import range_pop, range_push
from tqdm import tqdm
from loguru import logger

from sorawm.cleaner.e2fgvi_hq_cleaner import *
from sorawm.utils.video_utils import merge_frames_with_overlap


@contextmanager
def nvtx(msg: str):
    range_push(msg)
    try:
        yield
    finally:
        range_pop()


class ProfileE2FGVIHDCleaner(E2FGVIHDCleaner):
    def clean(self, frames: np.ndarray, masks: np.ndarray) -> List[np.ndarray]:
        with nvtx("ProfileE2FGVIHDCleaner.clean_total"):
            with nvtx("setup_basic_params"):
                video_length = len(frames)
                chunk_size = int(self.config.chunk_size_ratio * video_length)
                overlap_size = int(self.config.overlap_ratio * video_length)
                num_chunks = int(np.ceil(video_length / (chunk_size - overlap_size)))
                h, w = frames[0].shape[:2]

            # Convert to tensors
            with nvtx("numpy_to_tensor"):
                imgs_all, masks_all = numpy_to_tensor(frames, masks)

            # Prepare binary masks for compositing
            with nvtx("prepare_binary_masks"):
                binary_masks = np.expand_dims(masks > 0, axis=-1).astype(
                    np.uint8
                )  # (T, H, W, 1)

            comp_frames = [None] * video_length
            logger.debug(
                f"Processing {video_length} frames in {num_chunks} chunks "
                f"(chunk_size={chunk_size}, overlap={overlap_size})"
            )

            for chunk_idx in tqdm(
                range(num_chunks), desc="Chunk", position=0, leave=True
            ):
                with nvtx(f"chunk_{chunk_idx:03d}_total"):
                    with nvtx("chunk_compute_indices"):
                        start_idx = chunk_idx * (chunk_size - overlap_size)
                        end_idx = min(start_idx + chunk_size, video_length)
                        actual_chunk_size = end_idx - start_idx

                    # Extract chunk data
                    with nvtx("chunk_extract_and_to_device"):
                        imgs_chunk = imgs_all[:, start_idx:end_idx, :, :, :].to(device)
                        masks_chunk = masks_all[:, start_idx:end_idx, :, :, :].to(
                            device
                        )
                        frames_np_chunk = frames[start_idx:end_idx]
                        binary_masks_chunk = binary_masks[start_idx:end_idx]

                    # Core inpainting / propagation
                    with nvtx("process_frames_chunk"):
                        comp_frames_chunk = self.process_frames_chunk(
                            actual_chunk_size,
                            self.config.neighbor_stride,
                            imgs_chunk,
                            masks_chunk,
                            binary_masks_chunk,
                            frames_np_chunk,
                            h,
                            w,
                        )

                    # Merge results with blending in overlap region
                    with nvtx("merge_frames_with_overlap"):
                        comp_frames = merge_frames_with_overlap(
                            result_frames=comp_frames,
                            chunk_frames=comp_frames_chunk,
                            start_idx=start_idx,
                            overlap_size=overlap_size,
                            is_first_chunk=(chunk_idx == 0),
                        )

                    # Clear GPU memory
                    with nvtx("chunk_cleanup"):
                        del imgs_chunk, masks_chunk, comp_frames_chunk
                        try:
                            torch.cuda.empty_cache()
                        except Exception:
                            pass

        return comp_frames


if __name__ == "__main__":
    CMD = Path.cwd() / "profile"

    masks_npy_path = CMD / "masks.npy"
    frames_npy_path = CMD / "frames.npy"

    with nvtx("load_numpy_inputs"):
        masks = np.load(masks_npy_path)
        frames = np.load(frames_npy_path)

    with nvtx("init_cleaner"):
        cleaner = ProfileE2FGVIHDCleaner()

    with nvtx("run_cleaner"):
        cleaned_frames = cleaner.clean(frames, masks)

    # np.save(CMD / "cleaned_frames.npy", cleaned_frames)
