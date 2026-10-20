# Tasks: inventory-movements

- [x] Criar definição da tabela `stock_movement` em `xano/table/stock_movement.xs`
- [x] Criar endpoint de entrada de estoque em `xano/api/smart_vision/stock_entry_POST.xs`
- [x] Criar endpoint de saída de estoque em `xano/api/smart_vision/stock_exit_POST.xs` com validação de saldo negativo
- [x] Atualizar `services/xano_client.py` com funções `record_stock_entry` e `record_stock_exit`
- [x] Verificar e validar conformidade com AGENTS.md (auditoria obrigatória prévia, transação atômica, validação de entradas)
