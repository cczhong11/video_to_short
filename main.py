# @title this part works fine which parse the output and get clips
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import re

from textwrap import wrap

required_video_file = "/Users/tianchenzhong/Downloads/video/alfred/seokmatthew.mp4"
# length = [0, 31, 46]
name = "matthew"
output = """**Clip 1:**

* **Timestamp:** 00:08:53 - 00:09:18
* **Description:** "Kpop idol creates protein-packed peanut butter magic with just powder and milk! 🤯"
* **Why it could go viral:** This clip showcases a surprising and healthy twist on peanut butter, which could spark curiosity and interest among viewers.

**Clip 2:**

* **Timestamp:** 00:10:45 - 00:10:57
* **Description:** "He tried to hide the burnt pancake, but we all saw it! 😂"
* **Why it could go viral:** This relatable moment of a cooking mishap adds humor and authenticity to the video, making it engaging and shareable.

**Clip 3:**

* **Timestamp:** 00:12:25 - 00:12:57
* **Description:** "Blind taste test! Can Gunwook guess the secret ingredient in this delicious pancake? 👀"
* **Why it could go viral:** This clip builds suspense and anticipation as viewers wait to see if Gunwook can identify the unique flavor.

**Clip 4:**

* **Timestamp:** 00:17:19 - 00:17:39
* **Description:** "Yujin approves! This banana peanut butter mint pancake is a winner! 😋"
* **Why it could go viral:** This clip highlights the successful creation of a unique and delicious pancake combination, potentially inspiring viewers to try it themselves.

**Clip 5:**

* **Timestamp:** 00:22:35 - 00:22:58
* **Description:** "One-handed cooking challenge! Can he make a heart-shaped pancake with just one hand? 💖"
* **Why it could go viral:** This clip adds a fun and challenging element to the video, keeping viewers engaged and entertained.

**Bonus Clip:**

* **Timestamp:** 00:28:47 - 00:29:37
* **Description:** "Pistachio pancake surprise! This unexpected flavor combination is a hit! 🤩"
* **Why it could go viral:** This clip introduces viewers to a unique and delicious flavor combination they may not have considered before.
'"""


def find_timestamps(input_string):
    # Define a regular expression pattern to match timestamps
    timestamp_pattern = r"\d{2}:\d{2}:\d{2}\b"

    # Find all occurrences of timestamps in the input string
    timestamps = re.findall(timestamp_pattern, input_string)

    return timestamps


timestamps = find_timestamps(output)
print("Timestamps found:", timestamps)


def timestamp_to_seconds(timestamp):
    # Split the timestamp string into hours, minutes, and seconds
    hours, minutes, seconds = map(int, timestamp.split(":"))

    # Calculate the total number of seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds

    return total_seconds


for i in range(0, len(timestamps) - 1, 2):
    starttime = timestamps[i]
    start_seconds = timestamp_to_seconds(starttime)
    endtime = timestamps[i + 1]
    end_seconds = timestamp_to_seconds(endtime)
    ffmpeg_extract_subclip(
        required_video_file,
        start_seconds,
        end_seconds,
        targetname=name + str(i + 1) + ".mp4",
    )


# @title this part which burns in caption has problem
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os


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


def burn_caption_to_video(
    video_path, caption, font="Arial-Bold", fontsize=50, color="white"
):
    # Check if the video file exists
    if not os.path.exists(video_path):
        print(f"Error: The file '{video_path}' does not exist.")
        return
    print(video_path)
    # Load the video clip
    video_clip = VideoFileClip(video_path)
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
    output_path = video_path.rsplit(".", 1)[0] + "_captioned.mp4"

    # Write the result to file
    result.write_videofile(
        output_path, codec="libx264", audio_codec="aac", fps=video_clip.fps
    )

    print(f"Caption burned successfully. Output saved to '{output_path}'")


def find_strings_between_quotation_marks(input_string):
    # Regular expression to find strings between quotation marks
    pattern = r'"(.*?)"'
    # Using re.findall to find all occurrences of the pattern in the input string
    matches = re.findall(pattern, input_string)
    return matches


strings_in_quotes = find_strings_between_quotation_marks(output)
print(strings_in_quotes)
folder = "/Users/tianchenzhong/Downloads/video/alfred/"
for i in range(0, len(timestamps) - 1, 2):
    video_path = folder + name + str(i + 1) + ".mp4"
    print(video_path)
    caption = strings_in_quotes[i]
    burn_caption_to_video(video_path, caption)
