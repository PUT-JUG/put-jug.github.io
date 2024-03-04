import subprocess
from glob import glob
import shutil
from git import Repo
from pathlib import Path

with open('repositories_list.txt', 'r') as file:
    repositories = file.readlines()
    repositories = [repo.strip() for repo in repositories]

Path('./repositories').mkdir(parents=True, exist_ok=True)
Path('./_site').mkdir(parents=True, exist_ok=True)

for repo in repositories:
  if len(repo) == 0:
    continue
  
  repo_name = repo.split('/')[-1].split('.')[0]
  
  print(f'Cloning {repo_name}...')
  Repo.clone_from(repo, f'./repositories/{repo_name}')
  
  print(f'Buiding {repo_name}...')
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
for repo in repositories:
  if len(repo) == 0:
    continue
  repo_name = repo.split('/')[-1].split('.')[0]
  txt += f'<a href="{repo_name}/index.html">{repo_name}</a><br>'
  
txt += '</body></html>'

with open(f'./_site/index.html', 'w') as file:
  file.write(txt)
