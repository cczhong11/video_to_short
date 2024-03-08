from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import re
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
from textwrap import wrap

OUTPUT = "/Users/tianchenzhong/Movies/kpop_test"


def split_caption(caption, max_width=20):
    """
    Splits a caption into multiple lines based on a maximum width.

    Args:
        caption (str): The caption to split.
        max_width (int): The maximum width of each line in characters.

    Returns:
        str: The caption with newline characters inserted to ensure it
             doesn't exceed the maximum width.
    """
    wrapped_lines = wrap(caption, max_width)
    return "\n".join(wrapped_lines)


def timestamp_to_seconds(timestamp):
    # Split the timestamp string into hours, minutes, and seconds
    hours, minutes, seconds = map(int, timestamp.split(":"))

    # Calculate the total number of seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds

    return total_seconds


def find_strings_between_quotation_marks(input_string):
    # Regular expression to find strings between quotation marks
    pattern = r'"(.*?)"'
    # Using re.findall to find all occurrences of the pattern in the input string
    matches = re.findall(pattern, input_string)
    return matches


class Video:
    def __init__(
        self,
        video_path,
        srt_path=None,
        caption_file=None,
        srt_in_video: bool = False,
        output_path=None,
    ):
        self.video_path = video_path
        self.srt_path = srt_path
        self.caption_file = caption_file
        self.srt_video_path = None
        if srt_in_video:
            self.srt_video_path = video_path
        self.video_name = video_path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        self.output_path = output_path
        if not self.output_path:
            self.output_path = OUTPUT

    def burn_srt_to_video(self):
        if not self.srt_path:
            print("Error: No SRT file provided.")
            return
        if self.srt_video_path:
            print("Error: SRT file already in video.")
            return
        video = VideoFileClip(self.video_path)
        generator = lambda txt: TextClip(txt, font="Arial", fontsize=24, color="white")
        subs = SubtitlesClip(self.srt_path, generator)
        subtitles = SubtitlesClip(subs, generator)
        # srt = SubtitlesClip(self.srt_path, video.size)

        result = CompositeVideoClip([video, subtitles.set_pos(("center", "bottom"))])
        output_path = self.video_path.rsplit(".", 1)[0] + "_captioned.mp4"
        self.srt_video_path = output_path
        result.write_videofile(output_path, codec="libx264", audio_codec="aac")

    def get_time_stamps_from_caption(self):
        with open(self.caption_file, "r") as file:
            lines = file.read()
        return self.find_timestamps(lines)

    def find_timestamps(self, input_string):
        # Define a regular expression pattern to match timestamps
        timestamp_pattern = r"\d{2}:\d{2}:\d{2}\b"

        # Find all occurrences of timestamps in the input string
        timestamps = re.findall(timestamp_pattern, input_string)

        return timestamps

    def cut_video(self):

        timestamps = self.get_time_stamps_from_caption()
        if not timestamps:
            print("Error: No timestamps found in caption file.")
            return
        self.timestamps = timestamps
        for i in range(0, len(timestamps) - 1, 2):
            output = os.path.join(
                self.output_path, self.video_name + str(i + 1) + ".mp4"
            )
            if os.path.exists(output):
                print(f"Error: The file '{output}' already exists.")
                continue
            starttime = timestamps[i]
            start_seconds = timestamp_to_seconds(starttime)
            endtime = timestamps[i + 1]
            end_seconds = timestamp_to_seconds(endtime)
            ffmpeg_extract_subclip(
                self.srt_video_path,
                start_seconds,
                end_seconds,
                targetname=os.path.join(
                    self.output_path, self.video_name + str(i + 1) + ".mp4"
                ),
            )

    def burn_caption_to_video(
        self, single_video_path, caption, font="Arial-Bold", fontsize=40, color="white"
    ):
        # Check if the video file exists
        if not os.path.exists(single_video_path):
            print(f"Error: The file '{single_video_path}' does not exist.")
            return
        print(single_video_path)
        output_path = single_video_path.rsplit(".", 1)[0] + "_captioned.mp4"
        if os.path.exists(output_path):
            print(f"Error: The file '{output_path}' already exists.")
            return
        # Load the video clip
        video_clip = VideoFileClip(single_video_path)
        if not video_clip.fps:
            video_clip.fps = 30  # Set a default fps if none is detected
        new_caption = split_caption(caption)
        y_position = (video_clip.size[1] / 2) + 50
        # Create a text clip (customize as needed)
        txt_clip = TextClip(
            new_caption,
            fontsize=fontsize,
            font=font,
            color=color,
            stroke_color="black",
            stroke_width=1,
        )

        # Position the text clip on the lower third of the video
        txt_clip = txt_clip.set_position(("center", y_position)).set_duration(
            video_clip.duration
        )

        # Overlay the text on the video
        result = CompositeVideoClip([video_clip, txt_clip])

        # Output file path
        output_path = single_video_path.rsplit(".", 1)[0] + "_captioned.mp4"

        # Write the result to file
        result.write_videofile(
            output_path, codec="libx264", audio_codec="aac", fps=video_clip.fps
        )

        print(f"Caption burned successfully. Output saved to '{output_path}'")

    def burn_captions_to_all_videos(self):
        with open(self.caption_file, "r") as file:
            text = file.read()
        descriptions = re.findall(r'\*\*Description:\*\* "(.*?)"', text)
        for i in range(0, len(self.timestamps) - 1, 2):
            video = os.path.join(
                self.output_path, self.video_name + str(i + 1) + ".mp4"
            )
            caption = descriptions[i // 2]
            self.burn_caption_to_video(video, caption)

    def upload_youtube(self):
        pass


v = Video(
    "/Users/tianchenzhong/Downloads/seokmatthew_captioned.mp4",
    "/Users/tianchenzhong/Downloads/U9vYbgk53mM.srt",
    caption_file="caption.txt",
    srt_in_video=True,
)

v.burn_srt_to_video()
print("burned srt")
v.cut_video()
print("cut video")
v.burn_captions_to_all_videos()
print("burned captions")
