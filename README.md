# LinkedIn Posts MCP - AI News Generator

A modern web application that fetches the latest AI news and generates professional bilingual LinkedIn posts using OpenAI's API with the Model Completion Protocol (MCP).

## Features

- 🔍 Fetches latest AI news using MCP (Model Context Protocol) server
- 🤖 Generates professional bilingual LinkedIn posts (English & Spanish)
- 📝 Uses OpenAI's GPT-4 with custom MCP prompts
- 🌐 **Modern web interface** that runs in your browser
- 📱 **Responsive design** - works on desktop, tablet, and mobile
- 🚀 **One-click generation** with real-time progress indicators
- 📋 **Copy to clipboard** functionality for easy posting
- 🔗 **Direct LinkedIn access** with one-click links
- ⚡ **AJAX-powered** - no page refreshes needed
- 🔧 Configurable via environment variables
- 🔄 Intelligent fallback to OpenAI-based news search if MCP server unavailable

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   MCP_SERVER_PATH=mcp-server-news  # Optional
   ```

## Usage

### Quick Start (Recommended)
```bash
# Launch the web UI (runs in browser)
./run_web_ui.sh
# or
./run_project.sh
```

### Alternative: Command Line
```bash
# Generate post only (command line)
./run_project.sh gen

# Setup project (install dependencies, check config)
./run_project.sh setup

# Show help
./run_project.sh help
```

### Manual Python Commands
```bash
# Generate post only
python linkedin_mcp.py

# Launch web UI directly
python linkedin_web_ui.py
```

### Web UI Features
The web-based UI provides:
- **🌐 Browser-based**: Runs in any modern web browser
- **📱 Responsive design**: Works on desktop, tablet, and mobile
- **🚀 One-click generation**: Click "Generate AI News Post" to create bilingual posts
- **📊 Real-time updates**: Live progress indicators and status updates
- **📋 Copy to clipboard**: One-click copying of either language version
- **🔗 Direct LinkedIn access**: One-click link to open LinkedIn
- **⚡ Modern interface**: Clean, professional design with Bootstrap
- **🔄 No page refresh**: AJAX-powered for smooth user experience

### How It Works
The application will:
1. Search for the latest AI news using MCP server (or OpenAI fallback)
2. Generate a bilingual LinkedIn post using OpenAI
3. Display the results in the web interface
4. Save the post to `linkedin_post.json`
5. Provide copy-to-clipboard functionality for easy posting

## API Keys

### Required
- **OpenAI API Key**: Get yours from [OpenAI Platform](https://platform.openai.com/api-keys)

### Web Interface
- **No additional API keys required** - Posts are generated and displayed in the web interface

### Optional
- **MCP Server Path**: Path to your MCP news server executable (defaults to `mcp-server-news`)

## Output Format

The generated LinkedIn post will be saved in `linkedin_post.json` with the following structure:

```json
{
  "title": "Post Title",
  "post_body_en": "English version of the LinkedIn post...",
  "post_body_es": "Spanish version of the LinkedIn post...",
  "link": "https://original-article-url.com"
}
```

## News Sources

The application searches for news using:
1. **MCP Server** (if available) - Uses Model Context Protocol for news search
2. **OpenAI Fallback** - Uses GPT-4 to search and summarize recent AI news

## MCP Protocol

This application implements a custom Model Completion Protocol (MCP) for communicating with OpenAI. The MCP prompt is designed to:
- Generate professional, company-branded content
- Create localized Spanish translations (not literal)
- Maintain appropriate tone and length constraints
- Include relevant hashtags and links

## Error Handling

The application includes robust error handling for:
- Missing API keys
- Network connectivity issues
- Invalid JSON responses
- Empty news results

## Web Interface Process

The project uses a modern web interface for maximum ease of use:

1. **Generate AI News Post**:
   - Click the "Generate AI News Post" button in the web interface
   - Watch real-time progress indicators as the post is generated

2. **Copy and Post to LinkedIn**:
   - View both English and Spanish versions side-by-side
   - Click "Copy" to copy either version to your clipboard
   - Click "Open LinkedIn" to go directly to LinkedIn
   - Paste the content and publish

3. **Benefits of Web Interface**:
   - No API rate limits or restrictions
   - Modern, responsive design that works on any device
   - Real-time progress tracking
   - One-click copying and LinkedIn access
   - No need for complex LinkedIn API setup
   - Works with any LinkedIn account type

## Requirements

- Python 3.7+
- Internet connection
- Valid OpenAI API key
- Flask (automatically installed with requirements.txt)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Optional MCP news server for enhanced news fetching

## License

This project is open source and available under the MIT License.
