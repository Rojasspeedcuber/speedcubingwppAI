# Speedcubing WhatsApp Bot

Bot para WhatsApp que ajuda praticantes de speedcubing enviando imagens e algoritmos para F2L, OLL e PLL.

## Funcionalidades

- Menu interativo para navegação
- Envio de imagens e algoritmos para casos específicos
- Agrupamento de algoritmos F2L e OLL por características similares
- Suporte para PLL com notação padrão
- API Flask para processamento de webhooks

## Requisitos

- Docker e Docker Compose
- Evolution API configurada para WhatsApp
- Python 3.11+

## Configuração

1. Clone este repositório
2. Copie o arquivo `.env.example` para `.env` e configure as variáveis:
   ```
   EVOLUTION_API_URL=http://sua-evolution-api.com
   EVOLUTION_API_KEY=sua-chave-api (se necessário)
   INSTANCE_NAME=nome-da-sua-instancia
   ```
3. Certifique-se que os arquivos de imagem estão no diretório `imagens_algoritmos`
   - F2L em `imagens_algoritmos/F2L`
   - OLL em `imagens_algoritmos/OLL`
   - PLL em `imagens_algoritmos/PLL`

## Inicialização

Para iniciar o bot, execute:

```bash
docker-compose up -d
```

Ou use o script fornecido:

```bash
./start.bat
```

O servidor estará disponível em `http://localhost:8000`

## Configuração da Evolution API

1. Configure a Evolution API seguindo a documentação oficial
2. Configure um webhook na Evolution API apontando para `http://seu-servidor:8000/webhook`

## Uso

Envie uma mensagem para o número associado à sua instância do WhatsApp e o bot responderá com o menu inicial.

## Estrutura dos Algoritmos

Os algoritmos estão organizados em:

1. **F2L (First 2 Layers)** - Agrupados por orientação de peças
2. **OLL (Orientation of Last Layer)** - Agrupados por padrões visuais
3. **PLL (Permutation of Last Layer)** - Listados por nome (A1, A2, U1, etc.)

## Tecnologias Utilizadas

- Flask: Framework web Python para API
- Docker: Containerização da aplicação
- Evolution API: Interface para WhatsApp