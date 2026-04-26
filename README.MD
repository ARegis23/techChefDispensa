# Permissões e Funcionalidades de Usuários

## 1. Usuário Administrador

O usuário administrador é o usuário principal da conta.  
O primeiro usuário autenticado no sistema é registrado como administrador da própria conta.

### 1.1 Autenticação

- Pode fazer login no sistema.
- Pode acessar o dashboard após autenticação.
- Pode encerrar a sessão usando logout.

### 1.2 Gerenciamento de usuários

- Pode acessar a página de listagem de usuários.
- Pode visualizar o próprio cadastro em uma seção separada como administrador.
- Pode visualizar todos os usuários vinculados à sua conta.
- Pode adicionar novos usuários membros.
- Pode editar usuários membros vinculados à sua conta.
- Pode editar o próprio cadastro.
- Pode alterar nome, e-mail e senha dos usuários membros.
- Pode alterar o próprio nome, e-mail e senha.
- Pode deletar usuários membros.
- Não pode deletar a si mesmo pela tela de gerenciamento.

### 1.3 Visualização da hierarquia

- O administrador aparece em uma área separada da listagem.
- Os usuários membros aparecem abaixo do administrador.
- A listagem apresenta a relação entre o administrador principal e seus usuários vinculados.

### 1.4 Navegação

- Pode acessar o dashboard.
- Pode acessar a página de usuários.
- Pode acessar a página de configurações.
- Pode acessar as páginas internas protegidas do sistema.
- Pode usar a opção de voltar nas páginas de usuários.

---

## 2. Usuário Membro

O usuário membro é criado pelo administrador e fica vinculado à conta principal.

### 2.1 Autenticação

- Pode fazer login no sistema.
- Pode acessar o dashboard após autenticação.
- Pode encerrar a sessão usando logout.

### 2.2 Gerenciamento de usuários

- Pode acessar a página de listagem de usuários.
- Pode visualizar o administrador principal.
- Pode visualizar os demais usuários membros vinculados à mesma conta.
- Pode editar apenas o próprio cadastro.
- Pode alterar o próprio nome, e-mail e senha.
- Não pode adicionar novos usuários.
- Não pode editar outros usuários membros.
- Não pode editar o administrador.
- Não pode deletar usuários.
- Não pode deletar a si mesmo pela tela atual.

### 2.3 Visualização da hierarquia

- Visualiza o administrador em uma seção separada.
- Visualiza os usuários membros abaixo do administrador.
- Entende sua posição dentro da conta principal.
- Os demais usuários aparecem apenas para visualização.

### 2.4 Navegação

- Pode acessar o dashboard.
- Pode acessar a página de usuários.
- Pode acessar a página de configurações.
- Pode acessar páginas internas protegidas do sistema.
- Pode usar a opção de voltar nas páginas de usuários.

---

## 3. Visitante não autenticado

O visitante é qualquer pessoa que ainda não realizou login no sistema.

### 3.1 Acesso

- Pode acessar a tela de login.
- Pode acessar a página sobre o projeto.
- Não pode acessar o dashboard.
- Não pode acessar a listagem de usuários.
- Não pode acessar a página de configurações.
- Não pode acessar páginas internas protegidas.

### 3.2 Redirecionamento

- Ao tentar acessar uma página interna, é redirecionado para a tela de login.
- Recebe mensagem informando que precisa fazer login para acessar o sistema.

---

# Regras gerais de permissão

## 1. Controle de sessão

- O sistema verifica se existe um usuário salvo na sessão Flask.
- Caso não exista usuário na sessão, o acesso às páginas internas é bloqueado.
- Após login válido, os dados principais do usuário são armazenados na sessão.

## 2. Controle por papel

O sistema trabalha inicialmente com dois papéis:

- `admin`
- `membro`

### Admin

- Gerencia a própria conta.
- Gerencia os membros vinculados.
- Pode adicionar, editar e deletar membros.

### Membro

- Acessa o sistema.
- Visualiza a estrutura de usuários.
- Edita apenas o próprio cadastro.

## 3. Controle por conta principal

- Cada usuário possui um `admin_uid`.
- O `admin_uid` indica a qual conta principal o usuário pertence.
- O administrador possui `admin_uid` igual ao próprio `uid`.
- Membros possuem `admin_uid` igual ao `uid` do administrador que os criou.
- Um usuário não pode editar dados de usuários pertencentes a outra conta.

---

# Rotas relacionadas a usuários

## 1. Login

### Rota

`/login`

### Função

- Exibe a tela de login.
- Permite autenticação do usuário.
- Após login válido, redireciona para o dashboard.

---

## 2. Criar sessão no backend

### Rota

`/auth/session-login`

### Função

- Recebe o token de autenticação do Firebase.
- Valida o token no backend usando Python.
- Cria a sessão Flask do usuário.
- Redireciona para o dashboard.

---

## 3. Logout

### Rota

`/logout`

### Função

- Limpa a sessão do usuário.
- Redireciona para a tela de login.

---

## 4. Listagem de usuários

### Rota

`/menu/usuarios`

### Função

- Lista o administrador principal em uma seção separada.
- Lista os usuários membros abaixo do administrador.
- Exibe botão de adicionar usuário apenas para administradores.
- Permite edição conforme o papel do usuário logado.

---

## 5. Adicionar usuário

### Rota

`/menu/usuarios/adicionar`

### Função

- Permite que o administrador crie um novo usuário membro.
- Cria o usuário no Firebase Authentication.
- Cria o registro do usuário no Firestore.
- Vincula o novo usuário ao administrador principal.
- Bloqueia acesso para usuários membros.

---

## 6. Editar usuário

### Rota

`/menu/usuarios/editar/<uid>`

### Função

- Permite editar nome, e-mail e senha.
- Permite que o administrador edite membros da própria conta.
- Permite que o membro edite apenas o próprio cadastro.
- Bloqueia edição de usuários de outras contas.
- Possui ação de atualizar.
- Possui ação de cancelar.
- Possui ação de deletar quando permitido.

## Admin pode modificar

### Configurações pessoais de acessibilidade
- Tema preferido.
- Tamanho do texto.
- Contraste da interface.
- Redução de animações.
- Densidade da interface.
- Preferência de fonte legível.

### Configurações de usuários
- Acessar gerenciamento de usuários.
- Adicionar usuários membros.
- Editar usuários membros.
- Deletar usuários membros.
- Editar o próprio perfil.

## Membro pode modificar

### Configurações pessoais de acessibilidade
- Tema preferido.
- Tamanho do texto.
- Contraste da interface.
- Redução de animações.
- Densidade da interface.
- Preferência de fonte legível.

### Configurações de usuários
- Visualizar usuários da conta.
- Editar apenas o próprio perfil.
- Não pode adicionar usuários.
- Não pode editar outros usuários.
- Não pode deletar usuários.

## Exportação de dados

O sistema possui uma funcionalidade de exportação dos dados da aplicação.

### Formato

- Os dados são exportados no formato JSON.
- O arquivo JSON é compactado no formato ZIP.

### Dados exportados

- Metadados da exportação.
- Usuários vinculados à conta principal.
- Alimentos cadastrados pelo grupo.

### Permissão

- Apenas o usuário administrador pode exportar todos os dados do grupo.

### Rota

`/menu/configuracoes/exportar-json`


-------------------------------------------------
-------------------------------------------------
-------------------------------------------------
# Testes recomendados

## 1. Testes com usuário administrador

- Fazer login com o usuário principal.
- Confirmar que o usuário aparece como administrador.
- Acessar a listagem de usuários.
- Confirmar que o botão "Adicionar novo usuário" aparece.
- Adicionar um novo usuário membro.
- Confirmar que o novo usuário aparece abaixo do administrador.
- Editar o nome do usuário membro.
- Editar o e-mail do usuário membro.
- Alterar a senha do usuário membro.
- Cancelar uma edição e confirmar que nada foi alterado.
- Deletar um usuário membro.
- Confirmar que o administrador não consegue deletar a si mesmo.

## 2. Testes com usuário membro

- Fazer login com um usuário membro.
- Confirmar que ele acessa o dashboard.
- Acessar a página de usuários.
- Confirmar que o administrador aparece separado.
- Confirmar que os demais membros aparecem abaixo.
- Confirmar que o botão "Adicionar novo usuário" não aparece.
- Tentar editar o próprio cadastro.
- Confirmar que a edição do próprio cadastro funciona.
- Tentar acessar a edição de outro usuário pela URL.
- Confirmar que o sistema bloqueia a ação.
- Confirmar que o membro não consegue deletar usuários.

## 3. Testes sem login

- Acessar `/menu/dashboard` sem estar logado.
- Confirmar redirecionamento para `/login`.
- Acessar `/menu/usuarios` sem estar logado.
- Confirmar redirecionamento para `/login`.
- Acessar `/menu/configuracoes` sem estar logado.
- Confirmar redirecionamento para `/login`.

## 4. Testes de segurança lógica

- Confirmar que um usuário membro não consegue adicionar usuários.
- Confirmar que um usuário membro não consegue editar outro membro.
- Confirmar que um usuário membro não consegue editar o administrador.
- Confirmar que o administrador só edita usuários vinculados ao próprio `admin_uid`.
- Confirmar que usuários de outra conta não podem ser manipulados.
- Confirmar que as permissões são verificadas no backend Python.

---

# Estado atual da implementação

## Já implementado ou planejado nesta etapa

- Login com autenticação Firebase.
- Validação do token no backend Flask.
- Criação de sessão Flask.
- Separação entre administrador e membro.
- Listagem de usuários vinculados à conta principal.
- Edição de usuários.
- Criação de usuários membros pelo administrador.
- Exclusão de usuários membros pelo administrador.
- Proteção de rotas internas.
- Controle de permissões no backend Python.

## Ainda pode ser evoluído futuramente

- Recuperação de senha.
- Confirmação de e-mail.
- Perfil com foto.
- Permissões mais específicas, como visualizador, editor e administrador secundário.
- Histórico de alterações dos usuários.
- Desativação de usuário sem excluir do Firebase Authentication.
- Tela visual mais elaborada com paleta oficial do projeto.