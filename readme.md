### ChatPDF

ChatPDF is a simple web application that allows users to upload a PDF file and interact with it through a chat interface. The application uses RAG (Retrieval-Augmented Generation) along with LangChain to process the PDF content, generate embeddings using HuggingFaceEmbeddings, and provide conversational responses powered by Ollama.

### Features
- **Upload PDF**: Easily upload your PDF files to the application.
- **Chat with PDFs**: Engage in a conversation with the content of your PDF.
- **State-of-the-Art Models**:
  - **Embeddings**: Powered by HuggingFaceEmbeddings (`BAAI/bge-small-en`).
  - **LLM**: Utilizing Ollama's `dolphin-mistral:latest` model for generating responses.

### Environment Configuration

Make sure to configure your environment variables as shown in the `.env` file:

```env
# Ollama server URL (use https://localhost:11434 if running locally)
OLLAMA_URL=http://localhost:11434

# Model used by Ollama
OLLAMA_MODEL="dolphin-mistral:latest"

# Hugging Face model for generating embeddings
HUGGING_FACE_MODEL_NAME="BAAI/bge-small-en"

# Device to run the Hugging Face model on ("cpu" or "cuda")
HUGGING_FACE_MODEL_KWARGS="cpu" 

# Path to store Chroma files
CHROMA_PATH="./tmp/chroma"

# File path to save the uploaded PDFs
UPLOAD_FOLDER='static/tmp/'
```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DevAro178/Learning-made-fun.git
   cd Learning-made-fun
   ```

2. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file with the content provided above.

4. Run the application:
   ```bash
   flask run
   ```

### Usage

- Navigate to the web interface.
- Upload a PDF file using the provided upload button.
- Start chatting with your PDF file through the chat interface.

### Credits

- **UI Design**: The user interface is inspired by [Emma Delaney's blog on Medium](https://emma-delaney.medium.com/how-to-create-your-own-chatgpt-in-html-css-and-javascript-78e32b70b4be).
  - **Author**: Emma Delaney

### License

This project is licensed under the MIT License. See the LICENSE file for more details.

### Contact

- **LinkedIn**: [Muhammad Ammad](https://www.linkedin.com/in/muhammad-ammad-123630224/)
- **Email**: [me.ammad1786@gmail.com](mailto:me.ammad1786@gmail.com)
