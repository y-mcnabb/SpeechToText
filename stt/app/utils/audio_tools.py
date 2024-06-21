import os
import subprocess
from tempfile import NamedTemporaryFile
from typing import Optional

from loguru import logger
from pydub import AudioSegment

from app.utils.file_tools import get_size_mb, suffix_to_filename


def convert_to_wav(input_file: str, output_file: Optional[str] = None) -> None:
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + ".wav"

    command = f'ffmpeg -i "{input_file}" -vn -acodec pcm_s16le -ar 44100 -ac 1 "{output_file}"'  # noqa

    try:
        subprocess.run(command, shell=True, check=True)
        logger.info(f'Successfully converted "{input_file}" to "{output_file}"')

    except subprocess.CalledProcessError as err:
        logger.info(
            f'Error: {err}, could not convert "{input_file}" to "{output_file}"'
        )  # noqa


def compress_large_audio(input_file: str, output_file: str, target_size_mb=24) -> None:
    # whisper only accepts audio files under 26MB, hardcoded here to 24 for an extra margin
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)

    # Calculate the current size of the audio file
    original_size_mb = get_size_mb(input_file)

    # Calculate the compression ratio needed to achieve the target size
    compression_ratio = target_size_mb / original_size_mb
    new_frame_rate = int(audio.frame_rate * compression_ratio)

    # Apply compression by reducing the frame rate
    audio.export(output_file, format="wav", parameters=["-ar", f"{new_frame_rate}"])

    # Export the compressed audio to a new WAV file
    # Log information about the compression
    compressed_size = get_size_mb(output_file)
    logger.info(f"Original size: {original_size_mb:.2f} MB")
    logger.info(f"Target size: {target_size_mb} MB")
    logger.info(f"Compressed size: {compressed_size:.2f} MB")


def compress_audio_file(data: bytes) -> bytes:
    tmp_files = []

    with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(data)
        tmp_files.append(tmp.name)
        tmp_filename = tmp.name

    # Compress file if too big
    target_size_mb = 24  # Whisper can only transcribe 25 MB or smaller audio files
    if get_size_mb(tmp_filename) > target_size_mb:
        tmp_filename_compressed = suffix_to_filename(tmp_filename, "_compressed")
        compress_large_audio(tmp_filename, tmp_filename_compressed)
        tmp_files.append(tmp_filename_compressed)
        tmp_filename = tmp_filename_compressed

        with open(tmp_filename, "rb") as f:
            data = f.read()

        os.remove(tmp_filename)

    return data
