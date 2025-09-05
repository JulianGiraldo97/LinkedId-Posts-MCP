# LinkedIn Posts MCP - AI News Generator

A Python application that fetches the latest AI news and generates professional bilingual LinkedIn posts using OpenAI's API with the Model Completion Protocol (MCP).

## Features

- 🔍 Fetches latest AI news using MCP (Model Context Protocol) server
- 🤖 Generates professional bilingual LinkedIn posts (English & Spanish)
- 📝 Uses OpenAI's GPT-4 with custom MCP prompts
- 💾 Outputs results to console and JSON file
- 🖥️ **Simple local UI** with one-click generation and copy-to-clipboard
- 🌐 **Web-based UI** that runs in your browser for maximum accessibility
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

### Quick Start with Web UI (Recommended)
```bash
# Launch the web-based UI (runs in browser)
./run_project.sh web
# or
./run_web_ui.sh
```

### Alternative: Local Desktop UI
```bash
# Launch the simple local UI (tkinter)
./run_project.sh ui
# or
./run_ui.sh
```

### Command Line Usage
```bash
# Run complete project (generate + manual posting)
./run_project.sh run

# Generate post only
./run_project.sh gen

# Manual posting (copy/paste to LinkedIn)
./run_project.sh manual

# Setup project (install dependencies, check config)
./run_project.sh setup

# Show help
./run_project.sh help
```

### Manual Python Commands
```bash
# Generate post only
python linkedin_mcp.py

# Manual posting interface
python linkedin_manual_poster.py
```

### Web UI Features (Recommended)
The web-based UI provides:
- **🌐 Browser-based**: Runs in any modern web browser
- **📱 Responsive design**: Works on desktop, tablet, and mobile
- **🚀 One-click generation**: Click "Generate AI News Post" to create bilingual posts
- **📊 Real-time updates**: Live progress indicators and status updates
- **📋 Copy to clipboard**: One-click copying of either language version
- **🔗 Direct LinkedIn access**: One-click link to open LinkedIn
- **⚡ Modern interface**: Clean, professional design with Bootstrap
- **🔄 No page refresh**: AJAX-powered for smooth user experience

### Desktop UI Features (Alternative)
The local desktop UI provides:
- **🖥️ Native application**: Runs as a desktop app using tkinter
- **One-click generation**: Click "Generate AI News Post" to create bilingual posts
- **Side-by-side display**: View English and Spanish versions simultaneously
- **Copy to clipboard**: One-click copying of either language version
- **Open LinkedIn**: Direct link to open LinkedIn in your browser
- **Real-time status**: Progress indicators and status messages
- **Error handling**: Clear error messages and validation

### Command Line Process
The scripts will:
1. Search for the latest AI news using MCP server (or OpenAI fallback)
2. Generate a bilingual LinkedIn post using OpenAI
3. Display the results in the console
4. Save the post to `linkedin_post.json`
5. Provide formatted posts ready for manual copying to LinkedIn

## API Keys

### Required
- **OpenAI API Key**: Get yours from [OpenAI Platform](https://platform.openai.com/api-keys)

### Manual Posting
- **No additional API keys required** - Posts are formatted for manual copying to LinkedIn

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

## Manual Posting Process

The project uses manual posting for maximum reliability and control:

1. **Generate AI News Post**:
   - Run the project to generate bilingual LinkedIn posts
   - Posts are automatically formatted and ready for copying

2. **Copy and Paste to LinkedIn**:
   - Copy the generated post text
   - Go to LinkedIn and create a new post
   - Paste the content and publish

3. **Benefits of Manual Posting**:
   - No API rate limits or restrictions
   - Full control over post timing and content
   - No need for complex LinkedIn API setup
   - Works with any LinkedIn account type

## Requirements

- Python 3.7+
- Internet connection
- Valid OpenAI API key
- Optional MCP news server for enhanced news fetching

### For Desktop UI (Optional)
- tkinter (usually included with Python, but may need separate installation on some systems)

**Installing tkinter (if needed):**
On some systems, tkinter may need to be installed separately:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**macOS (with Homebrew):**
```bash
brew install python-tk
```

**Windows:**
tkinter is usually included with Python installations.

### For Web UI (Recommended)
- Flask (automatically installed with requirements.txt)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## License

This project is open source and available under the MIT License.
