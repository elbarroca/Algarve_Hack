# 🚀 Algarve Hack - Frontend

Frontend moderno e responsivo construído com Next.js 16, React 19 e Tailwind CSS 4.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-16.0.1-black)
![React](https://img.shields.io/badge/React-19.2.0-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue)

## ✨ Características

- 🎨 **Design Moderno**: Interface limpa com gradientes e animações suaves
- 📱 **Responsivo**: Funciona perfeitamente em mobile, tablet e desktop
- ⚡ **Performance**: Otimizado com Next.js App Router e Server Components
- 🎭 **Animações**: Transições elegantes e efeitos interativos
- 🧩 **Modular**: Componentes reutilizáveis e bem organizados
- 🎯 **TypeScript**: Type safety em todo o projeto
- 🌙 **Temas**: Suporte para dark/light mode
- ♿ **Acessível**: Segue as melhores práticas de acessibilidade

## 🏗️ Estrutura do Projeto

```
frontend/
├── app/
│   ├── components/         # 10+ componentes reutilizáveis
│   │   ├── AnimatedButton.tsx
│   │   ├── BackgroundEffects.tsx
│   │   ├── ContactForm.tsx
│   │   ├── FeatureCard.tsx
│   │   ├── Footer.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── NavigationBar.tsx
│   │   ├── ProjectCard.tsx
│   │   ├── StatCard.tsx
│   │   └── TestimonialCard.tsx
│   ├── sections/           # 4 seções principais
│   │   ├── AboutSection.tsx
│   │   ├── ContactSection.tsx
│   │   ├── HeroSection.tsx
│   │   └── ServicesSection.tsx
│   ├── hooks/              # Custom React Hooks
│   │   ├── useInView.ts
│   │   ├── useMediaQuery.ts
│   │   └── useScrollPosition.ts
│   ├── types/              # TypeScript types
│   ├── utils/              # Funções utilitárias
│   │   ├── animations.ts
│   │   └── constants.ts
│   ├── globals.css         # Estilos globais
│   ├── layout.tsx          # Layout raiz
│   └── page.tsx            # Página principal
├── public/                 # Assets estáticos
└── package.json
```

## 🚀 Como Executar

### Pré-requisitos

- Node.js 18+ instalado
- npm, yarn, pnpm ou bun

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

4. Abra [http://localhost:3000](http://localhost:3000) no seu navegador

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

### UI Components

- **AnimatedButton**: Botões com animações (primary, secondary, outline)
- **FeatureCard**: Cards para exibir funcionalidades
- **NavigationBar**: Navegação responsiva com scroll detection
- **ContactForm**: Formulário com validação
- **Footer**: Footer completo com links e informações
- **LoadingSpinner**: Indicador de carregamento
- **ProjectCard**: Cards para projetos
- **StatCard**: Cards de estatísticas
- **TestimonialCard**: Cards de depoimentos
- **BackgroundEffects**: Efeitos de fundo animados

### Sections

- **HeroSection**: Hero principal da landing page
- **AboutSection**: Informações sobre a empresa
- **ServicesSection**: Serviços oferecidos
- **ContactSection**: Formulário de contacto

### Custom Hooks

- **useScrollPosition**: Detecta posição e direção do scroll
- **useMediaQuery**: Verifica media queries (mobile, tablet, desktop)
- **useInView**: Intersection Observer para animações

## 🎯 Tecnologias

- **[Next.js 16](https://nextjs.org/)**: Framework React
- **[React 19](https://react.dev/)**: Biblioteca UI
- **[TypeScript](https://www.typescriptlang.org/)**: Type safety
- **[Tailwind CSS 4](https://tailwindcss.com/)**: Estilização
- **[Google Fonts](https://fonts.google.com/)**: Inter & Space Grotesk

## 🎨 Paleta de Cores

```css
Primary Blue:    #3b82f6
Primary Purple:  #8b5cf6
Accent Cyan:     #06b6d4
Dark BG:         #0f172a
Light BG:        #ffffff
```

## 📱 Responsividade

Breakpoints:
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## ⚡ Performance

- Server Components por padrão
- Code splitting automático
- Otimização de fontes
- Lazy loading quando apropriado
- CSS-in-JS com Tailwind

## ♿ Acessibilidade

- ARIA labels em botões
- Navegação por teclado
- Contraste adequado (WCAG AA)
- Elementos semânticos
- Focus states visíveis

## 🌟 Destaques

✅ **Código 100% Original**: Completamente reescrito do zero
✅ **Type-Safe**: TypeScript em todo o código
✅ **Modular**: Arquitetura limpa e reutilizável
✅ **Documentado**: Código bem comentado
✅ **Sem Erros**: Sem erros de linting ou TypeScript
✅ **Performance**: Otimizado para velocidade
✅ **Acessível**: Segue melhores práticas

## 📚 Documentação

Consulte os arquivos de documentação:

- `app/styles/README.md`: Guia de estilos completo
- Código bem comentado em todos os componentes
- Props tipadas com TypeScript

## 🔧 Configuração

### Fonts
Configuradas em `app/layout.tsx`:
- Inter (primary font)
- Space Grotesk (accent font)

### Metadata
```typescript
title: "Algarve Hack - Inovação & Tecnologia"
description: "Plataforma de inovação e desenvolvimento tecnológico no Algarve"
```

## 🚀 Deploy

### Vercel (Recomendado)
```bash
npm run build
# Deploy com Vercel CLI ou GitHub integration
```

### Build Manual
```bash
npm run build
npm start
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE na raiz do repositório.

## 👥 Equipa

Desenvolvido com ❤️ pela equipa Algarve Hack

## 📧 Contacto

- **Email**: info@algarvehack.pt
- **Website**: [algarvehack.pt](https://algarvehack.pt)
- **GitHub**: [@algarvehack](https://github.com/algarvehack)

---

**Made with ❤️ in Algarve, Portugal** 🇵🇹
