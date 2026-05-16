# TechChef Despensa — Documentação Técnica

> Sistema web de gestão de despensa com controle de usuários, alimentos e importações via API externa.

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Stack Tecnológica](#2-stack-tecnológica)
3. [Arquitetura e Estrutura](#3-arquitetura-e-estrutura)
4. [Autenticação e Sessão](#4-autenticação-e-sessão)
5. [Modelo de Dados](#5-modelo-de-dados)
6. [Papéis e Permissões](#6-papéis-e-permissões)
7. [Rotas da Aplicação](#7-rotas-da-aplicação)
8. [Módulos e Serviços](#8-módulos-e-serviços)
9. [Integração com Open Food Facts](#9-integração-com-open-food-facts)
10. [Exportação de Dados](#10-exportação-de-dados)
11. [Acessibilidade e Configurações](#11-acessibilidade-e-configurações)
12. [Status do Sistema](#12-status-do-sistema)
13. [Dependências](#13-dependências)

---

## 1. Visão Geral

O **TechChef Despensa** é uma aplicação web multi-tenant para gestão de despensas domésticas ou corporativas. Permite que grupos de usuários cadastrem, importem e gerenciem alimentos de forma colaborativa, com controle granular de permissões por papel (administrador e membro).

**Principais funcionalidades:**

- Cadastro e gestão de alimentos (manual e via código de barras)
- Importação de dados nutricionais pela API Open Food Facts
- Controle de acesso multi-tenant por `admin_uid`
- Exportação de dados em JSON compactado (ZIP)
- Configurações de acessibilidade por usuário

---

## 2. Stack Tecnológica

| Camada                | Tecnologia                 |
|-----------------------|----------------------------|
| Backend               | Python 3.10+ / Flask 3.1.3 |
| Banco de dados        | Firebase Firestore         |
| Autenticação          | Firebase Authentication    |
| Frontend              | HTML / CSS / JavaScript    |
| API externa           | Open Food Facts v2         |
| Variáveis de ambiente | python-dotenv 1.0.1        |

---

## 3. Arquitetura e Estrutura

A aplicação segue uma arquitetura em camadas com separação entre rotas, serviços e configuração.

```
techChefDispensa/
├── app.py                        # Ponto de entrada da aplicação
├── requirements.txt              # Dependências Python
├── .env                          # Variáveis de ambiente (não versionado)
│
├── config/
│   └── firebase_config.py        # Inicialização do Firebase
│
├── routes/
│   ├── auth_routes.py            # Login, logout, sessão
│   ├── usuario_routes.py         # CRUD de usuários
│   ├── alimento_routes.py        # CRUD de alimentos
│   ├── importacao_routes.py      # CRUD de importações
│   └── configuracao_routes.py    # Exportação e acessibilidade
│
├── services/
│   ├── usuario_service.py
│   ├── alimento_service.py
│   ├── importacao_service.py
│   └── open_food_facts_service.py
│
└── templates/                    # HTML (Jinja2)
```

---

## 4. Autenticação e Sessão

O sistema utiliza **Firebase Authentication** para validação de identidade e **sessão Flask** para controle de acesso às rotas.

### Fluxo de login

```
Cliente → POST /auth/session-login (token Firebase)
       → Backend valida token via firebase-admin
       → Cria session["usuario"]
       → Redireciona para /dashboard
```

### Estrutura da sessão

```python
session["usuario"] = {
    "uid": "...",
    "nome": "...",
    "email": "...",
    "papel": "admin" | "membro",
    "admin_uid": "..."   # chave do grupo/conta
}
```

### Proteção de rotas

Todas as rotas internas utilizam o decorator `@login_required`, que verifica a presença de `session["usuario"]`. Sem sessão válida, o usuário é redirecionado para `/login` com mensagem de aviso.

---

## 5. Modelo de Dados

O Firestore organiza os dados em três coleções principais.

### 5.1 Usuários

```
usuarios/{uid}
├── uid
├── nome
├── email
├── papel              # "admin" | "membro"
├── admin_uid          # uid do administrador do grupo
├── criado_em
└── atualizado_em
```

### 5.2 Alimentos

```
contas/{admin_uid}/alimentos/{barcode}
├── barcode
├── nome
├── marca
├── categoria
├── peso
├── alergenos
├── kcal
├── carboidratos
├── proteinas
├── fibras
├── sodio
├── gorduras_totais
├── gorduras_saturadas
├── gorduras_trans
├── acucares_totais
├── acucares_adicionados
├── origem_dados       # "api" | "manual"
├── criado_por
├── criado_por_nome
├── criado_em
└── atualizado_em
```

### 5.3 Importações

```
contas/{admin_uid}/importacoes/{importacao_id}
├── barcode
├── [campos nutricionais — mesma estrutura de alimentos]
├── origem             # "Open Food Facts"
├── origem_dados       # "api" | "manual"
├── url_consulta
├── status             # ver estados abaixo
├── observacao
├── admin_uid
├── criado_por
├── criado_por_nome
├── atualizado_por
├── atualizado_por_nome
├── criado_em
└── atualizado_em
```

**Ciclo de vida do status de importação:**

```
importado ──────────────────────────────► aprovado
    │                                        ▲
    ▼                                        │
nao_encontrado ──► revisado ────────────────┘
                      │
                      ▼
             enviado_para_alimentos
```

---

## 6. Papéis e Permissões

### 6.1 Administrador (`papel: "admin"`)

O administrador é o proprietário da conta. Seu `admin_uid` é igual ao próprio `uid`.

| Módulo        | Permissões                                                                                  |
|---------------|---------------------------------------------------------------------------------------------|
| Autenticação  | Login, logout, dashboard                                                                    |
| Usuários      | Visualizar todos, adicionar membros, editar membros, editar próprio perfil, deletar membros |
| Alimentos     | Visualizar, adicionar, editar, deletar, sobrescrever por barcode                            |
| Importações   | Importar, visualizar, editar, deletar, aprovar, enviar para alimentos                       |
| Exportação    | Exportar JSON + ZIP completo do grupo                                                       |
| Configurações | Todas as opções de acessibilidade                                                           |

> O administrador **não pode deletar a si mesmo**.

### 6.2 Membro (`papel: "membro"`)

O membro compartilha o mesmo `admin_uid` do administrador do seu grupo.

| Módulo         | Permissões                                                        |
|----------------|-------------------------------------------------------------------|
| Autenticação   | Login, logout, dashboard                                          |
| Usuários       | Visualizar admin e outros membros, editar apenas o próprio perfil |
| Alimentos      | Visualizar, adicionar, editar                                     |
| Importações    | Importar por barcode, visualizar, editar                          |
| Exportação     | Sem acesso                                                        |
| Configurações  | Todas as opções de acessibilidade                                 |

### 6.3 Visitante (não autenticado)

Acesso restrito às rotas públicas `/login` e `/sobre`. Qualquer tentativa de acessar área protegida resulta em redirecionamento para `/login`.

### 6.4 Isolamento multi-tenant

Cada operação no banco verifica o `admin_uid` do usuário logado. Usuários de grupos diferentes não conseguem acessar ou modificar dados uns dos outros, mesmo que estejam autenticados.

---

## 7. Rotas da Aplicação

### Autenticação

| Método | Rota                  | Descrição                              |
|--------|-----------------------|----------------------------------------|
| GET    | `/login`              | Tela de login                          |
| POST   | `/auth/session-login` | Cria sessão a partir do token Firebase |
| GET    | `/logout`             | Encerra a sessão                       |

### Usuários

| Método   | Rota                          | Descrição            | Papel mínimo           |
|----------|-------------------------------|----------------------|------------------------|
| GET      | `/menu/usuarios`              | Listagem de usuários | membro                 |
| GET/POST | `/menu/usuarios/adicionar`    | Criar membro         | admin                  |
| GET/POST | `/menu/usuarios/editar/<uid>` | Editar usuário       | admin / próprio perfil |

### Alimentos

| Método   | Rota                               | Descrição             | Papel mínimo |
|----------|------------------------------------|-----------------------|--------------|
| GET      | `/menu/alimentos`                  | Listagem de alimentos | membro       |
| GET/POST | `/menu/alimentos/adicionar`        | Criar alimento        | membro       |
| GET/POST | `/menu/alimentos/editar/<barcode>` | Editar alimento       | membro       |

### Importações

| Método   | Rota                                           | Descrição               | Papel mínimo |
|----------|------------------------------------------------|-------------------------|--------------|
| GET      | `/menu/importacoes`                            | Listagem de importações | membro       |
| GET/POST | `/menu/importacoes/adicionar`                  | Importar por barcode    | membro       |
| GET/POST | `/menu/importacoes/editar/<id>`                | Editar importação       | membro       |
| POST     | `/menu/importacoes/deletar/<id>`               | Deletar importação      | admin        |
| POST     | `/menu/importacoes/aprovar/<id>`               | Aprovar → vira alimento | admin        |
| POST     | `/menu/importacoes/enviar-para-alimentos/<id>` | Marcar como enviado     | admin        |

### Configurações

| Método   | Rota                                | Descrição                      | Papel mínimo |
|----------|-------------------------------------|--------------------------------|--------------|
| GET/POST | `/menu/configuracoes`               | Preferências de acessibilidade | membro       |
| GET      | `/menu/configuracoes/exportar-json` | Exportar dados do grupo        | admin        |

---

## 8. Módulos e Serviços

### `importacao_service.py`

Responsável por todo o ciclo de vida das importações.

| Função                                                  | Descrição                                      |
|---------------------------------------------------------|------------------------------------------------|
| `importar_por_barcode(usuario, barcode)`                | Consulta Open Food Facts e salva no Firestore  |
| `listar_importacoes(usuario)`                           | Lista importações do grupo ordenadas por data  |
| `buscar_importacao(usuario, importacao_id)`             | Busca importação pelo ID                       |
| `montar_dados_importacao_formulario(form, usuario)`     | Prepara dados do formulário para salvar        |
| `atualizar_importacao(usuario, id, dados)`              | Atualiza importação existente                  |
| `deletar_importacao(usuario, importacao_id)`            | Remove importação do Firestore                 |
| `aprovar_importacao(usuario, importacao_id)`            | Cria alimento e marca importação como aprovada |
| `marcar_importacao_enviada_para_alimentos(usuario, id)` | Atualiza status sem criar alimento             |

### `usuario_service.py`

Gerencia operações de usuários com isolamento por `admin_uid`.

### `alimento_service.py`

Gerencia o CRUD de alimentos. Chamado por `aprovar_importacao` para promover uma importação.

### `open_food_facts_service.py`

Encapsula a chamada à API externa e normaliza os campos nutricionais retornados.

---

## 9. Integração com Open Food Facts

A busca de alimentos por código de barras utiliza a API pública do Open Food Facts v2.

**Endpoint consultado:**
```
GET https://world.openfoodfacts.org/api/v2/product/{barcode}
```

**Comportamento:**

- Se o produto **é encontrado**: campos nutricionais são preenchidos automaticamente e o status da importação é definido como `importado`.
- Se o produto **não é encontrado**: um registro vazio é criado com status `nao_encontrado` para preenchimento manual posterior.

**Campos mapeados:**

`nome`, `marca`, `categoria`, `peso`, `alergenos`, `kcal`, `carboidratos`, `proteinas`, `fibras`, `sodio`, `gorduras_totais`, `gorduras_saturadas`, `gorduras_trans`, `acucares_totais`, `acucares_adicionados`

---

## 10. Exportação de Dados

Disponível apenas para administradores via `/menu/configuracoes/exportar-json`.

**O que é exportado:**
- Todos os usuários do grupo
- Todos os alimentos do grupo

**Formato de saída:** arquivo `.json` compactado em `.zip`

---

## 11. Acessibilidade e Configurações

Todos os usuários (admin e membro) podem personalizar a interface com as seguintes opções:

| Configuração           | Opções                     |
|------------------------|----------------------------|
| Tema                   | Claro, Escuro, Sistema     |
| Tamanho do texto       | Pequeno, Normal, Grande    |
| Contraste              | Normal, Alto               |
| Animações              | Ativadas, Reduzidas        |
| Densidade da interface | Compacta, Normal, Espaçada |
| Fonte legível          | Padrão, Dislexia-friendly  |

---

## 12. Status do Sistema

| Funcionalidade                       | Status       |
|--------------------------------------|--------------|
| Autenticação Firebase                | Implementado |
| Controle por papel (admin/membro)    | Implementado |
| Multi-tenant por admin_uid           | Implementado |
| CRUD de usuários                     | Implementado |
| CRUD de alimentos                    | Implementado |
| CRUD de importações                  | Implementado |
| Integração Open Food Facts           | Implementado |
| Aprovação de importação → alimento   | Implementado |
| Exportação JSON + ZIP                | Implementado |
| Upload de JSON em lote               | Implementado |
| Configurações de acessibilidade      | Implementado |
| Recuperação/confirmação de e-mail    | Planejado    |
| Foto de perfil                       | Planejado    |
| Papéis granulares adicionais         | Planejado    |
| Histórico de alterações              | Planejado    |
| Desativação de usuário (sem excluir) | Planejado    |

---

## 13. Dependências

```txt
# Web framework
Flask==3.1.3

# Firebase (Authentication + Firestore)
firebase-admin==6.6.0

# Variáveis de ambiente
python-dotenv==1.0.1
```

Para instalar:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

*Documentação gerada em maio de 2026 — TechChef Despensa*
