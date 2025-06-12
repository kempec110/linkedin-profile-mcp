from mcp.server.fastmcp import FastMCP
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
# Create an MCP server
mcp = FastMCP("LinkedIn Profile Analyzer")

DATA_FILE = "linkedin_posts.json"
COMMENTS_DATA_FILE = "linkedin_posts_with_comments.json"
rapidapi_key = os.getenv("RAPIDAPI_KEY")

@mcp.tool()
def fetch_and_save_linkedin_posts(username: str) -> str:
    """Fetch LinkedIn posts for a given username and save them in a JSON file."""
    
    url = "https://linkedin-data-api.p.rapidapi.com/get-profile-posts"
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }
    querystring = {"username": username}
    
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        raise Exception(f"Error fetching posts: {response.status_code} - {response.text}")

    data = response.json()
    posts = []
    for post in data.get('data', []):
        posts.append({
                "Post URL": post.get('postUrl', ''),
                "Text": post.get('text', ''),
                "Like Count": post.get('likeCount', 0),
                "Total Reactions": post.get('totalReactionCount', 0),
                "Posted Date": post.get('postedDate', ''),
                "Posted Timestamp": post.get('postedDateTimestamp', ''),
                "Share URL": post.get('shareUrl', ''),
                "Author Name": f"{post.get('author', {}).get('firstName', '')} {post.get('author', {}).get('lastName', '')}",
                "Author Profile": post.get('author', {}).get('url', ''),
                "Author Headline": post.get('author', {}).get('headline', ''),
                "Author Profile Picture": post.get('author', {}).get('profilePictures', [{}])[0].get('url', ''),
                "Main Image": post.get('image', [{}])[0].get('url', '') if post.get('image') else '',
                "All Images": ", ".join([img.get('url', '') for img in post.get('image', [])]),
        })
    
    # Save data to a JSON file
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4)
    
    return f"Data saved in {DATA_FILE}"

@mcp.tool()
def get_saved_posts(start: int = 0, limit: int = 5) -> dict:
    """
    Retrieve saved LinkedIn posts with pagination.
    
    Args:
        start (int): Index of the first post to retrieve.
        limit (int): Number of posts to return (Max: 5).
    
    Returns:
        dict: Contains retrieved posts and a flag for more data availability.
    """
    if not os.path.exists(DATA_FILE):
        return {"message": "No data found. Fetch posts first using fetch_and_save_linkedin_posts().", "posts": []}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            posts = json.load(f)

        total_posts = len(posts)

        # Ensure limit does not exceed 5 posts
        limit = min(limit, 5)

        paginated_posts = posts[start:start + limit]

        return {
            "posts": paginated_posts,
            "total_posts": total_posts,
            "has_more": start + limit < total_posts
        }

    except json.JSONDecodeError:
        return {"message": "Error reading data file. JSON might be corrupted.", "posts": []}
    
@mcp.tool()
def search_posts(keyword: str) -> dict:
    """
    Search saved LinkedIn posts for a specific keyword.
    
    Args:
        keyword (str): The keyword to search for in post text.
    
    Returns:
        dict: List of posts matching the keyword.
    """
    if not os.path.exists(DATA_FILE):
        return {"message": "No data found. Fetch posts first.", "posts": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    filtered_posts = [post for post in posts if keyword.lower() in post.get("Text", "").lower()]

    return {
        "keyword": keyword,
        "total_results": len(filtered_posts),
        "posts": filtered_posts[:5],  # Show only first 10 results initially
        "has_more": len(filtered_posts) > 5
    }

@mcp.tool()
def get_top_posts(metric: str = "Like Count", top_n: int = 5) -> dict:
    """
    Get the top LinkedIn posts based on a specific engagement metric.

    Args:
        metric (str): The metric to rank posts by. Options: "Like Count", "Total Reactions".
        top_n (int): Number of top posts to return.

    Returns:
        dict: List of top posts sorted by the selected metric.
    """
    if not os.path.exists(DATA_FILE):
        return {"message": "No data found. Fetch posts first.", "posts": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    if metric not in ["Like Count", "Total Reactions"]:
        return {"message": "Invalid metric. Use 'Like Count' or 'Total Reactions'."}

    sorted_posts = sorted(posts, key=lambda x: x.get(metric, 0), reverse=True)

    return {"metric": metric, "posts": sorted_posts[:top_n]}

from datetime import datetime

@mcp.tool()
def get_posts_by_date(start_date: str, end_date: str) -> dict:
    """
    Retrieve posts within a specified date range.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        dict: List of posts within the date range.
    """
    if not os.path.exists(DATA_FILE):
        return {"message": "No data found. Fetch posts first.", "posts": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {"message": "Invalid date format. Use 'YYYY-MM-DD'."}

    filtered_posts = [
        post for post in posts if start_dt <= datetime.strptime(post["Posted Date"], "%Y-%m-%d") <= end_dt
    ]

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_results": len(filtered_posts),
        "posts": filtered_posts[:5],  # Show only first 10 results initially
        "has_more": len(filtered_posts) > 5
    }

# =============================================================================
# NEW COMMENT FUNCTIONALITY ADDED BELOW
# =============================================================================

@mcp.tool()
def fetch_post_with_comments(post_urn: str) -> str:
    """
    Fetch a specific LinkedIn post with all its comments using the post URN.
    
    Args:
        post_urn (str): The URN/ID of the LinkedIn post (e.g., '7181285160586211328')
    
    Returns:
        str: Status message about the operation
    """
    
    url = "https://linkedin-data-api.p.rapidapi.com/get-profile-post-and-comments"
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }
    querystring = {"urn": post_urn}
    
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        raise Exception(f"Error fetching post with comments: {response.status_code} - {response.text}")

    data = response.json()
    
    if not data.get('success', False):
        raise Exception(f"API returned unsuccessful response: {data.get('message', 'Unknown error')}")
    
    # Extract post data
    post_data = data.get('data', {}).get('post', {})
    comments_data = data.get('data', {}).get('comments', [])
    
    # Structure the post data
    post_info = {
        "Post URN": post_urn,
        "Post Text": post_data.get('text', ''),
        "Like Count": post_data.get('likeCount', 0),
        "Total Reactions": post_data.get('totalReactionCount', 0),
        "Comments Count": post_data.get('commentsCount', 0),
        "Reposts Count": post_data.get('repostsCount', 0),
        "Posted Date": post_data.get('postedDate', ''),
        "Posted Timestamp": post_data.get('postedDateTimestamp', ''),
        "Author": {
            "Name": f"{post_data.get('author', {}).get('firstName', '')} {post_data.get('author', {}).get('lastName', '')}",
            "Username": post_data.get('author', {}).get('username', ''),
            "Headline": post_data.get('author', {}).get('headline', ''),
            "Profile URL": post_data.get('author', {}).get('url', ''),
            "Profile Picture": post_data.get('author', {}).get('profilePictures', [{}])[0].get('url', '') if post_data.get('author', {}).get('profilePictures') else ''
        },
        "Comments": []
    }
    
    # Process comments
    for comment in comments_data:
        comment_info = {
            "Comment URN": comment.get('entityUrn', ''),
            "Text": comment.get('text', ''),
            "Created Date": comment.get('createdAtString', ''),
            "Created Timestamp": comment.get('createdAt', ''),
            "Like Count": comment.get('totalSocialActivityCounts', {}).get('likeCount', 0),
            "Total Reactions": comment.get('totalSocialActivityCounts', {}).get('totalReactionCount', 0),
            "Permalink": comment.get('permalink', ''),
            "Is Pinned": comment.get('isPinned', False),
            "Is Edited": comment.get('isEdited', False),
            "Author": {
                "Name": f"{comment.get('author', {}).get('firstName', '')} {comment.get('author', {}).get('LastName', '')}",
                "Username": comment.get('author', {}).get('username', ''),
                "Title": comment.get('author', {}).get('title', ''),
                "LinkedIn URL": comment.get('author', {}).get('linkedinUrl', ''),
                "URN": comment.get('author', {}).get('urn', ''),
                "ID": comment.get('author', {}).get('id', '')
            }
        }
        post_info["Comments"].append(comment_info)
    
    # Load existing data or create new list
    try:
        with open(COMMENTS_DATA_FILE, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []
    
    # Check if post already exists and update, or add new
    post_exists = False
    for i, existing_post in enumerate(existing_data):
        if existing_post.get("Post URN") == post_urn:
            existing_data[i] = post_info
            post_exists = True
            break
    
    if not post_exists:
        existing_data.append(post_info)
    
    # Save updated data
    with open(COMMENTS_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4)
    
    return f"Post with {len(comments_data)} comments saved to {COMMENTS_DATA_FILE}"

@mcp.tool()
def fetch_post_comments_paginated(post_urn: str, sort: str = "mostRelevant", page: int = 1) -> str:
    """
    Fetch comments for a specific LinkedIn post with pagination support.
    
    Args:
        post_urn (str): The URN/ID of the LinkedIn post (e.g., '7169084130104737792')
        sort (str): Sorting method - 'mostRelevant' or other sorting options
        page (int): Page number for pagination (starts from 1)
    
    Returns:
        str: Status message about the operation
    """
    
    url = "https://linkedin-data-api.p.rapidapi.com/get-profile-posts-comments"
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }
    querystring = {
        "urn": post_urn,
        "sort": sort,
        "page": str(page)
    }
    
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        raise Exception(f"Error fetching post comments: {response.status_code} - {response.text}")

    data = response.json()
    
    if not data.get('success', False):
        raise Exception(f"API returned unsuccessful response: {data.get('message', 'Unknown error')}")
    
    # Extract comments data
    comments_data = data.get('data', [])
    total_comments = data.get('total', 0)
    total_pages = data.get('totalPage', 1)
    pagination_token = data.get('paginationToken', '')
    
    # Structure the comments data
    comments_info = {
        "Post URN": post_urn,
        "Page": page,
        "Sort": sort,
        "Total Comments": total_comments,
        "Total Pages": total_pages,
        "Pagination Token": pagination_token,
        "Comments": []
    }
    
    # Process comments
    for comment in comments_data:
        comment_info = {
            "Text": comment.get('text', ''),
            "Created Date": comment.get('createdAtString', ''),
            "Created Timestamp": comment.get('createdAt', ''),
            "Permalink": comment.get('permalink', ''),
            "Is Pinned": comment.get('isPinned', False),
            "Is Edited": comment.get('isEdited', False),
            "Thread URN": comment.get('threadUrn', ''),
            "Author": {
                "Name": comment.get('author', {}).get('name', ''),
                "Username": comment.get('author', {}).get('username', ''),
                "Title": comment.get('author', {}).get('title', ''),
                "LinkedIn URL": comment.get('author', {}).get('linkedinUrl', ''),
                "URN": comment.get('author', {}).get('urn', ''),
                "ID": comment.get('author', {}).get('id', '')
            }
        }
        comments_info["Comments"].append(comment_info)
    
    # Load existing paginated comments or create new list
    paginated_file = f"linkedin_comments_paginated_{post_urn}.json"
    try:
        with open(paginated_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {"pages": {}, "metadata": {}}
    
    # Store page data
    existing_data["pages"][str(page)] = comments_info
    existing_data["metadata"] = {
        "post_urn": post_urn,
        "total_comments": total_comments,
        "total_pages": total_pages,
        "last_updated": comments_info["Comments"][0]["Created Date"] if comments_data else "",
        "pages_fetched": list(existing_data["pages"].keys())
    }
    
    # Save updated data
    with open(paginated_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4)
    
    return f"Page {page} with {len(comments_data)} comments saved to {paginated_file}. Total: {total_comments} comments across {total_pages} pages"

@mcp.tool()
def get_saved_posts_with_comments(start: int = 0, limit: int = 3) -> dict:
    """
    Retrieve saved LinkedIn posts with comments with pagination.
    
    Args:
        start (int): Index of the first post to retrieve.
        limit (int): Number of posts to return (Max: 3 due to comment data size).
    
    Returns:
        dict: Contains retrieved posts with comments and pagination info.
    """
    if not os.path.exists(COMMENTS_DATA_FILE):
        return {"message": "No posts with comments found. Fetch posts with comments first using fetch_post_with_comments().", "posts": []}

    try:
        with open(COMMENTS_DATA_FILE, "r", encoding="utf-8") as f:
            posts = json.load(f)

        total_posts = len(posts)

        # Ensure limit does not exceed 3 posts (due to comment data size)
        limit = min(limit, 3)

        paginated_posts = posts[start:start + limit]

        return {
            "posts": paginated_posts,
            "total_posts": total_posts,
            "has_more": start + limit < total_posts
        }

    except json.JSONDecodeError:
        return {"message": "Error reading comments data file. JSON might be corrupted.", "posts": []}

@mcp.tool()
def get_saved_paginated_comments(post_urn: str, page: int = None) -> dict:
    """
    Retrieve saved paginated comments for a specific post.
    
    Args:
        post_urn (str): The URN/ID of the LinkedIn post
        page (int, optional): Specific page to retrieve. If None, returns all pages.
    
    Returns:
        dict: Paginated comments data
    """
    paginated_file = f"linkedin_comments_paginated_{post_urn}.json"
    
    if not os.path.exists(paginated_file):
        return {"message": f"No paginated comments found for post {post_urn}. Fetch comments first using fetch_post_comments_paginated().", "data": {}}

    try:
        with open(paginated_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if page is not None:
            page_str = str(page)
            if page_str in data.get("pages", {}):
                return {
                    "metadata": data.get("metadata", {}),
                    "page_data": data["pages"][page_str]
                }
            else:
                return {"message": f"Page {page} not found. Available pages: {list(data.get('pages', {}).keys())}", "data": {}}
        else:
            return data

    except json.JSONDecodeError:
        return {"message": "Error reading paginated comments file. JSON might be corrupted.", "data": {}}

@mcp.tool()
def search_comments(keyword: str, post_urn: str = None, include_paginated: bool = True) -> dict:
    """
    Search through saved comments for a specific keyword.
    
    Args:
        keyword (str): The keyword to search for in comment text.
        post_urn (str, optional): Limit search to a specific post URN.
        include_paginated (bool): Whether to include paginated comments in search.
    
    Returns:
        dict: List of comments and posts matching the keyword.
    """
    results = []
    
    # Search in full posts with comments (from fetch_post_with_comments)
    if os.path.exists(COMMENTS_DATA_FILE):
        with open(COMMENTS_DATA_FILE, "r", encoding="utf-8") as f:
            posts = json.load(f)
        
        for post in posts:
            # If post_urn is specified, only search that post
            if post_urn and post.get("Post URN") != post_urn:
                continue
                
            # Search in post text
            if keyword.lower() in post.get("Post Text", "").lower():
                results.append({
                    "type": "post",
                    "source": "full_post_data",
                    "post_urn": post.get("Post URN"),
                    "post_text": post.get("Post Text"),
                    "author": post.get("Author", {}).get("Name"),
                    "posted_date": post.get("Posted Date")
                })
            
            # Search in comments
            for comment in post.get("Comments", []):
                if keyword.lower() in comment.get("Text", "").lower():
                    results.append({
                        "type": "comment",
                        "source": "full_post_data",
                        "post_urn": post.get("Post URN"),
                        "comment_urn": comment.get("Comment URN"),
                        "comment_text": comment.get("Text"),
                        "comment_author": comment.get("Author", {}).get("Name"),
                        "comment_date": comment.get("Created Date"),
                        "comment_likes": comment.get("Like Count"),
                        "post_author": post.get("Author", {}).get("Name")
                    })
    
    # Search in paginated comments if enabled
    if include_paginated:
        # Find all paginated comment files
        for file in os.listdir('.'):
            if file.startswith('linkedin_comments_paginated_') and file.endswith('.json'):
                file_post_urn = file.replace('linkedin_comments_paginated_', '').replace('.json', '')
                
                # If post_urn is specified, only search that post's paginated comments
                if post_urn and file_post_urn != post_urn:
                    continue
                
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        paginated_data = json.load(f)
                    
                    # Search through all pages
                    for page_num, page_data in paginated_data.get("pages", {}).items():
                        for comment in page_data.get("Comments", []):
                            if keyword.lower() in comment.get("Text", "").lower():
                                results.append({
                                    "type": "comment",
                                    "source": "paginated_data",
                                    "post_urn": file_post_urn,
                                    "page": page_num,
                                    "comment_text": comment.get("Text"),
                                    "comment_author": comment.get("Author", {}).get("Name"),
                                    "comment_date": comment.get("Created Date"),
                                    "permalink": comment.get("Permalink")
                                })
                except (json.JSONDecodeError, FileNotFoundError):
                    continue

    return {
        "keyword": keyword,
        "post_urn_filter": post_urn,
        "total_results": len(results),
        "results": results[:15],  # Show only first 15 results
        "has_more": len(results) > 15,
        "sources_searched": ["full_post_data"] + (["paginated_data"] if include_paginated else [])
    }

@mcp.tool()
def get_top_commented_posts(top_n: int = 5) -> dict:
    """
    Get the posts with the most comments.

    Args:
        top_n (int): Number of top posts to return.

    Returns:
        dict: List of posts sorted by comment count.
    """
    if not os.path.exists(COMMENTS_DATA_FILE):
        return {"message": "No posts with comments found.", "posts": []}

    with open(COMMENTS_DATA_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    # Sort posts by number of comments
    sorted_posts = sorted(posts, key=lambda x: len(x.get("Comments", [])), reverse=True)
    
    top_posts = []
    for post in sorted_posts[:top_n]:
        top_posts.append({
            "Post URN": post.get("Post URN"),
            "Post Text": post.get("Post Text")[:200] + "..." if len(post.get("Post Text", "")) > 200 else post.get("Post Text"),
            "Author": post.get("Author", {}).get("Name"),
            "Posted Date": post.get("Posted Date"),
            "Comments Count": len(post.get("Comments", [])),
            "Total Reactions": post.get("Total Reactions"),
            "Like Count": post.get("Like Count")
        })

    return {"metric": "comments_count", "posts": top_posts}

@mcp.tool()
def get_comment_analytics(post_urn: str = None) -> dict:
    """
    Get analytics about comments including most active commenters, engagement patterns, etc.
    
    Args:
        post_urn (str, optional): Analyze comments for a specific post URN.
    
    Returns:
        dict: Comment analytics data.
    """
    if not os.path.exists(COMMENTS_DATA_FILE):
        return {"message": "No posts with comments found.", "analytics": {}}

    with open(COMMENTS_DATA_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    all_comments = []
    commenters = {}
    
    for post in posts:
        # If post_urn is specified, only analyze that post
        if post_urn and post.get("Post URN") != post_urn:
            continue
            
        for comment in post.get("Comments", []):
            all_comments.append(comment)
            
            # Track commenters
            author_name = comment.get("Author", {}).get("Name", "Unknown")
            if author_name not in commenters:
                commenters[author_name] = {
                    "comment_count": 0,
                    "total_likes": 0,
                    "username": comment.get("Author", {}).get("Username", ""),
                    "title": comment.get("Author", {}).get("Title", "")
                }
            
            commenters[author_name]["comment_count"] += 1
            commenters[author_name]["total_likes"] += comment.get("Like Count", 0)

    # Sort commenters by activity
    top_commenters = sorted(commenters.items(), key=lambda x: x[1]["comment_count"], reverse=True)[:10]
    
    # Sort by engagement (likes)
    most_liked_comments = sorted(all_comments, key=lambda x: x.get("Like Count", 0), reverse=True)[:5]
    
    analytics = {
        "total_comments": len(all_comments),
        "unique_commenters": len(commenters),
        "average_likes_per_comment": sum(c.get("Like Count", 0) for c in all_comments) / len(all_comments) if all_comments else 0,
        "top_commenters": [{"name": name, **data} for name, data in top_commenters],
        "most_liked_comments": [{
            "text": comment.get("Text", "")[:150] + "..." if len(comment.get("Text", "")) > 150 else comment.get("Text", ""),
            "author": comment.get("Author", {}).get("Name"),
            "likes": comment.get("Like Count", 0),
            "date": comment.get("Created Date")
        } for comment in most_liked_comments],
        "post_urn_filter": post_urn
    }
    
    return analytics

if __name__ == '__main__':
    mcp.run()