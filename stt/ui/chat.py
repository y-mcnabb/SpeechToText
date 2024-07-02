import os

#from langchain.model_laboratory import R import RAG
import pandas as pd

from ui.utils import initialise_azure_openai_chat, read_text_file


def response_identify_language(prompt: str) -> str:
    client = initialise_azure_openai_chat()
    response = client.chat.completions.create(
        model=os.getenv("AZURE_GPT_DEPLOYMENT_NAME"),
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that helps tram drivers and technicians in their own language.",
            },
            {
                "role": "user",
                "content": f"What is the language of the following text? Answer with just the name of language:\n{prompt}",
            },
        ],
    )
    return response.choices[0].message.content


def response_review_transcription(prompt: str) -> str:
    client = initialise_azure_openai_chat()
    response = client.chat.completions.create(
        model=os.getenv("AZURE_GPT_DEPLOYMENT_NAME"),
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that helps tram drivers and technicians in their own language.",
            },
            {
                "role": "user",
                "content": f"""Your task is to review the following trasncription of a tram machanic's description\n
                of their repair and maintenance incident, and replace any words that seem to be incorrectly transcribed.\n  
                Pay attention to the coherence of the text, and the mentioning of technical terms, abreviations, models names and numbers.\n
                Pay special attention to technical terminology related to trams and their engines, wheels, break systems.\n
                The description will oftentime be in Dutch, but some of the technical terms may be in English.\n
                If there are English words in the text, for example: speed sensor, don't change it to the Dutch equivalent.\n
                Don't change the text except for the corrections. Don't summarize it.\n   
                Here is the transcript you need to review and correct (if necessary):\n {prompt}\n""",
            },
        ],
    )
    return response.choices[0].message.content


def response_identify_report(prompt: str) -> str:
    client = initialise_azure_openai_chat()
    response = client.chat.completions.create(
        model=os.getenv("AZURE_GPT_DEPLOYMENT_NAME"),
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that helps tram drivers and technicians send reports or ask questions about malfunctions or repair.",
            },
            {
                "role": "user",
                "content": f"""What is the topic of the following text? 
                Choose one option out of the following three: 
                1. Malfunction report, 
                2. Repair report, 
                3. Question about a tram system or malfunction to be sent to the knowledge base.
                The text:\n{prompt}""",
            },
        ],
    )
    return response.choices[0].message.content


def response_fault_report(prompt: str) -> str:
    client = initialise_azure_openai_chat()
    response = client.chat.completions.create(
        model=os.getenv("AZURE_GPT_DEPLOYMENT_NAME"),
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that helps tram drivers submit their fault report.",
            },
            {
                "role": "user",
                "content": f"""Restucture the following text into a malfunction report that includes only the components listed below.
                Write only one sentence for each of these components.
                1. Which system in tram was defective.
                2. What are the fault symptoms or the nature of the problem?
                3. What is the fault cause?
                \n{prompt}""",
            },
        ],
    )
    return response.choices[0].message.content


def response_repair_report(system_prompt_path: str, human_prompt_path: str, transcript:str) -> str:
    
    system_prompt = read_text_file(system_prompt_path)
    human_prompt = read_text_file(human_prompt_path)
    #transcript = read_text_file(transcript_path)
    human_transcript_prompt = human_prompt.format(transcript=transcript)
    
    client = initialise_azure_openai_chat()
    response = client.chat.completions.create(
        model=os.getenv("AZURE_GPT_DEPLOYMENT_NAME"),
        messages=[
            {
                "role": "system",
                "content": f"{system_prompt}"
            },
            {
                "role": "user",
                "content": f"{human_transcript_prompt}", 
            },
        ],
    )
    return response.choices[0].message.content


def response_review_report(transcription: str, prompt: str) -> str:
    client = initialise_azure_openai_chat()
    response = client.chat.completions.create(
        model=os.getenv("AZURE_GPT_DEPLOYMENT_NAME"),
        messages=[
            {
                "role": "system",
                "content": "You are a Dutch-speaking AI assistant that helps tram drivers and technicians send reports or ask questions about malfunctions or repair.",
            },
            {
                "role": "user",
                "content":
                    f"""Please remove from the Dautch report below information that is not in the reference Datch text. 
                    Preserve the structure and language of the report.
                    Here is the report:\n{prompt} and here is the reference text:\n{transcription}."""
            },
        ],
    )
    return response.choices[0].message.content

# def load_rag(path='data/context/woordenlijst_werk_termen_20240304.csv'):
#     word_df = pd.read_csv(csv_file, sep=';')   
#     word_list = word_df["words"].tolist()

#     # Initialize RAG model
#     rag = RAG()

#     # Set the context for the RAG model using the list of words
#     rag.add_context(word_list)

#     # Generate text using RAG model and prompt
#     generated_text = rag.generate(prompt)

#     # Print the generated text
#     print(generated_text)
