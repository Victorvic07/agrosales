# Design — Frontend Base do AgroSales

**Data:** 2026-07-16  
**Escopo:** Login, autenticação, layout principal, navegação por perfil, responsividade e páginas-base dos módulos.

## 1. Objetivo

Criar o frontend inicial do AgroSales em Angular com Angular Material, fornecendo uma base profissional, responsiva e segura para as próximas telas do sistema.

Esta etapa não implementará ainda as funcionalidades completas de produtos, lotes, clientes, pedidos ou usuários. Ela entregará a estrutura necessária para que esses módulos sejam adicionados posteriormente sem retrabalho.

## 2. Stack

- Angular com componentes standalone
- Angular Material
- Angular Router
- HttpClient
- Reactive Forms
- TypeScript
- SCSS
- Testes unitários do Angular

## 3. Arquitetura

```text
src/app/
├── core/
│   ├── auth/
│   ├── guards/
│   ├── interceptors/
│   ├── models/
│   └── services/
├── layout/
│   ├── app-shell/
│   ├── sidebar/
│   └── topbar/
├── features/
│   ├── login/
│   ├── dashboard/
│   ├── products/
│   ├── product-variations/
│   ├── lots/
│   ├── customers/
│   ├── orders/
│   └── users/
└── shared/
    ├── components/
    └── material/
```

### 3.1 Core

Autenticação, persistência da sessão, guards, interceptor HTTP, modelos compartilhados e tratamento global de erros.

### 3.2 Layout

Menu lateral recolhível, barra superior, área principal de conteúdo, comportamento responsivo, exibição do usuário autenticado e logout.

### 3.3 Features

Cada domínio terá uma página-base própria e carregamento lazy.

### 3.4 Shared

Componentes e recursos reutilizáveis, sem regras específicas de negócio.

## 4. Identidade visual

- verde como cor primária;
- branco como base;
- laranja como cor de destaque;
- tons neutros para fundo, bordas e textos secundários.

A interface deve transmitir modernidade e agronegócio sem aparência excessivamente rústica.

## 5. Tela de login

Tela dividida em duas áreas.

### 5.1 Área visual

- identidade AgroSales;
- mensagem curta sobre gestão agrícola e comercial;
- ilustração ligada ao agronegócio;
- fundo com predominância de verde.

### 5.2 Área do formulário

- e-mail;
- senha;
- mostrar ou ocultar senha;
- “Lembrar de mim”;
- botão de entrada;
- carregamento;
- mensagens de erro.

### 5.3 Responsividade

Em telas pequenas, a área visual será reduzida e o formulário ocupará a maior parte da tela.

## 6. Sessão e autenticação

O `AuthService` será a única fonte de verdade da sessão.

### 6.1 Armazenamento

Com “Lembrar de mim”:

- token e sessão em `localStorage`.

Sem “Lembrar de mim”:

- token e sessão em `sessionStorage`.

Componentes não acessarão diretamente os storages.

### 6.2 Dados mantidos

- `access_token`;
- dados básicos do usuário;
- perfil;
- estado autenticado.

### 6.3 Logout

- limpar `localStorage` e `sessionStorage`;
- limpar o estado interno;
- redirecionar para `/login`.

## 7. Interceptor HTTP

- anexar Bearer token às requisições protegidas;
- não anexar token ao login;
- tratar `401` limpando a sessão e indo para `/login`;
- tratar `403` indo para `/access-denied`;
- preservar mensagens úteis do backend.

## 8. Rotas

```text
/login
/dashboard
/products
/product-variations
/lots
/customers
/orders
/users
/access-denied
```

Haverá rota curinga para 404.

### 8.1 Redirecionamento após login

- sem rota anterior: `/dashboard`;
- com rota anterior válida: voltar para ela.

### 8.2 Lazy loading

As páginas de features serão carregadas sob demanda.

## 9. Controle de acesso

### Administrador

Dashboard, Produtos, Variações, Lotes, Clientes, Pedidos e Usuários.

### Produtor

Dashboard, Produtos, Variações, Lotes, Clientes e Pedidos.

### Vendedor

Dashboard, Produtos, Clientes e Pedidos.

O controle ocorrerá em duas camadas:

- esconder itens sem permissão;
- bloquear acesso direto por URL e redirecionar para `/access-denied`.

## 10. Layout interno

### 10.1 Menu lateral

- recolhível no desktop;
- sobreposto no celular;
- logo AgroSales;
- itens filtrados por perfil;
- item ativo destacado;
- botão de sair.

### 10.2 Barra superior

- título da página;
- nome do usuário;
- perfil;
- botão para abrir ou recolher menu;
- ação de logout.

### 10.3 Conteúdo

Cada página-base terá título, breadcrumb, área de conteúdo e mensagem temporária do módulo.

## 11. Páginas auxiliares

### 11.1 Acesso negado

Página 403 com mensagem clara e botão para voltar ao Dashboard.

### 11.2 Página não encontrada

Página 404 com mensagem clara e botão para voltar ao Dashboard ou Login.

## 12. Tratamento de erros

- credenciais inválidas;
- usuário inativo;
- token expirado;
- API indisponível;
- erro de validação;
- acesso sem permissão.

## 13. Testes

- login bem-sucedido;
- credenciais inválidas;
- persistência com e sem “Lembrar de mim”;
- interceptor adicionando token;
- logout limpando sessão;
- guard de autenticação;
- guard de perfil;
- menu por permissão;
- retorno à rota anterior;
- comportamento básico do layout responsivo.

## 14. Critérios de conclusão

- login real funcionando;
- sessão persistindo conforme a opção escolhida;
- rotas protegidas;
- menu por perfil;
- logout funcionando;
- páginas 403 e 404;
- layout responsivo;
- testes principais passando;
- páginas-base acessíveis conforme permissão.

## 15. Fora do escopo

- dashboard com dados reais;
- CRUD completo dos módulos;
- relatórios;
- gráficos;
- deploy de produção.
