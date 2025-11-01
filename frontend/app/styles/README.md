# Guia de Estilos - Algarve Hack

## Paleta de Cores

### Cores Primárias
- **Azul Primário**: `#3b82f6` (Blue-500)
- **Azul Escuro**: `#2563eb` (Blue-600)
- **Roxo**: `#8b5cf6` (Purple-500)
- **Ciano**: `#06b6d4` (Cyan-500)

### Cores de Fundo
- **Fundo Escuro Principal**: `#0f172a` (Slate-900)
- **Fundo Escuro Secundário**: `#1e293b` (Slate-800)
- **Fundo Claro**: `#ffffff` (White)
- **Fundo Claro Secundário**: `#f8fafc` (Slate-50)

### Cores de Texto
- **Texto Principal Claro**: `#f1f5f9` (Slate-100)
- **Texto Secundário**: `#cbd5e1` (Slate-300)
- **Texto Muted**: `#94a3b8` (Slate-400)
- **Texto Principal Escuro**: `#0f172a` (Slate-900)

### Cores de Estado
- **Sucesso**: `#10b981` (Green-500)
- **Erro**: `#ef4444` (Red-500)
- **Aviso**: `#f59e0b` (Amber-500)
- **Info**: `#3b82f6` (Blue-500)

## Tipografia

### Fontes
- **Fonte Principal**: Inter (Google Fonts)
  - Weights: 300, 400, 500, 600, 700
- **Fonte de Destaque**: Space Grotesk (Google Fonts)
  - Weights: 400, 500, 600, 700

### Tamanhos de Texto
- **Display**: `text-8xl` (96px)
- **Heading 1**: `text-6xl` (60px)
- **Heading 2**: `text-5xl` (48px)
- **Heading 3**: `text-3xl` (30px)
- **Body Large**: `text-xl` (20px)
- **Body**: `text-base` (16px)
- **Small**: `text-sm` (14px)
- **Tiny**: `text-xs` (12px)

## Espaçamento

### Sistema de Espaçamento
Utilizamos o sistema de espaçamento do Tailwind:
- `spacing-1` = 4px
- `spacing-2` = 8px
- `spacing-4` = 16px
- `spacing-6` = 24px
- `spacing-8` = 32px
- `spacing-12` = 48px
- `spacing-16` = 64px
- `spacing-20` = 80px
- `spacing-32` = 128px

## Bordas e Sombras

### Border Radius
- **Small**: `rounded-lg` (8px)
- **Medium**: `rounded-xl` (12px)
- **Large**: `rounded-2xl` (16px)
- **Full**: `rounded-full` (9999px)

### Sombras
- **Small**: `shadow-sm`
- **Medium**: `shadow-md`
- **Large**: `shadow-lg`
- **Extra Large**: `shadow-xl`
- **2XL**: `shadow-2xl`
- **Glow**: `shadow-blue-500/50`

## Animações

### Duração
- **Fast**: `duration-200` (200ms)
- **Normal**: `duration-300` (300ms)
- **Slow**: `duration-500` (500ms)
- **Slower**: `duration-1000` (1000ms)

### Easing
- **Linear**: `ease-linear`
- **In**: `ease-in`
- **Out**: `ease-out`
- **In-Out**: `ease-in-out`

### Animações Customizadas
- **fadeInUp**: Fade in com movimento para cima
- **float**: Movimento flutuante contínuo
- **pulse-glow**: Pulsação de opacidade
- **gradient**: Gradiente animado

## Componentes Base

### Botões
```tsx
// Primary Button
<button className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl font-semibold text-white">

// Secondary Button
<button className="px-8 py-4 bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl">

// Outline Button
<button className="px-8 py-4 border-2 border-blue-500 rounded-xl">
```

### Cards
```tsx
<div className="p-6 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl">
```

### Inputs
```tsx
<input className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500">
```

## Gradientes

### Gradientes de Fundo
```css
bg-gradient-to-r from-blue-500 to-purple-600
bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900
bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400
```

### Gradientes de Texto
```tsx
<span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
```

## Responsividade

### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Uso
```tsx
className="text-base md:text-lg lg:text-xl"
className="grid-cols-1 md:grid-cols-2 lg:grid-cols-4"
className="px-4 md:px-8 lg:px-16"
```

## Acessibilidade

- Sempre use `aria-label` em botões de ícone
- Inclua `alt` text em todas as imagens
- Mantenha contraste adequado (mínimo 4.5:1)
- Use elementos semânticos HTML
- Suporte navegação por teclado

## Performance

- Use `backdrop-blur` com moderação
- Otimize imagens com Next.js Image
- Lazy load componentes pesados
- Use `will-change` apenas quando necessário
- Minimize uso de sombras complexas

