# Class AI Agent

An AI-powered agent built with NVIDIA's API for processing class transcripts, generating summaries, and answering questions about class content.

## Features

- 📝 **Transcript Management**: Store and organize class transcripts
- 🤖 **AI Summarization**: Automatically generate summaries using NVIDIA's Nemotron model
- 💬 **Q&A System**: Ask questions about specific classes or across multiple classes
- 🖥️ **CLI Interface**: Interactive and command-line interfaces for easy usage
- 💾 **Persistent Storage**: JSON-based storage for transcripts and summaries

## Setup

### Prerequisites

- Python 3.8 or higher
- NVIDIA API key ([Get one here](https://build.nvidia.com/))

### Installation

1. Clone the repository:
```bash
cd nvidiahack2025
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
```bash
export NVIDIA_API_KEY="your_api_key_here"
```

Or pass it directly when running the CLI:
```bash
python cli.py --api-key "your_api_key_here"
```

## Usage

### Interactive Mode (Recommended)

Simply run the CLI without arguments for an interactive menu:

```bash
python cli.py
```

You'll be presented with options to:
1. Add a new class transcript
2. List all classes
3. Ask a question
4. View/Generate summary
5. Exit

### Command-Line Mode

#### Add a transcript from a file:
```bash
python cli.py add cs101-lecture1 --title "Introduction to Python" --file transcript.txt
```

#### Add a transcript from text:
```bash
python cli.py add cs101-lecture2 --title "Data Structures" --text "Today we learned about lists and dictionaries..."
```

#### List all classes:
```bash
python cli.py list
```

#### Ask a question about a specific class:
```bash
python cli.py ask cs101-lecture1 "What are the main topics covered?"
```

#### Ask a question across all classes:
```bash
python cli.py ask all "What did we learn about Python data structures?"
```

#### View or generate a summary:
```bash
python cli.py summary cs101-lecture1
```

#### Regenerate a summary:
```bash
python cli.py summary cs101-lecture1 --regenerate
```

## Programmatic Usage

You can also use the agent directly in your Python code:

```python
from class_agent import ClassAIAgent

# Initialize the agent
agent = ClassAIAgent(api_key="your_api_key")

# Add a transcript
agent.add_class_transcript(
    class_id="cs101-lecture1",
    transcript="Today we covered Python basics...",
    title="Introduction to Python"
)

# Ask a question (streaming)
for chunk in agent.ask_question("cs101-lecture1", "What are the key takeaways?"):
    print(chunk, end='', flush=True)

# Get a summary
summary = agent.summarize_transcript("cs101-lecture1")
print(summary)

# Ask across multiple classes
for chunk in agent.ask_across_classes("Compare the topics from all lectures"):
    print(chunk, end='', flush=True)
```

## Project Structure

```
nvidiahack2025/
├── ai_agent.py           # Base NVIDIA AI agent wrapper
├── transcript_manager.py # Transcript storage and management
├── class_agent.py        # Main class AI agent with summarization and Q&A
├── cli.py               # Command-line interface
├── requirements.txt     # Python dependencies
├── transcripts/         # Storage directory for transcripts (auto-created)
└── README.md           # This file
```

## How It Works

1. **Transcript Storage**: Transcripts are stored as JSON files in the `transcripts/` directory with metadata including title, timestamp, and summary.

2. **Summarization**: Uses NVIDIA's Nemotron Nano 9B model with thinking tokens to generate comprehensive summaries of class content.

3. **Q&A System**: Provides context from transcripts (and summaries) to the AI model to answer questions accurately, citing specific parts of the class when relevant.

4. **Cross-Class Search**: Can search and synthesize information across multiple class transcripts to answer comparative or broader questions.

## API Details

This project uses NVIDIA's API with the following configuration:
- **Model**: `nvidia/nvidia-nemotron-nano-9b-v2`
- **Features**: Thinking tokens for improved reasoning
- **Streaming**: Supports real-time response streaming

## Examples

### Example Transcript

Create a file `example_transcript.txt`:
```
In today's lecture, we covered the fundamentals of machine learning.

We started with supervised learning, where the algorithm learns from labeled data. 
The main types are classification and regression. Classification predicts categories, 
while regression predicts continuous values.

Next, we discussed unsupervised learning, which finds patterns in unlabeled data. 
Common techniques include clustering and dimensionality reduction.

Key takeaways:
1. Always split your data into training and test sets
2. Feature engineering is crucial for model performance
3. Start simple before trying complex models

Homework: Implement a linear regression model on the housing dataset.
```

Then add it:
```bash
python cli.py add ml101-lecture1 --title "Intro to Machine Learning" --file example_transcript.txt
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
