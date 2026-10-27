---
name: cybersecurity
description: Define controles de segurança e conformidade LGPD para plataformas de dados — classificação, modelo de ameaças, IAM, rede, criptografia, segredos, logs, backup contra ransomware, resposta a incidentes e regulação setorial (BACEN 4.893, SUSEP, ANS, PCI) — em AWS, GCP, Azure, OCI e on-premise/ZimaOS. Use ao revisar uma arquitetura, preparar um DPA ou endurecer um servidor.
---

# Skill — Cybersecurity

## LGPD — o essencial para plataformas de dados
- **Papéis**: o cliente é **controlador**; a consultoria (e as clouds) são **operadoras** e suboperadoras. Contrato (DPA) define instruções, sigilo, subcontratação e devolução/eliminação.
- **Bases legais** (art. 7): execução de contrato, obrigação legal, legítimo interesse (com teste de balanceamento), consentimento, proteção do crédito, entre outras. **Dados sensíveis** (art. 11: saúde, biometria, origem racial, religião, etc.) exigem bases mais restritas.
- **Crianças e adolescentes** (art. 14): melhor interesse; cuidado redobrado.
- **Direitos dos titulares** (art. 18): acesso, correção, anonimização, portabilidade, eliminação — a plataforma precisa conseguir localizar e excluir dados de um titular.
- **Decisões automatizadas** (art. 20): direito de revisão — guardar explicação dos modelos.
- **RIPD** (relatório de impacto) quando houver alto risco ou dado sensível em escala.
- **Incidentes**: comunicar à ANPD e aos titulares em até **3 dias úteis** do conhecimento, quando houver risco ou dano relevante (Resolução CD/ANPD nº 15/2024).
- **Transferência internacional** (art. 33): permitida com mecanismos adequados (cláusulas-padrão aprovadas pela ANPD); setor público/regulado pode exigir dados no Brasil.

## Regulação setorial (pontos de atenção)
- **BACEN** (Res. CMN 4.893/2021; Res. BCB 85/2021 para IPs): política de segurança cibernética, plano de resposta, contratação de nuvem relevante com comunicação ao regulador, acesso do BACEN aos dados, local de armazenamento informado.
- **SUSEP**: segurança cibernética e prestação de informação; seguradoras e corretoras grandes.
- **ANS**: dados de beneficiários (sensíveis).
- **PCI-DSS**: nunca guardar PAN/CVV no data lake; tokenizar na origem.

## Controles mínimos (MVP)
1. **Identidade**: SSO corporativo quando existir; MFA obrigatório; contas nominais; menor privilégio; acesso administrativo just-in-time; sem usuários compartilhados.
2. **Rede**: bancos e buckets privados; acesso por VPN/zero trust (Tailscale, Cloudflare Access, Entra/IAP); nada de RDP/SSH exposto.
3. **Criptografia**: em repouso (chave gerenciada; CMK do cliente se exigido) e em trânsito (TLS 1.2+).
4. **Segredos**: cofre (Secrets Manager, Secret Manager, Key Vault, OCI Vault, OpenBao); rotação; nada em código ou `.env` versionado.
5. **Logs e auditoria**: trilha de acesso a dados pessoais; logs de administração imutáveis por 1 ano (ou o que a regulação pedir).
6. **Backup 3-2-1**: 3 cópias, 2 mídias, 1 fora do site e **imutável** (Object Lock / immutability / retenção bloqueada). Teste de restauração mensal.
7. **Vulnerabilidades**: imagens de contêiner fixadas por versão e escaneadas (Trivy); atualizações mensais; dependências com Dependabot/Renovate.
8. **Dados fora de produção**: mascaramento/pseudonimização ou dados sintéticos.
9. **BI**: RLS por unidade/carteira; exportação de dados pessoais restrita.
10. **LLM**: não enviar dado pessoal a API externa sem base legal e contrato sem treino; filtrar PII antes (Presidio) quando `ia.llm_privacidade = anonimizado`.

## Modelo de ameaças rápido (STRIDE sobre o fluxo)
| Ameaça | Exemplo na plataforma | Controle típico |
|---|---|---|
| Spoofing | Credencial de pipeline vazada | Identidade de carga de trabalho (OIDC), rotação |
| Tampering | Alteração de dados na bronze | Bronze imutável, versionamento, checksums |
| Repudiation | "Não fui eu que exportei" | Logs de acesso com identidade nominal |
| Information disclosure | Bucket público, painel sem RLS | Block Public Access, RLS, DLP |
| Denial of service | Ransomware no servidor on-premise | Backup imutável fora do site, EDR, segmentação |
| Elevation of privilege | Conta de serviço com admin | Papéis mínimos, revisão trimestral |

## Por cloud
| Controle | AWS | GCP | Azure | OCI |
|---|---|---|---|---|
| Identidade | IAM Identity Center + SCPs | Cloud Identity + Org Policies | Entra ID + Conditional Access + PIM | Identity Domains + políticas |
| Postura | Security Hub, GuardDuty, Config | Security Command Center | Defender for Cloud, Azure Policy | Cloud Guard, Security Zones |
| Chaves/segredos | KMS, Secrets Manager | Cloud KMS, Secret Manager | Key Vault (HSM gerenciado) | Vault |
| Rede privada | VPC endpoints, PrivateLink | Private Service Connect, VPC-SC | Private Endpoints | Private Endpoints, Service Gateway |
| Auditoria | CloudTrail, CloudTrail Lake | Cloud Audit Logs | Activity Log, Log Analytics | Audit (365 dias) |
| Backup imutável | S3 Object Lock, AWS Backup Vault Lock | Bucket Lock, Backup vault | Immutable Blob, Backup vault imutável | Retention rules (bloqueadas) |
| Dados | Macie, Lake Formation | Sensitive Data Protection (DLP), policy tags | Purview | Data Safe |
| WAF | AWS WAF, Shield | Cloud Armor | Front Door WAF | OCI WAF |

## On-premise / ZimaOS (servidor da consultoria)
- Nenhuma porta aberta no roteador: acesso por **Tailscale** (rede privada) ou **Cloudflare Tunnel + Access** (com MFA) para a interface web.
- ZimaOS atualizado; senha forte + 2FA no painel; usuário administrador separado do uso diário.
- Contêineres com versão fixa, sem `privileged`, volumes só onde precisam; segredos no `.env` com permissão 600 fora do Git.
- Disco de dados criptografado quando possível; backup criptografado (restic/Kopia) para B2/R2 com Object Lock.
- Separação por cliente: banco, usuário e chave de backup próprios.
- Monitorar: Uptime Kuma (disponibilidade), alertas de disco/temperatura, CrowdSec no proxy.

## Plano de resposta a incidentes (resumo)
1. **Detectar**: alertas de postura, acessos anômalos, falhas de backup.
2. **Conter**: revogar credenciais, isolar recurso, preservar evidências (snapshots, logs).
3. **Avaliar**: dados afetados, titulares, risco; envolver DPO.
4. **Comunicar**: ANPD e titulares (3 dias úteis), cliente imediatamente (operador → controlador).
5. **Recuperar**: restaurar de backup imutável; rotacionar segredos.
6. **Aprender**: relatório e ações corretivas em 15 dias.

## Antipadrões
- "Está na VPN, então é seguro" sem MFA nem log.
- Backup no mesmo servidor/conta que o dado.
- Copiar produção para dev "só para testar".
- Chave de acesso de cloud em planilha ou no código.
