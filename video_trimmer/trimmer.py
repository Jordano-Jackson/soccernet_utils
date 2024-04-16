import os
import cv2
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

def trim_video(video_list, start_frame, end_frame, output_dir, fps=25):
    """
    Trim video and save to local directory
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for video_path in video_list:
        absolute_path = video_path[0]
        relative_path = video_path[1] 

        final_output_dir = os.path.join(output_dir, os.path.dirname(relative_path))
        if not os.path.exists(final_output_dir):
            os.makedirs(final_output_dir)

        cap = cv2.VideoCapture(absolute_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_path = os.path.join(final_output_dir, os.path.basename(relative_path))
        print(relative_path, final_output_dir)
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        current_frame = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if current_frame >= start_frame and current_frame <= end_frame:
                out.write(frame)
            current_frame += 1
            if current_frame > end_frame:
                break

        cap.release()
        out.release()

    print("Video trimming done.")


def find_video_files(directory):

    """
    Search for video files in the specified directory

    Args:
    - directory (str): path to the directory

    Returns:
    - list: A list of paths of all videos(only mp4 format)
    """

    video_list = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.mp4'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                #video_list.append(full_path)
                video_list.append((full_path, relative_path))
                print(relative_path)
    
    return video_list

def main(args):
    video_list = find_video_files(args.path)
    trim_video(video_list, args.start_frame, args.end_frame, args.output_dir, args.fps)

if __name__ == '__main__': 
    parser = ArgumentParser(description='parser', formatter_class=ArgumentDefaultsHelpFormatter)    
    parser.add_argument('--path',   required=True, type=str, help='Path to the dataset folder' )
    parser.add_argument('--output_dir',   required=True, type=str, help='Path to the folder to be stored trimmed videos' )
    parser.add_argument('--start_frame', required=False, type=int, default=63, help='Starting frame number from which the video will be trimmed')
    parser.add_argument('--end_frame', required=False, type=int, default=87, help='Ending frame number at which the video trimming will stop')
    parser.add_argument('--fps', required=False, type=int, default=17, help='Number of frames per second')

    args = parser.parse_args()

    main(args)