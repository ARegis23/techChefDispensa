# 🍳 TechChef Despensa

Sistema web para gestão inteligente de alimentos, usuários e dados nutricionais, com integração a APIs externas e suporte a acessibilidade.

## 📌 Objetivo

O **TechChef Despensa** foi desenvolvido com o objetivo de auxiliar no controle de alimentos e informações nutricionais dentro de um ambiente familiar ou colaborativo.

A aplicação permite:

> Cadastro e gerenciamento de alimentos
> Importação de dados via API externa
> Controle de usuários por grupo
> Exportação e importação de dados
> Personalização de acessibilidade

## ⚙️ Funcionalidades
    # 👤 Autenticação
        Login via Firebase
        Sessão protegida
        Logout

    # 👥 Usuários
        Admin e membros
        CRUD completo de usuários
        Controle por grupo (admin_uid)
        Permissões diferenciadas:
        Admin gerencia todos
        Membros editam apenas seus dados
    # 🍎 Alimentos
        Cadastro manual
        Integração com Open Food Facts via barcode
        Edição e exclusão
        Tabela completa com dados nutricionais

    # 🔄 Importações 
        Importação por barcode
        Busca automática na API
        Edição manual dos dados
        Status:
            importado
            não encontrado
            revisado
            aprovado
        Aprovação envia para coleção de alimentos
        Exclusão de registros

    # 📥 Importação de Arquivos (UI explícita)
        Upload de arquivo JSON
        Processamento dos dados
        Feedback visual:
            Sucesso
            Erros
        Quantidade processada

    # 📤 Exportação de Dados
        Exporta:
            Usuários
            Alimentos
        Formato:
            JSON compactado em ZIP

     # 🎨 Acessibilidade
        Tema:
            Claro
            Escuro
            Sistema
        Tamanho de fonte
        Contraste
        Redução de animações
        Densidade de interface
        Fonte legível

## ⚠️ Validações Implementadas
    Campos obrigatórios
    Validação de tipos numéricos
    Tratamento de erros com feedback ao usuário
    Proteção de rotas com login_required
    Controle de permissões por tipo de usuário

## 👨‍💻 Desenvolvedores
    Alisson Regis Rodrigues dos Santos
    Daniel Ferreira dos Santos

## 📄 Licença
    Este projeto é acadêmico e sem fins comerciais.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python (Flask)
- **Banco de dados:** Firebase Firestore
- **Autenticação:** Firebase Authentication
- **Frontend:** HTML + CSS + Jinja2
- **API externa:** Open Food Facts
- **Outros:**
  - JSON
  - ZIP (exportação de dados)


🚧 Melhorias futuras:

    Dashboard com métricas
    Filtros avançados de alimentos
    Upload de imagens de produtos
    Histórico de alterações