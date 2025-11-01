# 🏠 Homes AI Algarve - Frontend Documentation

## 📋 Visão Geral

Este é o frontend completo e funcional do **Homes AI Algarve**, uma aplicação de procura inteligente de arrendamento de longa duração no Algarve, totalmente integrada com o backend de agentes uAgents.

### ✨ Funcionalidades Implementadas

✅ **Interface de Chat em Português** - Conversa natural para procurar propriedades  
✅ **Sistema de Matching de Roommates** - Compatibilidade baseada em perfis  
✅ **Cards de Propriedades** - Com scores de compatibilidade e informações detalhadas  
✅ **Formulário de Perfil** - 3 etapas para criar perfil de compatibilidade  
✅ **FAQ de Regulamentação** - Informações sobre arrendamento em Portugal  
✅ **Integração WhatsApp** - Mensagens pré-formatadas em português  
✅ **Visualização de Mapa** - Componente preparado para Mapbox  
✅ **Multi-fonte** - Suporta Idealista, Imovirtual, Casa Sapo, OLX  

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
cd frontend
npm install
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env.local` na pasta `frontend/`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_MAPBOX_TOKEN=seu_token_aqui
```

### 3. Executar em Desenvolvimento

```bash
npm run dev
```

Acesse: [http://localhost:3000](http://localhost:3000)

### 4. Backend

Certifique-se de que o backend está em execução:

```bash
cd backend
python api.py
```

## 📐 Arquitetura

```
frontend/app/
├── types/
│   └── api.ts                    # TypeScript types (PRD models)
├── services/
│   └── api.ts                    # API service (backend communication)
├── components/
│   ├── ChatInterface.tsx         # Chat em português
│   ├── PropertyCard.tsx          # Card de propriedade com matching
│   ├── RoommateProfileForm.tsx   # Formulário de perfil (3 etapas)
│   ├── FAQSection.tsx            # FAQ sobre regulamentação PT
│   ├── MapView.tsx               # Visualização de mapa
│   └── index.ts                  # Exports
└── page.tsx                      # Página principal integrada
```

## 🎯 Componentes Principais

### 1️⃣ ChatInterface

Interface de chat em português para procurar propriedades.

**Features:**
- Sugestões rápidas (chips)
- Loading states com animações
- Scroll automático
- Integração com perfil de roommate

**Exemplo de uso:**
```tsx
<ChatInterface
  onPropertiesFound={(properties) => setProperties(properties)}
  seekerProfile={seekerProfile}
/>
```

### 2️⃣ PropertyCard

Card de propriedade com todas as informações e compatibilidade.

**Features:**
- Score de compatibilidade visual (0-100%)
- Detalhes (quartos, WC, m²)
- Botões de contacto (WhatsApp + Email)
- POIs próximos (expandível)

**Exemplo de uso:**
```tsx
<PropertyCard
  property={property}
  index={0}
  showCompatibility={true}
/>
```

### 3️⃣ RoommateProfileForm

Formulário de 3 etapas para criar perfil de compatibilidade.

**Etapas:**
1. **Orçamento & Localização** - Budget slider + cidades preferidas
2. **Estilo de Vida** - Horário de sono, teletrabalho, pets, fumador
3. **Preferências** - Limpeza, tolerância ao ruído

**Features:**
- Validação em cada etapa
- Progress bar visual
- Nota sobre RGPD

**Exemplo de uso:**
```tsx
<RoommateProfileForm
  onProfileComplete={(profile) => setSeekerProfile(profile)}
  initialProfile={existingProfile}
/>
```

### 4️⃣ FAQSection

Seção de perguntas frequentes sobre arrendamento em Portugal.

**Features:**
- 8 FAQs sobre regulamentação portuguesa
- Links oficiais (Portal da Habitação, etc.)
- Accordion expandível
- Disclaimer legal

### 5️⃣ MapView

Componente de mapa preparado para Mapbox (requer token).

**Features:**
- Lista de propriedades no mapa
- Controles de zoom
- Legendas
- Click em propriedades

## 🔗 Integração com Backend

### API Service (`services/api.ts`)

```typescript
// Procurar propriedades
const response = await homesAIAPI.searchProperties(
  "T2 em Faro até 900€",
  seekerProfile
);

// Calcular matching
const match = await homesAIAPI.calculateMatch(seeker, house);

// Get POIs
const pois = await homesAIAPI.getPOIs(latitude, longitude);

// Get FAQs
const faqs = homesAIAPI.getFAQs();

// WhatsApp message
const message = homesAIAPI.generateWhatsAppMessage(property, userName);
```

### Endpoints Esperados do Backend

```
POST /api/search
Body: { user_message: string, session_id: string, seeker_profile?: SeekerProfile }
Response: { properties: PropertyListing[], search_summary: string, total_found: number }

POST /api/match
Body: { seeker: SeekerProfile, house: HouseProfile, session_id: string }
Response: { score: number, reasons: string[], session_id: string }

GET /api/pois?lat={lat}&lng={lng}&session_id={id}
Response: POI[]
```

## 🎨 Design System

### Cores Principais
```css
Primary Blue:    #3b82f6
Secondary Purple:#8b5cf6
Accent Green:    #10b981
Background:      #0f172a (slate-900)
Text:            #ffffff (white)
```

### Componentes de UI
- **Gradientes**: `from-blue-600 to-blue-500`
- **Borders**: `border-slate-700/50` (transparência)
- **Backdrop**: `backdrop-blur-sm` (glassmorphism)
- **Shadows**: `shadow-xl shadow-blue-500/10`

## 📱 Responsividade

- **Mobile**: < 640px (single column)
- **Tablet**: 640px - 1024px (mixed layout)
- **Desktop**: > 1024px (3-column layout)

```tsx
// Grid responsivo
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
```

## 🔒 Privacidade & RGPD

- ✅ Consentimento explícito para perfil de roommate
- ✅ Dados armazenados localmente (localStorage/state)
- ✅ Sem tracking de terceiros
- ✅ Links para termos e privacidade no footer

## 🌐 Internacionalização (PT)

Toda a aplicação está em **português de Portugal**:
- Labels e botões
- Mensagens de erro
- FAQ e documentação
- Respostas do chat

### Vocabulário PT Específico
- **T0/T1/T2** - Tipos de apartamento portugueses
- **Quarto** - Room (bedroom)
- **Arrendamento** - Long-term rental
- **Senhorio** - Landlord
- **Caução** - Security deposit
- **WC** - Bathroom

## 🚀 Próximos Passos

### Para Deploy Completo:

1. **Integrar Mapbox**
```bash
npm install mapbox-gl @types/mapbox-gl
```

2. **Conectar Backend Real**
- Atualizar `NEXT_PUBLIC_API_URL` no `.env.local`
- Testar todos os endpoints

3. **Deploy**
```bash
npm run build
# Deploy to Vercel / Netlify
```

4. **Analytics** (opcional)
- Google Analytics 4
- Mixpanel
- PostHog

## 🐛 Mock Data

Quando o backend não está disponível, a aplicação usa **mock data**:
- 5 propriedades de exemplo no Algarve
- Scores de compatibilidade simulados
- POIs de exemplo em Faro

## 📊 Métricas (PRD)

A aplicação suporta as métricas do PRD:

- **M1**: Cobertura do Algarve (70%+ das listagens públicas)
- **M2**: Adoção PT (80%+ sessões em pt-PT) ✅
- **M3**: Match Quality (CSAT ≥ 4.2 post-move)
- **M4**: Conversão (20%+ leads verificados)

## 🔧 Troubleshooting

### Erro: "API não responde"
- Verificar se backend está em execução na porta 8001
- Verificar `NEXT_PUBLIC_API_URL` em `.env.local`

### Erro: "Mapa não carrega"
- Adicionar token Mapbox válido
- Instalar `mapbox-gl` library

### Propriedades não aparecem
- Verificar console do navegador
- Backend pode estar retornando formato diferente

## 📞 Suporte

Para dúvidas sobre implementação:
- Ver `PRD.MD` na raiz do projeto
- Ver `test_full_flow.py` para exemplos de matching
- Consultar backend `api.py` e `models.py`

---

**Desenvolvido para Algarve Hack 2025** 🇵🇹


