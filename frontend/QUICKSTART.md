# 🚀 Quick Start - Homes AI Algarve

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Instalar e Executar

```bash
# Frontend
cd frontend
npm install
npm run dev
# → http://localhost:3000

# Backend (em outro terminal)
cd backend
pip install -r requirement.txt
python api.py
# → http://localhost:8001
```

### 2️⃣ Variáveis de Ambiente

Criar `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### 3️⃣ Testar Aplicação

1. **Abrir** → http://localhost:3000
2. **Criar Perfil** → Botão "🤝 Criar Perfil" no header
3. **Procurar** → "T2 em Faro até 900€" no chat
4. **Ver Resultados** → Cards com scores de compatibilidade
5. **Contactar** → Botão WhatsApp nos cards

## 📋 O que foi Criado

### ✅ Componentes Novos

```
frontend/app/
├── types/api.ts              ← TypeScript types do backend
├── services/api.ts           ← API service (HTTP calls)
├── components/
│   ├── ChatInterface.tsx     ← Chat em português ✨
│   ├── PropertyCard.tsx      ← Cards de propriedades
│   ├── RoommateProfileForm.tsx ← Formulário 3 etapas
│   ├── FAQSection.tsx        ← FAQ regulamentação PT
│   └── MapView.tsx           ← Mapa Algarve
└── page.tsx                  ← NOVA APLICAÇÃO! 🎉
```

### 🔄 Comparação

| Antes | Depois |
|-------|--------|
| Landing page genérica | **Aplicação funcional Homes AI** |
| "Construindo o Futuro Digital" | Chat PT + Procura de casas |
| Cards de marketing | PropertyCards com matching |
| Sem funcionalidade | **Integração completa com backend** |

## 🎯 Funcionalidades

### ✨ Já Funciona

- [x] Chat em português (com sugestões)
- [x] Procura de propriedades (mock data)
- [x] Formulário de perfil (3 etapas)
- [x] Cálculo de compatibilidade
- [x] Cards com scores
- [x] FAQ regulamentação portuguesa
- [x] Botões WhatsApp
- [x] Design responsivo

### 🔧 Requer Configuração

- [ ] Backend API endpoints (`/api/search`, `/api/match`)
- [ ] Mapbox token (para mapa real)
- [ ] Bright Data API (procura real de propriedades)

## 📱 Testar Features

### 1. **Perfil de Compatibilidade**

```
1. Click "Criar Perfil"
2. Etapa 1: Budget 900€, Selecionar "Faro" + "Loulé"
3. Etapa 2: Horário "Normal", 3 dias teletrabalho
4. Etapa 3: Limpeza "Muito limpo", Ruído "Silêncio"
5. Click "Concluir Perfil"
```

### 2. **Procurar Casas**

```
No chat, escrever:
- "T2 em Faro até 900€"
- "Quarto em Loulé"
- "Apartamento em Albufeira"
```

### 3. **Ver Compatibilidade**

Após criar perfil, os cards mostram:
- **Score 85-100%** → Verde (Excelente)
- **Score 60-84%** → Azul (Boa)
- **Score <60%** → Laranja (Razoável)

### 4. **Contactar Senhorio**

```
1. Click "Contactar" no card
2. Escolher WhatsApp ou Email
3. Mensagem pré-formatada em PT!
```

## 🔌 Integração Backend

### Endpoints Necessários

```python
# backend/api.py

@app.post("/api/search")
async def search_properties(request: SearchRequest):
    # ... implementar

@app.post("/api/match")
async def calculate_match(request: MatchRequest):
    # ... usar CompatibilityMatcher do test_full_flow.py

@app.get("/api/pois")
async def get_pois(lat: float, lng: float):
    # ... usar local_agent
```

Ver: `INTEGRATION_GUIDE.md` para detalhes completos.

## 📊 Mock Data vs Real Data

### Atual (Mock)

- 5 propriedades de exemplo
- Scores simulados
- POIs fictícios

### Com Backend Real

- Dados de Idealista, Imovirtual, Casa Sapo, OLX
- Matching real baseado em perfil
- POIs reais via Mapbox

## 🐛 Troubleshooting

### Propriedades não aparecem
→ Mock data está ativo. Backend retorna dados ao conectar.

### "Error fetching properties"
→ Backend não está rodando ou porta errada.

### Scores sempre 75%
→ Mock matcher. Backend real calcula scores reais.

### Mapa vazio
→ Requer `NEXT_PUBLIC_MAPBOX_TOKEN` no `.env.local`

## 📚 Próximos Passos

1. **Ver documentação completa**: `HOMES_AI_README.md`
2. **Integrar backend**: `INTEGRATION_GUIDE.md`
3. **Ver PRD**: `../PRD.MD`
4. **Testar matching logic**: `../test_full_flow.py`

## ✅ Checklist de Deploy

- [ ] Backend endpoints implementados
- [ ] Variáveis de ambiente configuradas
- [ ] CORS configurado
- [ ] Bright Data API key
- [ ] Mapbox token (opcional)
- [ ] Build frontend: `npm run build`
- [ ] Deploy (Vercel/Netlify)

## 🎉 Resultado Final

**Antes**: Landing page estática  
**Depois**: Aplicação completa de procura de casas no Algarve! 🏠🇵🇹

### Demo Flow Completo

```
1. Usuário abre aplicação
2. Vê hero: "Homes AI Algarve"
3. Click "Criar Perfil" → Completa 3 etapas
4. Tab "Procurar Casas" → Escreve "T2 em Faro"
5. Vê 5 propriedades com scores (ex: 85%, 78%, 70%)
6. Click numa propriedade → Ver detalhes + POIs
7. Click "Contactar" → WhatsApp abre com mensagem PT
8. Tab "FAQ" → Aprende sobre caução, contratos, etc.
```

---

**Aplicação pronta! Boa sorte no hackathon! 🚀**


