import subprocess
from glob import glob
import shutil
from git import Repo
from pathlib import Path
import os

access_token = os.environ.get('ACCESS_TOKEN')

with open('repositories_list.txt', 'r') as file:
    repositories = file.read().split('\n')
    repositories = [repo.split(';') for repo in repositories if len(repo) > 0]

Path('./repositories').mkdir(parents=True, exist_ok=True)
Path('./_site').mkdir(parents=True, exist_ok=True)

for beauty_name, repo in repositories:
  
  repo_name = repo.split('/')[-1].split('.')[0]
  
  print(f'Cloning {beauty_name} from {repo}...')
  
  repo_request = f'https://bartoszptak:{access_token}@' + repo.split('https://')[1]
  
  Repo.clone_from(repo_request, f'./repositories/{repo_name}')
  
  print(f'Buiding {beauty_name}...')
  subprocess.run([f'python3', f'./repositories/{repo_name}/compile.py', f'--working-directory', f'./repositories/{repo_name}'])
  
  print(f'Create index.html for {repo_name}...')
  files_to_index = glob(f'./repositories/{repo_name}/public/*.html', recursive=True)
  files_to_index = [f for f in files_to_index if '_pandoc' not in f]
  files_to_index = sorted(files_to_index)
  
  txt = '<html><body>'
  for file in files_to_index:
    file = file.split('/')[-1]
    txt += f'<a href="{file}">{file}</a><br>'
  txt += '</body></html>'
  
  with open(f'./repositories/{repo_name}/public/index.html', 'w') as file:
    file.write(txt)
  
  shutil.move(f'./repositories/{repo_name}/public/', f'./_site/{repo_name}')
  
# Generate index.html for the root

print('Create index.html for the root...')
txt = '<html><body>'
for beauty_name, repo in sorted(repositories):
  if len(repo) == 0:
    continue
  repo_name = repo.split('/')[-1].split('.')[0]
  print(f'Adding {repo_name} to index.html...')
  txt += f'<a href="{repo_name}/index.html">{beauty_name}</a><br>'
  
txt += '</body></html>'

with open(f'./_site/index.html', 'w') as file:
  file.write(txt)
