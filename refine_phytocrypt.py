#!/usr/bin/env python3
"""
Refine a video into PhytoCrypt smooth modern cartoon style.
Run:
    python refine_phytocrypt.py --input input.mp4 --output refined.mp4
"""

import os
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
from sklearn.cluster import KMeans
from tqdm import tqdm
import argparse
import tempfile

NUM_QUANT_COLORS = 6
BILATERAL_ITER = 3
BILATERAL_D = 9
BILATERAL_SIGMA = 75
EDGE_BLUR = 1
EDGE_THRESHOLD = 45
GLOW_STRENGTH = 0.35
HUE_SHIFT = -20
SATURATION_BOOST = 1.15
STROKE_WEIGHT = 1.0

def quantize_colors(img_bgr, n_colors=6):
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w, _ = img.shape
    X = img.reshape((-1,3)).astype(np.float32) / 255.0
    kmeans = KMeans(n_clusters=n_colors, random_state=0, n_init=4).fit(X)
    centers = (kmeans.cluster_centers_ * 255).astype(np.uint8)
    labels = kmeans.labels_
    quant = centers[labels].reshape((h,w,3))
    return cv2.cvtColor(quant, cv2.COLOR_RGB2BGR)

def edge_mask(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    lap = cv2.Laplacian(gray, cv2.CV_8U, ksize=3)
    _, thresh = cv2.threshold(lap, EDGE_THRESHOLD, 255, cv2.THRESH_BINARY)
    if EDGE_BLUR > 0:
        thresh = cv2.GaussianBlur(thresh, (3,3), EDGE_BLUR)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    thick = cv2.dilate(thresh, kernel, iterations=int(max(1, round(STROKE_WEIGHT))))
    mask = 255 - thick
    return cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

def stylize_frame(img):
    smooth = img.copy()
    for _ in range(BILATERAL_ITER):
        smooth = cv2.bilateralFilter(smooth, BILATERAL_D, BILATERAL_SIGMA, BILATERAL_SIGMA)

    quant = quantize_colors(smooth, NUM_QUANT_COLORS)

    hsv = cv2.cvtColor(quant, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,0] = (hsv[:,:,0] + (HUE_SHIFT / 2.0)) % 180
    hsv[:,:,1] = np.clip(hsv[:,:,1] * SATURATION_BOOST, 0, 255)
    quant = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    edges = edge_mask(img)
    combined = (quant.astype(np.float32) * (edges.astype(np.float32)/255.0)).astype(np.uint8)

    gray = cv2.cvtColor(combined, cv2.COLOR_BGR2GRAY)
    _, bright = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    glow = cv2.GaussianBlur(cv2.bitwise_and(combined, combined, mask=bright), (0,0), 15)
    final = cv2.addWeighted(combined.astype(np.float32), 1.0, glow.astype(np.float32), GLOW_STRENGTH, 0)
    return final.astype(np.uint8)

def process_video(input_path, output_path):
    clip = VideoFileClip(input_path)
    fps = clip.fps

    temp_dir = tempfile.mkdtemp(prefix="phyto_")
    frame_paths = []

    for i, frame in enumerate(tqdm(clip.iter_frames(dtype="uint8"), desc="Processing frames")):
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out = stylize_frame(bgr)
        path = os.path.join(temp_dir, "frame_%06d.png" % i)
        cv2.imwrite(path, out)
        frame_paths.append(path)

    from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
    final_clip = ImageSequenceClip(
        [cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB) for p in frame_paths],
        fps=fps
    )

    if clip.audio is not None:
        final_clip = final_clip.set_audio(clip.audio)

    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()
    process_video(args.input, args.output)
