import os
import multiprocessing
from flask import Flask
from flask import jsonify, request
from PIL import Image
app = Flask(__name__)


NEW_SIZE = (300, 300)


def worker_main(queue, frames_dict, l):
    print(os.getpid(), "working")

    # Init the global lock for all processes
    global lock
    lock = l

    # The main worker loop
    while True:
        item = queue.get(True)
        resize_image(item["path"], os.getpid())

        # Update the shared dict under the lock so that only one process can update it at a time
        lock.acquire()
        frames_dict[item["n"]] -= 1
        lock.release()


def resize_image(path, pid=0):
    img = Image.open(path)
    img = img.resize(NEW_SIZE, Image.LANCZOS)
    img.save(path)
    print(f"image {path} has been resized by {pid}")


@app.route('/', methods=['POST'])
def resize():
    args = request.get_json()
    n, paths = args.get("n"), args.get("paths")

    # Init the shared dict for instance n with the count of paths
    frames_dict[n] = len(paths)

    # If no paths supplied, respond with error, otherwise start processing
    if paths:
        # Add all paths to queue so that they could be processed in parallel
        for path in paths:
            queue.put({"path": path, "n": n})

        # Wait until the instance is finished to respond successfully
        while True:
            if frames_dict[n] == 0:
                break
        return jsonify({"status": "Resize task added to queue"}), 200
    else:
        return jsonify({"status": "No image path supplied"}), 500


if __name__ == '__main__':
    # Multiprocessing init
    queue = multiprocessing.Queue()
    frames_dict = multiprocessing.Manager().dict()
    l = multiprocessing.Lock()
    the_pool = multiprocessing.Pool(multiprocessing.cpu_count(), worker_main, (queue, frames_dict, l))

    # Run flask app
    app.run()
