# Corpus de referência — Assistente LGPD para Desenvolvedores

> Observação: este corpus foi estruturado para fins educacionais e de demonstração do projeto de portfólio. Ele resume pontos práticos da LGPD para equipes de tecnologia. Para uso jurídico real, consulte o texto integral oficial da Lei nº 13.709/2018, orientações da ANPD e o jurídico/DPO da organização.

---

## Página 01 — Visão geral da LGPD para software

A Lei Geral de Proteção de Dados Pessoais estabelece regras para o tratamento de dados pessoais no Brasil. Em projetos de software, isso impacta coleta, armazenamento, compartilhamento, retenção, segurança, logs, integrações, analytics, suporte e treinamento de modelos. Um sistema deve tratar dados pessoais somente quando houver finalidade legítima, base legal adequada, transparência para o titular e medidas de segurança proporcionais ao risco.

Para desenvolvedores, a LGPD não é apenas uma obrigação documental. Ela deve aparecer em decisões de arquitetura: quais campos são coletados, por quanto tempo ficam armazenados, quem pode acessar, como são auditados, como são excluídos e como incidentes são comunicados. Também é importante diferenciar dado pessoal comum, dado pessoal sensível e dado anonimizado.

Boas práticas técnicas incluem minimização de dados, criptografia em trânsito e repouso, controle de acesso por perfil, logs sem exposição desnecessária de dados, mascaramento em ambientes de teste, trilhas de auditoria, revisão de integrações com terceiros e documentação das decisões de tratamento.

---

## Página 02 — Artigo 5º: conceitos essenciais

O Art. 5º define conceitos fundamentais. Dado pessoal é informação relacionada a pessoa natural identificada ou identificável. Dado pessoal sensível envolve origem racial ou étnica, convicção religiosa, opinião política, filiação sindical, dado referente à saúde ou vida sexual, dado genético ou biométrico, quando vinculado a uma pessoa natural. Dado anonimizado é aquele que não permite identificar o titular, considerando meios técnicos razoáveis.

Também são relevantes os papéis de controlador, operador e encarregado. O controlador toma decisões sobre o tratamento; o operador trata dados em nome do controlador; o encarregado atua como canal de comunicação entre controlador, titulares e ANPD. Em sistemas, isso ajuda a definir responsabilidades entre empresa, fornecedores, gateways, CRMs, ferramentas de suporte e provedores de cloud.

Implicação prática: antes de modelar tabelas, filas, eventos ou logs, é necessário classificar os dados. CPF, e-mail, telefone, endereço IP e identificadores de usuário normalmente são dados pessoais. Dados de saúde, biometria e informações de crianças demandam cuidado reforçado.

---

## Página 03 — Artigo 6º: princípios

O Art. 6º apresenta princípios que orientam todo tratamento de dados: finalidade, adequação, necessidade, livre acesso, qualidade dos dados, transparência, segurança, prevenção, não discriminação e responsabilização. Para software, os princípios mais recorrentes são finalidade, necessidade, transparência e segurança.

Finalidade significa que o dado deve ser tratado para propósitos legítimos, específicos e informados. Necessidade significa coletar apenas o mínimo necessário. Transparência significa deixar claro para o titular como seus dados serão usados. Segurança e prevenção exigem medidas técnicas e administrativas para proteger os dados contra acessos indevidos, vazamentos e usos não autorizados.

Exemplo: se o objetivo é autenticar um usuário, talvez e-mail e senha sejam suficientes; pedir CPF, data de nascimento e endereço completo sem justificativa pode violar o princípio da necessidade. Logs de erro também devem evitar armazenar payloads completos com dados pessoais.

---

## Página 04 — Artigo 7º: bases legais para dados pessoais comuns

O Art. 7º trata das bases legais para o tratamento de dados pessoais comuns. Entre as bases mais usadas em sistemas estão: consentimento, cumprimento de obrigação legal ou regulatória, execução de contrato, exercício regular de direitos, proteção da vida, tutela da saúde, legítimo interesse, proteção do crédito e execução de políticas públicas.

A base legal deve ser definida antes do tratamento. Consentimento não é sempre a melhor base, pois precisa ser livre, informado e inequívoco, além de poder ser revogado. Em muitos sistemas transacionais, execução de contrato ou obrigação legal podem ser mais adequadas. Para analytics, prevenção a fraude e melhoria de produto, pode haver legítimo interesse, desde que exista avaliação de proporcionalidade e respeito aos direitos do titular.

Exemplo: armazenar CPF para emissão de nota fiscal pode estar relacionado a obrigação legal. Guardar e-mail para login pode estar ligado à execução de contrato. Usar histórico de navegação para marketing personalizado pode exigir análise mais cuidadosa e, em alguns casos, consentimento.

---

## Página 05 — Artigo 11: dados pessoais sensíveis

Dados pessoais sensíveis exigem proteção reforçada. O tratamento pode ocorrer em hipóteses específicas, como consentimento destacado, cumprimento de obrigação legal, políticas públicas, estudos por órgão de pesquisa, exercício regular de direitos, proteção da vida, tutela da saúde, prevenção à fraude e segurança do titular em processos de identificação e autenticação.

Em software, campos sensíveis devem ser evitados quando não forem indispensáveis. Se forem necessários, deve-se aplicar controles adicionais: restrição de acesso, criptografia, segregação, auditoria, mascaramento, retenção menor e revisão de integrações. Dados de saúde, biometria e informações sobre menores são exemplos que exigem cuidado maior.

Exemplo: armazenar laudos médicos em um sistema de RH é muito mais sensível do que armazenar e-mail corporativo. O acesso deve ser limitado, justificado e auditável.

---

## Página 06 — Artigo 18: direitos do titular

O Art. 18 prevê direitos dos titulares, como confirmação da existência de tratamento, acesso aos dados, correção de dados incompletos ou desatualizados, anonimização, bloqueio ou eliminação de dados desnecessários, portabilidade, informação sobre compartilhamento e revogação do consentimento.

Para sistemas, esses direitos exigem mecanismos práticos. É recomendável ter processos e endpoints internos para localizar dados por titular, exportar informações, corrigir registros, anonimizar dados e registrar a execução da solicitação. Sistemas distribuídos devem mapear onde os dados estão: bancos relacionais, logs, data lakes, filas, backups, ferramentas de suporte e integrações.

Exemplo: se um cliente pede exclusão da conta, o sistema precisa saber quais dados podem ser eliminados, quais devem ser mantidos por obrigação legal e quais podem ser anonimizados.

---

## Página 07 — Artigo 37: registro das operações de tratamento

O Art. 37 trata da manutenção de registro das operações de tratamento de dados pessoais. Esse registro ajuda a demonstrar governança, finalidade, base legal, categorias de dados, sistemas envolvidos, compartilhamentos, prazos de retenção e medidas de segurança.

Em tecnologia, isso se conecta com inventário de dados, data catalog, documentação de APIs, diagramas de fluxo de dados, trilhas de auditoria e registros de consentimento. Quanto mais distribuída for a arquitetura, maior a necessidade de rastreabilidade.

Exemplo: um microserviço que envia eventos de usuário para uma ferramenta de marketing deve ter documentado quais campos são enviados, por qual finalidade, com qual base legal, por quanto tempo são retidos e quem é o fornecedor envolvido.

---

## Página 08 — Artigo 46: segurança da informação

O Art. 46 estabelece que agentes de tratamento devem adotar medidas de segurança, técnicas e administrativas aptas a proteger os dados pessoais contra acessos não autorizados e situações acidentais ou ilícitas de destruição, perda, alteração, comunicação ou difusão.

Medidas técnicas comuns incluem autenticação forte, autorização por perfil, criptografia, gestão de segredos, mascaramento, backups seguros, monitoramento, segregação de ambientes, proteção de logs e testes de segurança. Medidas administrativas incluem políticas, treinamentos, gestão de fornecedores, resposta a incidentes e revisão periódica de acessos.

Exemplo: salvar chaves de API ou dados pessoais em repositórios Git públicos aumenta o risco de incidente. Ambientes de desenvolvimento devem usar dados sintéticos ou anonimizados sempre que possível.

---

## Página 09 — Artigo 48: incidentes de segurança

O Art. 48 trata da comunicação de incidentes de segurança que possam acarretar risco ou dano relevante aos titulares. Quando há vazamento, acesso indevido ou exposição de dados pessoais, a organização deve avaliar impacto, natureza dos dados, quantidade de titulares afetados, medidas técnicas aplicadas e necessidade de comunicação à ANPD e aos titulares.

Para equipes de software, é importante ter logs auditáveis, plano de resposta a incidentes, classificação de severidade, canal de acionamento do DPO e mecanismos para contenção. O tempo de resposta depende da capacidade de identificar o que vazou, quando, por qual sistema e quais titulares foram impactados.

Exemplo: exposição pública de uma planilha com CPF e e-mail de clientes exige triagem imediata, remoção do acesso, investigação, registro do incidente e avaliação formal de comunicação.

---

## Página 10 — Retenção, minimização e descarte

A retenção de dados deve estar vinculada à finalidade e à base legal. Dados não devem ser mantidos indefinidamente apenas por conveniência. Quando a finalidade se encerra, a organização deve avaliar se há obrigação legal de manter, necessidade de defesa em processo, ou se deve eliminar/anonimizar.

Sistemas devem implementar políticas de retenção. Isso pode incluir jobs de expurgo, anonimização após determinado prazo, separação entre dados operacionais e históricos, e documentação de exceções. Backups também precisam ser considerados, pois podem conter dados eliminados do banco principal.

Exemplo: dados de candidatos não aprovados em processo seletivo podem ter prazo de retenção limitado. Guardar currículos eternamente sem transparência e sem base legal adequada pode gerar risco.

---

## Página 11 — Compartilhamento com terceiros e operadores

Quando dados são compartilhados com fornecedores, integrações ou ferramentas externas, é necessário avaliar finalidade, base legal, segurança, contrato e responsabilidades. Fornecedores podem atuar como operadores ou controladores independentes, dependendo do caso.

Arquiteturas modernas frequentemente usam gateways de pagamento, CRMs, analytics, ferramentas de e-mail, cloud, help desk e data warehouses. Cada integração deve ser mapeada. O envio de dados deve ser mínimo e proporcional à finalidade. Também é importante revisar transferências internacionais e controles do fornecedor.

Exemplo: enviar nome, e-mail, telefone, CPF e histórico completo de compra para uma ferramenta de marketing, quando apenas e-mail seria suficiente, pode violar minimização e aumentar risco.

---

## Página 12 — Boas práticas para times de desenvolvimento

Antes de criar uma nova funcionalidade, o time deve perguntar: qual dado pessoal será coletado, por quê, por quanto tempo, quem acessa, com quem será compartilhado, qual a base legal, como o titular será informado e como o dado será protegido. Essa análise pode ser documentada em um checklist de privacy by design.

Boas práticas: usar dados sintéticos em desenvolvimento, evitar logs com dados pessoais, criptografar campos críticos, versionar decisões de arquitetura, revisar permissões, auditar consultas sensíveis, manter catálogo de dados, revisar contratos com fornecedores e criar testes de regressão para garantir que dados sensíveis não vazem em respostas de API.

O objetivo não é impedir o uso de dados, mas permitir uso responsável, auditável e proporcional ao risco. Um assistente RAG com ferramenta de citação de artigo ajuda desenvolvedores a consultar rapidamente referências e registrar decisões, mas não substitui o jurídico ou o DPO.
