- PRD
    
    # PRD — Homes AI Algarve (PT) + Roommate Matching — v1.0 (2025-11-01)
    
    > Scope type: New + Port/Localization of your existing steve-dusty-homes-ai repo to the Algarve long-term rental market in Portuguese, with roommate/house-based matching and basic regulatory guidance.
    > 
    
    ---
    
    ## 1) Pin the Goal
    
    **Single-sentence goal:**
    
    Launch a Portuguese-language, Algarve-focused housing assistant that (a) surfaces long-term rental supply from major PT sources, (b) matches tenants and roommates to compatible houses, and (c) helps users navigate local rules—within a hackathon-viable MVP.
    
    **North Star metric:**
    
    Time-to-first viable match (TFFM) ≤ **7 days** from user signup.
    
    **Success metrics (targets):**
    
    - M1 Algarve coverage: ≥ **70%** of public long-term listings found in **Faro, Loulé, Portimão, Lagos, Albufeira**.
    - PT language adoption: ≥ **80%** sessions in **pt-PT** without fallback to EN.
    - Match quality (post-move CSAT 1–5): **≥ 4.2**.
    - Conversion: **≥ 20%** of registered seekers submit at least one verified lead.
    
    **Guardrails:**
    
    - **GDPR** compliance; explicit consent for profile data + roommate attributes.
    - Respect source **ToS/robots**; prefer APIs/feeds where available.
    - Latency p95 chat turn **< 3s**, geocode/POI bundle **< 6s**.
    - Non-discrimination (housing + employment law); no targeting by protected classes.
    
    ---
    
    ## 2) Rapid Landscape Research (decision-relevant facts)
    
    - **Long-term rentals tight in Algarve**; tourism & AL (Alojamento Local) reduce supply; municipalities monitor AL and promote LT conversions. *Implication:* prioritize **LT** discovery and filtering (exclude ST/AL by default). [1][2]
    - **PT listing ecosystems:** major sources are **Idealista**, **Imovirtual**, **Casa Sapo**, **OLX Imóveis**, plus **Facebook groups** & local agencies. *Implication:* integrate multi-source search; de-dupe by address/URL. [3][4][5][6]
    - **Mais Habitação (Lei n.º 56/2023)** altered AL rules; municipalities like Lisbon/Porto paused new AL registrations; Algarve has local nuances. *Implication:* add lightweight assistant answers on **AL vs Arrendamento** and **contratos**. [7][8]
    - **GDPR**: special categories & profiling require consent; data minimization + purpose limitation. *Implication:* explicit opt-in for roommate traits; anonymize contact until match. [9]
    - **Student demand (UAlg)** and **digital nomads** seasonal pressure. *Implication:* include **room/coliving** supply and **roommate match**. [10]
    
    > Assumptions (to validate fast):
    > 
    > 
    > A1: We can legally fetch public listing pages and store summary metadata for matching (respecting ToS).
    > 
    > A2: Students and nomads accept **compatibility scoring** (sleep schedule, smoking, pets, budget, commute).
    > 
    > A3: Landlords in Algarve respond via WhatsApp more than email; add WhatsApp deep-links.
    > 
    
    **How to validate:** 5 quick calls with UAlg students + 5 Algarve agents; crawl-test 500 URLs; WhatsApp CTA A/B.
    
    ---
    
    ## 3) PRD (Lean)
    
    ### Overview
    
    - **Summary:** PT-localized Homes AI that chats in Portuguese, discovers Algarve LT listings, scores compatibility for **houses** and **roommates**, geocodes & shows POIs, and answers simple regulatory FAQs.
    - **Version/Date:** v1.0 / 2025-11-01
    - **Status:** Plan → Hackathon MVP
    
    ### Target Users & JTBD
    
    - **Students (UAlg)** — “Help me find an affordable room near campus with compatible housemates.”
    - **Residents/locals** — “Find a T1/T2 long-term within budget & commute.”
    - **Digital nomads** — “Medium-term room w/ good internet and quiet hours.”
    - **Landlords/agents** — “Fill rooms faster with pre-qualified, matched tenants.”
    
    ### Problem Statement & Hypotheses
    
    - **Problem:** Algarve LT supply is opaque/fragmented; roommate fit is hard; regulations are confusing.
    - **Hypotheses:**
        
        H1: Multi-source aggregation + PT chat cuts search time by **30%**.
        
        H2: Compatibility score **>70** predicts **CSAT ≥4** post-move.
        
        H3: Light regulatory guidance reduces churn at booking step by **15%**.
        
    
    ### Scope / Out of Scope
    
    - **In:** PT UI, Algarve municipalities, LT rentals focus; roommate/house matching; PT geocoding & POIs; simple regulation Q&A; lead handoff to landlord.
    - **Out (MVP):** Payment/escrow, KYC, contract generation, full AL compliance adjudication.
    
    ### Assumptions & Risks
    
    - **Data risk:** Source ToS / rate limits → add **throttle + cache**, honor robots.txt.
    - **Legal risk:** Profiling roommate traits → **explicit consent + opt-out**; no protected-class filters.
    - **Quality risk:** Duplicate and stale listings → **URL/addr fingerprint + recency filter**.
    - **Ops risk:** Multi-agent timeouts → **bounded waits + graceful partials**.
    
    ### Functional Requirements (R-IDs)
    
    | ID | Requirement | Rationale | Priority | Acceptance Test | Trace |
    | --- | --- | --- | --- | --- | --- |
    | **R1** | **Portuguese locale**: All UX & agent replies default **pt-PT**; EN fallback toggle. | Hackathon/local users | Must | User sets `pt-PT`; all system/agent strings are PT; >95% messages in PT. | PT adoption |
    | **R2** | **Algarve geofilter** across **Faro, Loulé, Portimão, Lagos, Albufeira, Tavira, Silves**. | Local focus & metrics | Must | Query “T1 Faro” returns only Algarve results; 0% Lisboa/Porto bleed. | Coverage |
    | **R3** | **Multi-source search**: Ingest summary cards (title, price, type, URL, address city, images if available) from **Idealista, Imovirtual, Casa Sapo, OLX**. | Supply breadth | Must | Given seed queries, ≥70% overlap with manual audit sample. | Coverage |
    | **R4** | **De-dupe** by URL + `(address_norm, price±5%, photos hash)` | Clean results | Must | Inject synthetic dups → one card remains. | Quality |
    | **R5** | **LT vs AL** classifier (regex + heuristics) → default LT. | Avoid short-term | Should | Listings tagged correctly ≥90% on labeled set (n≥200). | Quality |
    | **R6** | **Roommate/House matching**: profile intake (budget, schedule, pets, cleanliness, noise tolerance, smoking, WFH) → **Compatibility score 0–100** | Core JTBD | Must | Two profiles with identical vectors score ≥95; known opposites ≤40. | NSM |
    | **R7** | **House-based** (unit) profile: house rules, bills, rooms, internet, gender/pet rules | Fit at household level | Should | House profile renders; match score uses house rules. | CSAT |
    | **R8** | **Portuguese map & POIs** (Mapbox country=PT; POIs localized names) | Decision support | Should | For top 5 results, show escolas/supermercados/saúde within 1–2km. | UX |
    | **R9** | **Regulation mini-assistant**: Q&A for arrendamento base, fiador, caução, AL basics, links to official pages | Reduce confusion | Should | 10 FAQs return concise PT answers + links. | Conversion |
    | **R10** | **Landlord handoff**: CTA WhatsApp deep-link with templated PT message; email fallback | Faster response | Must | Click opens wa.me with prefilled PT message containing listing URL. | Conversion |
    | **R11** | **Analytics** events + dashboard: search, view, match, outbound, reply-rate | Iterate fast | Must | Events visible in dashboard; weekly decision review. | Ops |
    
    ### Non-functional
    
    - **Performance:** p95 chat <3s; batch geocode/POI <6s; crawl per domain ≤ 2 rps.
    - **Reliability:** graceful degradation if a source fails; show partial results + banner.
    - **Security/Privacy:** GDPR; explicit consent; hashed emails; opt-out delete.
    - **Accessibility:** PT copy readable (B1+), color contrast AA.
    - **Compliance:** no discriminatory filters; legal links not legal advice.
    
    ### User Stories & Acceptance (Gherkin)
    
    - **US1 — PT discovery**
        
        **Given** browser locale pt-PT, **when** I ask “Procuro T2 em Faro até 900€” **then** the agent replies in PT and results are Algarve only.
        
    - **US2 — Roommate match**
        
        **Given** I completed a roommate quiz, **when** I view a house profile, **then** I see a **Compatibilidade 0–100** and top 3 reasons (e.g., “horário de sono compatível”).
        
    - **US3 — Landlord outreach**
        
        **Given** I tap “Contactar via WhatsApp”, **then** WhatsApp opens with a PT template including link, preço e data disponível.
        
    - **US4 — Regulation FAQ**
        
        **When** I ask “Posso pedir recibo de renda eletrónico?”, **then** I get a concise PT answer + official link.
        
    
    ### UX Notes (textual)
    
    - Left panel: PT chat (chips: “T1”, “Quartos”, “Até 800€”); badge **Longo Prazo**.
    - Map: Algarve default; top card with image, price, score, POIs (escolas, supermercados).
    - Match explainer: three green ticks, two amber cautions.
    - Regulatory microcard: “Caução: normalmente 1–2 rendas” + “Ler mais”.
    
    ### Analytics/Telemetry
    
    Events: `search_submitted`, `listing_seen`, `match_score_viewed`, `cta_whatsapp_click`, `faq_viewed`, `faq_link_click`.
    
    Props: city, price_band, bedroom_type, score_bucket, locale.
    
    Dashboards: Coverage %, TFFM, CTR WhatsApp, FAQ usage.
    
    Cadence: weekly review + A/B on templates.
    
    ### Dependencies
    
    - **Data**: Idealista/Imovirtual/CasaSapo/OLX (respect ToS; prefer official feeds if available).
    - **Infra**: Mapbox, Supabase (profiles, matches), Bright Data MCP (optional), uAgents, Next.js.
    - **Legal**: PT housing links (IHU/Portal Habitação), GDPR counsel.
    
    ### Release Plan
    
    - **Alpha (Hackathon week):** PT UI, Algarve filter, 2 sources (Idealista+Imovirtual) via Bright Data MCP or cached sample, basic roommate score, WhatsApp CTA, Mapbox PT.
    - **Beta (Month 1):** Add CasaSapo+OLX, de-dup robust, regulation mini-assistant, POIs.
    - **GA (Month 2):** House profiles, dashboard, student funnels (UAlg).
    
    ### Open Questions (ranked)
    
    1. ToS/API status for each portal? Feeds available?
    2. Municipality nuances for AL vs LT in Algarve cities?
    3. Minimum viable roommate traits without sensitive categories?
    4. Landlord contact preference split (WhatsApp vs email) in Algarve?
    
    ### Change Log
    
    - v1.0 (2025-11-01): Initial PT/Algarve PRD with roommate module.
    
    ---
    
    ## 4) Quality Gate (sample on R1, R3, R6)
    
    - **R1 (PT locale):** singular ✔; unambiguous ✔; necessary ✔; feasible ✔; verifiable ✔ (language check); traced to PT adoption.
    - **R3 (Multi-source):** singular ✔; feasible ⚠ (ToS) → mitigation: throttle + cached samples; verifiable via recall audit.
    - **R6 (Roommate score):** singular ✔; necessary ✔; feasible ✔ (vector similarity with weights); test with labeled pairs; traces to NSM & CSAT.
    
    ---
    
    ## 5) Working-Backwards — PR/FAQ (1-page)
    
    ### Press Release (draft)
    
    **FARO, 2025-11-30 — “Homes AI chega ao Algarve: encontrar casa e colegas de casa, em Português.”**
    
    Hoje lançamos o **Homes AI Algarve**, um assistente em **português** que agrega ofertas de **arrendamento de longo prazo** no Algarve e cria **combinações inteligentes** entre pessoas e casas. Em minutos, os estudantes, residentes e nómadas digitais descobrem T1/T2 ou quartos compatíveis, com localização no mapa, pontos de interesse e respostas rápidas sobre caução, recibos e contratos. É simples: conversa natural → resultados reais → contacto direto por WhatsApp.
    
    **Como funciona:**
    
    1. Diz onde quer viver e o orçamento. 2) Vê casas e quartos com pontuação de compatibilidade. 3) Contacta o senhorio com mensagem PT pronta a enviar. 4) Tira dúvidas comuns com o mini-assistente de regras.
    
    **Começar:** Acede à app web, escolhe “Algarve”, responde ao mini-questionário de roommate e inicia a conversa em português.
    
    ### FAQ (recorte, 12 Q&A)
    
    1. **Quais fontes?** Idealista, Imovirtual, Casa Sapo e OLX (quando permitido), além de agências locais.
    2. **É só longo prazo?** Por defeito sim; sinalizamos anúncios de AL/curto prazo.
    3. **Como calculam compatibilidade?** Vetor de preferências (horários, orçamento, pets, fumo, WFH).
    4. **Privacidade?** Cumprimos **RGPD**; consentimento explícito; pode apagar dados.
    5. **Discriminação?** Não permitimos filtros por atributos protegidos.
    6. **WhatsApp porquê?** Senhorios respondem mais rápido—modelo conversacional local.
    7. **Garantem veracidade?** Não; mostramos fontes e data—e removemos sinalizações reportadas.
    8. **Custos?** MVP gratuito; futuro “Pro” para agentes/casas com destaque.
    9. **E se um portal falhar?** Resultados parciais + aviso; tentamos outra fonte.
    10. **Regulação/contratos?** FAQ informativa com links oficiais; não é aconselhamento jurídico.
    11. **Cobertura Algarve?** Cinco concelhos chave no MVP; expandimos com procura.
    12. **Como reporto fraude?** Botão “Sinalizar” no cartão → revisão em 24–48h.
    
    ---
    
    ## 6) Conclusion & Action Plan
    
    **Go/No-Go:** **GO** for Hackathon MVP — clear local pain, feasible PT port, strong differentiation via roommate/house scoring.
    
    **Top Risks & Mitigations**
    
    1. **Source ToS / stability** → throttle, cached seed data for demo, request partner feeds.
    2. **Data quality (stale/dup)** → strict de-dup + recency filter; user reporting.
    3. **Privacy profiling** → minimal traits, explicit consent, anonymized contact pre-match.
    
    **DACI**
    
    - **Driver:** Ricardo (PM/Tech lead)
    - **Approver:** Hackathon lead / partner mentor
    - **Contributors:** Data (scraper ops), FE (Next.js), Agents (uAgents), Legal reviewer
    - **Informed:** UAlg community partners; local agencies
    
    **30/60/90**
    
    - **30d:** Ship Algarve MVP (PT UI, 2 sources, roommate score v1, WhatsApp CTA, PT FAQ lite).
    - **60d:** Add 2 sources + de-dup robust, POIs, dashboard, house profiles.
    - **90d:** Municipality info pages, partner feeds, beta to 200 users via UAlg.
    
    **Backlog Slice (Top 10)**
    
    1. PT i18n files + agent prompts (Must, S)
    2. Algarve geofilter + Mapbox PT (Must, S)
    3. Source adapters (Idealista, Imovirtual) via Bright Data MCP + cache (Must, M)
    4. De-dup (addr/URL/photo hash) (Must, M)
    5. Roommate quiz + score function (Must, M)
    6. House profile schema (Should, S)
    7. WhatsApp template PT (Must, S)
    8. Regulation FAQ content + links (Should, S)
    9. POIs PT categories (Should, S)
    10. Analytics events + dashboard (Must, S)
    
    **Decision Log**
    
    - 2025-11-01: Chosen Algarve-first PT launch; roommate scoring in MVP; WhatsApp CTA.
    
    ---
    
    ## 7) If Info is Missing → Question List & Validation Plan
    
    - Do portals offer **official feeds** we can use short-term? *Owner:* Data lead, **ETA 3d**.
    - Municipality **AL vs LT** nuances by city (e.g., quotas, incentives)? *Owner:* Research, **ETA 5d**.
    - UAlg channel partnerships for student onboarding? *Owner:* Outreach, **ETA 7d**.
    - Landlord comms preference split? Quick poll of first 50 leads. *Owner:* Ops, **ETA 10d**.
    
    ---
    
    ## Repo Mapping & PT Implementation Plan
    
    Use your provided structure; below are **only the diffs/additions** needed for PT Algarve + roommate:
    
    ### Backend (uAgents)
    
    - **New**: `agents/matching_agent.py`
        - Input: `SeekerProfile`, `HouseProfile` (Supabase tables).
        - Output: `{score: 0–100, reasons: [top3]}` using weighted cosine on normalized vectors.
    - **Modify:** `agents/research_agent.py`
        - Search prompts → **Portuguese & Algarve cities**.
        - Domain allowlist: `idealista.pt`, `imovirtual.com`, `casasapo.pt`, `olx.pt`.
        - Geocoder: `country=PT`.
        - LT/AL classifier: simple heuristics (`“alojamento local”, “short-term”, “AL-”` → AL flag).
    - **Modify:** `agents/mapbox_agent.py`
        - `country: "PT"`; address normalization PT.
    - **New:** `agents/faq_agent.py`
        - PT mini-assistant with 10 curated Q&As; always include official link field.
    - **Models additions (`agents/models.py`)**
        
        ```python
        class SeekerProfile(Model):
            budget_min: Optional[int]; budget_max: int
            schedule: Literal["early","standard","late"]
            pets: bool; smoking: bool; wfh_days: int
            cleanliness: Literal["low","med","high"]
            noise_tolerance: Literal["low","med","high"]
            preferred_cities: List[str]
        
        class HouseProfile(Model):
            city: str
            rooms: int
            rules_pets: bool; rules_smoking: bool
            quiet_hours: str
            bills_included: bool
            internet_speed_mbps: Optional[int]
        
        class MatchRequest(Model):
            seeker: SeekerProfile; house: HouseProfile; session_id: str
        
        class MatchResponse(Model):
            score: float; reasons: List[str]; session_id: str
        
        ```
        
    - **Supabase tables (sketch):**
        - `seekers(id, user_id, traits jsonb, created_at)`
        - `houses(id, landlord_id, attrs jsonb, listing_url, city, created_at)`
        - Index on `(city, created_at)`
    
    ### Frontend (Next.js)
    
    - **i18n:** `lib/i18n.ts` + PT copy; `ChatInterface` starts in PT.
    - **Chips:** quick filters (T0/Quarto/T1/T2; €600–€1200; Cidades Algarve).
    - **Match card:** “**Compatibilidade 83/100** — horários e higiene combinam.”
    - **WhatsApp CTA:** prefilled PT text:
        
        > Olá, vi o seu anúncio em {fonte}. Orçamento {€}, entrada {data}, somos {n} pessoas. Podemos agendar visita?
        > 
    
    ---
    
    ## References (bibliography)
    
    1. **Housing pressures in Algarve (context)** — *General analyses on LT supply vs tourism in PT.* (2023–2025).
    2. **Municipal roles & LT initiatives** — *Local gov announcements on housing & AL adjustments*. (2023–2025).
    3. **Idealista Portugal** — Leading PT property portal (coverage reference). 2025. https://www.idealista.pt/
    4. **Imovirtual** — PT property listings (coverage reference). 2025. https://www.imovirtual.com/
    5. **Casa Sapo** — PT property marketplace. 2025. https://www.casasapo.pt/
    6. **OLX Imóveis** — General classifieds with rentals segment. 2025. https://www.olx.pt/imoveis/
    7. **Lei n.º 56/2023** (“Mais Habitação”) — Alterações ao regime de AL e habitação. 2023. https://dre.pt/
    8. **DL 128/2014** (com alterações) — Regime do Alojamento Local. 2014–2018–2023. https://dre.pt/
    9. **RGPD / GDPR** — Regulamento (UE) 2016/679 (perfis & consentimento). 2018. https://eur-lex.europa.eu/
    10. **Universidade do Algarve (UAlg)** — Student housing context (demand reference). 2025. https://www.ualg.pt/
    
    > Notes: Exact municipality specifics and freshest AL rules vary; confirm during implementation. Links above are authoritative starting points; fetch latest circulars/avisos municipais.
    > 
    
    ---
    
    ### Appendix A — Glossary
    
    - **AL**: Alojamento Local (short-term).
    - **LT**: Long-term rental (arrendamento).
    - **T0/T1/T2**: PT typology (studios/1-bed/2-bed).
    - **CSAT**: Customer satisfaction.
    
    ### Appendix B — Metrics Dictionary
    
    - **Coverage %**: (# listings captured in audit / total visible across sources) per city, 7-day window.
    - **TFFM**: Days from signup to first landlord reply on a viable listing (budget, city match).
    - **Match Score**: 0–100 weighted vector similarity; bucketed (≤40 low, 41–70 med, ≥71 high).
    
    ---
    
    ## What I’ll ship for the Hackathon MVP (concrete next steps)
    
    1. **PT text & prompts** (R1): add `pt-PT.json`, set default; translate system prompts.
    2. **Algarve filter** (R2): constant of 7 municipalities; `country=PT` in geocoder.
    3. **Two sources via MCP + cache** (R3): Idealista + Imovirtual queries in PT; persist top 300 summary cards.
    4. **Roommate score v1** (R6): traits form → vector → score + reasons.
    5. **WhatsApp CTA** (R10): wa.me deep-link generator + PT template.
    6. **FAQ lite** (R9): 10 curated Q&A with official links.
    
    If you want, I can also generate the **matching_agent.py** stub + **models** additions to drop straight into `backend/agents/`, plus a small **Supabase schema** for `seekers` and `houses`.