# Porta 3389 (RDP): Exploração de Identidade e Disseminação Pandêmica de Ransomware

O Remote Desktop Protocol (RDP), projetado para operar na porta TCP 3389, é a tecnologiafundamental que permite acesso remoto interativo e interface gráfica em ecossistemas
Microsoft Windows.<sup>3</sup> Devido à sua ubiquidade em ambientes corporativos e à conveniência
que proporciona para a administração remota e o teletrabalho, o RDP é simultaneamente uma
ferramenta indispensável e um dos vetores de ataque mais perigosos na internet atual. O RDP
é notório por acumular um histórico de vulnerabilidades de segurança severas ao longo dos
anos, sendo amplamente reconhecido como o vetor de acesso inicial predominante explorado
por gangues de ransomware e corretores de acesso inicial (Initial Access Brokers).<sup>1</sup>

A prevalência da exposição do RDP é alarmante. Varreduras recentes em mecanismos de
busca de infraestrutura revelam a impressionante marca de mais de 3,5 milhões de sistemas
globalmente expondo a porta 3389 diretamente à internet pública.<sup>2</sup> Um relatório aprofundado
da Unidade 42 apontou que 73% das organizações analisadas mantinham alguma forma de
serviço RDP exposto publicamente, com avaliações de superfície de ataque indicando que
quase uma em cada quatro vulnerabilidades críticas descobertas estava diretamente
relacionada a servidores RDP mal configurados.<sup>4</sup>

A essência da ameaça direcionada ao RDP reside na exploração sistemática de identidades.
Relatórios de inteligência de resposta a incidentes revelam uma tendência inegável:
vulnerabilidades relacionadas a credenciais e abuso de identidade desempenham um papel
crítico em aproximadamente 90% de todos os incidentes de segurança cibernética
registrados.<sup>5</sup> A facilidade com que um atacante consegue interagir com a interface de
autenticação do Windows remotamente viabiliza a execução de ataques automatizados de
força bruta.</sup>4</sup> Quando o protocolo RDP está exposto para 0.0.0.0/0 em uma instância EC2 do
Windows, não há necessidade de exploits complexos de corrupção de memória; o atacante
precisa apenas testar milhares de combinações de senhas até obter sucesso, frequentemente
valendo-se da prevalência de políticas de senha fracas nas organizações.<sup>1</sup>

Para quantificar empiricamente a agressividade deste ambiente ameaçador, a equipe de
pesquisa de resposta a incidentes da Sophos conduziu um experimento prático (honeypot).
Um servidor configurado propositalmente com a porta RDP aberta foi exposto à internet por
um período de apenas 15 dias. Os dados coletados forneceram métricas vitais sobre a
ferocidade e o volume do cenário de ameaças automatizadas.<sup>1</sup>

|        Métrica de Ataque RDP Observada (Período de 15 dias)        |  Valor Mensurado  |
|:------------------------------------------------------------------:|:-----------------:|
|        Tempo transcorrido até a primeira tentativa de invasão      | Menos de 1 minuto |
|       Volume total de tentativas de login falhas registradas       |    > 2.000.000    |
|      Quantidade de nomes de usuário únicos testados peloa bots     |      137.500      |
| Quantidade de endereços IP de origem únicos realizando a varredura |        999        |

O estudo da Sophos também revelou um padrão tático consistente na escolha dos alvos pelosscripts de ataque automatizados. As tentativas de força bruta não são randômicas; elas
concentram-se assimetricamente em variações do usuário com os maiores privilégios do
sistema, visando o controle absoluto após a quebra da senha. A distribuição dos alvos reflete
uma abordagem sistemática por parte dos invasores.<sup>1</sup>

| Nome de Usuário Alvo | Contagem de Tentativas de Força Bruta |
|:--------------------:|:-------------------------------------:|
|     administrator    |                866.862                |
|     administrador    |                152.289                |
|    administrateur    |                111.460                |
|        backup        |                 94.541                |
|         admin        |                 88.367                |
|         user         |                 24.030                |
|        scanner       |                 18.781                |
|        escaner       |                 12.455                |
|        usuario       |                 12.238                |
|         Guest        |                 8.784                 |

A análise meticulosa destes dados experimentais refuta conclusivamente uma falácia comum
na administração de redes: a segurança por obscuridade. Muitos administradores, na tentativa
de mitigar o risco, alteram a porta de escuta padrão do RDP de 3389 para portas efêmeras
altas e obscuras, na crença falha de que isso evadirá os scanners automatizados. A pesquisa
empírica provou que essa tática é completamente ineficaz; indexadores avançados como
Censys e as próprias botnets de ransomware utilizam assinaturas de protocolo e identificam
facilmente o banner e o handshake característicos do RDP, independentemente do número da
porta configurada no sistema operacional.<sup>1</sup> Adicionalmente, se o servidor for configurado
incorretamente sem a exigência de Autenticação no Nível da Rede (Network Level
Authentication - NLA), os atacantes podem estabelecer uma conexão e interagir com a tela de
login gráfica antes mesmo de fornecerem qualquer credencial.<sup>1</sup> Isso consome rapidamente os
recursos do servidor, facilita a enumeração de domínio e serve como um conduto ideal para
ataques de negação de serviço (DoS). A exposição da porta 3389 para o mundo é, do ponto de
vista da arquitetura em nuvem, um convite explícito para o desdobramento de ransomware,
exigindo que plataformas de conformidade, como o AWS Trusted Advisor e o Security Hub,
classifiquem automaticamente essa regra de entrada como uma violação de segurança de
risco crítico (vermelho).<sup>6</sup>

## Referências citadas

1. Remote Desktop Protocol: Exposed RDP (is dangerous) | SOPHOS, acessado em
fevereiro 27, 2026,
https://www.sophos.com/en-us/blog/remote-desktop-protocol-exposed-rdp-is-
dangerous

2. The 2 Most Dangerous and Attacked Ports in Your Environment - FullArmor Corp,
acessado em fevereiro 27, 2026,
https://fullarmor.com/the-2-most-dangerous-and-attacked-ports-in-your-enviro
nment/

3. ​Remote desktop protocol TCP port 3389 security risks and vulnerabilities -
Specops Software, acessado em fevereiro 27, 2026,
https://specopssoft.com/blog/remote-desktop-protocol-port-3389-vulnerabilities/

4. ​Playbook of the week: Responding to RDP Brute Force Attacks - Palo Alto
Networks Blog, acessado em fevereiro 27, 2026,
https://www.paloaltonetworks.com/blog/security-operations/playbook-of-the-we
ek-responding-to-rdp-brute-force-attacks/

5. ​Unit 42: Nearly two-thirds of breaches now start with identity abuse |
CyberScoop, acessado em fevereiro 27, 2026,
https://cyberscoop.com/attackers-abuse-identity-unit42-palo-alto-networks-inci
dent-response-report/

6. ​AWS Foundational Security Best Practices standard in Security Hub CSPM,
acessado em fevereiro 27, 2026,
https://docs.aws.amazon.com/securityhub/latest/userguide/fsbp-standard.html