import json
import os
import shutil
from pathlib import Path

from git import Repo
from jinja2 import Environment, FileSystemLoader, select_autoescape

from compilation import compile_repo


def main():
    access_token = os.environ.get('ACCESS_TOKEN')

    with open('repositories_list.txt', 'r') as file:
        repositories = file.read().split('\n')
        repositories = [repo.strip() for repo in repositories if len(repo) > 0]

    site_path = Path('_site')
    resources_path = Path('resources')
    repositories_path = Path('repositories')

    site_path.mkdir(parents=True, exist_ok=True)
    repositories_path.mkdir(parents=True, exist_ok=True)

    # Copy static files for the site
    shutil.copytree(resources_path / 'site', site_path, dirs_exist_ok=True)

    jinja_env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape()
    )

    entries = []
    for repo in repositories:
        repo_name = repo.split('/')[-1].split('.')[0]

        repo_dir = Path(f'repositories/{repo_name}')
        if not repo_dir.exists():
            print(f'Cloning {repo}...')

            repo_request = f'https://dzbanobot:{access_token}@' + repo.split('https://')[1]
            repo = Repo.clone_from(repo_request, repo_dir)
        else:
            repo = Repo(repo_dir)

        config = load_json(repo_dir / 'config.json')
        lang = config['lang']
        name = config['name']
        display_name = f'{lang} {name}'

        print(f'Building {repo_name}...')
        try:
            entries.append(
                compile_repo(display_name, name, repo, site_path / repo_name, jinja_env, resources_path / 'pandoc')
            )
        except Exception as e:
            print(f'Error compiling {repo_name}: {e}')

    # Build index for the root
    template = jinja_env.get_template('browse.html')
    rendered_html = template.render(
        can_go_up=False,
        entries=sorted(entries, key=lambda entry: entry['sorting_name'])
    )
    with open(site_path / 'index.html', 'w') as output_file:
        output_file.write(rendered_html)


def load_json(path: Path) -> dict | list:
    with open(path, 'r') as file:
        return json.load(file)


if __name__ == '__main__':
    main()
