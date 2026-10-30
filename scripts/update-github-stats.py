#!/usr/bin/env python3
"""Atualiza o cartão local com dados públicos reais da API do GitHub."""

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json
from urllib.request import Request, urlopen


def main():
    username = 'luscamasfei'
    source = f'https://api.github.com/users/{username}'
    request = Request(source, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'luscamasfei-profile-stats',
        'X-GitHub-Api-Version': '2022-11-28',
    })
    with urlopen(request, timeout=30) as response:
        user = json.load(response)
    assert user['login'].lower() == username
    keys = ('public_repos', 'followers', 'following')
    assert all(type(user[key]) is int and user[key] >= 0 for key in keys)
    now = datetime.now(timezone.utc)
    snapshot = {
        'username': username,
        'source': source,
        'retrieved_at': now.isoformat(timespec='seconds'),
        **{key: user[key] for key in keys},
    }
    metrics = [
        ('REPOSITÓRIOS', 'PÚBLICOS', user['public_repos']),
        ('SEGUIDORES', '', user['followers']),
        ('SEGUINDO', '', user['following']),
    ]
    description = '; '.join(f'{label} {extra}: {value}' for label, extra, value in metrics)
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="224" viewBox="0 0 720 224" role="img" aria-labelledby="title desc">
  <title id="title">Estatísticas públicas de {username} no GitHub</title>
  <desc id="desc">{escape(description)}. Consulta em {now:%d/%m/%Y %H:%M} UTC. Retrato estático.</desc>
  <rect x="0.5" y="0.5" width="719" height="223" rx="4" fill="#0b0b0b" stroke="#424242"/>
  <path d="M1 20V1h20 M699 223h20v-19" fill="none" stroke="#bdbdbd"/>
  <text x="28" y="33" fill="#e4e4e4" font-family="monospace" font-size="18">{username} / GitHub</text>
  <path d="M28 50h664 M252 72v100 M468 72v100" stroke="#303030"/>
''']
    for x, (label, extra, value) in zip((144, 360, 576), metrics):
        parts.append(f'''  <g text-anchor="middle" font-family="monospace">
    <text x="{x}" y="112" fill="#eeeeee" font-size="44">{value}</text>
    <text x="{x}" y="145" fill="#bdbdbd" font-size="16">{label}</text>
    <text x="{x}" y="165" fill="#bdbdbd" font-size="16">{extra}</text>
  </g>''')
    parts.append(f'''  <text x="28" y="204" fill="#a8a8a8" font-family="monospace" font-size="14">CONSULTA: {now:%d/%m/%Y %H:%M} UTC · DADOS PÚBLICOS</text>
</svg>
''')
    assets = Path(__file__).resolve().parents[1] / 'assets'
    assets.joinpath('github-stats.json').write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assets.joinpath('github-stats.svg').write_text('\n'.join(parts), encoding='utf-8')
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
