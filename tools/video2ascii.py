import cv2
import argparse


def frame_to_ascii(frame, width):
    ascii_chars = "@%#*+=-:. "
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert the frame color to gray scale
    frame = cv2.resize(frame, (width, int(frame.shape[0] / frame.shape[1] * width * 0.6)))  # Resize the frame
    ascii_str = ""
    for pixels in frame:
        for pixel in pixels:
            ascii_str += ascii_chars[pixel // 32]
        ascii_str += "\n"
    return ascii_str


def convert_video_to_ascii(video_file_path, output_file_path, width, skip_frames):
    video = cv2.VideoCapture(video_file_path)
    frame_count = 0
    with open(output_file_path, "w") as f:
        while True:
            ret, frame = video.read()
            if not ret:
                break
            if frame_count % skip_frames == 0:
                ascii_frame = frame_to_ascii(frame, width)
                f.write(ascii_frame + "\n" + "<END_FRAME>\n")
            frame_count += 1
    video.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", help="Path to the video", required=True)
    parser.add_argument("-o", "--output", help="Path to the output file", required=True)
    parser.add_argument("-w", "--width", help="Resulting width of the video", default=40, type=int)
    parser.add_argument("-s", "--skip_frames", help="Number of frames to skip", default=10, type=int)
    args = parser.parse_args()
    convert_video_to_ascii(args.video, args.output, args.width, args.skip_frames)
