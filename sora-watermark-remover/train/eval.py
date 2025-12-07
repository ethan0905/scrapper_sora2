from pathlib import Path

import numpy as np
from ultralytics import YOLO

from sorawm.configs import WATER_MARK_DETECT_YOLO_WEIGHTS
from sorawm.utils.video_utils import VideoLoader

# based on the sora tempalte to detect the whole, and then got the icon part area.

model = YOLO(WATER_MARK_DETECT_YOLO_WEIGHTS)
model.eval()

results = model("resources/first_frame.png")  # Predict on an image

print(results)
