# Introdução ao Paradigma de Segurança em Ambientes de Nuvem e a Superfície de Ataque

A adoção onipresente de infraestruturas baseadas em nuvem, com destaque para
ecossistemas como a Amazon Web Services (AWS), redefiniu fundamentalmente a arquitetura
de redes corporativas e, por conseguinte, a superfície de ataque disponível para atores
maliciosos. Historicamente, a segurança de rede dependia de perímetros físicos rígidos e
firewalls de borda que isolavam ativos internos da internet pública. No paradigma de nuvem,
essa complexidade de hardware foi transferida para o gerenciamento lógico de recursos,
regido pelo modelo de responsabilidade compartilhada. Este modelo estipula categoricamente
que o provedor de nuvem assegura a infraestrutura subjacente, enquanto o cliente retém a
responsabilidade inalienável pela segurança das configurações, dados e identidades
implantadas sobre essa infraestrutura.<sup>1</sup>

O principal mecanismo de controle de acesso à rede em instâncias de computação (como o
Amazon Elastic Compute Cloud - EC2) é o Security Group, que atua como um firewall virtual
de inspeção de estado (stateful) operando diretamente na interface de rede elástica da
instância.<sup>2</sup> A eficácia deste mecanismo de defesa é inversamente proporcional à
permissividade de suas regras. O erro de configuração mais crítico, prevalente e sistêmico em
ambientes de nuvem é a implementação de regras de entrada (inbound) irrestritas,
representadas tecnicamente pelas notações de Classless Inter-Domain Routing (CIDR)
0.0.0.0/0 para o protocolo IPv4 e ::/0 para o protocolo IPv6.<sup>2</sup> A aplicação destas notações
instrui o hipervisor da AWS a aceitar pacotes de rede de qualquer endereço IP globalmente
roteável para a porta especificada, efetivamente obliterando o isolamento de rede e expondo o
serviço diretamente à internet hostil.<sup>2</sup>

A gravidade desta configuração é amplificada pela velocidade e sofisticação das ferramentas
de varredura modernas. A internet pública contemporânea é caracterizada por um ruído de
fundo constante de sondagens automatizadas. Organizações de inteligência de ameaças e
indexadores de dispositivos (como Shodan, Censys e Shadowserver Foundation) operam
varreduras contínuas em todo o espaço de endereçamento IP global, mapeando portas
abertas, capturando banners de serviços e catalogando vulnerabilidades em tempo real.<sup>3</sup>
Paralelamente a esses atores benignos, sindicatos de cibercriminosos e botnets automatizadas
executam o mesmo processo com intenções predatórias. Relatórios de resposta a incidentesdemonstram que a latência entre a exposição de um serviço em nuvem e a primeira tentativa
de invasão automatizada é frequentemente mensurada em segundos; em experimentos
controlados, ataques de força bruta iniciaram-se em menos de um minuto após a abertura de
uma porta <sup>3</sup>, e comprometimentos totais de bancos de dados ocorreram em meros sete
minutos.<sup>4</sup> Mais alarmante, provedores de inteligência cibernética registraram intrusões
bem-sucedidas em infraestruturas de nuvem ocorrendo dentro de uma janela de 51 segundos
após o provisionamento do recurso vulnerável.<sup>5</sup>

O presente documento fornece uma fundamentação teórica exaustiva sobre os vetores de
ataque, mecanismos de exploração e impactos em cascata associados a portas de rede que
são historicamente os alvos preferenciais quando expostas publicamente. A análise decompõe
as ameaças dirigidas a protocolos de gerenciamento e acesso remoto (SSH na porta 22 e RDP
na porta 3389) e aprofunda-se criticamente nas vulnerabilidades inerentes à exposição de
sistemas de gerenciamento de banco de dados relacionais e NoSQL (MySQL na porta 3306,
PostgreSQL na porta 5432, Redis na porta 6379 e MongoDB na porta 27017). A compreensão
granular dos incidentes reais e das táticas, técnicas e procedimentos (TTPs) associados a essas
portas é o alicerce para a concepção de scanners de vulnerabilidade preventivos. Além disso, a
análise demonstrará que, no contexto específico da AWS, a exposição destes serviços
transcende o comprometimento do servidor individual; ela atua como o vetor inicial crítico para
ataques complexos de roubo de credenciais via Instance Metadata Service (IMDS), resultando
em escalonamento de privilégios, movimentação lateral e o potencial colapso de toda a
identidade da nuvem corporativa.<sup>6</sup>

## Referências citadas

1. 9 Critical AWS Security Risks: A Comprehensive List - SentinelOne, acessado em
fevereiro 27, 2026,
https://www.sentinelone.com/cybersecurity-101/cloud-security/aws-security-risk
s/

2. Control traffic to your AWS resources using security groups - Amazon Virtual
Private Cloud, acessado em fevereiro 27, 2026,
https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html

3. Remote Desktop Protocol: Exposed RDP (is dangerous) | SOPHOS, acessado em
fevereiro 27, 2026,
https://www.sophos.com/en-us/blog/remote-desktop-protocol-exposed-rdp-is-
dangerous

4. Protecting Postgres: Key Security Takeaways from a Postgres Honeypot - Hunters
Security, acessado em fevereiro 27, 2026,
https://www.hunters.security/en/blog/protecting-postgres

5. Event-Driven Cloud Security Architecture: Implementation Guide - Cy5.io,
acessado em fevereiro 27, 2026,
https://www.cy5.io/blog/event-driven-cloud-security-architecture/

6. IMDS Abused: Hunting Rare Behaviors to Uncover Exploits | Wiz Blog, acessado
em fevereiro 27, 2026, https://www.wiz.io/blog/imds-anomaly-hunting-zero-day