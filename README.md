# LinkedIn Profile Explorer MCP

A comprehensive LinkedIn data extraction MCP (Model Context Protocol) server that integrates seamlessly with Claude Desktop. Fetch, explore, and search through LinkedIn posts and comments with powerful filtering and discovery tools.

## 🚀 What This Tool Does

This MCP server transforms Claude Desktop into a powerful LinkedIn data exploration platform. You can:

- **📊 Extract LinkedIn Posts**: Fetch and browse posts from any public LinkedIn profile
- **💬 Comment Discovery**: Extract and explore comments with engagement metrics
- **🔍 Smart Search**: Search through posts and comments with keyword filtering
- **📈 Performance Insights**: Discover top performing posts and comment engagement
- **📅 Date-Based Filtering**: Filter content by specific date ranges
- **👥 Engagement Discovery**: Identify most active commenters and popular discussions

## 🎯 Features

### Post Extraction
- Fetch all posts from any public LinkedIn profile
- Search posts by keywords
- Discover top performing posts by likes and reactions
- Filter posts by date range
- Paginated access to large datasets

### Comment Exploration
- **Complete Comment Threads**: Fetch posts with all their comments in one go
- **Paginated Comment Loading**: Handle large comment threads efficiently
- **Comment Search**: Find specific discussions across all saved data
- **Engagement Discovery**: Discover most active commenters and popular comments
- **Comment Performance**: Track likes and reactions on individual comments

## 📋 Prerequisites

- **Python 3.7+** installed on your system
- **Claude Desktop** application
- **RapidAPI account** with LinkedIn Data API access

## 🛠️ Setup Guide

### Step 1: Get Your RapidAPI Key

1. **Visit RapidAPI**: Go to [LinkedIn Data API on RapidAPI](https://rapidapi.com/rockapis-rockapis-default/api/linkedin-data-api)
2. **Create Account**: Sign up for a free RapidAPI account if you don't have one
3. **Subscribe to API**: Click "Subscribe" on the LinkedIn Data API page
4. **Choose Plan**: Select a plan (free tier available for testing)
5. **Get Your Key**: Copy your RapidAPI key from the dashboard

### Step 2: Download and Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/kempec110/linkedin-mcp.git
   cd linkedin-mcp
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Environment File**:
   - Create a file named `.env` in the project folder
   - Add your RapidAPI key:
   ```env
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```

### Step 3: Configure Claude Desktop

1. **Locate Claude Desktop Config**:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Edit Configuration File**:
   Open the config file and add the LinkedIn MCP server:
   ```json
   {
     "mcpServers": {
       "linkedin-analyzer": {
         "command": "python",
         "args": ["C:/path/to/your/linkedin-mcp/main.py"],
         "env": {
           "RAPIDAPI_KEY": "your_rapidapi_key_here"
         }
       }
     }
   }
   ```

   **Important**: Replace `C:/path/to/your/linkedin-mcp/main.py` with the actual path to your `main.py` file.

3. **Restart Claude Desktop**: Close and reopen Claude Desktop to load the new MCP server.

### Step 4: Verify Installation

1. **Open Claude Desktop**
2. **Start New Conversation**
3. **Test the Connection**: Type something like:
   ```
   Can you help me explore LinkedIn posts? What tools do you have available?
   ```

If successful, Claude should show you the available LinkedIn data extraction tools.


## 📚 How to Use

### Basic Post Extraction

1. **Fetch Posts from a Profile**:
   ```
   Fetch LinkedIn posts for the username "john-doe"
   ```

2. **Search Through Posts**:
   ```
   Search all saved posts for mentions of "artificial intelligence"
   ```

3. **Get Top Performing Posts**:
   ```
   Show me the top 5 posts by like count
   ```

### Advanced Comment Exploration

1. **Fetch Post with All Comments**:
   ```
   Get all comments for LinkedIn post URN 7169084130104737792
   ```

2. **Search Comments**:
   ```
   Search all comments for the keyword "AI" and show engagement metrics
   ```

3. **Explore Comment Engagement**:
   ```
   Show me comment insights including top commenters and most liked comments
   ```

### Data Filtering and Discovery

1. **Filter by Date**:
   ```
   Show me posts from January 2024 to March 2024
   ```

2. **Get Comment Insights**:
   ```
   Explore comment engagement patterns for post 7169084130104737792
   ```

## 🔧 Available Tools

### Core Post Tools
| Tool | Description |
|------|-------------|
| `fetch_and_save_linkedin_posts` | Fetch posts from any LinkedIn username |
| `get_saved_posts` | Retrieve saved posts with pagination |
| `search_posts` | Search posts by keywords |
| `get_top_posts` | Get highest performing posts |
| `get_posts_by_date` | Filter posts by date range |

### Comment Exploration Tools *(New!)*
| Tool | Description |
|------|-------------|
| `fetch_post_with_comments` | Get complete post with all comments |
| `fetch_post_comments_paginated` | Load comments with pagination support |
| `get_saved_posts_with_comments` | Retrieve posts with comment data |
| `get_saved_paginated_comments` | Access specific comment pages |
| `search_comments` | Search through all comment text |
| `get_top_commented_posts` | Find most discussed posts |
| `get_comment_analytics` | Comprehensive comment engagement insights |

## 📁 Project Structure

```
linkedin-mcp/
├── main.py                              # Main MCP server implementation
├── requirements.txt                     # Python dependencies
├── .env                                # Environment variables (your API key)
├── README.md                           # This documentation
├── linkedin_posts.json                # Saved posts data
├── linkedin_posts_with_comments.json  # Posts with complete comment threads
└── linkedin_comments_paginated_*.json # Individual paginated comment files
```

## 🔑 Data Files Explained

- **`linkedin_posts.json`**: Basic post data without comments
- **`linkedin_posts_with_comments.json`**: Complete posts with all associated comments
- **`linkedin_comments_paginated_*.json`**: Individual files for each post's paginated comments

## 🚨 Troubleshooting

### Common Issues

1. **"MCP server not found"**:
   - Check that the path in `claude_desktop_config.json` is correct
   - Ensure `main.py` exists at the specified location
   - Restart Claude Desktop after config changes

2. **"API key error"**:
   - Verify your RapidAPI key is correct in the `.env` file
   - Check that you're subscribed to the LinkedIn Data API on RapidAPI
   - Ensure the `.env` file is in the same directory as `main.py`

3. **"No data found" errors**:
   - Fetch posts first using `fetch_and_save_linkedin_posts`
   - Check that JSON files are being created in the project directory

### Getting Help

If you encounter issues:
1. Check the file paths in your configuration
2. Verify your API key is working on RapidAPI
3. Ensure all dependencies are installed
4. Restart Claude Desktop after making changes

## 🔒 Privacy & Ethics

- This tool only accesses **public LinkedIn data**
- Always respect LinkedIn's terms of service
- Use responsibly and don't overwhelm the API with excessive requests
- Be mindful of privacy when exploring others' content

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork the Repository**
2. **Create a Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**kempec110** - [GitHub Profile](https://github.com/kempec110)

## 🙏 Acknowledgments

- **rugvedp** - Original LinkedIn MCP implementation and foundation
- **RapidAPI** - Providing reliable LinkedIn data access
- **Anthropic** - Claude AI platform and MCP framework
- **LinkedIn Data API** - Comprehensive LinkedIn data endpoints

## 📈 API Integration Details

This project integrates with the following RapidAPI endpoints:

### Primary Endpoints
- **`GET /get-profile-posts`**: Fetch posts from LinkedIn profiles
- **`GET /get-profile-post-and-comments`**: Get complete post with all comments
- **`GET /get-profile-posts-comments`**: Paginated comment loading

### API Configuration
- **Base URL**: `https://linkedin-data-api.p.rapidapi.com`
- **Required Headers**: 
  - `x-rapidapi-key`: Your RapidAPI key
  - `x-rapidapi-host`: `linkedin-data-api.p.rapidapi.com`

---
