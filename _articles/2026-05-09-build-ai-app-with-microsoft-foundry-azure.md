---
layout: article
title: "Build AI App with Microsoft Foundry & Azure"
author: "Imoh Etuk"
author_github: "imohweb"
date: 2026-05-09
published: true
tags: [microsoft-foundry, azure, ai-agents, fastapi, react, azd, github-actions, key-vault]
description: "Live build of an AI Agent–powered Customer Support App with Microsoft Foundry, FastAPI, React, and Azure — provisioned with Bicep and deployed three ways (local, azd, GitHub Actions OIDC)."
event_date: "Saturday, May 9, 2026"
event_time: "6:00 PM CEST"
event_venue: "Online — Microsoft Teams"
registration_url: "https://www.meetup.com/malta-microsoft-ai-user-group/events/313848364/"
canonical_url: "https://mmaug-org.github.io/community-articles/articles/2026-05-09-build-ai-app-with-microsoft-foundry-azure.html"
speakers:
  - "Imoh Etuk"
---

## What we will build

A fully working **AI Agent–powered Customer Support App** running on Azure:

- **Frontend** — React 18 + Vite + TypeScript on Azure App Service
- **Backend** — Python 3.11 + FastAPI on Azure App Service
- **AI** — Microsoft Foundry Agent (`gpt-4o-mini`) with three function tools:
  `create_ticket`, `lookup_ticket`, `list_open_tickets`
- **Data** — Azure Database for PostgreSQL Flexible + Azure Blob Storage
- **Identity** — Managed Identity end-to-end, no API keys
- **IaC** — Bicep, deployed with Azure Developer CLI (`azd up`)

## Three deployment paths covered

1. **Local** — `uvicorn` + `npm run dev` for inner-loop coding.
2. **`azd up`** — one-shot provisioning + deployment of the whole stack.
3. **GitHub Actions** — CI per layer (`backend-ci`, `frontend-ci`, `infra-ci`) plus
   a `deploy-azd` workflow that runs `azd up` from CI using **OIDC federated credentials**
   — no client secrets in the repo.

## Production hardening focus

A dedicated section on **Azure Key Vault**: why secrets must never live in `.env`,
how to wire `@Microsoft.KeyVault(SecretUri=…)` references into App Service config,
and why **Managed Identity + RBAC** is the modern alternative to access policies.

## Repo

The full source code, Bicep templates, GitHub Actions workflows, and demo script
are open-sourced at:

[github.com/MMAUG-ORG/build-ai-app-with-MSFoundry-Azure](https://github.com/MMAUG-ORG/build-ai-app-with-MSFoundry-Azure)

## Recording

A link to the session recording will be added here after the event.
