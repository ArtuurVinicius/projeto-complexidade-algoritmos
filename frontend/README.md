# Frontend - Sistema de Rotas

Frontend desenvolvido em Vue.js para o sistema de rotas de Recife.

## Estrutura

```
frontend/
├── index.html           # Arquivo HTML principal
├── main.js              # Ponto de entrada da aplicação
├── App.vue              # Componente raiz
├── style.css            # Estilos globais
├── vite.config.js       # Configuração do Vite
├── package.json         # Dependências do projeto
├── components/
│   ├── SearchBar.vue    # Barra de busca com filtros
│   ├── Sidebar.vue      # Painel lateral com informações
│   └── MapArea.vue      # Área reservada para o mapa
└── README.md            # Este arquivo
```

## Instalação e Execução

### 1. Instalar dependências
```bash
npm install
```

### 2. Executar em desenvolvimento
```bash
npm run dev
```

A aplicação abrirá automaticamente em `http://localhost:5173`

### 3. Build para produção
```bash
npm run build
```

## Componentes

### SearchBar
- Barra de busca para inserir o endereço
- Filtros interativos (Restaurantes, Hotéis, etc.)
- Ícones visuais para cada filtro

### Sidebar
- Exibe informações do local pesquisado
- Botões de ação (Rotas, Salvar, Próximo, Enviar para smartphone)
- Menu com opções adicionais

### MapArea
- Espaço reservado para integração futura do mapa
- Atualmente exibe um placeholder em branco

## Próximas Etapas

- [ ] Integrar Google Maps ou biblioteca de mapas similar
- [ ] Conectar com a API backend para buscar rotas
- [ ] Implementar lógica de filtros
- [ ] Adicionar visualização de rotas no mapa
- [ ] Implementar autenticação de usuário

## Tecnologias Utilizadas

- **Vue.js 3** - Framework frontend
- **Vite** - Build tool
- **CSS3** - Estilização
