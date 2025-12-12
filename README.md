
# 🏦 Bank of Maharashtra RAG-based Loan Product Assistant

[![Project Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)](https://github.com/yourusername/yourrepo)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Built with LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-9cf.svg)](https://github.com/langchain-ai/langgraph)
[![Powered by Gemini](https://img.shields.io/badge/LLM-Gemini_2.5_Flash-4285F4.svg)](https://ai.google/gemini)

> A reliable, fact-based AI assistant designed to answer complex user queries about Bank of Maharashtra's loan products using **Retrieval-Augmented Generation (RAG)** and a sophisticated workflow management system.

---

## 🧭 Table of Contents

* [Project Overview](#-project-overview)
* [Architectural Decisions](#-architectural-decisions)
* [How It Works (End-to-End Pipeline)](#-how-it-works-end-to-end-pipeline)
* [Project Structure](#-project-structure)
* [Project Setup](#-project-setup)
* [Key Libraries](#-key-libraries)
* [Data Strategy: Chunking, Processing, & Storage](#-data-strategy-chunking-processing--storage)
* [Model and Tool Choices](#-model-and-tool-choices)
* [Challenges Faced](#-challenges-faced)
* [Potential Improvements](#-potential-improvements)
* [🚀 Quick Start](#-quick-start)
* [🤝 Support](#-support)

---

## 🌟 Project Overview

This project implements an AI assistant specializing in **Bank of Maharashtra (BOM) loan products**. It leverages the **RAG** paradigm to provide accurate, up-to-date, and contextually relevant answers by combining:

1.  **Retrieval:** Contextually relevant data chunks from scraped official bank documentation.
2.  **Generation:** Advanced language modeling (Gemini 2.5 Flash) for fluent, natural, and explanatory responses.

The core goal is to minimize LLM "hallucinations" by grounding all answers in verifiable, scraped data.

---

## 🏗️ Architectural Decisions

The pipeline is built for **modularity**, **extensibility**, and **high performance**.

* **Hybrid Reasoning (RAG):** Combines the factual rigor of retrieval with the explanatory power of an LLM.
* **Workflow Management (LangGraph):** The query flow is represented as a state machine using `langgraph`. This allows for easy extension (e.g., adding a fact-checking step or dynamic tool routing).
* **Separation of Concerns:** Data handling (scraping/chunking) is completely decoupled from the RAG runtime for maintainability.
* **Local Vector Store (FAISS):** Ensures high-speed, low-latency, in-memory dense retrieval, crucial for a real-time assistant.

---

## ⚙️ How It Works (End-to-End Pipeline)

The system uses a sequential workflow managed by LangGraph:

1.  **User Query → Analyzer:** The LLM checks if the user's initial query is too ambiguous or terse and requires reformulation for better retrieval.
2.  **Optional Rewriting (LLM):** If needed, the LLM rewrites the query to be more specific, keyword-rich, and optimized for semantic search.
3.  **Retriever (FAISS):** The refined query is encoded and used to perform a vector similarity search against the **FAISS-based store** to fetch the top **K** most relevant document snippets.
4.  **Responder (LLM):** The retrieved context and the original query are passed to the LLM (Gemini 2.5 Flash), which synthesizes a fluent, well-structured final answer.
5.  **Explainability:** The answer is generated with reference to the specific document chunks used, ensuring transparency and trust.

---

## 📂 Project Structure

```bash
proj_1211_new/
│
├── rag_pipeline/
│   ├── agentic_rag.py          # 🚀 Main RAG workflow (LangGraph entrypoint)
│   ├── chunking.py             # Data chunking logic
│   └── embedding.py            # Embedding generation routines
│
├── scrapping_scripts/          # Scripts for extracting data from BOM website/docs
│   ├── script_1.py             # ... per-source scraping files
│   └── run_all_scripts.py      # Batch orchestrator for scraping
│
├── data/
│   ├── raw/                    # Raw text from scraping
│   ├── chunks/                 # Chunked, preprocessed text
│   ├── processed_data/         # Stagewise, cleaned data
│   └── vector_store/           # FAISS index (faiss_index.bin) and metadata
│
├── utils/
│   └── preprocess_text.py      # Shared text cleanup and normalization functions
│
├── requirements.txt
└── test_pipeline.py            # Test scripts

```

🛠️ Project Setup
-----------------

### 1\. Clone the repository

Bash

```
git clone [https://github.com/yourusername/yourrepo.git](https://github.com/yourusername/yourrepo.git)
cd yourrepo

```

### 2\. Environment Setup

Install dependencies using the recommended package manager:

Bash

```
# Using 'uv' (recommended for speed)
uv pip install -r requirements.txt

# Alternatively, using standard 'pip'
# pip install -r requirements.txt

```

### 3\. Set Environment Variables

Create a file named **`.env`** in the root directory and add your key:

Code snippet

```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

```

> **Note:** The Gemini API key is mandatory for the LLM-backed generation and query rewriting steps.

### 4\. Prepare Data

Follow these steps to create or refresh the vector store:

| **Step** | **Script** | **Action** |
| --- | --- | --- |
| **Scrape Data** | `scrapping_scripts/run_all_scripts.py` | Extracts raw documents from the source(s) into `/data/raw/`. |
| **Preprocess & Chunk** | `rag_pipeline/chunking.py` | Cleans, normalizes, and splits the raw text into manageable chunks (`/data/chunks/`). |
| **Embed & Index** | `rag_pipeline/embedding.py` | Converts chunks into dense vectors and saves them in the **FAISS** vector store (`/data/vector_store/`). |

### 5\. Run the Assistant

Start the interactive terminal session:

Bash

```
python rag_pipeline/agentic_rag.py

```

You will be prompted to enter questions about Bank of Maharashtra loan products.

* * * * *

📚 Key Libraries
----------------

| **Category** | **Library** | **Purpose** |
| --- | --- | --- |
| **LLM/RAG** | `google-generativeai` | Primary access to **Gemini 2.5 Flash** for generation and reasoning. |
| **Orchestration** | `langgraph` | Manages the complex state-based workflow of the RAG pipeline. |
| **Vector Store** | `faiss` | High-performance similarity search for low-latency retrieval. |
| **Embedding** | `sentence-transformers` | Used to generate high-quality semantic embeddings from text chunks. |
| **Scraping** | `requests`, `bs4` | Used in the scraping scripts for data extraction. |

* * * * *

💾 Data Strategy: Chunking, Processing & Storage
------------------------------------------------

### Raw Data

-   **Source:** Scraped from multiple official/semi-structured Bank of Maharashtra web sources.

-   **Storage:** Preserved in `/data/raw/` for transparency and reproducibility.

### Preprocessing

-   Text is aggressively cleaned to remove noise: scripts, repeated headers/footers, legal disclaimers, and boilerplate text.

-   Normalization (case, punctuation, whitespace) is applied to ensure chunk consistency.

### Chunking Rationale

-   Uses custom logic to maximize **topical coherence** within each chunk while adhering to the embedding model's input limits.

-   Chunk size and overlap were **empirically tuned** to achieve the best balance between context preservation and relevance during retrieval.

### Vector Store Management

-   The **all-MiniLM-L6-v2** model is used to embed each chunk.

-   The vectors are indexed in FAISS, and crucial **metadata** (like original source document/URL) is saved to power the final source attribution.

* * * * *

🧠 Model and Tool Choices
-------------------------

| **Component** | **Model/Tool** | **Rationale** |
| --- | --- | --- |
| **Embedding Model** | `all-MiniLM-L6-v2` | Chosen for its **speed**, small footprint, and solid semantic performance on financial/technical documents. |
| **LLM (Generation)** | **Gemini 2.5 Flash** | Used for high-quality **final answer synthesis** and prompt rewriting. Selected for enterprise-grade quality and reliable API access. |
| **Retrieval Index** | **FAISS Flat Index** | Provides **fastest nearest-neighbor search**, which is a critical bottleneck for RAG performance. |

* * * * *

⚠️ Challenges Faced
-------------------

-   **Dynamic/Messy Source Pages:** Required writing custom, highly robust scraping scripts for 15+ different document layouts and sources.

-   **Data Quality Issues:** Significant cleaning effort needed to remove duplicate boilerplate text, ambiguous tables, and unhelpful legal footnotes.

-   **Chunking Granularity:** Fine-tuning chunk size was a major challenge; had to find the 'sweet spot' that kept related concepts together without overwhelming the LLM's context window.

-   **API Limits:** Implemented an adaptive backoff and retry mechanism (in `_safe_generate()`) to handle Gemini API quota limits robustly.

-   **Metadata Integrity:** Maintaining a precise link between the FAISS vector index order and the corresponding chunk metadata was vital for accurate source attribution.

* * * * *

📈 Potential Improvements
-------------------------

-   **Hybrid Search:** Implement a combination of semantic vector search (for concept queries) and sparse keyword-based search (for named entity or exact match queries).

-   **Advanced Chunking:** Explore more sophisticated chunking algorithms like sentence boundary detection with dynamic windowing or topic-based segmentation.

-   **Web UI:** Develop a simple web frontend using Streamlit or Flask that visually presents the final answer alongside the retrieved source chunks.

-   **Incremental Indexing:** Set up a process for periodic re-scraping and indexing to ensure the assistant remains up-to-date with new product launches or term changes.

-   **Fine-Tuning:** Fine-tune the embedding model or a smaller LLM on the specific financial domain corpus for superior performance.

* * * * *

🚀 Quick Start
--------------

Use these commands to get the RAG assistant running locally:

Bash

```
# 1. Install dependencies
uv pip install -r requirements.txt

# 2. Export your LLM API key (replace 'your_key_here')
echo "GEMINI_API_KEY=your_key_here" > .env

# 3. (Optional) Scrape and refresh data
python scrapping_scripts/run_all_scripts.py

# 4. (Optional) Re-chunk & re-embed if data was refreshed
python rag_pipeline/chunking.py
python rag_pipeline/embedding.py

# 5. Run the Assistant
python rag_pipeline/agentic_rag.py

```

* * * * *

🤝 Support
----------

For issues, troubleshooting, or help with expanding the project, please feel free to raise an issue in the repository or contact the maintainer directly.