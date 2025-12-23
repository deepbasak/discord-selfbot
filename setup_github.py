#!/usr/bin/env python3
"""
Script to create a GitHub repository and push the code.
Supports both GitHub API (with token) and manual instructions.
"""

import subprocess
import sys
import json
import os

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def create_repo_with_api(repo_name, description, token, is_private=False):
    """Create a GitHub repository using the API."""
    import urllib.request
    import urllib.error
    
    url = "https://api.github.com/user/repos"
    data = {
        "name": repo_name,
        "description": description,
        "private": is_private,
        "auto_init": False
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
    req.add_header("Authorization", f"token {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/vnd.github.v3+json")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return True, result.get("clone_url", ""), None
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        return False, None, error_msg
    except Exception as e:
        return False, None, str(e)

def main():
    print("=" * 60)
    print("GitHub Repository Setup")
    print("=" * 60)
    print()
    
    # Check if already has remote
    stdout, stderr, code = run_command("git remote -v", check=False)
    if "origin" in stdout:
        print("⚠️  Repository already has a remote 'origin'")
        print(f"Current remotes:\n{stdout}")
        response = input("\nDo you want to continue and add a new remote? (y/n): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            return
    
    # Get repository name
    repo_name = input("Enter GitHub repository name (or press Enter for 'discord-selfbot'): ").strip()
    if not repo_name:
        repo_name = "discord-selfbot"
    
    # Get description
    description = input("Enter repository description (or press Enter for default): ").strip()
    if not description:
        description = "Advanced Discord SelfBot with Selenium Integration"
    
    # Ask for privacy
    is_private_input = input("Make repository private? (y/n, default: n): ").strip().lower()
    is_private = is_private_input == 'y'
    
    print("\n" + "=" * 60)
    print("Choose method to create repository:")
    print("1. Use GitHub API (requires Personal Access Token)")
    print("2. Manual creation (I'll provide instructions)")
    print("=" * 60)
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        # API method
        print("\nTo create a Personal Access Token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Click 'Generate new token (classic)'")
        print("3. Select scope: 'repo' (full control of private repositories)")
        print("4. Generate and copy the token")
        print()
        
        token = input("Enter your GitHub Personal Access Token: ").strip()
        if not token:
            print("❌ Token is required for API method.")
            return
        
        print("\n🔄 Creating repository on GitHub...")
        success, clone_url, error = create_repo_with_api(repo_name, description, token, is_private)
        
        if success:
            print(f"✅ Repository created successfully!")
            print(f"   URL: {clone_url}")
            
            # Add remote and push
            print("\n🔄 Adding remote origin...")
            run_command(f'git remote add origin {clone_url}')
            
            # Get default branch name
            stdout, _, _ = run_command("git branch --show-current")
            branch = stdout if stdout else "master"
            
            print(f"🔄 Pushing to GitHub (branch: {branch})...")
            stdout, stderr, code = run_command(f"git push -u origin {branch}")
            
            if code == 0:
                print("✅ Successfully pushed to GitHub!")
                print(f"\n🌐 Repository URL: https://github.com/{repo_name.split('/')[-1] if '/' in repo_name else 'YOUR_USERNAME/' + repo_name}")
            else:
                print("❌ Error pushing to GitHub:")
                print(stderr)
                print("\nYou may need to:")
                print("1. Set up your GitHub credentials")
                print("2. Use SSH instead of HTTPS")
                print(f"3. Manually push with: git push -u origin {branch}")
        else:
            print(f"❌ Failed to create repository: {error}")
            print("\nFalling back to manual method...")
            choice = "2"
    
    if choice == "2":
        # Manual method
        print("\n" + "=" * 60)
        print("Manual Setup Instructions:")
        print("=" * 60)
        print("\n1. Go to: https://github.com/new")
        print(f"2. Repository name: {repo_name}")
        print(f"3. Description: {description}")
        print(f"4. Visibility: {'Private' if is_private else 'Public'}")
        print("5. DO NOT initialize with README, .gitignore, or license")
        print("6. Click 'Create repository'")
        print()
        print("After creating the repository, run these commands:")
        print("=" * 60)
        
        # Get username
        username = input("Enter your GitHub username: ").strip()
        if not username:
            username = "YOUR_USERNAME"
        
        # Get default branch
        stdout, _, _ = run_command("git branch --show-current")
        branch = stdout if stdout else "master"
        
        print(f"\ngit remote add origin https://github.com/{username}/{repo_name}.git")
        print(f"git branch -M {branch}")
        print(f"git push -u origin {branch}")
        print("=" * 60)
        
        # Ask if they want to run commands now
        response = input("\nHave you created the repository? (y/n): ").strip().lower()
        if response == 'y':
            print("\n🔄 Adding remote origin...")
            run_command(f'git remote add origin https://github.com/{username}/{repo_name}.git')
            
            print(f"🔄 Setting branch name to {branch}...")
            run_command(f"git branch -M {branch}")
            
            print(f"🔄 Pushing to GitHub...")
            stdout, stderr, code = run_command(f"git push -u origin {branch}")
            
            if code == 0:
                print("✅ Successfully pushed to GitHub!")
                print(f"\n🌐 Repository URL: https://github.com/{username}/{repo_name}")
            else:
                print("❌ Error pushing to GitHub:")
                print(stderr)
                print("\nYou may need to authenticate. Try:")
                print("1. Use GitHub Desktop")
                print("2. Set up SSH keys")
                print("3. Use a Personal Access Token")
        else:
            print("\nRun the commands above after creating the repository.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

