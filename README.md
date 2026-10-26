# ResearchAI — LangChain Multi-Agent Research System

ResearchAI is an open-source research assistant that turns a question into a cited, reviewable report. It searches the web, extracts content from a relevant page, drafts a report, and asks a critic chain to review the result. A Streamlit interface lets you inspect and download each stage of the research.

## Features

- Web search powered by Tavily
- Article text extraction with multiple HTML parsing libraries
- LLM-generated reports and critic feedback
- Streamlit chat interface with in-session research history
- Separate views and downloads for reports, search results, extracted content, feedback, and source links

## Requirements

- Python 3.10 or newer
- A [Groq API key](https://console.groq.com/keys)
- A [Tavily API key](https://app.tavily.com/)

The configured chat model is `qwen/qwen3.8-27b` through Groq. The application also includes the LangChain Google GenAI integration as a dependency, although Groq is the provider currently configured in the agent code.

## Installation

Clone the repository and move into its directory:

```bash
git clone https://github.com/hanifsidhartha26/LangChain-Multi-Agent-Research-System.git
cd LangChain-Multi-Agent-Research-System
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a `.env` file in the repository root and add your API keys:

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Keep `.env` private; do not commit API keys or other secrets.

## Run the app

Start the Streamlit interface from the repository root:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, enter a research question in the chat input, and wait for the pipeline to complete. The result tabs provide the report, search results, extracted page content, critic feedback, and source links. Use the download buttons to export the individual outputs.

For a simple command-line example, run:

```bash
python main.py
```

`main.py` runs the research pipeline for a sample topic and prints its output to the terminal.

## Architecture

```text
Research question
       |
       v
Streamlit UI (app.py)
       |
       v
Research pipeline (src/pipelines/pipeline.py)
       |
       +--> Search agent --> Tavily web search
       |
       +--> Reader agent --> fetch and extract a source page
       |
       +--> Writer chain --> draft a structured report
       |
       +--> Critic chain --> provide a score, strengths, and improvements
       |
       v
Results shown in the UI and available to download
```

The search and reader workers and the writer and critic chains are defined in `src/agents/agents.py`. Web search and page extraction tools live in `src/tools/tools.py`. The pipeline coordinates those components and returns the search results, scraped content, report, and feedback to the UI.

## Technologies

- **Python** — application language
- **Streamlit** — interactive web interface
- **LangChain** — model integrations, prompt templates, tools, and output parsing
- **Groq** — configured LLM provider, using `qwen/qwen3.8-27b`
- **Tavily** — web search API
- **Requests, Trafilatura, Readability, Beautiful Soup, and lxml** — page retrieval and content extraction
- **python-dotenv** — local environment-variable loading

## Project structure

```text
.
├── app.py                  # Streamlit chat and research-results UI
├── main.py                 # Command-line example
├── requirements.txt        # Python dependencies
└── src/
    ├── agents/agents.py    # Search/reader workers and writer/critic chains
    ├── pipelines/          # Research pipeline orchestration
    └── tools/tools.py      # Web search and page extraction tools
```

## Contributing

Contributions are welcome. Open an issue to discuss a bug or proposed change, then submit a pull request with a clear description of the change and any relevant validation steps. Never include API keys or other secrets in a contribution.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
