from pathlib import Path

from sorawm.core import SoraWM
from sorawm.schemas import CleanerType

if __name__ == "__main__":
    input_video_path = Path("resources/dog_vs_sam.mp4")
    output_video_path = Path("outputs/sora_watermark_removed")

    # 1. LAMA is fast and good quality, but not time consistent.
    sora_wm = SoraWM(cleaner_type=CleanerType.LAMA)
    sora_wm.run(input_video_path, Path(f"{output_video_path}_lama.mp4"))

    # 2. E2FGVI_HQ ensures time consistency, but will be very slow on no-cuda device.
    sora_wm = SoraWM(cleaner_type=CleanerType.E2FGVI_HQ)
    sora_wm.run(input_video_path, Path(f"{output_video_path}_e2fgvi_hq.mp4"))
