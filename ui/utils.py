import os
import subprocess
from typing import Optional, Tuple

import pandas as pd
import streamlit as st
from jiwer import wer
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from loguru import logger
from openai import AzureOpenAI
from pydub import AudioSegment
from streamlit.delta_generator import DeltaGenerator


def initialise_azure_openai_speech() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_SPEECH_DEPLOYMENT_NAME"),
    )


def initialise_azure_openai_chat() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )


def initialize_dynamic_chat():
    return ChatOpenAI(model=os.getenv("AZURE_GPT_DEPLOYMENT_NAME"))


def load_css(file_name: str) -> DeltaGenerator:
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def load_html(file_name: str) -> DeltaGenerator:
    with open(file_name) as f:
        st.markdown(f.read(), unsafe_allow_html=True)


def load_rag(path="data/context/woordenlijst_werk_termen_20240304.csv"):
    word_df = pd.read_csv(path, sep=";")
    word_list = word_df["words"].tolist()

    vectorstore = FAISS.from_texts(word_list, embedding=OpenAIEmbeddings())

    retriever = vectorstore.as_retriever()

    return retriever


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


def load_prompts(path: str, prompt_type: str) -> Tuple[str, str]:
    with open(os.path.join(path, prompt_type, "system_content.txt"), "r") as f:
        system_content = f.read()

    with open(os.path.join(path, prompt_type, "user_content.txt"), "r") as f:
        user_content = f.read()

    return system_content, user_content


def get_size_mb(file):
    """Get filesize in MB"""
    size_bytes = os.path.getsize(file)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb


def suffix_to_filename(file_path, suffix):
    """Adds a suffix to the end of the filename (but before the extension)"""
    base_name, extension = os.path.splitext(file_path)
    new_file_path = f"{base_name}{suffix}{extension}"
    return new_file_path


def compress_large_audio_file(
    input_file: str, output_file: str, target_size_mb=24
) -> None:
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


def convert_any_to_wav(input_file: str, output_file: str):
    file_format = input_file.split(".")[1]
    sound = AudioSegment.from_file(input_file, format=file_format)
    sound.export(output_file, format="wav")


def write_to_file(text, filename):
    """Write the given text to a file with line breaks after every period.

    Args:
        text (str): The text to write to the file.
        filename (str): The name of the file to write to.
    """
    # Write the modified text to the file
    with open(filename, "w") as file:
        file.write(text)


def read_text_file(filename):
    """Read the content of a text file.

    Args:
        filename (str): The name of the text file to read.

    Returns:
        str: The content of the text file.
    """
    try:
        with open(filename, "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None


def convert_any_to_wav(input_file: str, output_file: str):
    file_format = input_file.split(".")[1]
    sound = AudioSegment.from_file(input_file, format=file_format)
    sound.export(output_file, format="wav")


def calculate_word_error_rate(reference: str, transcription: str) -> float:
    """
    Calculate word error rate of transcription based on gold transcription reference.

    Args:
        reference: Gold transcription to compare model transcription by
        transcription: Model transcription to evaluate the accuracy of

    Returns:
        A float value of the error rate
    """
    wer_score = wer(reference, transcription)
    print(f"Word Error Rate is: {wer_score}")
    return wer_score
