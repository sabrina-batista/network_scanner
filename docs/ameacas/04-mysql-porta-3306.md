# Porta 3306 (MySQL): Vazamento de Dados em Massa e Exploração de Banners

O MySQL, juntamente com seu derivado direto, o MariaDB, opera tradicionalmente na porta
TCP 3306. A escala global da exposição imprudente deste protocolo é monumental e
representa uma das maiores falhas sistêmicas na higiene de redes mundial. Uma varredura
extensiva e não intrusiva realizada pela organização de pesquisa cibernética The Shadowserver
Foundation revelou um cenário preocupante: a existência de mais de 3,6 milhões de servidores
MySQL acessíveis publicamente.<sup>1</sup> Durante esta varredura, os pesquisadores não utilizaram
exploits agressivos; eles meramente emitiram requisições de conexão padrão. O fato de mais
de dois milhões desses servidores responderem ativamente com o "Server Greeting" (o banner
inicial do servidor) confirma que o serviço está perfeitamente disponível para interação e
potencial exploração externa.<sup>1</sup>

Os dados estruturados fornecidos pela varredura da Shadowserver delineiam a magnitude e
os detalhes técnicos da exposição global de instâncias MySQL <sup>1</sup>:

| Protocolo de Rede |   População Total de Instâncias Encontradas | Respostas com "Server Greeting" (Instâncias Expostas) | Instâncias Expostas Operando Sem Suporte a Criptografia TLS |
|:-----------------:|:-------------------------------------------:|:-----------------------------------------------------:|:-----------------------------------------------------------:|
|        IPv4       |                  3.957.457                  |                       2.279.908                       |                          1.163.249                          |
|        IPv6       |                  1.421.010                  |                       1.343.993                       |                          1.307.795                          |

O risco iminente de expor a porta 3306 origina-se em múltiplos vetores técnicos
interconectados que facilitam o comprometimento da infraestrutura:

1. A Extensa Ausência de Criptografia em Trânsito (TLS): A estatística mais alarmante
exposta no relatório não é apenas o número de instâncias acessíveis, mas a ausência
crítica de segurança criptográfica. Aproximadamente 1,16 milhão de servidores
operando sobre IPv4 e espantosos 1,3 milhão de servidores sobre IPv6 transmitem suas
comunicações de banco de dados sem nenhum suporte a Transport Layer Security
(TLS).<sup>1</sup> Esta falha arquitetônica significa que qualquer credencial de autenticação, cada
query SQL elaborada, e o próprio payload dos dados confidenciais retornados transitam
em texto plano puro. Em ambientes de nuvem, se esse tráfego não for encapsulado por
uma Virtual Private Cloud (VPC) rigorosa ou se a instância comunicar-se diretamente
com origens externas, a comunicação torna-se flagrantemente vulnerável a ataques de
interceptação sofisticados (Man-in-the-Middle) e farejamento passivo de pacotes
(packet sniffing), resultando em roubo de credenciais antes mesmo de o atacante tocar
no banco.<sup>2</sup> A discrepância notável na adoção de TLS no IPv6 aponta para prováveisfalhas sistêmicas na configuração automatizada de implantações mais recentes, que
muitas vezes ignoram o endurecimento (hardening) de segurança em novos protocolos.

2. 2.​ Reconhecimento e Exploração Baseada em Banner (Banner Grabbing): Assim que
um pacote atinge a porta 3306, a saudação inicial e amigável do servidor (o banner)
revela involuntariamente informações de inteligência tática cruciais para o atacante.
Banners capturados no mundo real frequentemente divulgam o nome exato do software
subjacente e sua versão precisa (por exemplo, 5.7.44-0ubuntu0.22.04.1-log ou
10.6.18-MariaDB).<sup>4</sup> Agentes de ameaça catalogam automaticamente essas versões e
consultam bases de dados de vulnerabilidades (como a lista CVE) em frações de
segundo. Banners que expõem versões antigas e sem patch, particularmente séries
anteriores do MariaDB (como as versões 10.3 a 10.5), frequentemente sofrem com
vulnerabilidades conhecidas de Execução Remota de Código (RCE) não autenticada e
falhas lógicas de desvio de autenticação (auth bypass), permitindo o controle do
servidor sem sequer a necessidade de força bruta.<sup>4</sup>

3. Credenciais Padrão e Falhas Críticas na Configuração de Bind: Um erro operacional
prevalente que afeta desenvolvedores inexperientes e scripts de implantação legados
ocorre quando o administrador configura o parâmetro bind-address no arquivo de
configuração my.cnf. Ao defini-lo como 0.0.0.0 ou *, o MySQL é forçado a escutar
conexões de todas as interfaces de rede disponíveis, em vez de se limitar ao seguro
127.0.0.1 (localhost).<sup>5</sup> Scanners automatizados são otimizados para encontrar
exatamente essas instâncias. Quando esta configuração pública é combinada com
credenciais fracas ou, pior ainda, contas root desprovidas de senha, o impacto é
instantâneo. Após o login livre como root, o fluxo padrão de ataque consiste em extrair
imediatamente o esquema completo da base de dados (INFORMATION_SCHEMA),
coletar hashes de senhas de outros usuários, roubar dados corporativos e,
frequentemente, utilizar esse acesso privilegiado para gravar e executar código
malicioso no nível do sistema operacional através de exploração de User Defined
Functions (UDF).<sup>4</sup> O impacto nos negócios é catastrófico, espelhando os princípios de
vazamentos notórios em larga escala onde bancos de dados desprotegidos expuseram
milhões de registros confidenciais sem qualquer obstáculo.<sup>3</sup>

## Referẽncias citadas

1. Over 3.6 million exposed MySQL servers on IPv4 and IPv6 | The Shadowserver
Foundation, acessado em fevereiro 27, 2026,
https://www.shadowserver.org/news/over-3-6m-exposed-mysql-servers-on-ipv4
-and-ipv6/

2. Your Database Exposure Risk | UpGuard, acessado em fevereiro 27, 2026,
https://www.upguard.com/blog/database-exposure

3. ​Millions of MySQL Servers are Publicly Exposed | eSecurity Planet, acessado em
fevereiro 27, 2026,
https://www.esecurityplanet.com/threats/millions-of-mysql-servers-are-publicly-
exposed/

4. ​Exposed DB Banners: MySQL, PostgreSQL, MSSQL, MongoDB | Red Secure Tech
LTD., acessado em fevereiro 27, 2026,
https://www.redsecuretech.co.uk/blog/post/exposed-db-banners-mysql-postgre
sql-mssql-mongodb/972

5. ​8 MySQL security mistakes that expose your database to attackers - Medium,
acessado em fevereiro 27, 2026,
https://medium.com/@ngza5tqf/8-mysql-security-mistakes-that-expose-your-da
tabase-to-attackers-bdd0e77a012e