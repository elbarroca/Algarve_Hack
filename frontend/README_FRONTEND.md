# 🚀 Algarve Hack - Frontend

Frontend moderno e responsivo construído com Next.js 16, React 19 e Tailwind CSS 4.

## ✨ Características

- 🎨 Design moderno e limpo com gradientes e animações
- 📱 Totalmente responsivo (mobile, tablet, desktop)
- ⚡ Performance otimizada com Next.js App Router
- 🎭 Animações suaves e transições elegantes
- 🌙 Suporte para modo escuro/claro
- 🧩 Componentes modulares e reutilizáveis
- 🎯 TypeScript para type safety
- 🎨 Tailwind CSS para estilização rápida

## 🏗️ Estrutura do Projeto

```
frontend/
├── app/
│   ├── components/         # Componentes React reutilizáveis
│   │   ├── AnimatedButton.tsx
│   │   ├── BackgroundEffects.tsx
│   │   ├── ContactForm.tsx
│   │   ├── FeatureCard.tsx
│   │   ├── Footer.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── NavigationBar.tsx
│   │   ├── ProjectCard.tsx
│   │   ├── StatCard.tsx
│   │   ├── TestimonialCard.tsx
│   │   └── index.ts
│   ├── hooks/              # Custom React Hooks
│   │   ├── useInView.ts
│   │   ├── useMediaQuery.ts
│   │   ├── useScrollPosition.ts
│   │   └── index.ts
│   ├── utils/              # Funções utilitárias
│   │   ├── animations.ts
│   │   └── constants.ts
│   ├── globals.css         # Estilos globais e variáveis CSS
│   ├── layout.tsx          # Layout principal
│   └── page.tsx            # Página principal
├── public/                 # Recursos estáticos
├── package.json
└── tsconfig.json
```

## 🚀 Como Executar

### Pré-requisitos

- Node.js 18+ instalado
- npm ou yarn

### Instalação

1. Navegue até a pasta frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Execute o servidor de desenvolvimento:
```bash
npm run dev
```

4. Abra o navegador em [http://localhost:3000](http://localhost:3000)

## 📦 Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Executar versão de produção
npm start

# Linting
npm run lint
```

## 🎨 Componentes Principais

### AnimatedButton
Botão com animações e variantes de estilo (primary, secondary, outline).

### FeatureCard
Card para exibir funcionalidades com ícones, títulos e descrições.

### NavigationBar
Barra de navegação responsiva com menu mobile.

### ContactForm
Formulário de contacto com validação e feedback visual.

### BackgroundEffects
Efeitos de fundo animados (orbs gradientes, grid pattern).

### Footer
Footer completo com informações, links e redes sociais.

## 🎯 Hooks Customizados

- **useScrollPosition**: Detecta posição e direção do scroll
- **useMediaQuery**: Verifica media queries para responsividade
- **useInView**: Detecta quando um elemento está visível no viewport

## 🎨 Paleta de Cores

```css
Primary: #3b82f6 (Azul)
Secondary: #8b5cf6 (Roxo)
Accent: #06b6d4 (Ciano)
Background Dark: #0f172a (Slate 900)
Background Light: #ffffff (Branco)
```

## 🌟 Animações

O projeto inclui várias animações:
- **fadeInUp**: Elementos aparecem de baixo para cima
- **float**: Movimento flutuante contínuo
- **pulse-glow**: Efeito de pulsação
- **Hover effects**: Transições suaves ao passar o mouse

## 📱 Responsividade

Breakpoints:
- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

## 🔧 Tecnologias

- **Next.js 16**: Framework React
- **React 19**: Biblioteca UI
- **TypeScript**: Type safety
- **Tailwind CSS 4**: Estilização
- **Google Fonts**: Inter & Space Grotesk

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.

## 👥 Equipa

Desenvolvido com ❤️ pela equipa Algarve Hack

