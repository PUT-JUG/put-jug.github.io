import shutil
import subprocess
from pathlib import Path
from typing import Any

from git import Repo
from jinja2 import Environment


def compile_repo(display_name: str, name: str, repo: Repo, output_dir: Path, jinja_env: Environment,
                 resources_path: Path) -> dict[str, Any]:
    src_dir = Path(repo.working_dir) / 'src'
    output_dir = output_dir
    if output_dir.exists():
        shutil.rmtree(output_dir)
        output_dir.mkdir()

    shutil.copytree(resources_path, output_dir, dirs_exist_ok=True)

    for entry in src_dir.iterdir():
        if entry.name.startswith('_') or entry.name.startswith('.'):
            if entry.is_dir():
                shutil.copytree(entry, output_dir / entry.name, dirs_exist_ok=True)
            else:
                shutil.copyfile(entry, output_dir / entry.name)

    entry = _compile_directory(src_dir, repo, output_dir, output_dir, jinja_env)
    entry['name'] = display_name
    entry['sorting_name'] = name
    entry['url'] = output_dir.name

    return entry


def _compile_directory(directory: Path, repo: Repo, base_output_dir: Path, output_dir: Path,
                       jinja_env: Environment) -> dict[str, Any]:
    entries = []
    latest_datetime = None
    for entry in directory.iterdir():
        if entry.name.startswith('_') or entry.name.startswith('.'):
            continue

        if entry.is_dir():
            entry = _compile_directory(entry, repo, base_output_dir, output_dir / entry.name, jinja_env)
        elif entry.suffix == '.md':
            entry = _compile_file(entry, repo, base_output_dir, output_dir)
        else:
            continue

        entries.append(entry)
        entry_datetime = entry['modification_time']
        if latest_datetime is None or entry_datetime > latest_datetime:
            latest_datetime = entry_datetime

    template = jinja_env.get_template('browse.html')
    rendered_html = template.render(
        can_go_up=True,
        entries=sorted(entries, key=lambda entry: entry['name'])
    )
    with open(output_dir / 'index.html', 'w') as output_file:
        output_file.write(rendered_html)

    return {
        'name': directory.name,
        'url': str(output_dir.relative_to(base_output_dir)),
        'modification_time': latest_datetime,
        'is_dir': True
    }


def _compile_file(document_path: Path, repo: Repo, base_output_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(exist_ok=True, parents=True)

    title = document_path.name.replace('.md', '')
    output_file_name = f'{title}.html'
    subprocess.run(['pandoc', str(document_path), '--from=markdown+table_captions',
                    '--to=html', '--standalone', '--mathjax',
                    f'--metadata=title:{title}',
                    f'--resource-path={base_output_dir}',
                    f'--include-in-header=_pandoc_head.html',
                    f'--include-before-body=_pandoc_header.html',
                    f'--include-after-body=_pandoc_footer.html',
                    '--css=_static/github-markdown-light.css',
                    '--css=_static/custom.css',
                    f'--output={output_dir / output_file_name}']
                   )

    commit = next(repo.iter_commits(paths=str(document_path)))
    return {
        'name': title,
        'url': output_file_name,
        'modification_time': commit.committed_datetime,
        'is_dir': False
    }
