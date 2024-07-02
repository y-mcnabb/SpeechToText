import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from ui.chat import read_text_file, response_repair_report
from ui.transcribe import transcribe_audio
from ui.utils import load_css, load_html

load_dotenv()


def main():
    # Settings
    st.set_page_config(
        page_title="Praat met Henk",
        initial_sidebar_state="collapsed",
        page_icon="ui/static/logo.svg",
    )
    load_html("./templates/header.html")
    load_css("./static/css/background.css")
    load_css("./static/css/menu.css")
    load_css("./static/css/buttons.css")

    # Upload MP3 or WAV audio file
    uploaded_file = st.file_uploader(
        "Upload an audio file", type=["mp3", "wav"]
    )

    file_path = None
    transcript = None
    text = None
    report = None
    corrected_report = None
    
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()
        
        # Display uploaded audio file for playback
        st.audio(audio_bytes, format="audio/wav")

        # Save audio file to a local temporary directory
        tmp_dir = tempfile.mkdtemp()
        file_path = os.path.join(tmp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

    if file_path is not None:
        # Convert audio to text
        transcript = transcribe_audio(file_path)
        
        if transcript is not None:
            with st.expander("Transcriptie bekijken"):
                st.write(transcript)

            with st.expander("Systeem prompt bekijken"):
                system_prompt = read_text_file("app/prompts/systeem_prompt.txt")
                st.write(system_prompt)
            
            with st.expander("Storingstemplate bekijken"):
                storingstemplate = read_text_file("app/prompts/storingstemplate.txt")
                st.write(storingstemplate)

            if st.button("Rapport maken"):
                report = response_repair_report(
                    "app/prompts/systeem_prompt.txt",
                    "app/prompts/storingstemplate.txt",
                    transcript)
                    
                if report is not None:
                    with st.expander("Rapport bekijken"):
                        st.write(report)

            # with col2:
            #      if st.button("Controleer de rapport"):
            #          corrected_report = response_review_report(transcript, report)
                     
            #          if corrected_report is not None:
            #             with st.expander("See transcribed text"):
            #                 st.write(corrected_report)

if __name__ == "__main__":
    main()
