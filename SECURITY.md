# Diretrizes de Segurança Institucional - Regenera Bank

## Estado Atual de Conformidade (Baseline DevSecOps)
Este repositório opera sob a política de **Zero Trust** e **Continuous Security**, assegurado por validações automatizadas e bloqueios em tempo real.

| Pilar de Segurança | Ferramenta / Protocolo | Status de Governança |
| :--- | :--- | :--- |
| **Identidade e Autoria** | GPG (GNU Privacy Guard) | **Enforced**. 100% dos commits exigem assinatura criptográfica amarrada ao e-mail institucional `finance@regenerabank.world`. |
| **Prevenção de Vazamentos (Secret Scanning)** | Gitleaks | **Active**. Varredura profunda em tempo de PR. Regras estritas aplicadas com `Allowlist` mantida em `.gitleaks.toml`. |
| **Análise de Composição (SCA) & IaC** | Trivy (Aqua Security) | **Active**. Bloqueio automático de *Merge* caso vulnerabilidades `HIGH` ou `CRITICAL` sejam detectadas em dependências ou Dockerfiles. |
| **Integração e Deploy Contínuo** | GitHub Actions | **Enforced**. Proteção de branch nativa. A `main` é fisicamente bloqueada para pushes diretos ou PRs com falhas de check. |
| **Isolamento de Ambiente** | 12-Factor App | **Compliant**. Zero credenciais estáticas em código. Variáveis injetadas estritamente em *Build/Runtime*. |

## Auditoria e Padrão ISO
A infraestrutura atende aos requisitos preliminares de esteiras seguras requeridas por normativas do Banco Central (BACEN / OpenBanking) e controles de acesso lógico da ISO/IEC 27001.
