# Synapse

Synapse is an AI agent that can execute tasks using tools and manage conversations. It is feature packed with streaming, multi-turn conversations, configurability, and is equipped with built-in tools for operating files, directory operations, text searching, shell executions, web access, memory layer and todo manager, All with insanely optimized context management, safety first approach, session management, MCP integrations, subagents and a minimalistic Terminal User Interface Design Choice.

Synapse is terminal agentic tool which cannot be rendered in web thus, it doesnot have a public testing url. You have to work a little bit to get it running. Sorry for that :(

## Setup

#### 1. Run `bash start.sh` if using in codespace if necessary.


OR


#### 1. Make Sure that you have python 3 or higher installed
```bash
pip install click ddgs fastmcp httpx openai platformdirs pydantic rich tiktoken tomli
```
#### 2. (Please if none of these works for you, consider asking to an AI. Sorry for inconvience)
```bash
# In mac
export API_KEY="YOUR_OPENROUTER_API_KEY" && export BASE_URL="https://openrouter.ai/api/v1"

# In Windows
$env:API_KEY="YOUR_OPENROUTER_API_KEY" && $env:BASE_URL="https://openrouter.ai/api/v1"
```

#### 3. You might need to go through .synapse/synapse_config.toml and change filesystem MCP

#### 4. Run the file
```bash
python main.py
```

#### 5. Now It's ready to be used.


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