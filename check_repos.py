import requests

username = "Stark-Expo-Tech-Exchange"
url = f"https://api.github.com/users/{username}/repos"

print(f"Checking repositories for: {username}")
print("=" * 50)

try:
    response = requests.get(url, headers={'User-Agent': 'DSTerminal-Test'})
    
    if response.status_code == 200:
        repos = response.json()
        print(f"✅ Found {len(repos)} public repository(ies)\n")
        
        for repo in repos:
            name = repo.get('name')
            private = repo.get('private', False)
            visibility = "🔒 Private" if private else "🌐 Public"
            default_branch = repo.get('default_branch', 'main')
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            
            print(f"📁 {name}")
            print(f"   Visibility: {visibility}")
            print(f"   Default branch: {default_branch}")
            print(f"   ⭐ {stars} | 🍴 {forks}")
            
            # Check if it has releases
            releases_url = f"https://api.github.com/repos/{username}/{name}/releases"
            releases_response = requests.get(releases_url, headers={'User-Agent': 'DSTerminal-Test'})
            if releases_response.status_code == 200:
                releases = releases_response.json()
                if releases:
                    print(f"   📦 Releases: {len(releases)} (latest: {releases[0].get('tag_name', 'Unknown')})")
                else:
                    print(f"   📦 No releases")
            print()
    elif response.status_code == 404:
        print(f"❌ User '{username}' not found")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")