---
name: devops
description: Infraestrutura como código (OpenTofu/Terraform), CI/CD com GitHub Actions via OIDC, contêineres, observabilidade, backup e DR para plataformas de dados em AWS, GCP, Azure, OCI e on-premise/ZimaOS com Docker Compose e GPU NVIDIA. Use ao provisionar ambientes, automatizar deploy de pipelines dbt/Dagster, montar monitoramento ou escrever runbooks.
---

# Skill — DevOps

## Repositório padrão por cliente
```
cliente-<slug>/
├── infra/            # OpenTofu: modules/ + envs/{dev,prod}/
├── ingestao/         # pipelines dlt (Python)
├── transformacao/    # projeto dbt
├── orquestracao/     # definições Dagster (assets, schedules, sensors)
├── automacoes/       # fluxos n8n exportados (JSON)
├── bi/               # exportações de painéis / modelos semânticos
├── docker/           # Dockerfile e compose
└── .github/workflows/
```
Trunk-based: PR com revisão → merge na `main` → deploy em dev automático → produção com aprovação manual.

## Alvo de execução por porte
| Porte | Alvo | Por quê |
|---|---|---|
| P | 1 VM (ou ZimaOS) com Docker Compose: Dagster + dbt + dlt + Metabase + Postgres | Mínimo de peças; ~R$ 0–500/mês |
| M | Contêineres serverless (Fargate, Cloud Run, Container Apps, OCI Container Instances) + serviços gerenciados de dados | Sem servidor para manter; paga o que roda |
| G | Kubernetes gerenciado (EKS, GKE Autopilot, AKS, OKE) + Helm | Muitos pipelines, escalonamento, isolamento |

## OpenTofu/Terraform
- Estado remoto com lock: S3 (lock nativo `use_lockfile`), GCS, Azure Storage (lease), OCI Object Storage (backend S3-compatível ou Resource Manager).
- Tags/labels obrigatórias: `cliente`, `ambiente`, `projeto`, `centro_custo`, `gerenciado_por=opentofu` — o FinOps depende disso.
- Módulos pequenos: `rede`, `armazenamento`, `warehouse`, `execucao`, `observabilidade`, `seguranca`.
- `tofu plan` no PR (comentário automático), `apply` só após merge/aprovação.

## CI/CD com GitHub Actions (sem segredo fixo)
| Cloud | Autenticação | Ação |
|---|---|---|
| AWS | OIDC → IAM Role | `aws-actions/configure-aws-credentials` |
| GCP | Workload Identity Federation | `google-github-actions/auth` |
| Azure | OIDC → federated credential | `azure/login` |
| OCI | API key no cofre do repositório | `oracle-actions/configure-oci-credentials` |
| ZimaOS | Tailscale na action + SSH com chave restrita | `tailscale/github-action` |

Etapas: `ruff` + `sqlfluff` → `pytest` → `dbt build --select state:modified+` contra dev → build/push de imagem (tag = SHA) → deploy → `dbt test` em produção → notificação.

## Observabilidade mínima
- **Pipelines**: sucesso/falha por asset (Dagster), duração, linhas carregadas.
- **Frescor**: `dbt source freshness` e checagem do último dado em cada mart.
- **Infra**: CPU, RAM, disco (alerta em 80%), temperatura (on-prem).
- **Custo**: orçamento mensal com alertas em 50/80/100% (ver FinOps).
- **Disponibilidade**: Uptime Kuma (on-prem) ou monitoramento sintético da cloud para BI e API.
- Canal de alerta: WhatsApp/Telegram/Teams via n8n; e-mail como redundância.

## Backup e DR
| RTO / RPO declarado | Estratégia |
|---|---|
| dias / 24 h | Backup diário (dump + bronze em object storage) fora do site; restauração manual documentada |
| horas / 1 h | Backups a cada hora (WAL/PITR), IaC pronta para recriar em outra região/zona, ensaio semestral |
| minutos / ~0 | Banco gerenciado multi-AZ + réplica entre regiões; front em DNS com failover; custo alto, só com justificativa |

## ZimaOS (servidor da consultoria) — operação
- Apps em `/DATA/AppData/<app>`; compose do projeto em `/DATA/AppData/plataforma`.
- GPU NVIDIA: confirme com `nvidia-smi`; no compose, `deploy.resources.reservations.devices` com `driver: nvidia`.
- Atualização: `docker compose pull && docker compose up -d` em janela combinada; versões fixadas no `.env`.
- Backups: restic diário de `/DATA/AppData/plataforma` (exceto modelos do Ollama, que se baixam de novo) para B2/R2.
- Acesso remoto: Tailscale (admin) e Cloudflare Tunnel (questionário público para clientes).
Detalhes em `infra/zimaos/README.md`.

## Por cloud — peças de infraestrutura
| | AWS | GCP | Azure | OCI |
|---|---|---|---|---|
| Rede | VPC + endpoints | VPC + PSC | VNet + Private Endpoints | VCN + Service Gateway |
| Contêiner serverless | ECS Fargate | Cloud Run | Container Apps | Container Instances |
| Kubernetes | EKS | GKE Autopilot | AKS | OKE |
| Registro de imagens | ECR | Artifact Registry | ACR | OCIR |
| Logs/métricas | CloudWatch | Cloud Logging/Monitoring | Azure Monitor | Logging/Monitoring |
| Agendamento | EventBridge Scheduler | Cloud Scheduler | Container Apps jobs (cron) | Resource Scheduler |
| IaC nativa | CloudFormation/CDK | Infrastructure Manager | Bicep | Resource Manager |

## Runbooks essenciais
1. Pipeline falhou → ver log do asset → reprocessar intervalo → se a fonte mudou de schema, abrir tarefa para o Engenheiro.
2. Fonte fora do ar → marcar painel como "dados de <data>" → avisar o dono → reprocessar ao voltar.
3. Disco cheio → limpar artefatos antigos/logs → ampliar volume → revisar retenção da bronze.
4. Restauração → seguir o procedimento, medir tempo, registrar.

## Antipadrões
- Kubernetes para 3 pipelines diários.
- Imagens `latest` em produção.
- Credencial de admin no CI.
- Alertas por e-mail que ninguém lê.
