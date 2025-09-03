# LinkedIn Posts MCP - AI News Generator

A Python application that fetches the latest AI news and generates professional bilingual LinkedIn posts using OpenAI's API with the Model Completion Protocol (MCP).

## Features

- 🔍 Fetches latest AI news using MCP (Model Context Protocol) server
- 🤖 Generates professional bilingual LinkedIn posts (English & Spanish)
- 📝 Uses OpenAI's GPT-4 with custom MCP prompts
- 💾 Outputs results to console and JSON file
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
./run_project.sh
```

### Individual Commands
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

## License

This project is open source and available under the MIT License.
