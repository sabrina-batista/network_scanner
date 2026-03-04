# O Motor de Avaliação de Políticas e Lógica de Decisão

O processo pelo qual a AWS decide se permite ou nega uma solicitação é determinístico e
segue uma sequência lógica rigorosa.<sup>1</sup> Cada chamada de API é submetida a este fluxo de
avaliação que considera todas as camadas de políticas aplicáveis.<sup>3</sup>

## O Fluxograma de Autorização

O motor de avaliação executa os seguintes passos para cada solicitação <sup>1</sup>:

1. 1.​ Negação Padrão: A avaliação começa com uma decisão implícita de "Deny".<sup>1</sup>

2. 2.​ Verificação de Negação Explícita: O motor vasculha todas as políticas aplicáveis
(Identidade, Recurso, SCP, RCP, Boundary). Se encontrar uma única instrução Deny que
corresponda à solicitação, a decisão final é imediatamente "Deny".<sup>1</sup> Este é o princípio de
que "o Deny sempre vence".<sup>2</sup>

3. 3.​ Avaliação de SCPs: A solicitação deve passar pelo filtro da SCP. Se a SCP não permitir a
ação (ou se houver uma negação explícita), o acesso é bloqueado.<sup>1</sup>

4. Avaliação de RCPs: De forma similar às SCPs, as RCPs são verificadas para garantir que
o recurso permite a operação vinda daquele principal.<sup>1</sup>

5. 5.​ Políticas de Recurso: Para alguns serviços (como S3 ou KMS), uma permissão explícita
em uma política de recurso pode conceder acesso, mesmo que não haja uma permissão
na política de identidade (desde que dentro da mesma conta e não bloqueada por
SCP/RCP).<sup>1</sup>

6. Permissions Boundaries e Session Policies: Se presentes, estas camadas atuam como
filtros adicionais. A ação deve ser explicitamente permitida por ambas para que a
avaliação continue.<sup>1</sup>

7. Políticas de Identidade: Finalmente, o motor verifica as políticas anexadas ao usuário ou
role. Deve haver pelo menos uma instrução Allow que corresponda à ação e ao recurso
solicitado.<sup>1</sup>

## Implicações Práticas da Lógica de Avaliação

A compreensão deste fluxo é crucial para o troubleshooting de permissões. Um erro comum
de configuração ocorre quando um administrador concede acesso em uma política de
identidade, mas esquece que uma SCP ou uma Permissions Boundary está bloqueando
silenciosamente a ação.<sup>3</sup> Além disso, a lógica de avaliação diferencia entre solicitações feitas
dentro da mesma conta e solicitações cross-account. No cenário cross-account, a confiança
deve ser estabelecida em ambas as pontas: a conta A deve permitir que seu usuário assuma a
role, e a conta B deve ter uma política de confiança que aceite identidades da conta A.<sup>1</sup>

## Referências citadas

1. AWS IAM: Policy Evaluation Logic — EXPLAINED | by Mehrdad Mohsenizadeh -
Medium, acessado em março 3, 2026,
https://medium.com/@mehrdadmohsenizadeh/aws-iam-policy-evaluation-logic-
0ba377e8fdaf

2. ​What is IAM Policy Evaluation? | Logic Explained | Tutorial for Beginners - YouTube,
acessado em março 3, 2026, https://www.youtube.com/watch?v=V8DTJ3FTS9c

3. Untangle AWS IAM Policy Logic and Move Toward Least Privilege - Sonrai
Security, acessado em março 3, 2026,
https://sonraisecurity.com/blog/untangle-aws-iam-policy-logic/