# SoraWatermarkCleaner

This project provides an elegant way to remove the sora watermark in the sora2 generated videos. 

<table>
  <tr>
    <td width="20%">
      <strong>Case1(25s)</strong>
    </td>
    <td width="80%">
      <video src="https://github.com/user-attachments/assets/55f4e822-a356-4fab-a372-8910e4cb3c28" 
             width="100%" controls></video>
    </td>
  </tr>
  <tr>
    <td>
      <strong>Case2(10s)</strong>
    </td>
    <td>
      <video src="https://github.com/user-attachments/assets/2773df41-62dc-4876-bd2f-4dd3ccac4b9e" 
             width="100%" controls></video>
    </td>
  </tr>
  <tr>
    <td>
      <strong>Case3(10s)</strong>
    </td>
    <td>
      <video src="https://github.com/user-attachments/assets/2bdba310-6379-48f2-a93c-6de857c4df3d" 
             width="100%" controls></video>
    </td>
  </tr>
</table>

⭐️: 

- **I'm excited to release [DeMark-World](https://github.com/linkedlist771/DeMark-World) – to the best of my knowledge, the first model capable of removing any watermark from AI-generated videos.**

- **We have provided another model which could preserve time consistency without flicker!**

- **We support batch processing now.**
- **For the new watermark with username,  the Yolo weights has been updated, try the new version watermark detect model, it should work better.**

- **We have uploaded the labelled datasets into huggingface, check this [dataset](https://huggingface.co/datasets/LLinked/sora-watermark-dataset) out. Free free to train your custom detector model or improve our model!**

- **One-click portable build is available** — [Download here](#3-one-click-portable-version) for Windows users! No installation required.

---

💝 If you find this project helpful, please consider [buying me a coffee](mds/reward.md) to support the development!

## 1. Method

The SoraWatermarkCleaner(we call it `SoraWm` later) is composed of two parsts:

- SoraWaterMarkDetector: We trained a yolov11s version to detect the sora watermark. (Thank you yolo!)

- WaterMarkCleaner: We refer iopaint's implementation for watermark removal using the lama model.

  (This codebase is from https://github.com/Sanster/IOPaint#, thanks for their amazing work!)

Our SoraWm is purely deeplearning driven and yields good results in many generated videos.



## 2. Installation

[FFmpeg](https://ffmpeg.org/) is needed for video processing, please install it first.  We highly recommend using the `uv` to install the environments:

1. installation:

```bash
uv sync
```

> now the envs will be installed at the `.venv`, you can activate the env using:
>
> ```bash
> source .venv/bin/activate
> ```

2. Downloaded the pretrained models:

The trained yolo weights will be stored in the `resources` dir as the `best.pt`.  And it will be automatically download from https://github.com/linkedlist771/SoraWatermarkCleaner/releases/download/V0.0.1/best.pt . The `Lama` model is downloaded from https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt, and will be stored in the torch cache dir. Both downloads are automatic, if you fail, please check your internet status.

3. Batch processing
Use the cli.py for batch processing

```
python cli.py [-h] -i INPUT -o OUTPUT [-p PATTERN] [--quiet]
```

examples:

```
# Process all .mp4 files in input folder
python batch_process.py -i /path/to/input -o /path/to/output
# Process all .mov files
python batch_process.py -i /path/to/input -o /path/to/output --pattern "*.mov"
# Process all video files (mp4, mov, avi)
python batch_process.py -i /path/to/input -o /path/to/output --pattern "*.{mp4,mov,avi}"
# Without displaying the Tqdm bar inside sorawm procrssing.
python batch_process.py -i /path/to/input -o /path/to/output --quiet
```

## 3. One-Click Portable Version

For users who prefer a ready-to-use solution without manual installation, we provide a **one-click portable distribution** that includes all dependencies pre-configured.

### Download Links

**Google Drive:**
- [Download from Google Drive](https://drive.google.com/file/d/1ujH28aHaCXGgB146g6kyfz3Qxd-wHR1c/view?usp=share_link)

**Baidu Pan (百度网盘) - For users in China:**
- Link: https://pan.baidu.com/s/1onMom81mvw2c6PFkCuYzdg?pwd=jusu
- Extract Code (提取码): `jusu`

### Features
- ✅ No installation required
- ✅ All dependencies included
- ✅ Pre-configured environment
- ✅ Ready to use out of the box

Simply download, extract, and run!

## 4.  Demo

To have a basic usage, just try the `example.py`:

> We provide two models to remove watermark. LAMA is fast but may have flicker on the cleaned area, which E2FGVI_HQ compromise this only requires cuda otherwise very slow on CPU or MPS.

```python
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

```

We also provide you with a `streamlit` based interactive web page, try it with:

> We also provide the switch here.

```bash
streamlit run app.py
```

<img src="assests/model_switch.png" style="zoom: 25%;" />

Batch processing is also supported, now you can drag a folder or select multiple files to process.
<img src="assests/streamlit_batch.png" style="zoom: 50%;" />


## 5. WebServer

Here, we provide a **FastAPI-based web server** that can quickly turn this watermark remover into a service.

We also have a frontUI for the webserver, to try this:

```bash
cd frontend && bun install && bun run build
```

And then start the server, the frontend UI will be just ready in root route:

> The task statuses are recoreded and can resume when server is down.

![image](assests/frontend.png)

Simply run:

```
python start_server.py
```

The web server will start on port **5344**.

You can view the FastAPI [documentation](http://localhost:5344/docs) for more details.

There are three routes available:

1. **submit_remove_task**

   > After uploading a video, a task ID will be returned, and the video will begin processing immediately.

<img src="resources/53abf3fd-11a9-4dd7-a348-34920775f8ad.png" alt="image" style="zoom: 25%;" />

2. **get_results**

You can use the task ID obtained above to check the task status.

It will display the percentage of video processing completed.

Once finished, the returned data will include a **download URL**.

3. **download**

You can use the **download URL** from step 2 to retrieve the cleaned video.

## 6. Datasets

We have uploaded the labelled datasets into huggingface, check this out https://huggingface.co/datasets/LLinked/sora-watermark-dataset. Free free to train your custom detector model or improve our model!

## 7. API

Packaged as a Cog and [published to Replicate](https://replicate.com/uglyrobot/sora2-watermark-remover) for simple API based usage.

## 8. License

 Apache License


## 9. Citation

If you use this project, please cite:

```bibtex
@misc{sorawatermarkcleaner2025,
  author = {linkedlist771},
  title = {SoraWatermarkCleaner},
  year = {2025},
  url = {https://github.com/linkedlist771/SoraWatermarkCleaner}
}
```

## 10. Acknowledgments

- [IOPaint](https://github.com/Sanster/IOPaint) for the LAMA implementation
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) for object detection
