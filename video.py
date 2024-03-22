from dataclasses import dataclass
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.tools.subtitles import SubtitlesClip
import re
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
from textwrap import wrap

from youtube import YouTube
import json

OUTPUT = "/Users/tianchenzhong/Movies/kpop_test"
FIREFOX_PATH = ""
assert (
    FIREFOX_PATH != ""
), "Please set the path to your Firefox profile in the FIREFOX_PATH variable"


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
    minutes, seconds = map(int, timestamp.split(":"))
    # hours, minutes, seconds = map(int, timestamp.split(":"))
    total_seconds = minutes * 60 + seconds
    # Calculate the total number of seconds
    # total_seconds = hours * 3600 + minutes * 60 + seconds

    return total_seconds


def find_strings_between_quotation_marks(input_string):
    # Regular expression to find strings between quotation marks
    pattern = r'"(.*?)"'
    # Using re.findall to find all occurrences of the pattern in the input string
    matches = re.findall(pattern, input_string)
    return matches


@dataclass
class Caption:
    title: str
    time_start: str
    time_end: str
    description: str
    tags: str


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
        self.caption_list = self.read_caption_file()

    def read_caption_file(self):
        with open(self.caption_file, "r") as file:
            rs = json.load(file)
        return [Caption(**r) for r in rs]

    def burn_srt_to_video(self):
        if not self.srt_path:
            print("Error: No SRT file provided.")
            return
        if self.srt_video_path:
            print("Error: SRT file already in video.")
            return
        video = VideoFileClip(self.video_path)
        generator = lambda txt: TextClip(
            split_caption(txt), font="Arial", fontsize=24, color="white"
        )
        subs = SubtitlesClip(self.srt_path, generator)
        subtitles = SubtitlesClip(subs, generator)
        # srt = SubtitlesClip(self.srt_path, video.size)

        result = CompositeVideoClip([video, subtitles.set_pos(("center", "bottom"))])
        output_path = self.video_path.rsplit(".", 1)[0] + "_captioned.mp4"
        self.srt_video_path = output_path
        result.write_videofile(output_path, codec="libx264", audio_codec="aac")

    def cut_video(self):

        for i in range(len(self.caption_list)):
            output = os.path.join(self.output_path, self.video_name + str(i) + ".mp4")
            if os.path.exists(output):
                print(f"Error: The file '{output}' already exists.")
                continue
            starttime = self.caption_list[i].time_start
            start_seconds = timestamp_to_seconds(starttime)
            endtime = self.caption_list[i].time_end
            end_seconds = timestamp_to_seconds(endtime)
            ffmpeg_extract_subclip(
                self.srt_video_path,
                start_seconds,
                end_seconds,
                targetname=os.path.join(
                    self.output_path, self.video_name + str(i) + ".mp4"
                ),
            )

    def burn_caption_to_video(
        self,
        single_video_path,
        caption,
        font="Arial-Bold",
        fontsize=40,
        color="white",
        add_background=False,
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
        video_clip = video_clip.set_position(("center", "center"))
        if add_background:
            video_width, video_height = video_clip.size
            # 假定大多数手机屏幕宽高比为9:16，可以根据你的需要调整
            aspect_ratio = 9 / 16
            # 为了保持视频原始宽高比，同时填充到手机屏幕尺寸，我们需要计算背景应有的尺寸
            # 如果视频宽度比基于9:16的高度计算的宽度小，我们就用这个宽度，否则直接使用视频宽度
            bg_width = video_width
            # 背景高度保持不变，即视频的高度加上字幕的高度（这里简化处理，实际上可能需要更精确地计算）
            bg_height = int(bg_width / aspect_ratio)

            bg_clip = ColorClip(
                size=(bg_width, bg_height), color=(0, 0, 0)
            ).set_duration(video_clip.duration)
        new_caption = split_caption(caption)
        print(new_caption)
        if add_background:
            y_position = bg_height // 2 - video_clip.size[1] // 2 - fontsize * 5
            new_caption = split_caption(caption, max_width=10)
        else:
            y_position = video_clip.size[1] // 2
        # Create a text clip (customize as needed)
        txt_clip = TextClip(
            new_caption,
            fontsize=fontsize,
            font=font,
            color=color,
            stroke_color="black",
            stroke_width=1,
        )
        print(y_position)

        txt_clip = txt_clip.set_position(("center", y_position)).set_duration(
            video_clip.duration
        )
        if add_background:
            result = CompositeVideoClip([bg_clip, video_clip, txt_clip])
        else:
            result = CompositeVideoClip([video_clip, txt_clip])

        # Output file path
        output_path = single_video_path.rsplit(".", 1)[0] + "_captioned.mp4"

        # Write the result to file
        result.write_videofile(
            output_path, codec="libx264", audio_codec="aac", fps=video_clip.fps
        )

        print(f"Caption burned successfully. Output saved to '{output_path}'")

    def burn_captions_to_all_videos(
        self, font="Arial-Bold", add_background=False, fontsize=40
    ):

        for i in range(len(self.caption_list)):
            video = os.path.join(self.output_path, self.video_name + str(i) + ".mp4")
            caption = self.caption_list[i].title
            self.burn_caption_to_video(
                video,
                caption,
                font=font,
                add_background=add_background,
                fontsize=fontsize,
            )

    def upload_youtube(self):

        for i in range(len(self.caption_list)):
            video = os.path.join(
                self.output_path, self.video_name + str(i) + "_captioned.mp4"
            )
            if not os.path.exists(video):
                print(f"Error: The file '{video}' does not exist.")
                continue
            y = YouTube(
                "account_uuid",
                "account_nickname",
                FIREFOX_PATH,
                video,
                {
                    "title": self.caption_list[i].title,
                    "description": self.caption_list[i].description,
                },
            )
            y.upload_video()


# y.upload_video()


v = Video(
    "mp4 path",
    "srt path",
    caption_file="caption.json",
)

v.burn_srt_to_video()
print("burned srt")
v.cut_video()
print("cut video")
v.burn_captions_to_all_videos(font="黑体-简-中等", add_background=True, fontsize=150)
print("burned captions")
v.upload_youtube()
