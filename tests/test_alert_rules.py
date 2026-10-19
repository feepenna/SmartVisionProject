# tests/test_alert_rules.py
"""Testes de simulação das regras de negócio de alertas e reposição (Change 05).

Estes testes exercitam, localmente, as mesmas regras implementadas no backend
XanoScript (funções e endpoints em xano/):

- Classificação de criticidade por faixas disjuntas (``classificar_produto``).
- Sugestão de reposição ``max(0, alvo - saldo)`` e sinalização de parâmetros
  incompletos (``replenishment``).
- Ciclo de vida do alerta: criação, auto-resolução por condição normalizada,
  silenciamento após resolução manual e nunca duplicar alerta aberto
  (``avaliar_alerta``).
- Detecção de inatividade diferenciando ``Inativo`` de ``SemHistorico``.
- Matriz de autorização por perfil validada no backend.

São regras de simulação que espelham o comportamento esperado do XanoScript;
a implementação autoritativa reside nos endpoints Xano.
"""

import unittest


# --------------------------------------------------------------------------- #
# Regras simuladas (espelham o backend XanoScript)
# --------------------------------------------------------------------------- #

ALERT_STATUSES = ["Ativo", "EmAcompanhamento", "Resolvido"]
ALERT_TYPES = ["LOW_STOCK", "INACTIVE"]

ALLOWED_ALERT_TRANSITIONS = {
    "Ativo": ["EmAcompanhamento", "Resolvido"],
    "EmAcompanhamento": ["Resolvido"],
    "Resolvido": [],  # estado final, não permite alteração retroativa
}

# Perfis autorizados (conforme domain-model / design da Change 05)
READ_ROLES = ["Gestor", "Estoquista", "Vendedor", "Técnico", "admin", "member"]
EVALUATE_ROLES = ["Gestor", "Estoquista", "admin"]
PARAMETER_ROLES = ["Gestor", "admin"]

DEFAULT_INACTIVITY_DAYS = 30


def classify_product(current_stock, min_stock, target_stock=None):
    """Classifica a criticidade por faixas disjuntas.

    Espelha ``Smart Vision/classificar_produto``:
    - ``critico`` quando saldo <= mínimo (tem precedência);
    - ``insuficiente`` quando saldo > mínimo e < alvo (só com alvo definido);
    - ``regular`` nos demais casos.
    """
    if current_stock <= min_stock:
        return "critico"
    if target_stock is not None and current_stock < target_stock:
        return "insuficiente"
    return "regular"


def replenishment_suggestion(current_stock, target_stock):
    """Sugestão de reposição = ``max(0, alvo - saldo)``.

    Retorna ``None`` quando não há alvo configurado (parâmetros incompletos).
    """
    if target_stock is None:
        return None
    return max(0, target_stock - current_stock)


def allowed_alert_transition(from_status, to_status):
    """Retorna True se a transição de status do alerta é permitida."""
    if from_status not in ALERT_STATUSES or to_status not in ALERT_STATUSES:
        return False
    return to_status in ALLOWED_ALERT_TRANSITIONS.get(from_status, [])


def can_read(role):
    return role in READ_ROLES


def can_evaluate(role):
    return role in EVALUATE_ROLES


def can_configure_parameters(role):
    return role in PARAMETER_ROLES


def evaluate_condition(alert_type, product, ultima_movimentacao_ts, now_ts):
    """Calcula se a condição do alerta está valendo.

    - LOW_STOCK: saldo <= mínimo.
    - INACTIVE: existe histórico e a última movimentação é anterior à janela.

    Um produto sem histórico nunca satisfaz INACTIVE.
    """
    if alert_type == "LOW_STOCK":
        return product.get("current_stock", 0) <= product.get("min_stock", 0)

    if alert_type == "INACTIVE":
        if ultima_movimentacao_ts is None:
            return False
        janela_dias = product.get("inactivity_days") or DEFAULT_INACTIVITY_DAYS
        limite = now_ts - (janela_dias * 86400)
        return ultima_movimentacao_ts < limite

    raise ValueError("Tipo de alerta inválido.")


def avaliar_alerta(product, alert_type, ultimo_alerta, ultima_movimentacao_ts, now_ts):
    """Simula o ciclo de vida de UMA condição de UM produto.

    Espelha ``Smart Vision/avaliar_alerta`` e retorna a ``acao`` esperada:
    ``criado``, ``resolvido``, ``silenciado``, ``condicao_normalizada``,
    ``ignorado`` ou ``nenhuma``.
    """
    condicao = evaluate_condition(alert_type, product, ultima_movimentacao_ts, now_ts)

    aberto = ultimo_alerta is not None and ultimo_alerta.get("status") != "Resolvido"

    if product.get("alerts_enabled", True) is False:
        return "ignorado"

    # A. Condição valendo e nenhum alerta aberto
    if condicao and not aberto:
        silenciado = (
            ultimo_alerta is not None
            and ultimo_alerta.get("status") == "Resolvido"
            and ultimo_alerta.get("resolution") == "manual"
            and ultimo_alerta.get("condition_cleared_at") is None
        )
        return "silenciado" if silenciado else "criado"

    # B. Condição normalizada com alerta aberto -> auto-resolução registrada
    if not condicao and aberto:
        return "resolvido"

    # C. Último resolvido ainda sem registro de normalização
    if (
        not condicao
        and not aberto
        and ultimo_alerta is not None
        and ultimo_alerta.get("status") == "Resolvido"
        and ultimo_alerta.get("condition_cleared_at") is None
    ):
        return "condicao_normalizada"

    return "nenhuma"


def inactivity_situation(current_stock, ultima_movimentacao_ts, inactivity_days, now_ts, monitored=True):
    """Situação de movimentação exibida pela consulta de produtos.

    Retorna ``Ativo``, ``Inativo`` ou ``SemHistorico``.
    """
    if ultima_movimentacao_ts is None:
        return "SemHistorico"
    limite = now_ts - (inactivity_days * 86400)
    return "Inativo" if ultima_movimentacao_ts < limite else "Ativo"


NOW = 1_800_000_000  # epoch (s) de referência para os testes
ONE_DAY = 86400


# --------------------------------------------------------------------------- #
# Testes
# --------------------------------------------------------------------------- #

class TestClassificationRules(unittest.TestCase):

    def test_saldo_igual_ao_minimo_e_critico(self):
        self.assertEqual(classify_product(5, 5, 20), "critico")

    def test_saldo_abaixo_do_minimo_e_critico(self):
        self.assertEqual(classify_product(0, 5, 20), "critico")

    def test_entre_minimo_e_alvo_e_insuficiente(self):
        self.assertEqual(classify_product(10, 5, 20), "insuficiente")

    def test_no_alvo_ou_acima_e_regular(self):
        self.assertEqual(classify_product(20, 5, 20), "regular")
        self.assertEqual(classify_product(25, 5, 20), "regular")

    def test_sem_alvo_acima_do_minimo_e_regular(self):
        # Sem alvo, o produto nunca é "insuficiente" (faixas disjuntas)
        self.assertEqual(classify_product(10, 5, None), "regular")

    def test_faixas_sao_disjuntas(self):
        # Cada saldo produz exatamente uma classificação
        for stock in range(0, 31):
            resultado = classify_product(stock, 5, 20)
            self.assertIn(resultado, ("critico", "insuficiente", "regular"))


class TestReplenishmentRules(unittest.TestCase):

    def test_sugestao_com_alvo(self):
        self.assertEqual(replenishment_suggestion(7, 20), 13)

    def test_saldo_acima_do_alvo_zera_sugestao(self):
        self.assertEqual(replenishment_suggestion(25, 20), 0)

    def test_saldo_igual_ao_alvo_zera_sugestao(self):
        self.assertEqual(replenishment_suggestion(20, 20), 0)

    def test_sem_alvo_retorna_none(self):
        self.assertIsNone(replenishment_suggestion(7, None))

    def test_sugestao_nunca_negativa(self):
        for saldo in range(0, 51):
            self.assertGreaterEqual(replenishment_suggestion(saldo, 20), 0)


class TestAlertTransitionRules(unittest.TestCase):

    def test_transicoes_permitidas(self):
        self.assertTrue(allowed_alert_transition("Ativo", "EmAcompanhamento"))
        self.assertTrue(allowed_alert_transition("Ativo", "Resolvido"))
        self.assertTrue(allowed_alert_transition("EmAcompanhamento", "Resolvido"))

    def test_transicoes_invalidas(self):
        # Resolvido é final e não há retorno para Ativo
        self.assertFalse(allowed_alert_transition("Resolvido", "Ativo"))
        self.assertFalse(allowed_alert_transition("Resolvido", "EmAcompanhamento"))
        # Não se pula direto de EmAcompanhamento para Ativo
        self.assertFalse(allowed_alert_transition("EmAcompanhamento", "Ativo"))

    def test_status_inexistente_e_invalido(self):
        self.assertFalse(allowed_alert_transition("Ativo", "QualquerCoisa"))
        self.assertFalse(allowed_alert_transition("QualquerCoisa", "Ativo"))


class TestEvaluateLifecycleRules(unittest.TestCase):

    def _produto(self, **kwargs):
        base = {"current_stock": 2, "min_stock": 5, "target_stock": 20, "alerts_enabled": True}
        base.update(kwargs)
        return base

    def test_cria_alerta_quando_condicao_vale_e_nao_ha_aberto(self):
        acao = avaliar_alerta(self._produto(), "LOW_STOCK", None, None, NOW)
        self.assertEqual(acao, "criado")

    def test_nao_duplica_alerta_ja_aberto(self):
        ultimo = {"status": "Ativo", "resolution": None, "condition_cleared_at": None}
        acao = avaliar_alerta(self._produto(), "LOW_STOCK", ultimo, None, NOW)
        self.assertEqual(acao, "nenhuma")

    def test_auto_resolve_quando_condicao_normaliza(self):
        ultimo = {"status": "Ativo", "resolution": None, "condition_cleared_at": None}
        produto = self._produto(current_stock=10)  # saldo acima do mínimo
        acao = avaliar_alerta(produto, "LOW_STOCK", ultimo, None, NOW)
        self.assertEqual(acao, "resolvido")

    def test_resolucao_manual_silencia_enquanto_condicao_persiste(self):
        ultimo = {"status": "Resolvido", "resolution": "manual", "condition_cleared_at": None}
        acao = avaliar_alerta(self._produto(), "LOW_STOCK", ultimo, None, NOW)
        self.assertEqual(acao, "silenciado")

    def test_produto_sem_historico_nao_gera_inactive(self):
        acao = avaliar_alerta(self._produto(current_stock=50), "INACTIVE", None, None, NOW)
        self.assertEqual(acao, "nenhuma")

    def test_inativo_com_historico_antigo_gera_alerta(self):
        produto = self._produto(current_stock=50)
        antiga = NOW - (40 * ONE_DAY)  # 40 dias atrás (> janela padrão de 30)
        acao = avaliar_alerta(produto, "INACTIVE", None, antiga, NOW)
        self.assertEqual(acao, "criado")

    def test_movimentacao_recente_nao_e_inativo(self):
        produto = self._produto(current_stock=50)
        recente = NOW - (5 * ONE_DAY)
        acao = avaliar_alerta(produto, "INACTIVE", None, recente, NOW)
        self.assertEqual(acao, "nenhuma")

    def test_monitoramento_desativado_ignora(self):
        produto = self._produto(alerts_enabled=False)
        acao = avaliar_alerta(produto, "LOW_STOCK", None, None, NOW)
        self.assertEqual(acao, "ignorado")

    def test_normalizacao_registrada_apos_resolucao(self):
        # Último resolvido (auto) sem condition_cleared_at e condição já normalizada
        ultimo = {"status": "Resolvido", "resolution": "condicao_normalizada", "condition_cleared_at": None}
        produto = self._produto(current_stock=10)
        acao = avaliar_alerta(produto, "LOW_STOCK", ultimo, None, NOW)
        self.assertEqual(acao, "condicao_normalizada")


class TestInactivityRules(unittest.TestCase):

    def test_sem_historico(self):
        self.assertEqual(inactivity_situation(50, None, 30, NOW), "SemHistorico")

    def test_inativo_fora_da_janela(self):
        ultima = NOW - (40 * ONE_DAY)
        self.assertEqual(inactivity_situation(50, ultima, 30, NOW), "Inativo")

    def test_ativo_dentro_da_janela(self):
        ultima = NOW - (10 * ONE_DAY)
        self.assertEqual(inactivity_situation(50, ultima, 30, NOW), "Ativo")

    def test_janela_do_produto_prevalece(self):
        ultima = NOW - (20 * ONE_DAY)
        # Janela de 15 dias -> 20 dias é inativo
        self.assertEqual(inactivity_situation(50, ultima, 15, NOW), "Inativo")
        # Janela de 30 dias -> 20 dias é ativo
        self.assertEqual(inactivity_situation(50, ultima, 30, NOW), "Ativo")


class TestAuthorizationRules(unittest.TestCase):

    def test_leitura_para_todos_os_perfis(self):
        for role in READ_ROLES:
            self.assertTrue(can_read(role), f"{role} deveria poder ler")

    def test_avaliacao_apenas_gestor_estoquista_admin(self):
        self.assertTrue(can_evaluate("Gestor"))
        self.assertTrue(can_evaluate("Estoquista"))
        self.assertTrue(can_evaluate("admin"))
        for role in ["Vendedor", "Técnico", "member"]:
            self.assertFalse(can_evaluate(role), f"{role} não deveria avaliar alertas")

    def test_parametros_apenas_gestor_admin(self):
        self.assertTrue(can_configure_parameters("Gestor"))
        self.assertTrue(can_configure_parameters("admin"))
        for role in ["Estoquista", "Vendedor", "Técnico", "member"]:
            self.assertFalse(can_configure_parameters(role), f"{role} não deveria configurar parâmetros")


if __name__ == "__main__":
    unittest.main()
