# Synapse

Synapse is an AI agent that can execute tasks using tools and manage conversations. It is feature packed with streaming, multi-turn conversations, configurability, and is equipped with built-in tools for operating files, directory operations, text searching, shell executions, web access, memory layer and todo manager, All with insanely optimized context management, safety first approach, session management, MCP integrations, subagents and a minimalistic Terminal User Interface Design Choice.

Synapse is a terminal-based agentic AI tool. Choose one of the three methods below to get started.


---

## Method 1: Download the Executable (Easiest)

No Python or setup required.

1. Go to the [latest release](https://github.com/BurningFlamesss/synapse/releases/latest)
2. Download the file for your OS:
   - `synapse.exe` — Windows
   - `synapse` — macOS
   - `synapse` — Linux
3. Run it — on first launch it will ask for your OpenRouter API key
4. Get a free API key at [openrouter.ai](https://openrouter.ai)

> **Windows users:** If you see a SmartScreen warning, click **More info → Run anyway**

---

## Method 2: GitHub Codespaces (No Local Setup)

1. Click below to open in Codespaces:

   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/BurningFlamesss/synapse)

2. Wait for the environment to set up automatically
3. Enter your OpenRouter API key when prompted
4. The agent starts automatically in the terminal

---

## Method 3: Manual Setup (Python)

Requires Python 3.12 or higher.

1. Clone the repo
```bash
   git clone https://github.com/BurningFlamesss/synapse
   cd synapse
```

2. Install dependencies
```bash
   pip install click ddgs fastmcp httpx openai platformdirs pydantic rich tiktoken tomli
```

3. Set your API key
```bash
   # macOS/Linux
   export API_KEY="your-openrouter-api-key"

   # Windows (PowerShell)
   $env:API_KEY="your-openrouter-api-key"
```

4. Run
```bash
   python main.py
```

> Optionally configure `.synapse/synapse_config.toml` to customise models, MCP servers, and more.


## Preview

![](https://cdn.hackclub.com/019de29e-5798-74ed-b316-fafb8da65172/Screenshot%202026-05-01%20135845.png)
![](https://cdn.hackclub.com/019de2a3-0afe-77fe-893e-be3d8fb80e50/Screenshot%202026-05-01%20140838.png)
![](https://cdn.hackclub.com/019de2aa-dfb6-7feb-8475-1e89ec865b64/Screenshot%202026-05-01%20141703.png)
![](https://cdn.hackclub.com/019de2a9-84f4-75a7-83f0-0f2a4c06d140/Screenshot%202026-05-01%20141534.png)

Yeah! These are four different image of the application. Due to my hands, there pictures arenot captured nicely yet I believe it some what that App works in my device 😅


## Tools
- read_file
- write_file
- edit
- shell
- list_dir
- grep
- glob
- web_search
- web_fetch
- todos
- memory
_(Extendable by adding more on .synapse/tools)_

## SubAgents
- Specialized subagents for specific tasks
- Configurable subagent definitions with custom tools and limits

### Some Builtin SubAgents
- subagent_codebase_investigator
- subagent_code_reviewer
_(Extendable by adding more on tools/subagents.py)_

## MCPS
- Connect to Model Context Protocol servers
- Use tools from MCP servers
- Support for stdio and HTTP/SSE transports

### Some MCPS Tool
- filesystem__read_file
- filesystem__read_text_file
- filesystem__read_media_file
- filesystem__read_multiple_files
- filesystem__write_file
- filesystem__edit_file
- filesystem__create_directory
- filesystem__list_directory
- filesystem__list_directory_with_sizes
- filesystem__directory_tree
- filesystem__move_file
- filesystem__search_files
- filesystem__get_file_info
- filesystem__list_allowed_directories
*(Complete control on you. Just add more on .synapse/synapse_configs.toml)*

## Hooks
- Execute scripts before/after agent runs
- Execute scripts before/after tool calls
- Error handling hooks
- Custom commands and scripts

### Some Builtin Hooks
- Log
*(Complete control on you. Just add more on .synapse/synapse_configs.toml and scripts at scripts/)*

## Context Management

- Automatic context compression when approaching token limits
- Tool output pruning to manage context size
- Token usage tracking

## Safety and Approval

- Multiple approval policies: on-request, auto, never, yolo
- Dangerous command detection and blocking
- Path-based safety checks
- User confirmation prompts for mutating operations

## Session Management

- Save and resume sessions
- Create checkpoints
- Persistent session storage

## Loop Detection

- Detects repeating actions
- Prevents infinite loops in agent execution

## Configuration

- Configurable working directory
- Tool allowlisting
- Developer and user instructions
- Shell environment policies
- MCP server configuration

## User Interface

- Terminal UI with formatted output
- Command interface: /help, /config, /tools, /mcp, /stats, /save, /resume, /checkpoint, /restore
- Real-time tool call visualization

## Disclaimer / Reviewers

This project might have some bugs which I hadnot yet noticed so if you found any, please email me at <a href="mailto:burningggflamesss@gmail.com">CLICK HERE</a>.


## Credits

- In the PACKAGES.md, I had listed the packages, I used for this.
- system.py prompts were copied from Rivaan.
- From the claude code leak, I utilized some of the code to build logic in the app
