# A Estrutura Fundamental da Linguagem de Políticas IAM

O cerne do sistema de autorização da AWS é o documento de política IAM, uma estrutura
declarativa escrita em JSON que define as permissões.<sup>2</sup> Essas políticas não operam de forma
isolada; elas são processadas por um motor de avaliação altamente determinístico que analisa
cada solicitação de API enviada aos serviços da AWS.<sup>3</sup> A composição técnica de uma instrução
de política (statement) é rigorosamente estruturada em quatro pilares fundamentais: o Efeito, a
Ação, o Recurso e a Condição.<sup>4</sup>

## Os Elementos Centrais do Esquema JSON

Cada política pode conter uma ou mais instruções que definem a lógica de acesso. O elemento
"Effect" (Efeito) é o interruptor binário da instrução, podendo assumir os valores Allow (Permitir)
ou Deny (Negar).<sup>6</sup> É imperativo notar que a AWS opera sob um modelo de "negação padrão", o
que implica que qualquer ação não explicitamente permitida é automaticamente bloqueada.<sup>3</sup>
O elemento "Action" (Ação) descreve a operação específica que está sendo permitida ou
negada, utilizando um prefixo de serviço seguido pelo nome da operação, como s3:ListBucket
ou ec2:RunInstances.<sup>2</sup> O "Resource" (Recurso) identifica os objetos sobre os quais a ação pode
ser executada, utilizando o formato Amazon Resource Name (ARN) para garantir unicidade
global.<sup>5</sup> Por fim, o elemento "Condition" (Condição) permite a introdução de lógica booleana
sofisticada, restringindo a validade da permissão a circunstâncias específicas, como o intervalo
de tempo, o endereço IP de origem ou a presença de autenticação multifatorial (MFA).<sup>4</sup>

| Elemento de Política |                   Função Arquitetural                   |          Exemplos de Implementação          |
|:--------------------:|:-------------------------------------------------------:|:-------------------------------------------:|
|        Version       |        Define a versão da linguagem da política.        |            Geralmente 2012-10-17.           |
|       Statement      |        Bloco contêiner para os elementos lógicos.       | Pode conter múltiplos objetos de instrução. |
|        Effect        | Determina o resultado da avaliação (Permissão/Negação). |                Allow, Deny.<sup>3</sup>                |
|        Action        |         Especifica a operação da API do serviço.        |       dynamodb:GetItem, kms:Decrypt.<sup>1</sup>       |
|       Resource       |              Define o alvo da ação via ARN.             |       arn:aws:s3:::nome-do-bucket/*.<sup>2</sup>       |
|       Condition      |         Estabelece restrições contextuais finas.        |       aws:SourceIp, aws:CurrentTime.<sup>2</sup>       |

## Dinâmicas de Chaves de Condição e Autorização Contextual

As chaves de condição representam a camada mais avançada de controle, permitindo a
implementação do Controle de Acesso Baseado em Atributos (ABAC).<sup>7</sup> Existem chaves de
condição globais, prefixadas por aws:, que são aplicáveis a todos os serviços, como
aws:PrincipalOrgID, que limita o acesso apenas a entidades dentro de uma organização
específica.<sup>8</sup> Chaves específicas de serviço atendem a necessidades particulares de cada
recurso; por exemplo, o Amazon S3 suporta chaves como s3:x-amz-server-side-encryption
para garantir que apenas objetos criptografados sejam carregados.<sup>2</sup>

## Referências citadas

1. Reference information for AWS Identity and Access Management ..., acessado em
março 3, 2026,
https://docs.aws.amazon.com/service-authorization/latest/reference/reference.ht
ml

2. How to Guide for AWS Service Reference Information and Condition Keys -
Medium, acessado em março 3, 2026,
https://medium.com/@Nelsonalfonso/how-to-guide-for-aws-service-reference-i
nformation-and-condition-keys-58b92245aa72

3. AWS IAM: Policy Evaluation Logic — EXPLAINED | by Mehrdad Mohsenizadeh -
Medium, acessado em março 3, 2026,
https://medium.com/@mehrdadmohsenizadeh/aws-iam-policy-evaluation-logic-
0ba377e8fdaf

4. IAM JSON policy elements: Condition - AWS Identity and Access Management,
acessado em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements
_condition.html

5. IAM JSON policy elements: Resource - AWS Identity and Access Management,
acessado em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements
_resource.html

6. IAM JSON policy elements: Effect - AWS Identity and Access Management,
acessado em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements
_effect.html

7. Managed policies and inline policies - AWS Identity and Access Management,
acessado em março 3, 2026,
https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-v
s-inline.html

8. ​AWS Resource Control Policies (RCPs): Everything You Need To Get Started -
Cyscale, acessado em março 3, 2026,
https://cyscale.com/blog/aws-resource-control-policies/