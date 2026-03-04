# Ciclo de Vida de Credenciais e Automação de Rotação

A gestão de segredos é um dos componentes mais críticos da segurança em nuvem. A AWS
desencoraja fortemente o uso de credenciais de longo prazo, promovendo o uso de tokens
temporários sempre que possível.<sup>2</sup>

## Credenciais Temporárias via STS e IAM Roles Anywhere

As IAM Roles fornecem segurança superior porque suas credenciais expiram
automaticamente.<sup>3</sup> Para cargas de trabalho que residem fora da AWS (em servidores
on-premises, por exemplo), o serviço "IAM Roles Anywhere" permite que essas máquinas
utilizem certificados X.509 de uma infraestrutura de chave pública (PKI) confiável para obter
credenciais temporárias da AWS.<sup>2</sup> Isso elimina a necessidade de armazenar Access Keys
permanentes em sistemas de arquivos locais, que são vulneráveis a exfiltração.<sup>2</sup>

## Rotação Automatizada com AWS Secrets Manager

Para cenários onde senhas ou chaves de API são necessárias, o AWS Secrets Manager oferece
um framework de rotação automatizada.<sup>6</sup> Integrado nativamente com serviços como RDS,
Redshift e DocumentDB, o Secrets Manager pode rotar senhas sem intervenção humana,
utilizando funções Lambda para atualizar tanto o segredo quanto o recurso alvo.<sup>6</sup>

|   Aspecto da Rotação  |                              Mecanismo de Implementação                             |                       Benefício de Segurança                       |
|:---------------------:|:-----------------------------------------------------------------------------------:|:------------------------------------------------------------------:|
|      Agendamento      |            Definição de janelas (ex: a cada 30 dias) no Secrets Manager.            |      Limita a validade temporal de um segredo comprometido.<sup>2</sup>      |
|   Lógica de Rotação   |                 Função Lambda customizada ou modelos pré-definidos.                 | Garante que a troca de senha siga os requisitos do sistema alvo.<sup>6</sup> |
| Estratégia de Usuário | Alternância entre dois usuários (User A/User B) ou troca de senha de usuário único. |  Evita downtime durante o processo de atualização da credencial.<sup>7</sup> |
|     Auditabilidade    |                 Logs de rotação enviados ao CloudWatch e CloudTrail.                |    Fornece trilha de auditoria para conformidade regulatória.<sup>6</sup>    |

A rotação eficiente frequentemente envolve manter duas versões do segredo válidas
simultaneamente por um breve período: a versão "corrente" (AWSCURRENT) e a versão
"anterior" (AWSPREVIOUS).<sup>8</sup> Isso permite que aplicações que já buscaram o segredo
continuem funcionando enquanto a nova versão é propagada, garantindo alta disponibilidade
em sistemas distribuídos.<sup>8</sup>

## IAM Access Analyzer e Geração de Políticas

O IAM Access Analyzer é a ferramenta primária para identificar acessos não intencionais. Eleanalisa políticas de recursos para sinalizar quais buckets S3, chaves KMS ou roles IAM são
acessíveis de fora da conta ou organização.<sup>1</sup> Além disso, o Access Analyzer pode analisar logs
do CloudTrail para gerar sugestões de políticas baseadas na atividade real.<sup>5</sup> Se uma aplicação
usou apenas três ações de S3 nos últimos 90 dias, o Access Analyzer pode gerar
automaticamente uma política contendo apenas essas três ações, substituindo uma política
s3:* excessivamente ampla.<sup>4</sup>

## Informações de Último Acesso (Last Accessed Information)

O console do IAM fornece dados sobre quando cada permissão foi utilizada pela última vez
por um usuário ou role.<sup>4</sup> Esta informação é vital para o saneamento de credenciais; se um
usuário tem permissão para o Amazon RDS mas não a utiliza há seis meses, essa permissão
pode ser removida com segurança, reduzindo o raio de explosão em caso de
comprometimento daquela identidade.<sup>4</sup>

## Referências citadas

1. What is IAM? - AWS Identity and Access Management, acessado em março 3,
2026, https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html

2. ​SEC02-BP05 Audit and rotate credentials periodically - Security Pillar - AWS
Documentation, acessado em março 3, 2026,
https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/sec_identities_
audit.html

3. ​IAM roles - AWS Identity and Access Management, acessado em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html

4. ​Security best practices in IAM - AWS Identity and Access Management, acessado
em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

5. ​AWS IAM Access Analyzer, acessado em março 3, 2026,
https://aws.amazon.com/iam/access-analyzer/

6. ​Automate Amazon RDS credential rotation with AWS Secrets Manager for primary
instances with read replicas, acessado em março 3, 2026,
https://aws.amazon.com/blogs/database/automate-amazon-rds-credential-rotati
on-with-aws-secrets-manager-for-primary-instances-with-read-replicas/

7. .​Rotate AWS Secrets Manager secrets, acessado em março 3, 2026,
https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.
html

8. ​Rotation of Secrets with AWS Secrets Manager - Mechanical Rock, acessado em
março 3, 2026,
https://www.mechanicalrock.io/blog/rotation-of-secrets-with-aws-secrets-manager