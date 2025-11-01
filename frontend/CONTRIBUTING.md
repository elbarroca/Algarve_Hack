# 🤝 Guia de Contribuição - Frontend Algarve Hack

Obrigado por considerar contribuir para o Algarve Hack! Este documento fornece diretrizes para contribuir com o frontend do projeto.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Padrões de Código](#padrões-de-código)
- [Estrutura de Commits](#estrutura-de-commits)
- [Pull Requests](#pull-requests)
- [Testes](#testes)

## 🤗 Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

## 🚀 Como Contribuir

### 1. Fork o Repositório

```bash
git clone https://github.com/algarvehack/algarvehack.git
cd algarvehack/frontend
```

### 2. Crie uma Branch

```bash
git checkout -b feature/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

### 3. Instale as Dependências

```bash
npm install
```

### 4. Execute o Projeto

```bash
npm run dev
```

### 5. Faça suas Alterações

- Siga os padrões de código
- Adicione testes se aplicável
- Atualize a documentação

### 6. Commit suas Mudanças

```bash
git add .
git commit -m "feat: adiciona nova funcionalidade"
```

### 7. Push para o GitHub

```bash
git push origin feature/nome-da-feature
```

### 8. Abra um Pull Request

Vá para o GitHub e abra um PR para a branch `main`.

## 📝 Padrões de Código

### TypeScript

```typescript
// ✅ BOM: Tipos explícitos
interface ButtonProps {
  variant: 'primary' | 'secondary';
  onClick: () => void;
  children: React.ReactNode;
}

// ❌ RUIM: Sem tipos
function Button(props) {
  // ...
}
```

### Componentes React

```typescript
// ✅ BOM: Componente funcional com tipos
export const Button: React.FC<ButtonProps> = ({ 
  variant, 
  onClick, 
  children 
}) => {
  return (
    <button 
      onClick={onClick}
      className={`btn-${variant}`}
    >
      {children}
    </button>
  );
};

// ❌ RUIM: Sem tipos ou estrutura clara
export default function Button(props) {
  return <button onClick={props.onClick}>{props.children}</button>
}
```

### Naming Conventions

```typescript
// Componentes: PascalCase
export const AnimatedButton = () => {};

// Hooks: camelCase com prefixo 'use'
export const useScrollPosition = () => {};

// Constantes: UPPER_SNAKE_CASE
export const API_BASE_URL = 'https://api.example.com';

// Funções: camelCase
export const formatDate = (date: Date) => {};

// Interfaces/Types: PascalCase
interface UserProfile {
  name: string;
  email: string;
}
```

### Estrutura de Arquivos

```typescript
// ✅ BOM: Import organizado
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { Button } from '@/components';
import { useAuth } from '@/hooks';
import { formatDate } from '@/utils';

import type { User } from '@/types';

// ❌ RUIM: Imports desordenados
import { Button } from '@/components';
import React from 'react';
import type { User } from '@/types';
import { useAuth } from '@/hooks';
```

### Tailwind CSS

```typescript
// ✅ BOM: Classes organizadas e legíveis
<div className="
  flex items-center justify-between
  px-8 py-6
  bg-slate-800/40 backdrop-blur-sm
  border border-slate-700/50
  rounded-2xl
  hover:border-slate-600
  transition-all duration-300
">

// ❌ RUIM: Classes desorganizadas
<div className="flex bg-slate-800/40 px-8 items-center border rounded-2xl py-6 justify-between hover:border-slate-600 border-slate-700/50 backdrop-blur-sm transition-all duration-300">
```

### Ordem das Classes Tailwind

1. Layout (flex, grid, block)
2. Positioning (relative, absolute)
3. Size (w-, h-)
4. Spacing (p-, m-)
5. Typography (text-, font-)
6. Colors (bg-, text-, border-)
7. Effects (shadow-, opacity-)
8. Transitions
9. Responsive
10. States (hover:, focus:)

## 💬 Estrutura de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/).

### Tipos de Commit

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (não afeta código)
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

### Exemplos

```bash
# Feature
git commit -m "feat: adiciona componente de modal"
git commit -m "feat(button): adiciona variante outline"

# Fix
git commit -m "fix: corrige bug no formulário de contacto"
git commit -m "fix(nav): resolve problema de menu mobile"

# Docs
git commit -m "docs: atualiza README com instruções"
git commit -m "docs(api): adiciona documentação de endpoints"

# Style
git commit -m "style: formata código com prettier"

# Refactor
git commit -m "refactor: melhora performance do componente"

# Test
git commit -m "test: adiciona testes para Button"

# Chore
git commit -m "chore: atualiza dependências"
```

## 🔄 Pull Requests

### Checklist

Antes de abrir um PR, certifique-se de:

- [ ] Código segue os padrões do projeto
- [ ] Testes passam (`npm run lint`)
- [ ] Não há erros de TypeScript
- [ ] Documentação está atualizada
- [ ] Commits seguem o padrão
- [ ] Branch está atualizada com `main`

### Template de PR

```markdown
## Descrição
Breve descrição das mudanças

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Execute `npm install`
2. Execute `npm run dev`
3. Navegue para...

## Screenshots (se aplicável)
[Adicione screenshots aqui]

## Checklist
- [ ] Código testado localmente
- [ ] Sem erros de lint
- [ ] Documentação atualizada
```

## 🧪 Testes

### Executar Linting

```bash
npm run lint
```

### Executar Build

```bash
npm run build
```

### Verificar Tipos

```bash
npx tsc --noEmit
```

## 🎨 Diretrizes de Design

### Cores

Use as cores definidas em `globals.css`:

```typescript
// ✅ BOM: Usa variáveis CSS
className="bg-slate-800 text-blue-400"

// ❌ RUIM: Cores arbitrárias
className="bg-[#1e293b] text-[#60a5fa]"
```

### Espaçamento

Use o sistema de espaçamento do Tailwind:

```typescript
// ✅ BOM: Espaçamento consistente
className="p-6 gap-4 mt-8"

// ❌ RUIM: Valores arbitrários
className="p-[24px] gap-[16px] mt-[32px]"
```

### Animações

Use as animações definidas em `utils/animations.ts`:

```typescript
// ✅ BOM: Usa animações predefinidas
className="transition-all duration-300 hover:scale-105"

// ❌ RUIM: Animações inline
style={{ transition: 'all 0.3s' }}
```

## 📚 Recursos Úteis

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [TypeScript Docs](https://www.typescriptlang.org/docs)

## 🐛 Reportar Bugs

Ao reportar bugs, inclua:

1. **Descrição clara** do bug
2. **Passos para reproduzir**
3. **Comportamento esperado**
4. **Comportamento atual**
5. **Screenshots** (se aplicável)
6. **Ambiente** (OS, Browser, Node version)

## 💡 Sugerir Features

Para sugerir novas features:

1. **Verifique** se já não existe uma issue similar
2. **Descreva** claramente a feature
3. **Explique** o caso de uso
4. **Considere** alternativas

## 🤔 Dúvidas?

Se tiver dúvidas:

- Abra uma [Issue](https://github.com/algarvehack/algarvehack/issues)
- Contacte-nos: dev@algarvehack.pt

## 🙏 Agradecimentos

Obrigado por contribuir para tornar o Algarve Hack melhor! 🎉

---

**Happy Coding!** 💻✨

