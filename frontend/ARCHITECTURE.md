# 🏗️ Arquitetura do Frontend - Algarve Hack

## Visão Geral

O frontend foi construído com Next.js 16 (App Router), React 19 e Tailwind CSS 4, seguindo as melhores práticas de desenvolvimento moderno.

## Estrutura de Diretórios

```
frontend/
├── app/
│   ├── components/          # Componentes React reutilizáveis
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
│   │   └── index.ts         # Barrel export
│   ├── sections/            # Seções da página
│   │   ├── AboutSection.tsx
│   │   ├── ContactSection.tsx
│   │   ├── HeroSection.tsx
│   │   ├── ServicesSection.tsx
│   │   └── index.ts
│   ├── hooks/               # Custom React Hooks
│   │   ├── useInView.ts
│   │   ├── useMediaQuery.ts
│   │   ├── useScrollPosition.ts
│   │   └── index.ts
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   ├── utils/               # Funções utilitárias
│   │   ├── animations.ts
│   │   └── constants.ts
│   ├── styles/              # Documentação de estilos
│   │   └── README.md
│   ├── globals.css          # Estilos globais
│   ├── layout.tsx           # Layout raiz
│   └── page.tsx             # Página principal
├── public/                  # Assets estáticos
├── ARCHITECTURE.md          # Este arquivo
├── README_FRONTEND.md       # Documentação do frontend
├── package.json
├── tsconfig.json
└── next.config.ts
```

## Princípios de Design

### 1. Componentes Reutilizáveis
- Todos os componentes são modulares e reutilizáveis
- Props tipadas com TypeScript
- Estilos consistentes usando Tailwind CSS

### 2. Separation of Concerns
- **Components**: UI components puros
- **Sections**: Composição de componentes em seções
- **Hooks**: Lógica reutilizável
- **Utils**: Funções auxiliares
- **Types**: Definições de tipos TypeScript

### 3. Performance
- Lazy loading de componentes
- Otimização de imagens com Next.js Image
- Server Components quando possível
- Client Components apenas quando necessário

### 4. Type Safety
- TypeScript em todos os arquivos
- Interfaces bem definidas
- Props tipadas

## Componentes Principais

### Components (`/app/components`)

#### AnimatedButton
Botão com animações e múltiplas variantes.

**Props:**
- `variant`: 'primary' | 'secondary' | 'outline'
- `size`: 'small' | 'medium' | 'large'
- `onClick`: Function
- `disabled`: boolean

#### FeatureCard
Card para exibir funcionalidades.

**Props:**
- `icon`: string
- `title`: string
- `description`: string
- `gradient`: string
- `isActive`: boolean
- `onHover`: (isHovered: boolean) => void

#### NavigationBar
Barra de navegação responsiva com scroll detection.

**Features:**
- Menu mobile
- Scroll-based styling
- Smooth animations

#### Footer
Footer completo com informações e links.

**Features:**
- Links rápidos
- Redes sociais
- Informações de contacto

### Sections (`/app/sections`)

#### HeroSection
Seção hero principal da landing page.

#### AboutSection
Seção sobre a empresa/equipa.

#### ServicesSection
Exibição dos serviços oferecidos.

#### ContactSection
Formulário de contacto e informações.

### Hooks (`/app/hooks`)

#### useScrollPosition
Detecta posição e direção do scroll.

```tsx
const { scrollPosition, isScrollingDown } = useScrollPosition();
```

#### useMediaQuery
Verifica media queries.

```tsx
const isMobile = useIsMobile();
const isDesktop = useIsDesktop();
```

#### useInView
Detecta quando elemento está visível.

```tsx
const { ref, isInView } = useInView({ threshold: 0.5 });
```

## Fluxo de Dados

```
page.tsx (State Management)
    ↓
Sections (Composition)
    ↓
Components (Presentation)
    ↓
Hooks (Logic)
```

## Estilização

### Sistema de Design
- **Cores**: Paleta definida em CSS variables
- **Tipografia**: Inter (primary), Space Grotesk (accent)
- **Espaçamento**: Sistema do Tailwind (4px base)
- **Animações**: Transições suaves (300ms padrão)

### Responsividade
```tsx
// Mobile First
className="text-base md:text-lg lg:text-xl"
className="grid-cols-1 md:grid-cols-2 lg:grid-cols-4"
```

### Temas
- Dark mode por padrão
- Light mode com prefers-color-scheme
- Transições suaves entre temas

## Animações

### CSS Animations
- **fadeInUp**: Entrada de elementos
- **float**: Movimento flutuante
- **pulse-glow**: Efeito de pulsação

### Framer Motion (Opcional)
Preparado para integração com Framer Motion para animações complexas.

## Estado

### Estado Local
- React useState para estado de componente
- React useEffect para side effects

### Estado Global (Futuro)
Preparado para integração com:
- Context API
- Zustand
- Redux Toolkit

## Roteamento

### Next.js App Router
- File-based routing
- Server Components por padrão
- Client Components com "use client"

## Otimizações

### Performance
- Code splitting automático
- Dynamic imports quando necessário
- Image optimization com next/image

### SEO
- Metadata configurável
- Semantic HTML
- Structured data ready

### Acessibilidade
- ARIA labels
- Keyboard navigation
- Screen reader friendly

## Testes (Preparado para)

```bash
# Unit Tests
npm run test

# E2E Tests
npm run test:e2e

# Component Tests
npm run test:component
```

## Deployment

### Build
```bash
npm run build
npm start
```

### Variáveis de Ambiente
```env
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_SITE_URL=
```

## Próximos Passos

1. **Integração com Backend**
   - API routes
   - Data fetching
   - Authentication

2. **Melhorias**
   - Testes unitários
   - E2E testing
   - Performance monitoring

3. **Features**
   - Blog
   - Dashboard
   - Admin panel

## Manutenção

### Atualizações
- Manter dependências atualizadas
- Seguir breaking changes do Next.js
- Atualizar Tailwind CSS

### Code Quality
- ESLint configurado
- Prettier para formatação
- TypeScript strict mode

## Recursos

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript](https://www.typescriptlang.org)

