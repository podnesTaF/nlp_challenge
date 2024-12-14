import os

def merge_transcriptions(transcriptions):
    """
    Merge a list of transcription strings into a single string.

    Args:
        transcriptions (list): List of transcription strings.

    Returns:
        str: Combined transcription.
    """
    return " ".join(transcriptions)

def clean_transcription(text):
    """
    Clean up and format transcription text.

    Args:
        text (str): Raw transcription text.

    Returns:
        str: Cleaned and formatted text.
    """
    return text.strip().capitalize()

def ensure_directories_exist(directories):
    """
    Ensure specified directories exist, create them if necessary.

    Args:
        directories (list): List of directory paths to validate.
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
