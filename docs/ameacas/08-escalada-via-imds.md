# O Efeito Cascata na Arquitetura AWS: Do Acesso ao Plano de Controle e Roubo de Credenciais via IMDS

A principal e mais profunda conclusão analítica que emerge, transcendendo as minúcias
técnicas e exploratórias de portas individuais específicas (seja a 22, 3389, 3306, 5432, 6379 ou
27017), é que no vasto ecossistema cibernético moderno de um provedor de infraestrutura
(notadamente a AWS), um host de aplicação raramente atua meramente como o ponto
terminal no plano estratégico e arquitetônico de um invasor cibernético.<sup>2</sup> A exposição
intencional ou acidental dessas portas atua, de forma inequívoca, como a cabeça de ponte – a
ponta de lança – para a iniciação de um vetor cibernético formidavelmente mais elusivo,
expansivo e devastador: a movimentação lateral baseada em identidade de nuvem.

Em paradigmas superados e data centers on-premises do passado, se um atacante lograsse
comprometer com sucesso um servidor de cache Redis isolado por meio de injeção de tarefas
cronéricas (cron jobs), o escopo geral da catástrofe estava logicamente restrito ao acesso às
VLANs (redes virtuais locais) internas mecanicamente conectadas àquele único equipamento
de rede e ao hardware do chassi subjacente.<sup>2</sup> Na infraestrutura orientada por software da
Amazon Web Services, um servidor provisionado não é mais apenas hardware genérico.

Trata-se de uma instância EC2 intrinsecamente imersa em uma arquitetura de controle definida
por software abrangente, portadora de um mecanismo onipresente de autodescoberta de
identidade e autorização incrivelmente privilegiado e sensível, categorizado como o Instance
Metadata Service (IMDS).<sup>2</sup> O IMDS desempenha a função de fornecer localmente, e sem a
necessidade de chaves estáticas (hardcoded) em código-fonte, um fluxo constante de dados
de configuração vitais, metadados da instância e, o mais importante, chaves de credenciais
temporárias para interagir de maneira fluidamente autenticada com outros serviços da nuvem(como depósitos S3, DynamoDB, ou KMS) de maneira autônoma.<sup>2</sup>

## A Dinâmica do Mecanismo de Abuso do IMDS e a Fuga do Perímetro

O IMDS foi desenhado para ser acessível única e exclusivamente a partir da própria instância
EC2, operando por meio de comunicações seguras direcionadas a um endereço de rede IP de
link-local rigorosamente fixo e não roteável externamente: 169.254.169.254.<sup>2</sup> A premissa de
segurança primária da AWS, intrínseca ao seu design inicial (notoriamente em sua primeira
iteração flexível, o IMDSv1), fundamentava-se em um modelo de confiança: supunha-se
implicitamente que apenas scripts de shell, aplicações em contêineres e códigos rodando de
boa-fé e previamente validados operando dentro do perímetro lógico da própria instância
tentariam contatar esse terminal privilegiado.<sup>2</sup> Contudo, esse paradigma desmorona
totalmente se um agente malicioso, por qualquer vetor, conseguir alavancar uma interface de
rede para comandar a emissão de requisições nascendo diretamente do interior do sistema da
instância EC2. Se o atacante estabelece um shell interativo completo ao explorar e
comprometer as credenciais SSH (na porta 22) <sup>3</sup>, se invoca e força a execução de um comando
arbitrários de sistema operacional via vulnerabilidade RCE no PostgreSQL (COPY FROM
PROGRAM) trafegando pela porta 5432 <sup>6</sup>, se implementa e dispara um script oculto alojado
dentro do cron do Redis operando sob a porta 6379 <sup>7</sup>, ou contorna as barreiras de filtragem
com engenharias complexas utilizando Server-Side Request Forgery (SSRF) visando aplicações
desprotegidas – o objetivo estratégico iminente, invariável e imediato do ator de ameaça
torna-se a exfiltração de chaves temporárias do IAM via IMDS.<sup>2</sup>

Um invasor proficiente conectado de forma não autorizada a qualquer um desses serviços
abertos executará taticamente as seguintes etapas lógicas sequenciais para comprometer
completamente a integridade do ambiente IAM do tenant (locatário) na AWS <sup>2</sup>:

1. Invocação Básica e Reconhecimento da Role: Inicialmente, a partir do prompt de
comando interno do servidor, o invasor realizará uma chamada e requisição HTTP
simples de reconhecimento, disparando nativamente: curl
http://169.254.169.254/latest/meta-data/iam/security-credentials/.<sup>2</sup>

2. Descoberta Dinâmica da Identidade: Esta requisição não protegida resultará na
resposta de listagem, pelo IMDS, do nome exato da função (IAM Role) atualmente
atrelada à permissão da instância em execução (por exemplo,
app-worker-database-role).<sup>2</sup> De posse do nome exato, o invasor formula uma segunda
e letal requisição direta para a raiz da credencial, anexando o nome recém-coletado ao
fim da URI consultada: curl
http://169.254.169.254/latest/meta-data/iam/security-credentials/app-worker-database-r
ole.<sup>2</sup>

3. Extração das Chaves Efêmeras: Em pronta resposta a esta solicitação aparentemente
legítima e internalizada, o microsserviço IMDS devolve na saída padrão (stdout) um
documento estruturado em formato JSON legível. Este documento valiosíssimo compila
sem restrições a chave de acesso pública (AccessKeyId), a correspondente chave de
acesso secreta e rigorosamente confidencial (SecretAccessKey), bem como o crucial e
vinculante token de autenticação de sessão gerado pelo AWS STS (Security TokenService) (Token).<sup>2</sup>

4. Exportação, Configuração Remota e Dominação: Utilizando comandos e funções
copiados, o atacante empacota furtivamente e exporta remotamente (exfiltração) esse
lote de credenciais sigilosas contidas no JSON diretamente para sua própria máquina e
estação de trabalho remota operando inteiramente fora do escopo da rede da AWS
controlada pela vítima. Utilizando o utilitário flexível AWS Command Line Interface (AWS
CLI) a partir de seu laptop remoto em outra jurisdição, o invasor implanta localmente os
tokens em seu arquivo ~/.aws/credentials. A partir desse instante fatídico, comandos
externos subsequentes, como a listagem ostensiva de repositórios (aws s3 ls), ou
requisições severas e onerosas de criação de frota de novos servidores (aws ec2
run-instances), passarão a ser invariavelmente interceptados e aceitos como legítimos e
chancelados com todo o peso e poder da identidade corporativa confiável, tornando o
atacante em um administrador sombra dentro da nuvem corporativa sem possuir uma
conta cadastrada formalmente no provedor.<sup>3</sup>

Esses padrões técnicos indeléveis confirmam sem margem para dúvidas que, ao abrir
descuidadamente uma única porta como a 27017 associada ao banco MongoDB, ou expor
indevidamente o portal 3306 atrelado aos bancos relacionais MySQL utilizando o seletor
universal de 0.0.0.0/0, o engenheiro de arquitetura de nuvem ou desenvolvedor inexperiente
não está meramente criando o risco e arriscando passivamente a integridade, manipulação ou
destruição dos dados confidenciais ali diretamente mantidos naquela base isolada.<sup>4</sup> Pela
arquitetura da AWS, ele está em essência cedendo livre e graciosamente, de forma direta nas
mãos de atacantes, verdadeiras chaves mestras e efêmeras para transitar pelo "reino" em
nuvem da organização de forma furtiva, camuflada na própria infraestrutura e invisível a
firewalls de borda.<sup>2</sup>

Este modelo letal e transversal resultou em falhas colossais e comprometimentos que
moldaram a indústria e geraram danos monetários estratosféricos. Incidentes notórios
refletem de forma brutal essas deficiências de configuração. O devastador vazamento da
provedora de cartões Capital One enquadra-se rigorosamente nesse princípio: uma aplicação
Web Application Firewall (WAF) mal configurada serviu perfeitamente como o canal remoto
intermediário indispensável para processar de forma não mitigada ataques na forma de SSRF.

Este vetor exploratório engenhoso e subversivo conseguiu induzir diretamente a infraestrutura
afetada a se conectar ativamente ao IMDS e enumerar os amplos recursos de nuvem globais,
varrendo de forma automatizada bases conectadas que, ironicamente, estavam em redes
supostamente não roteáveis à internet. Como consequência avassaladora e irrefreável da
extração do token, as permissões associadas foram instantaneamente abusadas, garantindo
passe livre para uma exfiltração dramática e não detectada em massa de mais de 100 milhões
de registros altíssimos, históricos e sensíveis pertencentes a clientes bancários sediados
pacificamente em caixas de armazenamento estático (Buckets S3), que anteriormente
acreditavam possuir proteções inexpugnáveis.<sup>5</sup> A exploração irrestrita dessa fraqueza e
deficiência persistiu com vazamentos sistêmicos ocorrendo frequentemente. Plataformas
amplas sofreram choques idênticos de controle de dados causados por credenciais acessíveis
de funcionários; incidentes corporativos, a exemplo do vazamento catastrófico da plataformaTwitch (onde cerca de 125 Gigabytes da estrutura e código inteiro confidencial fluíram
irremediavelmente devido a uma má configuração de servidor desatenta), sublinham ainda
mais o imperativo universal na nuvem: toda identidade comprometida resulta de forma
unânime e certeira em uma cascata sem freios de danos reputacionais que são incontroláveis a
longo prazo.<sup>5</sup> Na brecha reportada e atribuída em infraestruturas como a operada pela
empresa Ubiquiti no evento marcante ocorrido em 2021, o atacante – utilizando os privilégios
amplos e insondáveis originários da obtenção inicial – expandiu sorrateira e horizontalmente
suas amarras em todos os níveis dos ecossistemas de desenvolvimento de software
subjacentes, culminando atrozmente em um enraizamento tão onipresente, complexo e
profundo nos registros e arquivos do provedor da nuvem e dos diretórios essenciais do
sistema da própria AWS que pesquisadores céticos questionavam tecnicamente se a
extirpação crível das ramificações ou persistências persistentes seria sequer possível ser
alcançada em sua completude.<sup>9</sup>

As proteções subsequentes, mitigadoras e de vanguarda projetadas e propostas pelo
provedor – nomeadamente a adoção vigorosamente forçada em todos os serviços novos da
segunda versão da arquitetura do metadados, conhecida na documentação como o seguro e
restritivo IMDSv2 – implementaram barreiras técnicas imponentes para barrar estes vetores
autônomos. A implementação atual desta arquitetura introduziu com severidade mandamental
restrições rígidas no ciclo das chamadas locais, como a obrigatória obrigatoriedade no
fornecimento e verificação do controle rígido de tokens embutidos profundamente em
cabeçalhos HTTP fixos (HttpTokens: required) durante cada transação e a rigorosa estipulação
e exigência restritiva de estritos limites máximos e intransponíveis do limite contábil de saltos e
encaminhamentos lógicos na rede de comunicação IP (HttpPutResponseHopLimit: 1).<sup>8</sup> Tais
adições engenhosas de defesa de fato blindaram efetivamente a estrutura subjacente e
reduziram massivamente o risco contra métodos que exploram chamadas curtas indiretas que
fluem utilizando a porta do navegador, que invariavelmente constituíam o cerne avassalador
das extrações via SSRF clássico.<sup>8</sup> Entretanto, no complexo arranjo que une vulnerabilidades em
sistemas remotos expostos na porta principal com privilégios completos adquiridos
internamente (um comprometimento total local da infraestrutura onde o atacante consolida
um escudo de proteção operando na máquina da vítima), se o indivíduo pernicioso detiver a
integridade e autoridade completa na camada superior para operar em ambiente interativo,
originando-se validamente a partir de uma conexão SSH irrestrita e não blindada, em uma
conexão de sistema ininterrupta estabelecida sorrateiramente através de falhas de banco de
dados como o Redis, ou através do domínio amplo oriundo e de credenciais de login falhas
associadas no RDP não restrito adequadamente por regras, tais proteções de limitação
temporal podem infelizmente ainda ser circunavegadas sem grande esforço metodológico.<sup>3</sup>

Esta constatação perturbadora demonstra e sublinha de modo irrefutável e perene que, na
vasta rede da nuvem e sob o modelo compartilhado vigente, nenhuma restrição virtual de
limitação de escopo pode genuinamente mitigar e anular o fato consumado e inegável do
próprio acesso concedido na máquina virtual; a fundação absoluta, final e não maleável sobre
as fronteiras protetoras da rede deve imperativamente repousar no rigor exato das fronteiras
invioláveis configuradas e mantidas estritamente no próprio portão de acesso virtual dainstância (o Security Group) implementado.<sup>1</sup>

## Referências citadas

1. Control traffic to your AWS resources using security groups - Amazon Virtual
Private Cloud, acessado em fevereiro 27, 2026,
https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html

2. ​IMDS Abused: Hunting Rare Behaviors to Uncover Exploits | Wiz Blog, acessado
em fevereiro 27, 2026, https://www.wiz.io/blog/imds-anomaly-hunting-zero-day

3. Threat news: TeamTNT stealing credentials using EC2 Instance Metadata | Sysdig,
acessado em fevereiro 27, 2026,
https://www.sysdig.com/blog/teamtnt-aws-credentials

4. Millions of MySQL Servers are Publicly Exposed | eSecurity Planet, acessado em
fevereiro 27, 2026,
https://www.esecurityplanet.com/threats/millions-of-mysql-servers-are-publicly-
exposed/

5. ​AWS Data Breach: Lesson From 4 High Profile Breaches | BlackFog, acessado em
fevereiro 27, 2026, https://www.blackfog.com/aws-data-breach/

6. ​Proactive PostgreSQL security: What we learned from the recent cryptomining
attack, acessado em fevereiro 27, 2026,
https://www.postgresql.fastware.com/blog/proactive-postgresql-security-what-
we-learned-from-the-recent-cryptomining-attack

7. ​RedisRaider: Weaponizing misconfigured Redis to mine ..., acessado em fevereiro
27, 2026,
https://securitylabs.datadoghq.com/articles/redisraider-weaponizing-misconfigur
ed-redis/

8. ​A Technical Dive into Attack & Defense of AWS EC2 Security. - Medium, acessado
em fevereiro 27, 2026,https://medium.com/devsecops-ai/a-technical-dive-into-attack-defense-of-aws-
ec2-security-f681f43d57b2

9. ​What happened in the Ubiquiti data breach? - Twingate, acessado em fevereiro
27, 2026, https://www.twingate.com/blog/tips/ubiquiti-data-breach