# Governança do Design System

**Documento:** DS-GOV-001  
**Responsável:** Don Paulo Ricardo  
**Revisão:** trimestral ou após incidente de interface  
**Aplicabilidade:** tokens, componentes, conteúdo visual e saídas de plataforma

## Objetivo

Manter uma fonte única para decisões visuais que afetam leitura, confirmação, erro e estado financeiro.

Cor não substitui texto.
Animação não substitui estado.
Interface não inventa resultado.

## Papéis

| Papel | Responsabilidade | Pode aprovar o próprio trabalho |
|---|---|---|
| Technical Owner | mantém fonte canônica e evidência | não |
| Accessibility Reviewer | valida contraste, foco, leitura e interação | não |
| Security Reviewer | valida cadeia de dependências e conteúdo sensível | não |
| Change Authority | autoriza promoção institucional | não |

A identidade nominal do Technical Owner está em `governance/owners.json`.
Os revisores independentes devem ser vinculados antes da adoção institucional.

## Controles obrigatórios

1. token muda em um lugar só;
2. build gera as quatro plataformas;
3. contraste crítico não recebe exceção;
4. estado `unknown` nunca oferece repetição cega;
5. release exige teste, manifesto e hash;
6. autor não aprova a própria mudança;
7. exceção possui prazo e dono;
8. evidência ausente bloqueia promoção.

## Fluxo de mudança

1. registrar motivo e risco;
2. alterar fonte canônica;
3. gerar saídas;
4. executar testes;
5. revisar impacto por plataforma;
6. obter revisão independente;
7. assinar commit e release;
8. promover;
9. observar regressão;
10. reverter se a leitura ou a operação ficarem ambíguas.

## Exceções

Exceção sem prazo vira regra escondida.

Toda exceção registra:

- controle afetado;
- risco aceito;
- autoridade;
- data de expiração;
- compensação;
- evidência;
- plano de encerramento.

Contraste, autoaprovação e repetição cega de transação não aceitam exceção.

## Evidências

- manifesto de arquivos;
- checksums;
- resultado dos testes;
- relatório de segurança;
- inventário de dependências;
- aprovação nominal;
- assinatura criptográfica;
- plano de rollback.

## Métricas

- violações de contraste: zero;
- divergências entre plataformas: zero;
- componentes sem foco visível: zero;
- releases autoaprovadas: zero;
- arquivos sem owner: zero;
- diferenças em build repetido: zero.

## Violação

Mudança que quebra controle bloqueante não entra.
Prazo comercial não muda isso.
