from typing import Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from moviepy.video.tools.subtitles import SubtitlesClip
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
from selenium_firefox import *
from selenium import webdriver
import time

YOUTUBE_TEXTBOX_ID = "textbox"
YOUTUBE_MADE_FOR_KIDS_NAME = "VIDEO_MADE_FOR_KIDS_MFK"
YOUTUBE_NOT_MADE_FOR_KIDS_NAME = "VIDEO_MADE_FOR_KIDS_NOT_MFK"
YOUTUBE_NEXT_BUTTON_ID = "next-button"
YOUTUBE_RADIO_BUTTON_XPATH = '//*[@id="radioLabel"]'
YOUTUBE_DONE_BUTTON_ID = "done-button"


from termcolor import colored


def build_url(youtube_video_id: str) -> str:
    """
    Builds the URL to the YouTube video.

    Args:
        youtube_video_id (str): The YouTube video ID.

    Returns:
        url (str): The URL to the YouTube video.
    """
    return f"https://www.youtube.com/watch?v={youtube_video_id}"


def error(message: str, show_emoji: bool = True) -> None:
    """
    Prints an error message.

    Args:
        message (str): The error message
        show_emoji (bool): Whether to show the emoji

    Returns:
        None
    """
    emoji = "❌" if show_emoji else ""
    print(colored(f"{emoji} {message}", "red"))


def success(message: str, show_emoji: bool = True) -> None:
    """
    Prints a success message.

    Args:
        message (str): The success message
        show_emoji (bool): Whether to show the emoji

    Returns:
        None
    """
    emoji = "✅" if show_emoji else ""
    print(colored(f"{emoji} {message}", "green"))


def info(message: str, show_emoji: bool = True) -> None:
    """
    Prints an info message.

    Args:
        message (str): The info message
        show_emoji (bool): Whether to show the emoji

    Returns:
        None
    """
    emoji = "ℹ️" if show_emoji else ""
    print(colored(f"{emoji} {message}", "magenta"))


def warning(message: str, show_emoji: bool = True) -> None:
    """
    Prints a warning message.

    Args:
        message (str): The warning message
        show_emoji (bool): Whether to show the emoji

    Returns:
        None
    """
    emoji = "⚠️" if show_emoji else ""
    print(colored(f"{emoji} {message}", "yellow"))


def question(message: str, show_emoji: bool = True) -> str:
    """
    Prints a question message and returns the user's input.

    Args:
        message (str): The question message
        show_emoji (bool): Whether to show the emoji

    Returns:
        user_input (str): The user's input
    """
    emoji = "❓" if show_emoji else ""
    return input(colored(f"{emoji} {message}", "magenta"))


class YouTube:
    """
    Class for YouTube Automation.

    Steps to create a YouTube Short:
    1. Generate a topic [DONE]
    2. Generate a script [DONE]
    3. Generate metadata (Title, Description, Tags) [DONE]
    4. Generate AI Image Prompts [DONE]
    4. Generate Images based on generated Prompts [DONE]
    5. Convert Text-to-Speech [DONE]
    6. Show images each for n seconds, n: Duration of TTS / Amount of images [DONE]
    7. Combine Concatenated Images with the Text-to-Speech [DONE]
    """

    def __init__(
        self,
        account_uuid: str,
        account_nickname: str,
        fp_profile_path: str,
        video_path: str,
        metadata: Dict[str, str],
    ) -> None:
        """
        Constructor for YouTube Class.

        Args:
            account_uuid (str): The unique identifier for the YouTube account.
            account_nickname (str): The nickname for the YouTube account.
            fp_profile_path (str): Path to the firefox profile that is logged into the specificed YouTube Account.
            niche (str): The niche of the provided YouTube Channel.
            language (str): The language of the Automation.

        Returns:
            None
        """
        self._account_uuid: str = account_uuid
        self._account_nickname: str = account_nickname
        self._fp_profile_path: str = fp_profile_path
        # self._niche: str = niche
        # self._language: str = language

        self.images = []

        # Initialize the Firefox profile
        self.options: Options = Options()

        # Set headless state of browser
        # if get_headless():
        #    self.options.add_argument("--headless")

        # Set the profile path
        self.options.add_argument("-profile")
        self.options.add_argument(fp_profile_path)

        # Set the service
        self.service: Service = Service(GeckoDriverManager().install())

        # Initialize the browser
        self.browser: webdriver.Firefox = webdriver.Firefox(
            service=self.service, options=self.options
        )
        self.video_path: str = video_path
        self.metadata = metadata

    def get_channel_id(self) -> str:
        """
        Gets the Channel ID of the YouTube Account.

        Returns:
            channel_id (str): The Channel ID.
        """
        driver = self.browser
        driver.get("https://studio.youtube.com")
        time.sleep(2)
        channel_id = driver.current_url.split("/")[-1]
        self.channel_id = channel_id

        return channel_id

    def upload_video(self) -> bool:
        """
        Uploads the video to YouTube.

        Returns:
            success (bool): Whether the upload was successful or not.
        """
        try:
            self.get_channel_id()

            driver = self.browser
            verbose = True

            # Go to youtube.com/upload
            driver.get("https://www.youtube.com/upload")

            # Set video file
            FILE_PICKER_TAG = "ytcp-uploads-file-picker"
            file_picker = driver.find_element(By.TAG_NAME, FILE_PICKER_TAG)
            INPUT_TAG = "input"
            file_input = file_picker.find_element(By.TAG_NAME, INPUT_TAG)
            file_input.send_keys(self.video_path)

            # Wait for upload to finish
            time.sleep(5)

            # Set title
            textboxes = driver.find_elements(By.ID, YOUTUBE_TEXTBOX_ID)

            title_el = textboxes[0]
            description_el = textboxes[-1]

            if verbose:
                info("\t=> Setting title...")

            title_el.click()
            time.sleep(1)
            title_el.clear()
            title_el.send_keys(self.metadata["title"])

            if verbose:
                info("\t=> Setting description...")

            # Set description
            time.sleep(10)
            description_el.click()
            time.sleep(0.5)
            description_el.clear()
            description_el.send_keys(self.metadata["description"])

            time.sleep(0.5)

            # Set `made for kids` option
            if verbose:
                info("\t=> Setting `made for kids` option...")

            is_for_kids_checkbox = driver.find_element(
                By.NAME, YOUTUBE_MADE_FOR_KIDS_NAME
            )
            is_not_for_kids_checkbox = driver.find_element(
                By.NAME, YOUTUBE_NOT_MADE_FOR_KIDS_NAME
            )

            # if not get_is_for_kids():
            is_not_for_kids_checkbox.click()
            # else:
            #    is_for_kids_checkbox.click()

            time.sleep(0.5)

            # Click next
            if verbose:
                info("\t=> Clicking next...")

            next_button = driver.find_element(By.ID, YOUTUBE_NEXT_BUTTON_ID)
            next_button.click()

            # Click next again
            if verbose:
                info("\t=> Clicking next again...")
            next_button = driver.find_element(By.ID, YOUTUBE_NEXT_BUTTON_ID)
            next_button.click()

            # Wait for 2 seconds
            time.sleep(2)

            # Click next again
            if verbose:
                info("\t=> Clicking next again...")
            next_button = driver.find_element(By.ID, YOUTUBE_NEXT_BUTTON_ID)
            next_button.click()

            # Set as unlisted
            if verbose:
                info("\t=> Setting as unlisted...")

            radio_button = driver.find_elements(By.XPATH, YOUTUBE_RADIO_BUTTON_XPATH)
            radio_button[2].click()

            if verbose:
                info("\t=> Clicking done button...")

            # Click done button
            done_button = driver.find_element(By.ID, YOUTUBE_DONE_BUTTON_ID)
            done_button.click()

            # Wait for 2 seconds
            time.sleep(2)

            # Get latest video
            if verbose:
                info("\t=> Getting video URL...")

            # Get the latest uploaded video URL
            driver.get(
                f"https://studio.youtube.com/channel/{self.channel_id}/videos/short"
            )
            time.sleep(2)
            videos = driver.find_elements(By.TAG_NAME, "ytcp-video-row")
            first_video = videos[0]
            anchor_tag = first_video.find_element(By.TAG_NAME, "a")
            href = anchor_tag.get_attribute("href")
            if verbose:
                info(f"\t=> Extracting video ID from URL: {href}")
            video_id = href.split("/")[-2]

            # Build URL
            url = build_url(video_id)

            self.uploaded_video_url = url

            if verbose:
                success(f" => Uploaded Video: {url}")

            # Add video to cache
            self.add_video(
                {
                    "title": self.metadata["title"],
                    "description": self.metadata["description"],
                    "url": url,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

            # Close the browser
            driver.quit()

            return True
        except:
            self.browser.quit()
            return False
