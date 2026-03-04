# Porta 22 (SSH): O Vetor de Acesso Inicial e a Ponte para o Plano de Controle

A porta TCP 22, designada para o protocolo Secure Shell (SSH), é a interface padrão de
administração para praticamente todos os sistemas baseados em Unix e Linux operando na
nuvem. Apesar das melhores práticas unânimes da indústria ditarem que o acesso SSH deve
ser restrito a endereços IP conhecidos, redes virtuais privadas (VPNs) ou substituído por
gerenciadores de sessão nativos da nuvem (como o AWS Systems Manager Session Manager),
a realidade operacional é drasticamente diferente.<sup>2</sup> Dados globais de telemetria revelam quemais de 20 milhões de sistemas expõem ativamente a porta 22 para a internet pública de forma
contínua.<sup>3</sup>

A exposição irrestrita da porta 22 viabiliza um espectro de ataques cibernéticos, variando
desde a exaustiva força bruta clássica e a pulverização de senhas (password spraying) até a
exploração tática de chaves criptográficas fracas, vazadas ou reutilizadas.<sup>1</sup> Em infraestruturas
como a AWS, o comprometimento inicial via SSH raramente é o objetivo final do atacante; ao
contrário, ele atua como a cabeça de ponte para o estabelecimento de persistência e para o
reconhecimento aprofundado do ambiente de nuvem adjacente.

O estudo das operações conduzidas pelo grupo cibercriminoso avançado conhecido como
TeamTNT fornece um compêndio claro de como a porta 22 é instrumentalizada em ambientes
modernos.<sup>4</sup> O TeamTNT especializou-se em orquestrar ataques em larga escala
especificamente direcionados contra infraestruturas de nuvem, instâncias virtuais, e clusters
de contêineres (como Docker e Kubernetes).<sup>4</sup> Quando este grupo identifica um serviço
vulnerável e obtém execução inicial de comandos, frequentemente abusando de conexões
SSH expostas com credenciais fracas, o comportamento do malware realiza uma transição
imediata da exploração local do host para o reconhecimento da arquitetura em nuvem.<sup>5</sup>

A mecânica de ataque documentada do TeamTNT demonstra um fluxo de comprometimento
altamente estruturado e focado em identidade: após o acesso via porta 22, o atacante utiliza
binários legítimos do sistema, como wget ou curl, para fazer o download de um script de shell
malicioso (frequentemente nomeado aws2.sh) a partir de sua infraestrutura de comando e
controle.<sup>4</sup> A análise comportamental deste script revela que ele não busca primeiramente
dados de aplicativos, mas sim credenciais estruturais de nuvem, empregando múltiplas
estratégias simultâneas de colheita.<sup>4</sup> O script realiza uma varredura rigorosa verificando
variáveis de ambiente previamente exportadas, inspeciona o interior de contêineres Docker em
execução em busca de chaves injetadas, e realiza buscas em caminhos de disco críticos, como
/root/.aws/credentials e diretórios /home/, visando extrair chaves de acesso estáticas da AWS.<sup>4</sup>

Se a busca em disco falhar, o atacante aproveita sua posição dentro da instância
comprometida para direcionar requisições ao Instance Metadata Service (IMDS) da AWS,
extraindo tokens de sessão temporários (aws_access_key_id, aws_secret_access_key,
aws_session_token) associados à IAM Role daquela máquina.<sup>4</sup> Este padrão evidencia que o
impacto da porta 22 exposta não é isolado à instância EC2 individual. Ao roubar estas
credenciais, o atacante transpõe a fronteira do sistema operacional Linux e passa a interagir
diretamente com as APIs de gerenciamento da AWS, habilitando uma movimentação lateral
severa que pode incluir a exfiltração de dados de buckets S3, a alteração de Security Groups e
a criação de novas instâncias computacionais em regiões não monitoradas para uso em
mineração de criptomoedas.<sup>6</sup> A porta 22 aberta, portanto, converte-se em um vetor de
comprometimento de identidade de nuvem.

## Referências citadas

1. 9 Critical AWS Security Risks: A Comprehensive List - SentinelOne, acessado em
fevereiro 27, 2026,
https://www.sentinelone.com/cybersecurity-101/cloud-security/aws-security-risk
s/

2. Top 10 AWS Security Misconfigurations and How to Avoid Them | by
Davebhargavi, acessado em fevereiro 27, 2026,https://medium.com/@davebhargavi507/top-10-aws-security-misconfigurations-
and-how-to-avoid-them-774fdf3b77c5

3. The 2 Most Dangerous and Attacked Ports in Your Environment - FullArmor Corp,
acessado em fevereiro 27, 2026,
https://fullarmor.com/the-2-most-dangerous-and-attacked-ports-in-your-enviro
nment/

4. Threat news: TeamTNT stealing credentials using EC2 Instance Metadata | Sysdig,
acessado em fevereiro 27, 2026,
https://www.sysdig.com/blog/teamtnt-aws-credentials

5. ​An analysis of a TeamTNT doppelgänger - Security Labs - Datadog, acessado em
fevereiro 27, 2026,
https://securitylabs.datadoghq.com/articles/analysis-of-teamtnt-doppelganger/

6. ​TeamTNT Operations Actively Enumerating Cloud Environments - Unit 42,
acessado em fevereiro 27, 2026,
https://unit42.paloaltonetworks.com/teamtnt-operations-cloud-environments/