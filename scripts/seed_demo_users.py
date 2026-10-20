#!/usr/bin/env python3
# scripts/seed_demo_users.py
"""Cria os usuários fictícios de demonstração da Change 06 no backend Xano.

O que faz (apenas em ambiente de desenvolvimento):
    1. Lê ``XANO_BASE_URL`` do arquivo ``.env`` (ou do ambiente).
    2. Verifica se o backend está publicado (grupo Authentication respondendo).
    3. Chama ``POST auth/signup`` do próprio backend — o Xano faz o hash da
       senha (bcrypt) e a senha em claro nunca é armazenada nem logada.
    4. Atribui o ``role`` correto via ``POST admin/user_role`` exigindo um
       usuário admin pré-existente (parâmetro ``--admin-email``).

Uso:
    python scripts/seed_demo_users.py
    python scripts/seed_demo_users.py --admin-email admin@smartvision.com

Segurança (AGENTS.md §9):
    - Nenhuma credencial real ou segredo de produção é embutido aqui.
    - As senhas fictícias ficam apenas no script (ambiente de desenvolvimento)
      e no card da tela de login; nunca em logs do backend.
    - O script falha com mensagem clara se o backend não estiver publicado —
      não simula nada.

Grupos Xano: a URL pública de cada grupo é {origem}/api:{canonical}/... —
canonics tirados de ``xano/api/<grupo>/<grupo>.xs``.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

# Usuários fictícios de demonstração — AMBIENTE DE DESENVOLVIMENTO.
DEMO_USERS = [
    {"name": "Gerente Demo", "email": "gerente@smartvision.com", "password": "Senha123!", "role": "Gestor"},
    {"name": "Supervisor Demo", "email": "supervisor@smartvision.com", "password": "Senha123!", "role": "Supervisor"},
    {"name": "Vendedor Demo", "email": "vendedor@smartvision.com", "password": "Senha123!", "role": "Vendedor"},
]

ROLES_VALIDOS = ["admin", "member", "Gestor", "Supervisor", "Estoquista", "Vendedor", "Técnico"]  # enum de xano/table/user.xs

# Canonics dos grupos de API (xano/api/<grupo>/<grupo>.xs → campo canonical).
AUTH_GROUP_CANONICAL = "RRY0Pj3A"        # api/authentication
MEMBERS_GROUP_CANONICAL = "NCs6_YME"     # api/members_accounts


def _load_env_file(path: str) -> None:
    """Carrega variáveis de um arquivo .env simples (sem dependências externas)."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def _group_base(base_url: str, canonical: str) -> str:
    """Base de um grupo Xano: {origem}/api:{canonical} (funciona com qualquer
    XANO_BASE_URL, mesmo já contendo o canonical de outro grupo)."""
    origin = "/".join(base_url.rstrip("/").split("/")[:3])
    return f"{origin}/api:{canonical}"


def _request(base: str, path: str, payload: dict | None = None,
             token: str | None = None, method: str = "POST") -> tuple[int, dict]:
    """HTTP JSON (stdlib); retorna (status_code, corpo parseado ou dict de erro)."""
    url = f"{base.rstrip('/')}/{path.lstrip('/')}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body) if body else {}
            except json.JSONDecodeError:
                return resp.status, {"message": body[:300]}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"message": body[:300]}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return 0, {"message": f"Falha de comunicação com o backend: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed de usuários de demonstração (dev).")
    parser.add_argument(
        "--admin-email",
        default=None,
        help="E-mail de um usuário já existente com role 'admin', usado para "
             "atribuir os roles dos usuários de demonstração.",
    )
    parser.add_argument(
        "--admin-password",
        default=None,
        help="Senha do usuário admin (ou variável ADMIN_PASSWORD no ambiente).",
    )
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _load_env_file(os.path.join(project_root, ".env"))

    # Valida roles contra o enum de xano/table/user.xs antes de qualquer chamada.
    for user in DEMO_USERS:
        if user["role"] not in ROLES_VALIDOS:
            print(
                f"ERRO: role '{user['role']}' não existe no enum da tabela user "
                f"(válidos: {', '.join(ROLES_VALIDOS)}).",
                file=sys.stderr,
            )
            return 1

    base_url = os.getenv("XANO_BASE_URL", "").strip()
    if not base_url:
        print("ERRO: XANO_BASE_URL não configurado. Defina no arquivo .env.", file=sys.stderr)
        return 1

    auth_base = _group_base(base_url, AUTH_GROUP_CANONICAL)
    members_base = _group_base(base_url, MEMBERS_GROUP_CANONICAL)

    # 1) Verificar se o backend está publicado (probe: senha errada → 401/403).
    status, body = _request(auth_base, "auth/login", {
        "email": "__seed_probe__@invalid.local",
        "password": "Probe1234",
    })
    if status == 0 or "Invalid api query" in str(body):
        print(
            "ERRO: os endpoints de autenticação não estão publicados neste "
            f"workspace Xano ({auth_base}).\n"
            "Publique o grupo Authentication (xano/api/authentication/*.xs) com "
            "o XanoScript push e execute este script novamente.",
            file=sys.stderr,
        )
        return 2
    print(f"Backend acessível ({auth_base}) — probe de login: HTTP {status}")

    # 2) Criar usuários de demonstração via signup (hash feito pelo Xano).
    for user in DEMO_USERS:
        status, body = _request(auth_base, "auth/signup", {
            "name": user["name"],
            "email": user["email"],
            "password": user["password"],
        })
        if status in (200, 201) and body.get("authToken"):
            print(f"  ✔ {user['email']}: criado (id={body.get('user_id')})")
        elif "already" in str(body).lower():
            print(f"  • {user['email']}: já existe — será reaproveitado (senha não é alterada por este script)")
        else:
            print(f"  ✖ {user['email']}: falha HTTP {status} — {body}", file=sys.stderr)
            return 3

    # 3) Atribuir roles (exige usuário admin existente).
    admin_email = args.admin_email
    admin_password = args.admin_password or os.getenv("ADMIN_PASSWORD")
    if not admin_email:
        print(
            "AVISO: roles não atribuídos. Rode novamente com "
            "--admin-email <admin existente> para definir Gestor/Supervisor/Vendedor.",
            file=sys.stderr,
        )
        return 0
    if not admin_password:
        print("ERRO: informe a senha do admin via --admin-password ou ADMIN_PASSWORD.", file=sys.stderr)
        return 1

    status, body = _request(auth_base, "auth/login", {"email": admin_email, "password": admin_password})
    if not (status in (200, 201) and body.get("authToken")):
        print(f"ERRO: login do admin falhou (HTTP {status}) — {body}", file=sys.stderr)
        return 4
    admin_token = body["authToken"]

    for user in DEMO_USERS:
        # Descobre o id do usuário logando com as próprias credenciais demo.
        status, body = _request(auth_base, "auth/login", {
            "email": user["email"],
            "password": user["password"],
        })
        target_id = None
        if status in (200, 201) and body.get("authToken"):
            me_status, me = _request(auth_base, "auth/me", token=body["authToken"], method="GET")
            if me_status in (200, 201):
                target_id = me.get("id")
                if me.get("role") == user["role"]:
                    print(f"  • {user['email']}: role já é '{user['role']}'")
                    continue
        if target_id is None:
            print(f"  ✖ {user['email']}: não foi possível obter o id para atribuir role", file=sys.stderr)
            continue
        status, body = _request(members_base, "admin/user_role", {
            "user_id": target_id,
            "new_role": user["role"],
        }, token=admin_token)
        if status in (200, 201):
            print(f"  ✔ {user['email']}: role '{user['role']}' aplicado")
        else:
            print(f"  ✖ {user['email']}: falha ao aplicar role — HTTP {status} {body}", file=sys.stderr)

    print("Seed concluído.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
