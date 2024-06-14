## Speech-to-Text Praat met Henk Techniek Assistant with Azure OpenAI Integration

### Overview

Welcome to the Speech-to-Text Techniek assistant Praat met Henk! This solution combines speech recognition technology with the power of Azure OpenAI services to seamlessly convert recorded audio, such as malfunction incident reports and maintenance updates. Beyond simple transcription and summarization, our assistant goes a step further by restructuring the transcribed text into a report following a given template, with the aim to ensure that all reports and updates are as complete and informative as possible.

### Key Features

**1. Speech-to-Text Conversion**

Effortlessly transcribe your recorded audio files into text using advanced speech recognition algorithms. The integration with Azure OpenAI services ensures high accuracy and reliability in converting spoken words into written form. Languages implemented are Dutch, English, and potentially Serbo-Croatian and Moroccan Arabic (with Berber as a remote possibility).

**2. GPT-Powered Summarization**

Harness the power of the OpenAI GPT model to generate concise reports following specific templates based on the transcribed content.

**3. Customization and Adaptability**

The restructured report can be tailored based on configuring parameters such as length, language preferences, and specific mandatory elements for the report (e.g. what system is malfunctioning? what is the specific problem?). Our solution is designed to be adaptable to various use cases, ensuring a personalized experience for every user. This allows this solution to be adapted to bus drivers, infrasturcture and other departments in HTM.

**4. Seamless Integration with DevOps**

Integrate our Speech-to-Text GPT Assistant directly into your DevOps workflow. Manage your transcriptions and summaries alongside your project code, making it easy to collaborate, track changes, and maintain a comprehensive record of your audio content.

## Getting Started

### Clone the Repository:

```
https://htmnl@dev.azure.com/htmnl/DataScience/_git/DataScience
```

... and then cd into the `stt` directory.

### Install Dependencies:

Poetry is a tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you. Poetry offers a lockfile to ensure repeatable installs, and can build your project for distribution.

For more information on how to install Poetry on your operating system, click [here](https://python-poetry.org/docs/#installation).

Once you have Poetry installed, run the following command from the root directory of the project:

```
poetry install
```

This command will also create a `.venv` virtual environment within your local project structure. Be sure to activate it before beginning with development.

If you need to add additional packages or libraries as you develop, run the following command:

```
poetry add <package_name>
```

### Configure Azure OpenAI Credentials:

Set up your Azure OpenAI credentials in a `.env` configuration file to enable seamless integration with the speech recognition and GPT services.

To allow web app deployment, storage write access, and OpenAI inference API calls, we'll be using our HTM Entra ID account. Make sure that you've got permissions to use these resources (with Data & Integration).

Make sure you have Azure Developer CLI installed. Please visit https://aka.ms/azure-dev for installation instructions and then, once installed, authenticate to your Azure account using 'azd auth login'.

### To run the strimlit app:

```
cd ui
streamlit run main.py
```
