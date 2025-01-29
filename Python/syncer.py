import os
import cv2
import ffmpeg
import numpy as np
from datetime import datetime
from natsort import natsorted
import subprocess

# 🔹 CONFIGURATION
IMAGE_FOLDER = "./Data3"
VIDEO_FILE = "phone_video.mp4"
OUTPUT_VIDEO = "output_synced.mp4"
HEATMAP_FPS = 5  # Heatmap images are captured at 5 FPS
VIDEO_FPS = 30  # Android video FPS
FRAME_HOLD = VIDEO_FPS // HEATMAP_FPS  # How many frames to duplicate
OUTPUT_FPS = VIDEO_FPS  # Final synchronized FPS

# 🔹 Step 1: Extract timestamps from heatmap filenames
def extract_timestamp(filename):
    """Extract timestamp from image filename in format: YYYY-MM-DD HH-MM-SS.SS"""
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)
    try:
        return datetime.strptime(name, "%Y-%m-%d %H-%M-%S.%f")
    except ValueError:
        return None

image_files = [os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.png', '.jpg'))]
image_files = natsorted(image_files, key=lambda x: extract_timestamp(x))  # Sort by timestamp

# 🔹 Step 2: Extract video duration
def get_video_duration(video_path):
    """ Get video duration in seconds """
    metadata = ffmpeg.probe(video_path)
    return float(metadata['format']['duration'])

video_duration = get_video_duration(VIDEO_FILE)

# 🔹 Step 3: Create 30 FPS Heatmap Video
def create_heatmap_video(image_files, output_file, frame_hold=FRAME_HOLD, fps=OUTPUT_FPS):
    """Create a heatmap video where each image is held for multiple frames to match 30 FPS."""
    first_image = cv2.imread(image_files[0])
    height, width, _ = first_image.shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    for img_path in image_files:
        frame = cv2.imread(img_path)
        for _ in range(frame_hold):  # Hold each frame for 6 frames
            video_writer.write(frame)

    video_writer.release()

heatmap_video = "heatmap_video.mp4"
create_heatmap_video(image_files, heatmap_video)

# 🔹 Step 4: Resize Heatmap Video to Match Video Duration
def stretch_heatmap_video(heatmap_video, video_duration, output_fps, output_file):
    """ Stretch heatmap video to match the Android video's duration """
    ffmpeg.input(heatmap_video).filter("setpts", f"({video_duration} / {video_duration})*PTS").output(output_file, r=output_fps).run()


stretched_heatmap_video = "stretched_heatmap_video.mp4"
stretch_heatmap_video(heatmap_video, video_duration, OUTPUT_FPS, stretched_heatmap_video)

# 🔹 Step 5: Merge Videos (Side-by-Side or Overlay)
def merge_videos(video1, video2, output_file, mode="side_by_side"):
    """Merge two videos: overlay or side-by-side"""
    if mode == "overlay":
        ffmpeg.input(video1).filter("scale", "iw/2", "-1").output(output_file).run()
    elif mode == "side_by_side":
        ffmpeg.hstack(
            ffmpeg.input(video1).filter("scale", "-1", "720"),  # Resize heatmap
            ffmpeg.input(video2).filter("scale", "-1", "720"),
            v=1, a=0
        ).output(output_file).run()

def resize_video(input_file, output_file, width=960, height=720):
    """ Resize the input video to the desired width and height """
    ffmpeg.input(input_file).filter("scale", width, height).output(output_file).run()


def merge_videos_side_by_side(video1, video2, output_file):
    """ Merge two videos side by side using filter_complex """
    out = ffmpeg.filter([video1, video2], 'hstack').output(output_file)

# Set desired resolution
desired_width = 960
desired_height = 720

# Resize both heatmap and Android videos
resized_heatmap_video = "resized_heatmap_video.mp4"
resized_android_video = "resized_android_video.mp4"

resize_video(stretched_heatmap_video, resized_heatmap_video, desired_width, desired_height)
resize_video(VIDEO_FILE, resized_android_video, desired_width, desired_height)

final_output = "final_synced_video.mp4"
merge_videos_side_by_side(resized_heatmap_video, resized_android_video, final_output)

print("✅ Video successfully created:", final_output)

## ffmpeg -i resized_android_video.mp4 -i resized_heatmap_video.mp4 -filter_complex "[0:v][1:v]hstack[out]" -map "[out]" output.mp4