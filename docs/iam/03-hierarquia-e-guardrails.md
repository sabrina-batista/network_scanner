# Managed Policies vs. Inline Policies

As políticas podem ser categorizadas pela forma como são gerenciadas e aplicadas. Políticas
Gerenciadas pela AWS (AWS Managed Policies) são criadas e mantidas pela própria Amazon
para funções de trabalho comuns, como AdministratorAccess ou ReadOnlyAccess.<sup>1</sup> Políticas
Gerenciadas pelo Cliente (Customer Managed Policies) oferecem maior controle, permitindo
que a organização crie versões próprias e aplique o princípio do privilégio mínimo.<sup>1</sup> Em
contraste, as Políticas Inline são incorporadas diretamente em um único usuário, grupo ou role,
criando uma relação de um-para-um que é difícil de escalar e não suporta versionamento,
sendo recomendadas apenas para exceções estritas onde a permissão deve ser deletada
juntamente com a identidade.<sup>1</sup>

| Tipo de Política |  Reusabilidade  |    Versionamento    |       Limite de Caracteres       |
|:----------------:|:---------------:|:-------------------:|:--------------------------------:|
|    AWS Managed   |  Alta (Global)  |    Sim (pela AWS)   |     Até 6.144 por política.<sup1</sup>     |
| Customer Managed | Alta (Na conta) | Sim (até 5 versões) |     Até 6.144 por política.<sup>1</sup>     |
|      Inline      |     Nenhuma     |         Não         | 2.048 (Usuário), 10.240 (Role).<sup>1</sup> |

## Service Control Policies (SCPs) e Resource Control Policies (RCPs)

No nível organizacional (AWS Organizations), as SCPs atuam como filtros centrais que limitam
as permissões máximas para todas as contas membros.<sup>5</sup> Uma SCP pode, por exemplo, impedir
que qualquer usuário (incluindo o root) em uma conta de produção delete logs do CloudTrail
ou utilize serviços em regiões não autorizadas.<sup>5</sup> É vital compreender que as SCPs não
concedem permissões; elas apenas estabelecem um teto sobre o qual as políticas IAM da
conta podem operar.<sup>6</sup>

Recentemente, a AWS introduziu as Resource Control Policies (RCPs) como um complemento
às SCPs para fortalecer o perímetro de dados.<sup>7</sup> Enquanto as SCPs focam no que as
identidades podem fazer, as RCPs focam no que pode ser feito com os recursos da
organização, independentemente de quem está fazendo a solicitação.<sup>4</sup> Elas permitem, por
exemplo, garantir que nenhum bucket S3 na organização seja acessível por qualquer principal
externo, mesmo que um administrador de conta crie acidentalmente uma política de bucket
excessivamente permissiva.<sup>4</sup> No lançamento, as RCPs suportam serviços críticos de dados
como S3, STS, KMS, SQS e Secrets Manager.<sup>7</sup>

## Permissions Boundaries (Limites de Permissões)

As Permissions Boundaries são uma funcionalidade avançada usada para delegar o
gerenciamento de permissões sem o risco de escalação de privilégios.<sup>3</sup> Um administrador
pode permitir que um desenvolvedor crie roles IAM para suas funções Lambda, mas anexar
uma Boundary a esse desenvolvedor que o impede de criar qualquer role com privilégios de
administrador. A permissão efetiva resultante é a intersecção entre a política de identidade e aPermissions Boundary.<sup>2</sup>

## Referências citadas

1. AWS IAM Inline vs. Managed Policies - Sysdig, acessado em março 3, 2026,
https://www.sysdig.com/learn-cloud-native/aws-iam-inline-vs-managed-policies

2. AWS IAM: Policy Evaluation Logic — EXPLAINED | by Mehrdad Mohsenizadeh -
Medium, acessado em março 3, 2026,
https://medium.com/@mehrdadmohsenizadeh/aws-iam-policy-evaluation-logic-
0ba377e8fdaf

3. Managed policies and inline policies - AWS Identity and Access Management,
acessado em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-v
s-inline.html

4. ​AWS Resource Control Policies (RCPs): Everything You Need To Get Started -
Cyscale, acessado em março 3, 2026,
https://cyscale.com/blog/aws-resource-control-policies/

5. ​Untangle AWS IAM Policy Logic and Move Toward Least Privilege - Sonrai
Security, acessado em março 3, 2026,
https://sonraisecurity.com/blog/untangle-aws-iam-policy-logic/

6. ​Service control policies (SCPs) - AWS Organizations, acessado em março 3, 2026,
https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_polici
es_scps.html

7. ​Introducing resource control policies (RCPs) to centrally restrict access to ... -
AWS, acessado em março 3, 2026,
https://aws.amazon.com/about-aws/whats-new/2024/11/resource-control-policie
s-restrict-access-aws-resources/