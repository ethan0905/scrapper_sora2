#!/bin/bash

CUDA_VISIBLE_DEVICES=0 nsys profile \
  --trace=cuda,cublas,nvtx,osrt,cudnn \
  --force-overwrite=true \
  -o profile/profile_process_chunk \
  python profile/run_process_chunk.py

# 仅追踪 cuda 和 nvtx，不追踪 cudnn/cublas，也不追踪系统调用(osrt)
# nsys profile \
#   --trace=cuda,nvtx \
#   --sample=none \
#   --cpuctxsw=none \
#   --force-overwrite=true \
#   -o profile/profile_lite \
#   python profile/run.py