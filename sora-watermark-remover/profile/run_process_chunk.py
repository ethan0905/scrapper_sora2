import numpy as np
from pathlib import Path
from contextlib import contextmanager
from typing import List

import torch
import torch.nn.functional as F
from torch.cuda.nvtx import range_pop, range_push
from tqdm import tqdm
from loguru import logger

from sorawm.cleaner.e2fgvi_hq_cleaner import *
from sorawm.utils.video_utils import merge_frames_with_overlap
from sorawm.models.model.e2fgvi_hq import InpaintGenerator


@contextmanager
def nvtx(msg: str):
    range_push(msg)
    try:
        yield
    finally:
        range_pop()


class ProfileInpaintGenerator(InpaintGenerator):
    def forward_bidirect_flow(self, masked_local_frames):
        with nvtx("InpaintGenerator.forward_bidirect_flow_total"):
            b, l_t, c, h, w = masked_local_frames.size()

            with nvtx("flow_downsample_interpolate"):
                masked_local_frames = F.interpolate(
                    masked_local_frames.view(-1, c, h, w),
                    scale_factor=1 / 4,
                    mode="bilinear",
                    align_corners=True,
                    recompute_scale_factor=True,
                )
                masked_local_frames = masked_local_frames.view(
                    b, l_t, c, h // 4, w // 4
                )

            with nvtx("flow_prepare_pairs"):
                mlf_1 = masked_local_frames[:, :-1, :, :, :].reshape(
                    -1, c, h // 4, w // 4
                )
                mlf_2 = masked_local_frames[:, 1:, :, :, :].reshape(
                    -1, c, h // 4, w // 4
                )

            with nvtx("spynet_forward"):
                pred_flows_forward = self.update_spynet(mlf_1, mlf_2)

            with nvtx("spynet_backward"):
                pred_flows_backward = self.update_spynet(mlf_2, mlf_1)

            with nvtx("flow_reshape"):
                pred_flows_forward = pred_flows_forward.view(
                    b, l_t - 1, 2, h // 4, w // 4
                )
                pred_flows_backward = pred_flows_backward.view(
                    b, l_t - 1, 2, h // 4, w // 4
                )

            return pred_flows_forward, pred_flows_backward

    def forward(self, masked_frames, num_local_frames):
        with nvtx("InpaintGenerator.forward_total"):
            l_t = num_local_frames
            b, t, ori_c, ori_h, ori_w = masked_frames.size()

            with nvtx("forward_normalize_local_frames"):
                masked_local_frames = (masked_frames[:, :l_t, ...] + 1) / 2

            with nvtx("forward_bidirect_flow_call"):
                pred_flows = self.forward_bidirect_flow(masked_local_frames)

            with nvtx("encoder_all_frames"):
                enc_feat = self.encoder(masked_frames.view(b * t, ori_c, ori_h, ori_w))

            with nvtx("split_local_ref_feat"):
                _, c, h, w = enc_feat.size()
                fold_output_size = (h, w)
                local_feat = enc_feat.view(b, t, c, h, w)[:, :l_t, ...]
                ref_feat = enc_feat.view(b, t, c, h, w)[:, l_t:, ...]

            with nvtx("feat_prop_module"):
                local_feat = self.feat_prop_module(
                    local_feat, pred_flows[0], pred_flows[1]
                )

            with nvtx("concat_local_ref"):
                enc_feat = torch.cat((local_feat, ref_feat), dim=1)

            with nvtx("temporal_focal_transformers_ss"):
                trans_feat = self.ss(enc_feat.view(-1, c, h, w), b, fold_output_size)

            with nvtx("temporal_transformer_blocks"):
                trans_feat = self.transformer([trans_feat, fold_output_size])

            with nvtx("sc_fuse"):
                trans_feat = self.sc(trans_feat[0], t, fold_output_size)
                trans_feat = trans_feat.view(b, t, -1, h, w)

            with nvtx("residual_add"):
                enc_feat = enc_feat + trans_feat

            with nvtx("decoder"):
                output = self.decoder(enc_feat.view(b * t, c, h, w))
                output = torch.tanh(output)

            return output, pred_flows


class ProfileE2FGVIHDCleaner(E2FGVIHDCleaner):
    def __init__(
        self,
        ckpt_path: Path = E2FGVI_HQ_CHECKPOINT_PATH,
        config: E2FGVIHDConfig = E2FGVIHDConfig(),
    ):
        with nvtx("cleaner_init_total"):
            with nvtx("ensure_model_downloaded"):
                ensure_model_downloaded(ckpt_path, E2FGVI_HQ_CHECKPOINT_REMOTE_URL)

            with nvtx("init_model"):
                self.model = ProfileInpaintGenerator().to(device)

            with nvtx("load_ckpt"):
                state = torch.load(ckpt_path, map_location=device)
                self.model.load_state_dict(state)

            with nvtx("model_eval_mode"):
                self.model.eval()

            self.config = config

    def clean(self, frames: np.ndarray, masks: np.ndarray) -> List[np.ndarray]:
        """
        重新 override clean，保证总流程也能在 nsys 里看到。
        """
        with nvtx("ProfileE2FGVIHDCleaner.clean_total"):
            with nvtx("setup_basic_params"):
                video_length = len(frames)
                chunk_size = int(self.config.chunk_size_ratio * video_length)
                overlap_size = int(self.config.overlap_ratio * video_length)
                num_chunks = int(np.ceil(video_length / (chunk_size - overlap_size)))
                h, w = frames[0].shape[:2]

            with nvtx("numpy_to_tensor"):
                imgs_all, masks_all = numpy_to_tensor(frames, masks)

            with nvtx("prepare_binary_masks"):
                binary_masks = np.expand_dims(masks > 0, axis=-1).astype(np.uint8)

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

                    with nvtx("chunk_extract_and_to_device"):
                        imgs_chunk = imgs_all[:, start_idx:end_idx, :, :, :].to(device)
                        masks_chunk = masks_all[:, start_idx:end_idx, :, :, :].to(
                            device
                        )
                        frames_np_chunk = frames[start_idx:end_idx]
                        binary_masks_chunk = binary_masks[start_idx:end_idx]

                    with nvtx("chunk_process_frames_chunk"):
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

                    with nvtx("merge_frames_with_overlap"):
                        comp_frames = merge_frames_with_overlap(
                            result_frames=comp_frames,
                            chunk_frames=comp_frames_chunk,
                            start_idx=start_idx,
                            overlap_size=overlap_size,
                            is_first_chunk=(chunk_idx == 0),
                        )

                    with nvtx("chunk_cleanup"):
                        del imgs_chunk, masks_chunk, comp_frames_chunk
                        try:
                            torch.cuda.empty_cache()
                        except Exception:
                            pass

        return comp_frames

    def process_frames_chunk(
        self,
        chunk_length: int,
        neighbor_stride: int,
        imgs_chunk: torch.Tensor,
        masks_chunk: torch.Tensor,
        binary_masks_chunk: np.ndarray,
        frames_np_chunk: np.ndarray,
        h: int,
        w: int,
    ) -> List[np.ndarray]:
        comp_frames_chunk = [None] * chunk_length

        for f in tqdm(
            range(0, chunk_length, neighbor_stride),
            desc=f"  Frame progress",
            position=1,
            leave=False,
        ):
            with nvtx(f"window_f_{f:05d}_total"):
                with nvtx("window_neighbor_ref_ids"):
                    neighbor_ids = [
                        i
                        for i in range(
                            max(0, f - neighbor_stride),
                            min(chunk_length, f + neighbor_stride + 1),
                        )
                    ]
                    ref_ids = get_ref_index(
                        f,
                        neighbor_ids,
                        chunk_length,
                        self.config.ref_length,
                        self.config.num_ref,
                    )

                with nvtx("window_select_tensors"):
                    selected_imgs = imgs_chunk[:1, neighbor_ids + ref_ids, :, :, :]
                    selected_masks = masks_chunk[:1, neighbor_ids + ref_ids, :, :, :]

                with torch.no_grad():
                    with nvtx("window_apply_mask"):
                        masked_imgs = selected_imgs * (1 - selected_masks)

                    with nvtx("window_pad_flip_concat"):
                        mod_size_h = 60
                        mod_size_w = 108
                        h_pad = (mod_size_h - h % mod_size_h) % mod_size_h
                        w_pad = (mod_size_w - w % mod_size_w) % mod_size_w

                        masked_imgs = torch.cat(
                            [masked_imgs, torch.flip(masked_imgs, [3])], 3
                        )[:, :, :, : h + h_pad, :]

                        masked_imgs = torch.cat(
                            [masked_imgs, torch.flip(masked_imgs, [4])], 4
                        )[:, :, :, :, : w + w_pad]

                    with nvtx("window_model_infer"):
                        pred_imgs, _ = self.model(masked_imgs, len(neighbor_ids))

                    with nvtx("window_crop_postprocess"):
                        pred_imgs = pred_imgs[:, :, :h, :w]
                        pred_imgs = (pred_imgs + 1) / 2
                        pred_imgs = pred_imgs.cpu().permute(0, 2, 3, 1).numpy() * 255

                    with nvtx("window_composite_back_to_frames"):
                        for i in range(len(neighbor_ids)):
                            idx = neighbor_ids[i]
                            img = np.array(pred_imgs[i]).astype(
                                np.uint8
                            ) * binary_masks_chunk[idx] + frames_np_chunk[idx] * (
                                1 - binary_masks_chunk[idx]
                            )

                            if comp_frames_chunk[idx] is None:
                                comp_frames_chunk[idx] = img
                            else:
                                comp_frames_chunk[idx] = (
                                    comp_frames_chunk[idx].astype(np.float32) * 0.5
                                    + img.astype(np.float32) * 0.5
                                )

        # 你用来中断 profiling 的断点，保留
        raise RuntimeError("Stop here")

        return comp_frames_chunk


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
