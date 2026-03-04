# Usuários IAM e o Usuário Raiz (Root)

O usuário raiz é a identidade criada juntamente com a conta AWS e possui permissões totais e
irrevogáveis sobre todos os recursos e faturamento.<sup>2</sup> A melhor prática de segurança dita que o
acesso ao usuário raiz deve ser estritamente limitado a tarefas administrativas excepcionais,
como o fechamento da conta ou a alteração de planos de suporte, devendo sempre estar
protegido por dispositivos MFA de hardware ou virtuais.<sup>3</sup> Usuários IAM, por outro lado, são
identidades criadas dentro da conta para representar pessoas ou aplicações específicas,
possuindo credenciais de longo prazo, como senhas de console ou chaves de acesso (Access
Keys).<sup>1</sup> Embora úteis, a tendência moderna de segurança privilegia o uso de roles para evitar aexposição dessas credenciais permanentes.<sup>5</sup>

## Arquitetura e Tipologia de IAM Roles

Diferente de um usuário, uma IAM Role não possui credenciais permanentes. Em vez disso, ela
é uma identidade que pode ser "assumida" por qualquer entidade confiável, recebendo em
troca credenciais de segurança temporárias válidas por um período curto.<sup>4</sup> Esse mecanismo é
operado pelo AWS Security Token Service (STS), que emite tokens que expiram
automaticamente.<sup>4</sup>

|  Categoria de Role  |                               Caso de Uso Principal                              |                             Mecanismo de Confiança                             |
|:-------------------:|:--------------------------------------------------------------------------------:|:------------------------------------------------------------------------------:|
|     Service Role    |              Permite que serviços AWS (EC2, Lambda) ajam em seu nome.            |        Trust Policy aponta para o serviço (ex: lambda.amazonaws.com).<sup>4</sup>        |
| Service-Linked Role | Roles pré-definidas vinculadas diretamente a um serviço para operações internas. | Criadas automaticamente pelo serviço; permissões não editáveis pelo usuário.<sup>4</sup> |
|  Cross-Account Role |                 Delegação de acesso entre diferentes contas AWS.                 |             Trust Policy define o ID da conta externa confiável.<sup>4</sup>             |
|   Federation Role   |            Acesso para usuários autenticados externamente (SAML/OIDC).           |       Trust Policy aponta para um Identity Provider (IdP) configurado.<sup>4</sup>       |

## Federação de Identidade e Acesso Cross-Account

A federação de identidade é a pedra angular da integração empresarial, permitindo que
usuários usem suas credenciais corporativas (via Active Directory ou outros sistemas
Okta/Azure AD) para acessar o console ou a CLI da AWS.<sup>6</sup> O processo utiliza padrões como
SAML 2.0 ou OpenID Connect (OIDC) para estabelecer um canal de confiança onde o IdP
atesta a identidade do usuário e a AWS mapeia essa identidade para uma IAM Role específica.<sup>3</sup>
Isso elimina a necessidade de criar usuários IAM individuais para cada funcionário,
simplificando o offboarding e aumentando a segurança centralizada.<sup>5</sup>

O acesso entre contas (cross-account) resolve o desafio de gerenciar recursos distribuídos em
uma estrutura multi-conta. Uma conta "confiante" cria uma role com uma política de
permissões que define o que pode ser feito e uma política de confiança (trust policy) que
especifica quem na conta "confiável" pode assumir essa role.<sup>4</sup> Para cenários que envolvem
terceiros, a introdução de um "External ID" na condição da política de confiança previne o
problema do "Confused Deputy", garantindo que a role só seja assumida no contexto correto
de um contrato específico.<sup>4</sup>

## Referências citadas

1. AWS IAM Inline vs. Managed Policies - Sysdig, acessado em março 3, 2026,
https://www.sysdig.com/learn-cloud-native/aws-iam-inline-vs-managed-policies

2. What is IAM? - AWS Identity and Access Management, acessado em março 3,
2026, https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html

3. IAM JSON policy elements: Condition - AWS Identity and Access Management,
acessado em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements
_condition.html

4. ​IAM roles - AWS Identity and Access Management, acessado em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html

5. ​Security best practices in IAM - AWS Identity and Access Management, acessado
em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

6. ​Identity providers and federation into AWS - AWS Identity and Access
Management, acessado em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers.html