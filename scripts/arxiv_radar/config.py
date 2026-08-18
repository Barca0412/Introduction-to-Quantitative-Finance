"""
Configuration module for LLM-Finance-Radar.
Contains all settings for arXiv categories, tags, LLM API, and data paths.
"""

import os
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Load environment variables from project root.
load_dotenv(BASE_DIR / ".env")

# Data directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Data file paths
PAPERS_FILE = DATA_DIR / "papers.json"
STATS_FILE = DATA_DIR / "stats.json"

# ============================================
# arXiv Categories
# ============================================
ARXIV_CATEGORIES = [
    "cs.AI",      # Artificial Intelligence
    "cs.CL",      # Computation and Language
    "cs.MA",      # Multiagent Systems
    "cs.IR",      # Information Retrieval
    "cs.SE",      # Software Engineering
    "cs.CE",      # Computational Engineering, Finance, and Science
    "q-fin.ST",   # Statistical Finance
    "q-fin.CP",   # Computational Finance
    "q-fin.PM",   # Portfolio Management
    "q-fin.TR",   # Trading and Market Microstructure
]

# # ============================================
# # Predefined Tags (15)
# # ============================================
# PREDEFINED_TAGS = {
#     "ai-finance": "AI/ML specifically applied to financial domains (stock prediction, portfolio optimization, risk management, credit scoring, fraud detection, quantitative trading, financial time series, sentiment analysis of financial data)",
#     "memory": "LLM memory mechanisms",
#     "agent-planning": "Agent planning and reasoning",
#     "deep-research": "Autonomous research agents",
#     "benchmark": "Evaluation frameworks",
#     "rag": "Retrieval-augmented generation",
#     "reasoning": "Chain-of-thought, tree-of-thought",
#     "multi-agent": "Multi-agent systems",
#     "code-generation": "AI-assisted programming",
#     "tool-use": "Function calling, tool usage",
#     "rlhf-alignment": "Reward learning and alignment",
#     "time-series": "Time series modeling",
#     "prompt-engineering": "Prompt engineering techniques",
#     "training-efficiency": "Efficient training methods",
#     "multimodal": "Multimodal models",
# }

"""
PREDEFINED_TAGS for LLM-Finance-Radar
Each tag value is a detailed description used in the LLM prompt to classify arXiv papers.
The descriptions are deliberately verbose to minimize false positives and false negatives.
"""

PREDEFINED_TAGS = {

    "ai-finance": """This tag covers all research at the intersection of artificial intelligence, machine learning, and the financial domain. A paper should be tagged ai-finance if it applies AI/ML methods to solve financial problems, or if it introduces financial datasets, benchmarks, or evaluation frameworks specifically designed for financial tasks.

Core areas include but are not limited to:
- **Stock and asset price prediction**: Using neural networks, transformers, LLMs, or other ML models to forecast stock prices, returns, volatility, or other financial time series. This includes technical analysis with ML, fundamental analysis with NLP, and hybrid approaches.
- **Portfolio optimization and management**: AI-driven asset allocation, portfolio construction, mean-variance optimization with ML enhancements, robo-advisory systems, dynamic rebalancing strategies using reinforcement learning, and risk-return tradeoff optimization.
- **Quantitative trading and market microstructure**: Algorithmic trading strategies, high-frequency trading models, market making with ML, order book modeling, limit order book prediction, trade execution optimization, transaction cost analysis, and market impact modeling.
- **Risk management and credit scoring**: Credit risk assessment, default prediction, Value-at-Risk (VaR) estimation with ML, stress testing, systemic risk analysis, counterparty risk modeling, and insurance risk modeling using AI methods.
- **Fraud detection and anti-money laundering (AML)**: Using ML/DL for detecting fraudulent transactions, anomalous trading patterns, insider trading detection, money laundering detection, and compliance automation.
- **Financial NLP and sentiment analysis**: Extracting financial signals from news, earnings calls, SEC filings, social media, analyst reports, or other textual financial data. Includes financial named entity recognition, financial question answering, and financial document understanding.
- **Financial forecasting**: Macroeconomic forecasting, interest rate prediction, exchange rate prediction, commodity price forecasting, inflation prediction, GDP forecasting, and economic indicator prediction using AI methods.
- **Derivatives pricing and computational finance**: Using neural networks or ML for option pricing, derivative valuation, Monte Carlo simulation acceleration, yield curve modeling, and stochastic calculus approximation.
- **Blockchain, cryptocurrency, and DeFi**: AI applications in crypto trading, DeFi protocol analysis, smart contract analysis, token valuation, and blockchain-based financial systems.
- **Financial agent systems**: LLM-based trading agents, multi-agent financial simulation, AI investment advisors, autonomous financial decision-making systems, and agent-based market simulation.
- **Financial benchmarks and datasets**: Papers that introduce or evaluate benchmarks specifically for financial AI tasks, such as financial QA benchmarks, trading strategy benchmarks, or financial NLP evaluation datasets.

Boundary clarification:
- DO tag: A paper that uses reinforcement learning to optimize a trading strategy → yes, this is ai-finance.
- DO tag: A paper that builds an LLM-based agent for investment research → yes, this is ai-finance.
- DO tag: A paper about time series forecasting that explicitly evaluates on financial datasets (stock prices, exchange rates) → yes, this is ai-finance.
- DO NOT tag: A general time series forecasting paper that only evaluates on weather or energy data → no, use time-series instead.
- DO NOT tag: A pure mathematical finance paper with no AI/ML component (e.g., pure stochastic calculus, pure option pricing theory) → no.
- DO NOT tag: A general NLP paper that happens to mention finance as one of many possible applications but does not actually experiment on financial data → no.

Key signals in title/abstract: "financial", "stock", "trading", "portfolio", "market", "asset pricing", "credit", "risk management", "fintech", "quantitative finance", "investment", "hedge fund", "alpha", "returns prediction", "earnings", "SEC filing", "Bloomberg", "S&P 500", "cryptocurrency", "DeFi".""",


    "memory": """This tag covers research on memory mechanisms for large language models and AI agents — specifically, how systems store, retrieve, update, and manage information beyond their immediate context window. A paper should be tagged memory if its primary contribution involves extending, augmenting, or analyzing the memory capabilities of neural models or agent systems.

Core areas include but are not limited to:
- **Long-term memory for LLMs**: Architectures and methods that allow language models to maintain and access information across conversations, sessions, or extended interactions. This includes persistent memory stores, memory databases, episodic memory systems, and long-term knowledge retention mechanisms.
- **Context window extension**: Research on extending the effective context length of transformers, including methods like sparse attention, sliding window attention, memory-augmented attention, landmark attention, and techniques that allow models to process documents far exceeding their native context window (e.g., 100K+ tokens).
- **Memory-augmented architectures**: Neural architectures that incorporate explicit external memory components, such as Memory Networks, Neural Turing Machines, Differentiable Neural Computers, memory-augmented transformers, and hybrid architectures combining parametric and non-parametric memory.
- **Retrieval-augmented memory**: Systems where the model retrieves from a memory store (distinct from RAG in that the focus here is on the memory management itself rather than retrieval from external knowledge bases). This includes memory indexing, memory compression, memory consolidation, and selective forgetting mechanisms.
- **Working memory and scratchpads**: Research on how models use intermediate computation space, working memory buffers, or scratchpad mechanisms to hold and manipulate information during complex reasoning tasks.
- **KV-cache optimization**: Methods for efficient key-value cache management in transformer inference, including KV-cache compression, eviction policies, quantization of cached states, and shared cache architectures for serving.
- **State and memory in recurrent and SSM architectures**: Memory mechanisms in state space models (Mamba, S4, etc.), RWKV, linear attention models, and other recurrent architectures that maintain hidden states as a form of compressed memory.
- **Agent memory systems**: Memory architectures for LLM-based agents, including how agents store and retrieve past observations, reflections, plans, and experiences. This covers memory streams (as in Generative Agents), reflection mechanisms, memory summarization, and hierarchical memory organization for agents.
- **Conversational memory**: Systems that track dialogue history, user preferences, and conversation context across multi-turn interactions, including personalization through memory and user modeling.
- **Memory evaluation and analysis**: Benchmarks, probing studies, or analytical work that measures how well models remember, retrieve, or utilize stored information, including studies on "lost in the middle" phenomena, needle-in-a-haystack tests, and context utilization analysis.

Boundary clarification:
- DO tag: A paper proposing a new architecture that adds an external memory bank to a transformer → yes.
- DO tag: A paper on KV-cache compression for efficient long-context inference → yes.
- DO tag: A paper about how LLM agents store and reflect on past experiences → yes.
- DO tag: A paper extending context windows from 4K to 128K tokens using novel attention mechanisms → yes.
- DO NOT tag: A paper about knowledge graphs or structured knowledge bases (unless the focus is specifically on using them as a memory mechanism for LLMs) → likely no, consider rag instead.
- DO NOT tag: A paper about model weights as "implicit memory" in a general discussion of neural network learning → no, too broad.
- DO NOT tag: A standard RAG paper where the focus is on retrieval quality rather than memory management → no, use rag instead.

Key signals in title/abstract: "memory", "long-term memory", "episodic memory", "memory-augmented", "context window", "context length", "KV cache", "memory retrieval", "memory bank", "state persistence", "memory stream", "conversational memory", "forgetting", "memory consolidation".""",


    "agent-planning": """This tag covers research on planning, reasoning, and decision-making capabilities of AI agents — particularly LLM-based agents that decompose complex tasks, create and execute plans, and adapt their strategies based on feedback. A paper should be tagged agent-planning if its primary contribution involves how autonomous agents formulate, execute, monitor, or revise plans to achieve goals.

Core areas include but are not limited to:
- **Task decomposition**: Methods for breaking down complex, high-level goals into manageable sub-tasks or sub-goals. This includes hierarchical task decomposition, recursive task splitting, and automatic generation of task dependency graphs.
- **Plan generation and search**: Algorithms and methods for generating action sequences to achieve goals, including tree search over action spaces (e.g., Monte Carlo Tree Search for agents), beam search over plans, plan enumeration, and LLM-based plan proposal.
- **ReAct and reasoning-action paradigms**: Research on frameworks where agents alternate between reasoning (thinking about what to do) and acting (executing actions in an environment), including ReAct, Reflexion, and related paradigms that interleave chain-of-thought reasoning with tool use or environment interaction.
- **Workflow orchestration**: Systems that coordinate multiple steps, tools, or sub-agents to complete complex workflows. This includes DAG-based workflow execution, conditional branching in agent plans, error recovery and re-planning, and dynamic workflow generation.
- **Goal-oriented agent architectures**: End-to-end architectures for autonomous agents that can pursue long-horizon goals, including systems like AutoGPT, BabyAGI, and other goal-driven agent frameworks that maintain and pursue objectives over many steps.
- **Planning under uncertainty**: Agent planning that accounts for stochastic environments, partial observability, or uncertain outcomes. This includes POMDP-based planning, contingency planning, and robust planning methods.
- **Self-reflection and plan revision**: Mechanisms by which agents evaluate the quality of their plans or past actions and revise their strategies accordingly. This includes self-critique, hindsight experience replay, and iterative refinement of plans based on execution feedback.
- **Embodied agent planning**: Planning for agents that operate in physical or simulated environments, including robotic task planning, navigation planning, and manipulation planning when driven by LLMs.
- **Web and computer-use agent planning**: Planning strategies for agents that interact with web browsers, desktop applications, or APIs to complete user tasks, including how agents decide which buttons to click, which forms to fill, and in what order.
- **Planning evaluation and benchmarks**: Benchmarks and evaluation methodologies specifically designed to assess agent planning capabilities, such as task completion rates, plan quality metrics, and planning efficiency measurements.
- **Skills and reinforcement learning for planning**: Using RL to train or improve agent planning capabilities, including skill discovery, option frameworks, and hierarchical RL for plan learning.

Boundary clarification:
- DO tag: A paper proposing a new framework for LLM agents to decompose and solve complex tasks step by step → yes.
- DO tag: A paper about an agent that searches over possible action sequences using MCTS to find optimal plans → yes.
- DO tag: A paper about ReAct-style agents that reason before acting → yes.
- DO tag: A paper about agent self-reflection and plan correction after execution failures → yes.
- DO NOT tag: A paper purely about chain-of-thought reasoning for math problems without any agent/action component → no, use reasoning instead.
- DO NOT tag: A paper about multi-agent cooperation protocols without focus on individual agent planning → no, use multi-agent instead.
- DO NOT tag: A paper about general reinforcement learning algorithms without specific application to LLM agent planning → no.

Key signals in title/abstract: "planning", "plan", "task decomposition", "agent", "autonomous agent", "workflow", "ReAct", "self-reflection", "goal-oriented", "action sequence", "sub-task", "re-planning", "agentic", "tool orchestration", "step-by-step execution".""",


    "deep-research": """This tag covers research on AI systems that can autonomously conduct multi-step research, investigation, or information synthesis — mimicking how a human researcher would explore a topic by searching, reading, analyzing, and synthesizing information from multiple sources. A paper should be tagged deep-research if it describes systems or methods for automated, iterative, deep information gathering and synthesis.

Core areas include but are not limited to:
- **Autonomous research agents**: AI systems that can independently formulate research questions, search for information across multiple sources (web, databases, APIs, documents), read and analyze found materials, and produce comprehensive research reports or answers. Examples include systems like Deep Research (by Google, OpenAI, or similar), automated literature review systems, and investigative AI agents.
- **Multi-step information gathering**: Systems that go beyond single-query search to perform iterative, adaptive information retrieval — where the results of one search inform the next query, creating a research trajectory. This includes multi-hop question answering over open-domain sources, follow-up question generation, and query refinement based on intermediate findings.
- **Literature survey and review automation**: AI systems that can automatically survey academic literature on a topic, identify key papers, extract findings, identify research gaps, and synthesize a coherent overview. This includes automated systematic review tools, citation network analysis for research discovery, and AI-assisted literature mapping.
- **Knowledge synthesis and report generation**: Methods for synthesizing information from multiple heterogeneous sources into coherent, comprehensive reports. This goes beyond simple summarization to include cross-source fact verification, conflicting information resolution, and structured knowledge assembly.
- **Fact-checking and verification agents**: Systems that autonomously verify claims by searching for evidence, cross-referencing multiple sources, and assessing the reliability of found information.
- **Scientific discovery agents**: AI systems designed to assist in or automate aspects of scientific discovery, including hypothesis generation, experiment design suggestion, data analysis, and conclusion synthesis.
- **Open-domain question answering with complex reasoning**: Systems that answer complex, open-ended questions by conducting research-like processes — breaking the question into sub-questions, gathering relevant information for each, and synthesizing a final answer.
- **Web browsing and exploration agents for research**: Agents that navigate the web, read pages, follow links, and collect information to answer research questions or compile knowledge on a topic.

Boundary clarification:
- DO tag: A paper describing an agent that iteratively searches the web, reads documents, and synthesizes a research report → yes.
- DO tag: A paper on automated literature review or survey generation systems → yes.
- DO tag: A paper about multi-hop open-domain QA where the system actively searches and reasons across multiple sources → yes.
- DO tag: A paper about fact-checking systems that autonomously gather evidence from multiple sources → yes.
- DO NOT tag: A standard RAG paper that does single-step retrieval + generation without iterative research → no, use rag instead.
- DO NOT tag: A simple document summarization paper without multi-step research components → no.
- DO NOT tag: A paper about web browsing agents primarily focused on task completion (e.g., booking flights) rather than information research → no, use agent-planning instead.
- DO NOT tag: A paper about search engine ranking or retrieval algorithms without the research agent component → no, consider rag.

Key signals in title/abstract: "deep research", "research agent", "literature review", "survey generation", "multi-step search", "information synthesis", "knowledge compilation", "investigative", "fact-checking", "evidence gathering", "multi-hop reasoning over documents", "autonomous research", "report generation from multiple sources".""",


    "benchmark": """This tag covers research that introduces, proposes, analyzes, or significantly extends evaluation frameworks, benchmarks, datasets, or leaderboards for assessing AI model capabilities. A paper should be tagged benchmark if its primary contribution is a new way to measure or evaluate AI system performance, or if it provides a significant meta-analysis of existing evaluation methods.

Core areas include but are not limited to:
- **New benchmark datasets**: Papers that introduce new evaluation datasets with carefully curated test cases, ground truth labels, and evaluation protocols. This includes benchmarks for language understanding, reasoning, coding, math, science, safety, alignment, and domain-specific tasks.
- **Evaluation frameworks and protocols**: Papers that propose new methodologies for evaluating AI systems, including novel metrics, evaluation pipelines, automated evaluation methods (LLM-as-judge), human evaluation protocols, and standardized testing procedures.
- **Leaderboard and ranking systems**: Papers that establish or analyze model ranking systems, including Elo-based rankings, arena-style evaluations, and comparative assessment methodologies.
- **Capability assessment**: Research focused on systematically measuring specific capabilities of AI models, such as reasoning ability, factual knowledge, instruction following, long-context understanding, multilingual ability, or tool use proficiency.
- **Safety and alignment evaluation**: Benchmarks specifically designed to measure model safety, harmlessness, honesty, alignment with human values, resistance to jailbreaking, toxicity generation tendencies, and bias assessment.
- **Agent and tool use benchmarks**: Evaluation frameworks for assessing LLM-based agents on tasks like web navigation, code execution, tool calling, and multi-step problem solving in interactive environments.
- **Domain-specific benchmarks**: Benchmarks designed for specific fields such as medicine (MedQA), law (LegalBench), finance (FinBench), science, education, or engineering.
- **Benchmark analysis and critique**: Meta-analyses of existing benchmarks, studies on benchmark contamination, data leakage, overfitting to benchmarks, benchmark saturation, and proposals for more robust evaluation practices.
- **Multimodal evaluation**: Benchmarks for vision-language models, audio-language models, and other multimodal systems.
- **Comparison studies**: Papers whose primary contribution is a comprehensive comparison of multiple models or methods on existing benchmarks, providing new insights about relative strengths and weaknesses.

Boundary clarification:
- DO tag: A paper that introduces a new benchmark dataset for evaluating LLM reasoning → yes.
- DO tag: A paper proposing LLM-as-judge as an evaluation methodology with validation studies → yes.
- DO tag: A paper analyzing benchmark contamination and proposing mitigation strategies → yes.
- DO tag: A paper that comprehensively compares 20+ models on a suite of benchmarks → yes.
- DO NOT tag: A paper that merely evaluates its proposed method on existing benchmarks as part of standard experimental validation → no (every ML paper does this, the benchmark must be the main contribution).
- DO NOT tag: A paper that creates a new dataset for training (not evaluation) purposes → no.
- DO NOT tag: A paper that happens to mention benchmark scores in passing → no.

Key signals in title/abstract: "benchmark", "evaluation", "leaderboard", "assessment", "measuring", "testing", "eval suite", "dataset for evaluation", "human evaluation", "LLM-as-judge", "arena", "comparison study", "capability assessment", "we evaluate", "we benchmark".""",


    "rag": """This tag covers research on Retrieval-Augmented Generation — systems and methods that combine information retrieval with language model generation to produce more accurate, grounded, and up-to-date responses. A paper should be tagged rag if it addresses the retrieval-generation pipeline, retrieval quality for LLM augmentation, or methods to improve how LLMs utilize retrieved information.

Core areas include but are not limited to:
- **RAG architectures and pipelines**: End-to-end systems that retrieve relevant documents or passages from a knowledge base and use them to augment LLM generation. This includes naive RAG, advanced RAG, modular RAG, and various pipeline designs (retrieve-then-read, iterative retrieval, adaptive retrieval).
- **Dense retrieval for RAG**: Methods for training and improving dense retrievers (e.g., based on BERT, Contriever, E5) specifically for the purpose of augmenting language model generation, including relevance modeling and passage ranking.
- **Chunking and indexing strategies**: Research on how to split, chunk, and organize documents for effective retrieval in RAG systems, including semantic chunking, hierarchical indexing, multi-granularity retrieval, and graph-based document structures.
- **Vector databases and embedding search**: Technologies and methods for efficient similarity search over document embeddings, including approximate nearest neighbor search, hybrid search (combining sparse and dense retrieval), and vector database optimization.
- **Query transformation and expansion**: Methods for reformulating or expanding user queries to improve retrieval quality, including query decomposition, HyDE (Hypothetical Document Embeddings), step-back prompting for retrieval, and multi-query approaches.
- **Reranking and filtering**: Post-retrieval processing to improve the relevance of retrieved documents before feeding them to the generator, including cross-encoder reranking, LLM-based reranking, and relevance filtering.
- **Faithful generation and grounding**: Methods to ensure that LLM outputs are faithful to the retrieved context, including attribution, citation generation, reducing hallucination through retrieval grounding, and verifiable generation.
- **RAG for specific domains**: Applying RAG to specialized domains such as legal, medical, scientific, or enterprise knowledge bases, where domain-specific retrieval and generation challenges arise.
- **Multi-modal RAG**: Systems that retrieve and utilize multi-modal information (images, tables, code) alongside text for augmented generation.
- **RAG evaluation**: Methods and benchmarks for evaluating RAG system performance, including retrieval quality metrics, generation faithfulness metrics, and end-to-end evaluation frameworks.
- **Agentic RAG**: Systems where an agent decides when, what, and how to retrieve, potentially making multiple retrieval calls and combining results through reasoning before generating a final response.

Boundary clarification:
- DO tag: A paper proposing a new RAG pipeline that improves retrieval quality for LLM question answering → yes.
- DO tag: A paper on reducing hallucination by grounding LLM outputs in retrieved documents → yes.
- DO tag: A paper about chunking strategies for building better RAG knowledge bases → yes.
- DO tag: A paper on vector database optimizations specifically for RAG use cases → yes.
- DO NOT tag: A paper about general information retrieval or search engines without the LLM generation component → no.
- DO NOT tag: A paper about memory systems for LLM agents (where the agent stores and retrieves its own experiences) → no, use memory instead.
- DO NOT tag: A paper about deep research agents that do iterative search (the focus there is on the research process, not the retrieval-generation pipeline) → no, use deep-research instead.

Key signals in title/abstract: "retrieval-augmented", "RAG", "retrieve and generate", "retrieval augmented", "grounded generation", "knowledge-grounded", "retrieved context", "vector search", "document retrieval for LLM", "chunking", "embedding retrieval", "hybrid search".""",


    "reasoning": """This tag covers research on the reasoning capabilities of large language models — how LLMs perform logical deduction, mathematical problem-solving, causal inference, commonsense reasoning, and other forms of structured thinking. A paper should be tagged reasoning if its primary focus is on understanding, improving, or evaluating the reasoning abilities of language models.

Core areas include but are not limited to:
- **Chain-of-thought (CoT) reasoning**: Research on prompting or training models to produce step-by-step reasoning traces, including zero-shot CoT, few-shot CoT, automatic CoT generation, and analysis of when and why CoT helps.
- **Tree-of-thought and graph-based reasoning**: Methods that explore multiple reasoning paths simultaneously, including tree search over reasoning steps, graph-of-thought, and other structured reasoning exploration approaches.
- **Mathematical reasoning**: LLMs solving mathematical problems, including arithmetic, algebra, geometry, calculus, competition mathematics, and formal theorem proving. This covers both prompting-based and training-based approaches to improve math capabilities.
- **Logical and formal reasoning**: Deductive reasoning, inductive reasoning, abductive reasoning, propositional logic, first-order logic, constraint satisfaction, and formal verification of reasoning steps.
- **Commonsense reasoning**: How models reason about everyday situations, physical world knowledge, social conventions, temporal reasoning, and causal relationships that humans take for granted.
- **Scientific reasoning**: LLMs reasoning about scientific concepts, experimental design, hypothesis testing, and scientific problem-solving.
- **Process reward models and verification**: Training models to evaluate the correctness of intermediate reasoning steps (not just final answers), including process reward models (PRMs), outcome reward models (ORMs), and self-verification mechanisms.
- **Reasoning with search and computation**: Integrating external computation (code execution, calculators, symbolic solvers) with LLM reasoning, including program-of-thought, PAL (Program-Aided Language models), and tool-augmented reasoning.
- **Reasoning scaling and test-time compute**: Research on how increasing computation at inference time (e.g., sampling more reasoning paths, using more search steps) improves reasoning quality, including best-of-N sampling, majority voting, and inference-time scaling laws.
- **Reasoning distillation and training**: Methods for training smaller models to reason better by distilling reasoning capabilities from larger models, or training on reasoning traces.
- **Multi-step and compositional reasoning**: How models handle problems requiring multiple reasoning steps, including compositional generalization, multi-hop reasoning, and systematic problem decomposition.

Boundary clarification:
- DO tag: A paper proposing a new prompting method to improve LLM mathematical reasoning → yes.
- DO tag: A paper training a process reward model to verify reasoning step correctness → yes.
- DO tag: A paper analyzing when chain-of-thought reasoning fails in LLMs → yes.
- DO tag: A paper on inference-time scaling of reasoning through more computation → yes.
- DO NOT tag: A paper about agent planning where reasoning is used in service of taking actions → no, use agent-planning instead (the focus there is on the planning/action loop, not reasoning itself).
- DO NOT tag: A paper about general model capabilities that mentions reasoning as one of many evaluated skills → no, use benchmark instead.
- DO NOT tag: A paper about prompt engineering techniques that happen to use CoT as one component → no, use prompt-engineering instead.

Key signals in title/abstract: "reasoning", "chain-of-thought", "CoT", "tree-of-thought", "mathematical reasoning", "logical reasoning", "step-by-step", "process reward", "verification of reasoning", "commonsense", "problem-solving", "inference-time compute", "reasoning traces", "self-consistency".""",


    "multi-agent": """This tag covers research on systems involving multiple AI agents that interact, communicate, collaborate, compete, or coordinate with each other to achieve individual or collective goals. A paper should be tagged multi-agent if it focuses on the dynamics, protocols, architectures, or outcomes of interactions between two or more autonomous agents.

Core areas include but are not limited to:
- **Multi-agent LLM systems**: Systems where multiple LLM instances (potentially with different roles, personas, or specializations) work together on tasks. This includes multi-agent debate, discussion, negotiation, collaborative problem-solving, and division of labor among LLM agents.
- **Agent communication protocols**: Research on how agents communicate with each other, including message passing schemes, shared memory architectures, structured communication languages, and natural language communication between agents.
- **Collaborative task solving**: Systems where multiple agents cooperate to solve tasks that are difficult for a single agent, including collaborative coding, collaborative research, collaborative writing, and distributed problem-solving.
- **Agent debate and adversarial interaction**: Systems where agents argue different positions, challenge each other's reasoning, or engage in adversarial interactions to improve output quality, including debate-based fact-checking and adversarial agent training.
- **Multi-agent reinforcement learning (MARL)**: RL methods designed for environments with multiple learning agents, including cooperative MARL, competitive MARL, mixed cooperative-competitive settings, and emergent communication in MARL.
- **Organizational structures for agents**: Research on how to organize multiple agents — hierarchical structures, flat structures, dynamic team formation, role assignment, and management of agent teams.
- **Agent society simulation**: Using multiple agents to simulate social dynamics, market behavior, organizational behavior, or other complex systems. This includes generative agent simulations, agent-based modeling with LLMs, and computational social science using agent simulations.
- **Multi-agent evaluation and benchmarks**: Benchmarks and evaluation methods specifically for multi-agent systems, including metrics for cooperation quality, communication efficiency, and collective task performance.
- **Swarm intelligence and collective behavior**: Research on emergent collective behaviors from simple agent interactions, including swarm robotics with AI components and collective decision-making.
- **Mixture-of-agents and routing**: Architectures that combine outputs from multiple models or agents through routing, aggregation, or selection mechanisms.

Boundary clarification:
- DO tag: A paper where multiple LLM agents debate to improve answer quality → yes.
- DO tag: A paper about hierarchical agent organizations for complex task solving → yes.
- DO tag: A paper on MARL algorithms for cooperative game playing → yes.
- DO tag: A paper simulating a society of LLM-based agents to study emergent social behaviors → yes.
- DO NOT tag: A paper about a single agent that uses multiple tools (that's tool-use or agent-planning, not multi-agent).
- DO NOT tag: A paper about ensemble methods that combine multiple model outputs without agent-like autonomy → no.
- DO NOT tag: A paper about mixture-of-experts within a single model architecture → no (MoE layers are not agents).

Key signals in title/abstract: "multi-agent", "multiagent", "multiple agents", "agent collaboration", "agent debate", "agent communication", "MARL", "cooperative agents", "agent society", "agent team", "multi-agent reinforcement learning", "agent interaction", "agent negotiation", "swarm".""",


    "code-generation": """This tag covers research on AI systems that generate, understand, complete, repair, translate, or reason about source code. A paper should be tagged code-generation if its primary contribution involves using AI (especially LLMs) for programming-related tasks, or if it introduces models, datasets, or benchmarks specifically designed for code intelligence.

Core areas include but are not limited to:
- **Code generation from natural language**: Systems that translate natural language descriptions, specifications, or instructions into executable source code in any programming language. This includes text-to-code, specification-to-implementation, and requirement-to-code systems.
- **Code completion and suggestion**: AI-powered autocomplete systems that predict and suggest the next lines of code during development, including inline suggestions, function completion, and contextual code proposals (similar to GitHub Copilot, Cursor, etc.).
- **Automated code repair and debugging**: Systems that automatically identify and fix bugs, vulnerabilities, or errors in source code, including automated program repair, vulnerability patching, and error localization.
- **Code review and quality analysis**: AI-assisted code review, static analysis with ML, code smell detection, and automated code quality assessment.
- **Code translation and migration**: Translating code from one programming language to another, modernizing legacy codebases, or adapting code for different frameworks or platforms.
- **Test generation**: Automatically generating unit tests, integration tests, or test cases for given code, including property-based test generation and mutation testing with AI.
- **AI-assisted software development (Vibe Coding)**: End-to-end AI-assisted development workflows where users describe what they want in natural language and AI generates complete applications, including agentic coding assistants that can create, modify, and debug entire projects.
- **Code understanding and analysis**: Models that understand code semantics, including code summarization, code search, code clone detection, and code-based question answering.
- **Repository-level code understanding**: AI systems that understand and can work with entire code repositories, including cross-file dependencies, project-level context, and large-scale code changes (e.g., SWE-bench style tasks).
- **Code models and architectures**: Training and architecture design of models specifically for code, including code-specific pretraining objectives, code tokenization strategies, and code-specialized model architectures.
- **Formal verification and proof generation**: Using AI to generate formal proofs, verify program correctness, or assist in formal methods.
- **CUDA and performance optimization**: Using AI to generate or optimize high-performance code, including CUDA kernel generation, compiler optimization, and code performance tuning.

Boundary clarification:
- DO tag: A paper about an LLM that generates Python code from natural language descriptions → yes.
- DO tag: A paper on automated bug repair using LLMs → yes.
- DO tag: A paper about an AI coding agent that can resolve GitHub issues autonomously → yes.
- DO tag: A paper about training code-specific LLMs (e.g., CodeLlama, DeepSeek-Coder) → yes.
- DO NOT tag: A paper about general LLM pretraining that happens to include some code in the training data → no.
- DO NOT tag: A paper about LLM agents that happen to execute Python code as part of a larger reasoning task (unless code generation is the primary focus) → no.
- DO NOT tag: A paper about natural language generation that uses code-like structured outputs → no.

Key signals in title/abstract: "code generation", "code completion", "program synthesis", "automated programming", "code repair", "bug fixing", "software engineering", "coding", "SWE-bench", "code LLM", "programming", "IDE", "Copilot", "coding assistant", "code review", "test generation", "vibe coding".""",


    "tool-use": """This tag covers research on how AI models (especially LLMs) interact with external tools, APIs, functions, and services to extend their capabilities beyond pure text generation. A paper should be tagged tool-use if it focuses on the mechanisms, training, or evaluation of models that call external tools or functions as part of their operation.

Core areas include but are not limited to:
- **Function calling**: Methods for training or prompting LLMs to generate structured function calls with correct parameters, including OpenAI-style function calling, tool-use fine-tuning, and constrained decoding for valid function signatures.
- **Tool selection and routing**: How models decide which tool to use from a set of available tools, including tool retrieval, tool ranking, and dynamic tool selection based on task requirements.
- **API integration**: Systems that enable LLMs to interact with external APIs (REST, GraphQL, etc.), including API documentation understanding, API call generation, and API response interpretation.
- **Model Context Protocol (MCP)**: Research related to standardized protocols for connecting LLMs with external tools and data sources, including MCP implementations, tool server architectures, and interoperability standards.
- **Tool-augmented language models**: Architectures and training methods that fundamentally integrate tool use into the language model, including Toolformer-style approaches where models learn when and how to call tools during generation.
- **Calculator, code interpreter, and search tools**: Systems that augment LLMs with specific tools like calculators for arithmetic, code interpreters for execution, search engines for information retrieval, and browsers for web interaction.
- **Computer use and GUI interaction**: AI systems that interact with graphical user interfaces, operating systems, web browsers, or desktop applications, including screen understanding, element localization, and action execution.
- **Tool creation and self-tooling**: Systems where LLMs create their own tools (e.g., writing Python functions) to solve problems, rather than using pre-defined tools.
- **Multi-tool orchestration**: Systems that coordinate the use of multiple tools in sequence or parallel to complete complex tasks, including tool pipelines and tool dependency management.
- **Tool use evaluation**: Benchmarks and evaluation methods for assessing how well models can use tools, including tool call accuracy, parameter correctness, and end-to-end task completion with tools.

Boundary clarification:
- DO tag: A paper about training LLMs to make accurate function calls → yes.
- DO tag: A paper about a new protocol for connecting LLMs to external services → yes.
- DO tag: A paper about LLMs that can use a web browser or computer GUI → yes.
- DO tag: A paper about evaluating tool-use capabilities of different models → yes.
- DO NOT tag: A paper about agent planning where tool use is just one component of a larger planning system → no, use agent-planning instead.
- DO NOT tag: A paper about RAG where retrieval is the "tool" but the focus is on generation quality → no, use rag instead.
- DO NOT tag: A paper about code generation where the generated code is not used as a tool by the model itself → no, use code-generation instead.

Key signals in title/abstract: "tool use", "tool calling", "function calling", "API", "tool-augmented", "Toolformer", "MCP", "Model Context Protocol", "computer use", "GUI agent", "tool learning", "external tools", "tool selection", "tool retrieval".""",


    "rlhf-alignment": """This tag covers research on aligning AI models with human preferences, values, and intentions through reinforcement learning from human feedback (RLHF) and related techniques. A paper should be tagged rlhf-alignment if it addresses how to train, fine-tune, or steer language models to be more helpful, harmless, and honest, or if it proposes new alignment training methodologies.

Core areas include but are not limited to:
- **RLHF (Reinforcement Learning from Human Feedback)**: The classic pipeline of training a reward model from human preference data and then optimizing a language model policy using RL algorithms (typically PPO) against that reward model.
- **DPO and direct alignment methods**: Direct Preference Optimization and its variants (IPO, KTO, ORPO, SimPO, etc.) that bypass explicit reward model training and directly optimize the policy from preference data. This includes theoretical analysis and practical improvements to these methods.
- **Reward modeling**: Training reward models or preference models from human feedback data, including reward model architectures, data collection strategies, reward hacking mitigation, and reward model evaluation.
- **RLVR (RL from Verifiable Rewards)**: Using automatically verifiable rewards (e.g., code execution results, math answer correctness) instead of human preferences to train models through RL.
- **Constitutional AI and self-alignment**: Methods where models participate in their own alignment process, including AI-generated feedback, self-critique, and iterative self-improvement for alignment.
- **Safety training and red-teaming**: Research on making models safer through training, including robustness to adversarial prompts (jailbreaking), refusal training, safety-specific fine-tuning, and red-teaming methodologies.
- **Human preference data and annotation**: Research on collecting, curating, and analyzing human preference data for alignment, including annotation methodologies, inter-annotator agreement, and preference data quality.
- **Value alignment theory**: Theoretical work on what it means to align AI systems with human values, including scalable oversight, debate, and other theoretical alignment approaches.
- **Instruction tuning and SFT**: Supervised fine-tuning methods that align models to follow instructions, including instruction dataset creation, formatting, and training procedures (while this is a precursor to RLHF, papers focused specifically on instruction tuning are included).
- **Alignment evaluation**: Benchmarks and methods for measuring how well-aligned a model is, including helpfulness, harmlessness, honesty evaluations, and alignment tax measurement.
- **Post-training optimization**: The broader category of post-pretraining alignment procedures, including the full pipeline from SFT → RLHF/DPO → evaluation.

Boundary clarification:
- DO tag: A paper proposing a new variant of DPO for more stable preference optimization → yes.
- DO tag: A paper on training reward models that are robust to reward hacking → yes.
- DO tag: A paper about red-teaming LLMs to find safety vulnerabilities → yes.
- DO tag: A paper using RL with verified code execution rewards to improve coding models → yes.
- DO NOT tag: A paper about general reinforcement learning without any connection to LLM alignment → no.
- DO NOT tag: A paper about LLM safety evaluation only (without alignment training methods) → no, use benchmark instead.
- DO NOT tag: A paper about fine-tuning for domain adaptation without preference/alignment components → no.

Key signals in title/abstract: "RLHF", "reinforcement learning from human feedback", "DPO", "direct preference optimization", "reward model", "alignment", "human preference", "safety training", "constitutional AI", "instruction tuning", "preference learning", "RLVR", "PPO", "helpful", "harmless", "honest".""",


    "time-series": """This tag covers research on modeling, forecasting, analyzing, and understanding time series data using AI/ML methods. A paper should be tagged time-series if it proposes or evaluates methods specifically designed for sequential temporal data, or if it introduces architectures, benchmarks, or techniques targeted at time series tasks.

Core areas include but are not limited to:
- **Time series forecasting**: Predicting future values of time series using deep learning, including transformer-based forecasters (PatchTST, iTransformer, TimesFM, etc.), state space models for time series, and neural forecasting methods.
- **Foundation models for time series**: Large pretrained models designed to handle diverse time series tasks across domains, including time series LLMs, universal forecasters, and zero-shot/few-shot time series models.
- **LLMs for time series**: Using large language models directly for time series analysis, including text-based time series encoding, prompt-based forecasting, and LLM-driven time series reasoning.
- **Time series classification and anomaly detection**: ML methods for classifying temporal patterns and detecting anomalies, outliers, or change points in time series data.
- **Multivariate time series analysis**: Methods that handle multiple correlated time series simultaneously, including spatial-temporal modeling, channel dependencies, and variable interaction modeling.
- **Time series generation and imputation**: Generating synthetic time series data, filling in missing values, and data augmentation techniques for temporal data.
- **Time series representation learning**: Learning useful representations or embeddings of time series for downstream tasks, including self-supervised pretraining on temporal data.
- **Domain-specific time series**: Time series methods applied to specific domains such as finance (stock prices, volatility), healthcare (ECG, EHR), energy (load forecasting), climate (weather prediction), and IoT sensor data.
- **Temporal point processes**: Modeling event sequences in continuous time, including Hawkes processes, neural temporal point processes, and event prediction.
- **Time series benchmarks**: Evaluation frameworks and datasets for assessing time series model performance across forecasting, classification, and other temporal tasks.

Boundary clarification:
- DO tag: A paper proposing a new transformer architecture for long-horizon time series forecasting → yes.
- DO tag: A paper about a foundation model pretrained on diverse time series datasets → yes.
- DO tag: A paper using LLMs to reason about time series patterns → yes.
- DO tag: A paper about anomaly detection in sensor time series data → yes.
- DO NOT tag: A paper about financial prediction that uses AI on non-temporal features (e.g., cross-sectional stock selection based on fundamentals) → no, use ai-finance instead.
- DO NOT tag: A paper about sequential decision-making in RL (action sequences are not time series forecasting) → no.
- DO NOT tag: A paper about NLP sequence modeling that happens to process text sequentially → no.
- OVERLAP NOTE: A paper about AI-based stock price time series forecasting should get BOTH time-series AND ai-finance tags.

Key signals in title/abstract: "time series", "forecasting", "temporal", "sequential data", "time-series", "temporal modeling", "multivariate time series", "anomaly detection in time series", "temporal pattern", "forecasting horizon", "look-back window", "temporal foundation model".""",


    "prompt-engineering": """This tag covers research on designing, optimizing, and analyzing prompts and instructions given to large language models to improve their performance on specific tasks. A paper should be tagged prompt-engineering if its primary contribution involves prompt design strategies, automated prompt optimization, or systematic analysis of how different prompting approaches affect model behavior.

Core areas include but are not limited to:
- **Prompt design strategies**: Systematic approaches to crafting effective prompts, including structured prompting, few-shot example selection and ordering, instruction formatting, role-playing prompts, and persona-based prompting.
- **In-context learning (ICL)**: Research on how models learn from examples provided in the prompt, including the mechanisms behind ICL, optimal example selection strategies, the effect of example ordering, and the relationship between ICL and fine-tuning.
- **Automated prompt optimization**: Methods for automatically searching for or optimizing prompts, including gradient-based prompt tuning (soft prompts), discrete prompt optimization (DSPy, APE, OPRO), evolutionary prompt search, and RL-based prompt optimization.
- **Soft prompts and prefix tuning**: Parameter-efficient methods that prepend learned continuous vectors to the input, including prompt tuning, prefix tuning, P-tuning, and other continuous prompt methods.
- **Instruction tuning and engineering**: Research on how to write better instructions for instruction-tuned models, including instruction decomposition, instruction complexity analysis, and meta-instructions.
- **Prompt robustness and sensitivity**: Studies on how sensitive model outputs are to prompt variations, including paraphrasing effects, prompt injection vulnerabilities, and methods for making prompts more robust.
- **System prompts and meta-prompting**: Research on system-level prompts that configure model behavior, including meta-prompts that instruct models how to approach classes of tasks.
- **Multi-turn prompt strategies**: Prompting techniques across multiple conversation turns, including scaffolding, progressive disclosure, and conversational steering.
- **Domain-specific prompting**: Prompt strategies tailored for specific domains or tasks, such as medical prompting, legal prompting, or scientific prompting.
- **Prompt compression and efficiency**: Methods for reducing prompt length while maintaining effectiveness, including context distillation, prompt summarization, and token-efficient prompting.

Boundary clarification:
- DO tag: A paper proposing a new automated prompt optimization algorithm → yes.
- DO tag: A paper systematically studying how few-shot example selection affects ICL performance → yes.
- DO tag: A paper about DSPy or similar frameworks for programmatic prompt engineering → yes.
- DO tag: A paper on prompt injection attacks and defenses → yes.
- DO NOT tag: A paper that uses CoT prompting as a method but whose main contribution is about reasoning ability → no, use reasoning instead.
- DO NOT tag: A paper about fine-tuning or RLHF that doesn't focus on prompts → no, use rlhf-alignment or training-efficiency instead.
- DO NOT tag: A paper that merely describes the prompts used in its experiments without prompting being the main contribution → no.

Key signals in title/abstract: "prompt", "prompting", "in-context learning", "ICL", "few-shot", "zero-shot", "instruction", "prompt optimization", "prompt tuning", "prefix tuning", "DSPy", "prompt engineering", "prompt design", "soft prompt", "prompt selection".""",


    "training-efficiency": """This tag covers research on making the training, fine-tuning, and inference of large models more efficient in terms of computational cost, memory usage, time, energy, or data requirements. A paper should be tagged training-efficiency if its primary contribution is a method, architecture, or technique that reduces the resources needed to train, adapt, or deploy AI models.

Core areas include but are not limited to:
- **Parameter-efficient fine-tuning (PEFT)**: Methods that adapt large pretrained models to new tasks by training only a small subset of parameters, including LoRA (and its variants: QLoRA, DoRA, AdaLoRA, rsLoRA), adapters, BitFit, and other parameter-efficient methods.
- **Model quantization**: Reducing model precision from FP32/FP16 to INT8/INT4/lower to reduce memory and compute requirements, including post-training quantization (PTQ), quantization-aware training (QAT), and mixed-precision quantization methods (GPTQ, AWQ, SqueezeLLM, etc.).
- **Knowledge distillation**: Training smaller "student" models to mimic larger "teacher" models, including logit distillation, feature distillation, and task-specific distillation methods for LLMs.
- **Model pruning and sparsity**: Removing unnecessary parameters or connections from models, including structured pruning, unstructured pruning, movement pruning, and sparse architectures.
- **Efficient architectures**: Novel model architectures designed for efficiency, including linear attention, state space models (Mamba, S4), RWKV, mixture-of-experts (MoE), and other architectures that reduce the quadratic cost of standard attention.
- **Distributed and parallel training**: Methods for training large models across multiple GPUs or machines, including data parallelism, tensor parallelism, pipeline parallelism, ZeRO optimization, FSDP, and communication-efficient distributed training.
- **Training optimization techniques**: Advanced optimization methods for faster convergence or better training stability, including learning rate schedules, gradient accumulation, mixed-precision training, gradient checkpointing, and flash attention.
- **Speculative decoding**: Methods for faster inference by using a smaller draft model to propose tokens that the larger model then verifies, including Medusa, EAGLE, and other speculative decoding variants.
- **Model serving and inference optimization**: Techniques for efficient model deployment, including batching strategies, continuous batching, PagedAttention (vLLM), TensorRT-LLM, and other serving frameworks and optimizations.
- **Data efficiency**: Methods for training models with less data, including curriculum learning, data selection, data mixing strategies, and active learning for LLMs.
- **Pretraining efficiency**: Research on making the pretraining phase itself more efficient, including optimal pretraining data composition, learning rate warmup strategies, and compute-optimal scaling (Chinchilla-style analysis).
- **Model merging and weight averaging**: Combining multiple trained models without additional training, including model soups, TIES merging, DARE, and task arithmetic on model weights.

Boundary clarification:
- DO tag: A paper proposing a new LoRA variant for more efficient fine-tuning → yes.
- DO tag: A paper on a new quantization method that reduces LLM memory by 4x → yes.
- DO tag: A paper about flash attention or other attention efficiency improvements → yes.
- DO tag: A paper on speculative decoding for faster inference → yes.
- DO tag: A paper about efficient MoE architecture design → yes.
- DO NOT tag: A paper about general model architecture innovation where efficiency is not the primary concern → no.
- DO NOT tag: A paper about RLHF training that happens to use LoRA → no (use rlhf-alignment, the LoRA usage is incidental).
- DO NOT tag: A paper about efficient retrieval for RAG (that's about retrieval efficiency, not model training efficiency) → no, use rag.

Key signals in title/abstract: "efficient", "efficiency", "LoRA", "quantization", "distillation", "pruning", "compression", "parameter-efficient", "PEFT", "speculative decoding", "inference speed", "memory reduction", "sparse", "mixture of experts", "MoE", "flash attention", "parallel training", "serving", "deployment", "compute-optimal".""",


    "multimodal": """This tag covers research on AI models that process, understand, generate, or reason across multiple modalities — typically combinations of text, images, video, audio, and structured data. A paper should be tagged multimodal if its primary contribution involves cross-modal understanding, multimodal architectures, or tasks that fundamentally require integrating information from different modalities.

Core areas include but are not limited to:
- **Vision-Language Models (VLMs)**: Models that jointly understand images and text, including GPT-4V, LLaVA, Qwen-VL, InternVL, and other large multimodal models (LMMs). This covers visual question answering, image captioning, visual reasoning, OCR with understanding, and document/chart understanding.
- **Multimodal pretraining**: Methods for pretraining models on paired multimodal data, including CLIP-style contrastive learning, image-text matching, and unified multimodal pretraining objectives.
- **Text-to-image and image generation**: Diffusion models, GANs, autoregressive image generators, and text-conditioned image synthesis systems (Stable Diffusion, DALL-E, Midjourney-style systems).
- **Video understanding and generation**: Models that process or generate video, including video captioning, video QA, temporal reasoning in video, text-to-video generation, and video editing.
- **Audio and speech models**: Multimodal models that integrate audio/speech with text, including speech-to-text, text-to-speech, audio understanding, and omni-models that handle voice + text + vision.
- **Document understanding**: Models that understand complex documents containing mixed text, tables, figures, and layouts, including document VQA, table extraction, and chart understanding.
- **Multimodal reasoning**: Research on how models reason across modalities, including visual chain-of-thought, multimodal mathematical reasoning (reasoning about diagrams), and cross-modal inference.
- **Multimodal agents**: Agents that can perceive and act in multimodal environments, using vision, language, and potentially audio to interact with the world.
- **3D understanding**: Models that understand 3D scenes, point clouds, or spatial relationships, often combined with language understanding.
- **Multimodal alignment**: Methods for aligning representations across modalities, including cross-modal retrieval, modality-specific encoders with shared decoders, and visual instruction tuning.
- **Multimodal evaluation**: Benchmarks for evaluating multimodal model capabilities across different tasks and modality combinations.

Boundary clarification:
- DO tag: A paper about a new VLM architecture that improves visual question answering → yes.
- DO tag: A paper about training a model that can understand documents with text, tables, and figures → yes.
- DO tag: A paper about text-to-image diffusion models → yes.
- DO tag: A paper about an omni-model that handles text + vision + audio → yes.
- DO NOT tag: A paper about a text-only LLM, even if it's very capable → no.
- DO NOT tag: A paper about computer vision without any language component → no.
- DO NOT tag: A paper about speech recognition without multimodal integration → no.
- DO NOT tag: A paper that uses images only as part of a data augmentation strategy for text tasks → no.

Key signals in title/abstract: "multimodal", "vision-language", "VLM", "visual question answering", "image-text", "text-to-image", "diffusion", "video understanding", "document understanding", "cross-modal", "vision and language", "large multimodal model", "LMM", "visual reasoning", "image captioning", "CLIP".""",

}

PRIMARY_FOCUS_TAGS = [
    "ai-finance",
    "agent-planning",
    "deep-research",
    "multi-agent",
    "tool-use",
    "reasoning",
    "memory",
    "rag",
    "time-series",
]

# ============================================
# LLM API Configuration (DashScope)
# ============================================
# DashScope API Key - Must be set via environment variable
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

# Base URL - Can be overridden via environment variable
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1")
DASHSCOPE_API_URL = f"{DASHSCOPE_BASE_URL}/chat/completions"

# Model name - Can be overridden via environment variable
MODEL_NAME = os.getenv("DASHSCOPE_MODEL", "qwen3.5-plus")
DISABLE_THINKING = os.getenv("DASHSCOPE_DISABLE_THINKING", "true").lower() == "true"

MAX_CONCURRENT = 20
MAX_RETRIES = 3
REQUEST_TIMEOUT = 90

# ============================================
# arXiv Fetching Configuration
# ============================================
# Include the current UTC date and keep a full week of slack for arXiv's
# weekday announcement cycle, weekends, and delayed submissions.
FETCH_DAYS = 7
MAX_RESULTS_PER_CATEGORY = 100

# ============================================
# Statistics Configuration
# ============================================
MIN_KEYWORD_COUNT = 3

# ============================================
# LLM Prompt Templates
# ============================================
PAPER_ANALYSIS_PROMPT = """You are an expert AI/Finance research analyst. Analyze the following paper with a precision-first mindset:

Title: {title}
Abstract: {abstract}

Extract the following information in JSON format:

{{
  "tags": ["tag1", "tag2"],
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "summary_zh": "2-3 sentences Chinese summary of the paper's main contribution and significance"
}}

Requirements:

1. "tags": Select from these predefined tags. Choose 0-3 tags.
   False positives are much worse than false negatives.
   Only assign a tag when the tag is a PRIMARY contribution clearly supported by the title/abstract.
   If none of the tags are truly central, return an empty list.
   Prioritize tags that surface AI/LLM/agent + finance, agent planning, deep research,
   multi-agent, tool-use, reasoning, and memory themes whenever they are truly central.

PREDEFINED TAGS AND STRICT DEFINITIONS:

- ai-finance: ONLY use if the paper's CORE contribution is applying AI/ML to financial domains. Examples: stock price prediction, portfolio optimization, credit scoring, fraud detection, quantitative trading strategies, risk management, financial time series analysis, sentiment analysis of financial markets, automated trading systems. DO NOT use for papers that merely evaluate on financial datasets - the main method must be finance-focused.

- memory: LLM memory mechanisms, working memory, context window management
- agent-planning: Agent planning, goal-oriented reasoning, hierarchical task planning
- deep-research: Autonomous research agents, self-improving AI systems
- benchmark: Evaluation frameworks, new datasets, benchmark comparisons
- rag: Retrieval-augmented generation, vector databases, document retrieval
- reasoning: Chain-of-thought, tree-of-thought, reasoning techniques
- multi-agent: Multi-agent systems, collaborative AI
- code-generation: AI-assisted programming, code generation, code completion
- tool-use: Function calling, tool usage, external API integration
- rlhf-alignment: Reward learning, alignment, human feedback
- time-series: Time series modeling (not limited to finance)
- prompt-engineering: Prompt engineering techniques
- training-efficiency: Efficient training methods, model compression
- multimodal: Multimodal models, vision-language models

2. "keywords": Extract 3-5 specific technical keywords/phrases from the paper.
3. "summary_zh": Write in academic Chinese, 2-3 sentences, highlighting main contribution.

IMPORTANT CRITERIA for "ai-finance" tag:
- The paper MUST address financial problems (stock markets, trading, risk, credit, etc.)
- The AI/ML method must be the core contribution, not just used as evaluation
- Papers about general NLP/CV methods that happen to use financial data should NOT get this tag
- Papers about advertising auctions, general optimization, or unrelated domains should NOT get this tag

IMPORTANT CRITERIA for the agentic focus tags:
- "agent-planning" ONLY if the paper is about autonomous agents, planning, workflow decomposition,
  long-horizon execution, re-planning, or reasoning-action loops; do NOT use for generic pipelines.
- "deep-research" ONLY if the paper is about autonomous multi-step information gathering, literature review,
  survey generation, evidence collection, or research/report synthesis; do NOT use because a paper is merely academic research.
- "tool-use" ONLY if using external tools/APIs/browser/computer/function calling is central.
- "multi-agent" ONLY if interaction or coordination among multiple agents is central.
- "memory" ONLY if memory, context persistence, retrieval memory, or KV/cache-style memory mechanisms are central.

EXPLICIT NON-EXAMPLES:
- Online advertising, recommendation, job markets, labor analytics, education, student analytics,
  renewable energy, generic economics, and e-commerce are NOT "ai-finance" unless the paper explicitly targets finance.
- A paper is NOT "deep-research" just because it performs analysis, experiments, or academic investigation.
- A paper is NOT "agent-planning" just because it has multiple stages or uses chain-of-thought.

Return only valid JSON, no extra text."""

TAG_LIST = ", ".join(f'"{tag}"' for tag in PREDEFINED_TAGS.keys())
FULL_PROMPT_TEMPLATE = PAPER_ANALYSIS_PROMPT.format(
    title="{title}",
    abstract="{abstract}",
    tag_list=TAG_LIST
)

# ============================================
# Category Display Names (for frontend)
# ============================================
CATEGORY_NAMES = {
    "cs.AI": "Artificial Intelligence",
    "cs.CL": "Computation and Language",
    "cs.MA": "Multiagent Systems",
    "cs.IR": "Information Retrieval",
    "cs.SE": "Software Engineering",
    "cs.CE": "Computational Engineering, Finance, and Science",
    "q-fin.ST": "Statistical Finance",
    "q-fin.CP": "Computational Finance",
    "q-fin.PM": "Portfolio Management",
    "q-fin.TR": "Trading and Market Microstructure",
}

# Tag display names (for frontend)
TAG_NAMES = {
    "ai-finance": "AI in Finance",
    "memory": "Memory",
    "agent-planning": "Agent Planning",
    "deep-research": "Deep Research",
    "benchmark": "Benchmark",
    "rag": "RAG",
    "reasoning": "Reasoning",
    "multi-agent": "Multi-Agent",
    "code-generation": "Code Generation",
    "tool-use": "Tool Use",
    "rlhf-alignment": "RLHF/Alignment",
    "time-series": "Time Series",
    "prompt-engineering": "Prompt Engineering",
    "training-efficiency": "Training Efficiency",
    "multimodal": "Multimodal",
}
