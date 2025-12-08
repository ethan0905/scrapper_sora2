# FFmpeg 可执行文件目录

## 用途

这个目录用于存放 FFmpeg 可执行文件，使项目成为真正的便携版（无需系统安装 FFmpeg）。

## Windows 用户配置步骤

### 1. 下载 FFmpeg

访问 [FFmpeg-Builds Release](https://github.com/BtbN/FFmpeg-Builds/releases) 页面：

- 下载最新的 `ffmpeg-master-latest-win64-gpl.zip`（约 120MB）
- 或者下载特定版本，如 `ffmpeg-n6.1-latest-win64-gpl-6.1.zip`

### 2. 解压并复制文件

1. 解压下载的 zip 文件
2. 在解压后的文件夹中找到 `bin` 目录
3. 将以下两个文件复制到**当前目录**（`ffmpeg/`）：
   - `ffmpeg.exe` - FFmpeg 主程序
   - `ffprobe.exe` - FFmpeg 媒体信息探测工具

### 3. 验证配置

完成后，此目录应包含：

```
ffmpeg/
├── .gitkeep
├── README.md
├── ffmpeg.exe    ← 你复制的文件
└── ffprobe.exe   ← 你复制的文件
```

### 4. 测试

运行项目中的测试脚本验证配置：

```bash
python test_ffmpeg_setup.py
```

如果配置正确，你将看到：`✓ 测试通过！FFmpeg已正确配置并可以使用`

## macOS/Linux 用户

如果需要便携版，请：

1. 下载对应平台的 FFmpeg 二进制文件
2. 将 `ffmpeg` 和 `ffprobe` 可执行文件放到此目录
3. 确保文件有执行权限：`chmod +x ffmpeg ffprobe`

## 注意事项

- 这些可执行文件不会被 git 提交（已在 `.gitignore` 中配置）
- 程序会自动检测并使用此目录下的 FFmpeg
- 如果此目录没有 FFmpeg，程序会尝试使用系统安装的版本

## 下载链接汇总

- **Windows**: https://github.com/BtbN/FFmpeg-Builds/releases
- **官方网站**: https://ffmpeg.org/download.html
- **镜像站点**: https://www.gyan.dev/ffmpeg/builds/ (Windows)

## 许可证

FFmpeg 使用 GPL 许可证，请遵守相关条款。

