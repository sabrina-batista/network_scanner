# Porta 6379 (Redis): Injeção de Tarefas Agendadas e Propagação de Worms

O Redis (Remote Dictionary Server) opera de forma padrão na porta TCP 6379. É globalmente
adotado como um cache de dados ultrarrápido, um broker de mensagens eficiente e um
banco de dados residente em memória altamente responsivo. Um problema estrutural crítico e
amplamente conhecido que aflige instâncias Redis mal configuradas é a sua predisposição a
aceitar conexões irrestritas não autenticadas caso o administrador não configure ativamente
uma senha.<sup>1</sup> Ademais, o protocolo subjacente de comunicação do Redis (RESP) é puramente
baseado em texto legível; por ser inerentemente transparente e livre de ofuscação
criptográfica no nível do protocolo em implantações simples, torna-se altamente suscetível a
interações parasitárias e manipulações de baixo nível quando exposto diretamente à
hostilidade da internet pública.<sup>1</sup>

A campanha de cryptojacking sofisticada nomeada RedisRaider, dissecada de forma abrangente por
pesquisadores da Datadog Security, expõe a taxonomia exata e as técnicas pelas quais a porta
6379 é explorada como o vetor primário de destruição.<sup>1</sup> Esta campanha, focada na exploração
de sistemas operacionais baseados em Linux, operava demonstrando um comportamento viral
similar ao de um worm de internet clássico, propagando-se autonomamente por meio da
exploração em massa sucessiva de serviços Redis expostos.<sup>1</sup> A intrincada cadeia de ataque
técnica desenrolava-se nos seguintes estágios metódicos <sup>1</sup>:

1. Reconhecimento Agressivo e Perfilamento do Host: O worm RedisRaider iniciava seu
ciclo de vida rastreando de forma indiscriminada e agressiva partes do espaço de
endereçamento IPv4, sondando especificamente a porta 6379 aberta. Ao estabelecer
uma conexão TCP bem-sucedida, o malware enviava imediatamente o comando nativo
INFO do Redis. Este comando legítimo atua como um farol de inteligência, retornando
estatísticas profundas do servidor, informações cruciais sobre o kernel e o sistema
operacional base. Se o banner de resposta confirmasse que o host subjacente era um
sistema Linux, o ataque prosseguia para a fase de exploração; caso contrário, era
ignorado.<sup>1</sup>

2. Abuso da Configuração Dinâmica e Injeção de Payload: A genialidade maliciosa e
destrutiva do vetor de ataque via Redis não se baseia na exploração de falhas complexas
de corrupção de memória (como buffer overflows), mas na apropriação indevida e
abuso de comandos legítimos de configuração em tempo real (como o CONFIG SET).
Uma vez conectado — seja de forma não autenticada devido à ausência de senha ou
após uma fase de força bruta contra senhas fracas comuns —, o malware utilizava o
comando SET básico para inserir na memória do Redis um script de shell altamente
malicioso, frequentemente codificado em Base64 para evitar quebra de linha. O invasor
atribuía a esse script uma chave arbitrária no banco (por exemplo, a chave nomeada t).<sup>1</sup>

3. Sequestro do Agendador de Tarefas do Sistema Operacional: O ponto de virada doataque envolvia a reconfiguração hostil do destino dos dados. Utilizando o comando
CONFIG SET dir, o atacante alterava silenciosa e dinamicamente o diretório de trabalho
onde o banco de dados Redis salvaria o seu conteúdo permanente no disco. O diretório
era alterado criticamente para caminhos restritos do sistema operacional, como
/etc/cron.d/ (o coração do diretório do agendador de tarefas periódicas do Linux).
Imediatamente a seguir, o comando CONFIG SET dbfilename apache renomeava o
arquivo de saída esperado.<sup>1</sup>

4. Disparo do Gatilho e Execução Fiel (Execution Trigger): Com a armadilha armada, o
atacante emitia o comando bgsave (Background Save). Este comando força o serviço
Redis a realizar um dump completo, descarregando toda a sua memória atual (incluindo
a chave injetada com o script malicioso) em um arquivo físico no disco. O resultado
inevitável é que o script em Base64, antes residente apenas na RAM, era gravado
diretamente dentro de /etc/cron.d/apache.<sup>1</sup> O serviço cron nativo do Linux, projetado
para ler qualquer arquivo nesse diretório em intervalos regulares, inevitavelmente
interpretava e executava essa nova carga com altos privilégios de sistema. A execução
desse script baixava binários sofisticados de servidores de Comando e Controle (C2),
implantava mecanismos de persistência e executava mineradores XMRig altamente
ofuscados na memória.<sup>1</sup>

5. Técnicas de Anti-Análise e Evasão Avançada: A sofisticação da campanha RedisRaider
evidencia a evolução das ameaças. O binário principal, escrito em Go, utilizava
ofuscadores avançados em tempo de compilação, como o Garble, mascarando
completamente nomes de pacotes e símbolos lógicos para frustrar as análises estáticas
de pesquisadores de segurança e produtos de defesa.<sup>1</sup> Além disso, o invasor
implementava táticas de evidência volátil (anti-forense) de excelência: enviava comandos
adicionais (usando argumentos como EX 120) para atribuir um Time-to-Live (TTL) de vida
curta de 120 segundos às chaves injetadas, e invocava comandos como del t
imediatamente após o dump do banco de dados para o cron. Isso removia qualquer
vestígio identificável do script malicioso do cache da RAM, impossibilitando
reconstruções de análise de incidentes.<sup>1</sup> A porta 6379 provou ser um conduíte
altamente eficaz e destrutivo, confirmando também ataques documentados
semelhantes visando nuvens por campanhas como a Spinning YARN.<sup>2</sup>

## Referências citadas

1. ​RedisRaider: Weaponizing misconfigured Redis to mine ..., acessado em fevereiro
27, 2026,
https://securitylabs.datadoghq.com/articles/redisraider-weaponizing-misconfigur
ed-redis/

2. ​Spinning YARN: A New Linux Malware Campaign Targets Docker, Apache Hadoop,
Redis and Confluence - Darktrace, acessado em fevereiro 27, 2026,
https://www.darktrace.com/blog/spinning-yarn-a-new-linux-malware-campaign-
targets-docker-apache-hadoop-redis-and-confluence