# **build-your-agent**

An open project initiated by the DeepModeling community focused on constructing intelligent agents for scientific research. 

We continuously release and share a collection of agent samples that are oriented towards real scientific research problems, to help developers understand practical agent architecture design and construction methods. These examples aim to span both user-friendly instructions and multiple cutting-edge application scenarios.


Our recent goals include:
- Define and validate a reference architecture for “scientific research agents”  
  *(Perception → Planning → Execution → Feedback)*
- Build sample agents for typical scientific scenarios:  
  - Domain-Specific Research Assistant: Retrieve and summarize literature based on keywords, and automatically generate review drafts
    - [paper_search_demo](agents/paper_search_demo) A demo for beginners to build their first agent, using searching and analyzing relevant papers from arxiv as an example. Inspired by the course of [Antropic and deeplearning-ai](https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic)
  - Materials Design Optimization Agent: Structure generation → Simulation calculation → Performance evaluation → Structure screening
    - [dpa_calculator](agents/dpa_calculator) An agent to use universal potential DPA-2.4 to automatically relax a materials structure and calcualte its property ( such as phonon). 
  - Drug Molecule Screening Agent: Molecule filtering and optimization process based on multiple drug-likeness properties
  - Omics Data Intelligent Analysis Agent: Integrate cross-domain data and tools to automatically complete result analysis
  - More ideas are welcome!
- Provide agent development guides and tutorial notebooks
- Support common agent frameworks: ADK / Camel / LangChain / Autogen
