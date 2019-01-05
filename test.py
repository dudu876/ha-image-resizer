import os
import cv2
import shutil
import requests
import argparse
import time

SERVICE_URL = "http://localhost:5000/"


def run_conversion(video, n):
    frames_paths = split_to_frames(video, n)
    start = time.time()
    requests.post(SERVICE_URL, json={"paths": frames_paths, "n": str(n)})
    end = time.time()
    print(f"Instance {n} finished, total runtime is {end-start:.2f} seconds,"
          f" conversion frame-rate is {len(frames_paths)/(end-start):.2f} frames per second")


def split_to_frames(video, n):
    os.mkdir(f"tmp/vid-instance{n}")
    vid_cap = cv2.VideoCapture(video)
    length = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    paths = []
    for i in range(length):
        success, image = vid_cap.read()
        if success:
            img_path = f"tmp/vid-instance{n}/frame{i}.jpg"
            cv2.imwrite(img_path, image)  # save frame as JPG file
            paths.append(img_path)
    return paths


if __name__ == '__main__':
    # Arguments handling
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", default=1, help="Number of instances")
    parser.add_argument("-m", default=1, help="Seconds to wait between instances")
    parser.add_argument("-f", "--file", default="SampleVideo_1280x720_1mb.mp4", help="Video file path")
    args = parser.parse_args()
    n, m, video = int(args.n), int(args.m), args.file

    # Clear temp dir if exist and create a new one
    tmp_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
    if os.path.isdir(tmp_dir_path):
        shutil.rmtree(tmp_dir_path)
    os.mkdir("tmp")

    # For each instance, run conversion and sleep for m seconds
    for n in range(int(n)):
        run_conversion(video, n+1)
        time.sleep(m)
