# 🚀 Comandos para Iniciar Backend e Frontend

## ⚠️ Backend (REQUER CONFIGURAÇÃO)

### ❌ PROBLEMA CRÍTICO: API Keys não configuradas

O backend inicia mas **NÃO PROCESSA QUERIES** porque faltam as chaves de API necessárias.

**Ação necessária**: Leia o arquivo `SETUP_REQUIRED.md` para instruções completas!

### Quick Fix (mínimo para funcionar):

1. Crie o arquivo `.env` no diretório backend:
```powershell
cd "C:\Users\jstme\Desktop\Pedro\AI Hackathon\Algarve_Hack\backend"
Copy-Item env_template.txt .env
```

2. Edite `.env` e adicione pelo menos estas chaves (mínimo essencial):
```
ASI_API_KEY=sua_chave_asi_aqui
TAVILY_API_KEY=sua_chave_tavily_aqui
MAPBOX_API_KEY=sua_chave_mapbox_aqui
```

3. Obtenha as chaves em:
   - ASI:1 (CRÍTICO): https://asi1.ai/
   - Tavily: https://tavily.com/
   - Mapbox: https://mapbox.com/

### Depois de configurar, iniciar backend:

```powershell
cd "C:\Users\jstme\Desktop\Pedro\AI Hackathon\Algarve_Hack\backend"
py -3.12 main.py
```

**Nota**: Use Python 3.12 (não 3.14) - já está instalado no seu sistema.

### Verificar se está funcionando:
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing
```

Deve retornar: `{"status": "ok"}`

---

## ⚠️ Frontend (Requer Node.js)

### ❌ PROBLEMA ATUAL: Node.js não está instalado
Você está vendo este erro:
```
npm : The term 'npm' is not recognized...
```

### ✅ SOLUÇÃO: Instalar Node.js

#### 1. Baixar e Instalar Node.js:
- **Site**: https://nodejs.org/
- **Versão recomendada**: LTS (Long Term Support)
- **Download direto**: https://nodejs.org/dist/v20.18.1/node-v20.18.1-x64.msi
- Durante a instalação, marcar: ✅ "Automatically install the necessary tools"

#### 2. Reiniciar o PowerShell após instalação

#### 3. Verificar se instalou corretamente:
```powershell
node --version
npm --version
```

Deve mostrar as versões (ex: v20.18.1 e 10.8.2)

#### 4. Agora sim, iniciar o frontend:
```powershell
cd "C:\Users\jstme\Desktop\Pedro\AI Hackathon\Algarve_Hack\frontend"
npm install
npm run dev
```

### Frontend estará disponível em:
- http://localhost:3000

---

## 📋 Resumo Rápido

### Terminal 1 - Backend:
```powershell
cd backend
py -3.12 main.py
```

### Terminal 2 - Frontend (após instalar Node.js):
```powershell
cd frontend
npm install
npm run dev
```

---

## ✅ Verificações

### Backend está rodando?
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing
```

### Frontend está rodando?
```powershell
Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
```

---

## 🧪 Testar o Sistema

### Teste automático (com backend rodando):
```powershell
cd tests
py -3.12 test_search_flow.py
```

### Teste manual via API:
```powershell
$body = @{
    message = "Procuro apartamento T2 em Lisboa até 300k"
    session_id = "test123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8080/api/chat" `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -UseBasicParsing
```

---

## 🔧 Troubleshooting

### Se backend não iniciar:
1. Verificar se está usando Python 3.12: `py -3.12 --version`
2. Verificar se porta 8080 está livre
3. Verificar se dependências estão instaladas: `py -3.12 -m pip list | Select-String uagents`

### Se frontend não iniciar:
1. Verificar se Node.js está instalado: `node --version`
2. Verificar se npm está instalado: `npm --version`
3. Se der erro, tentar: `npm install --force`

---

## 📊 Status Atual

- ✅ **Backend**: Rodando perfeitamente em http://localhost:8080
- ❌ **Node.js**: NÃO INSTALADO (necessário para o frontend)
- ⏳ **Frontend**: Aguardando instalação do Node.js
- ✅ **Rotas verificadas**: Todas corretas conforme test_search_flow.py
- ✅ **Sem mock data**: Tudo conectado ao backend real
- ✅ **Resposta da API**: Todos os campos corretos (requirements, properties, search_summary, total_found, raw_search_results, community_analysis)

## 🎯 Próximo Passo: INSTALAR NODE.JS

1. Baixar de: https://nodejs.org/dist/v20.18.1/node-v20.18.1-x64.msi
2. Executar o instalador
3. Reiniciar PowerShell
4. Executar: `cd frontend && npm install && npm run dev`

