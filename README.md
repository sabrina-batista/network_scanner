# AWS Port Sentinel

O **AWS Port Sentinel** é um scanner preventivo e periódico de vulnerabilidades de rede para infraestruturas AWS. Ele analisa automaticamente as regras de entrada (*inbound*) de todos os Security Groups em busca de portas inseguras expostas para o mundo (`0.0.0.0/0` ou `::/0`).

Se uma exposição for detectada, o sistema envia imediatamente um alerta detalhado via e-mail (SMTP), permitindo uma resposta rápida da equipe de segurança.

## Funcionalidades

- **Análise Multi-Região:** Varre instâncias EC2 em múltiplas regiões da AWS simultaneamente.
- **Configuração via JSON:** Portas consideradas inseguras são definidas em um arquivo JSON externo (as portas são as chaves).
- **Detecção de "All Traffic":** Alerta quando um Security Group expõe todo o tráfego para o mundo (`IpProtocol = -1`).
- **Notificação SMTP:** Compatível com Gmail, Outlook/Office365, SendGrid e qualquer servidor SMTP.
- **Execução Periódica:** Projetado para rodar via `cron` em uma VM/instância (ex.: EC2) de forma preventiva.

## Estrutura do projeto

Sugestão de estrutura:

- `config/unsafe_ports.json`
- `src/scanner.py`
- `src/emailer_smtp.py`
- `src/main.py`
- `requirements.txt`

## Pré-requisitos

1. **AWS IAM Role (recomendado) ou credenciais AWS:** Permissões de leitura no EC2 e STS.
2. **Python 3.9+** na máquina que vai executar o scanner.
3. **Acesso a um servidor SMTP** (host, porta, usuário e senha/app password).

## Configuração

### 1) Portas inseguras (`config/unsafe_ports.json`)

Edite o arquivo JSON com as portas consideradas inseguras. **As chaves devem ser as portas em formato string**.

Exemplo:

```json
{
  "22": { "name": "SSH", "severity": "high", "reason": "Acesso administrativo exposto" },
  "3389": { "name": "RDP", "severity": "critical", "reason": "Acesso remoto Windows exposto" },
  "3306": { "name": "MySQL", "severity": "high", "reason": "Banco de dados exposto publicamente" }
}
```

### 2) Variáveis de ambiente

O projeto utiliza variáveis de ambiente para configurar regiões, SMTP e destinatários do alerta.

| Variável | Exemplo | Descrição |
|---|---|---|
| `UNSAFE_PORTS_PATH` | `config/unsafe_ports.json` | Caminho do JSON de portas inseguras |
| `AWS_REGIONS` | `us-east-1,sa-east-1` | Regiões a escanear (CSV) |
| `AWS_REGION` | `us-east-1` | Alternativa para região única (usada se `AWS_REGIONS` não existir) |
| `ONLY_RUNNING` | `true` | Se `true`, avalia somente instâncias `running` |
| `SMTP_HOST` | `smtp.gmail.com` | Host do servidor SMTP |
| `SMTP_PORT` | `465` | Porta (465 para SSL/TLS, 587 para STARTTLS) |
| `SMTP_USER` | `alertas@empresa.com` | Usuário do SMTP |
| `SMTP_PASSWORD` | `senha-ou-app-password` | Senha / App Password |
| `SMTP_USE_TLS` | `true` | Usa SMTP SSL/TLS (normalmente 465) |
| `SMTP_USE_STARTTLS` | `false` | Usa STARTTLS (normalmente 587) |
| `EMAIL_SENDER` | `alertas@empresa.com` | Remetente do e-mail |
| `EMAIL_RECIPIENTS` | `sec@empresa.com,infra@empresa.com` | Destinatários (CSV) |

#### Exemplos de SMTP

- **Gmail** (recomendado usar **App Password**):
  - `SMTP_HOST=smtp.gmail.com`
  - `SMTP_PORT=465`
  - `SMTP_USE_TLS=true`
  - `SMTP_USE_STARTTLS=false`

- **Office 365 / Outlook**:
  - `SMTP_HOST=smtp.office365.com`
  - `SMTP_PORT=587`
  - `SMTP_USE_TLS=false`
  - `SMTP_USE_STARTTLS=true`

## Execução em uma VM AWS (EC2)

### Passo 1: Criar instância e IAM Role

1. Crie uma instância EC2 (Amazon Linux 2023 ou Ubuntu).
2. Crie/associe uma **IAM Role** à instância com permissões mínimas para leitura.
   - Para começar rápido: `AmazonEC2ReadOnlyAccess`.
   - Ideal (mínimo necessário): permissões para `ec2:DescribeInstances`, `ec2:DescribeSecurityGroups` e `sts:GetCallerIdentity`.

> Usar IAM Role evita armazenar `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` no servidor.

### Passo 2: Instalar dependências

Amazon Linux:

```bash
sudo yum update -y
sudo yum install -y python3-pip
pip3 install -r requirements.txt
```

Ubuntu:

```bash
sudo apt-get update -y
sudo apt-get install -y python3-pip
pip3 install -r requirements.txt
```

### Passo 3: Criar script de execução

Crie `run_scanner.sh` na pasta do projeto:

```bash
#!/bin/bash
set -euo pipefail

# Regiões
export AWS_REGIONS="us-east-1,sa-east-1"
export ONLY_RUNNING="true"

# JSON de portas inseguras
export UNSAFE_PORTS_PATH="config/unsafe_ports.json"

# SMTP
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="465"
export SMTP_USER="seu-email@gmail.com"
export SMTP_PASSWORD="sua-app-password"
export SMTP_USE_TLS="true"
export SMTP_USE_STARTTLS="false"

# Email
export EMAIL_SENDER="seu-email@gmail.com"
export EMAIL_RECIPIENTS="sec@empresa.com,infra@empresa.com"

python3 -m src.main
```

Depois:

```bash
chmod +x run_scanner.sh
./run_scanner.sh
```

## Execução periódica (cron)

Para execução preventiva, configure o `cron`.

1. Abra o crontab:

```bash
crontab -e
```

2. Exemplo: executar a cada 30 minutos e salvar logs:

```cron
*/30 * * * * /home/ec2-user/aws-sentinel/run_scanner.sh >> /home/ec2-user/aws-sentinel/scanner.log 2>&1
```

> Ajuste os caminhos conforme seu usuário e diretório (em Ubuntu pode ser `/home/ubuntu/...`).

## Boas práticas e segurança

- **Não use senha principal** do e-mail: prefira **App Password** quando possível.
- **Menor privilégio** na IAM Role (somente leitura necessária).
- **Evite spam:** o programa só envia e-mail quando houver achados. Se quiser anti-duplicação (não reenviar o mesmo alerta), implemente persistência (DynamoDB/S3) para registrar alertas já enviados.

## Troubleshooting

- **Sem e-mail chegando**:
  - Verifique `scanner.log` (se usando cron).
  - Confirme credenciais SMTP, porta e modo (`TLS` vs `STARTTLS`).
  - Confirme se o provedor SMTP permite envio a partir da sua VM (alguns bloqueiam porta 25).

- **Erro de permissão AWS**:
  - Verifique se a instância EC2 está com IAM Role anexada.
  - Confirme permissões `DescribeInstances`, `DescribeSecurityGroups` e `GetCallerIdentity`.
