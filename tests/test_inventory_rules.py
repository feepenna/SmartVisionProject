# tests/test_inventory_rules.py
"""Testes de simulação das regras de negócio de inventário e conciliação (Change 03).

Estes testes exercitam, localmente, as mesmas regras implementadas no backend
XanoScript (tabelas e endpoints em xano/api/smart_vision/):

- Classificação de divergência (sem divergência / falta / sobra).
- Transições permitidas do ciclo de vida do inventário.
- Separação de funções (o contador não aprova a própria divergência).
- Idempotência de aplicação de ajuste (um ajuste aplicado uma vez por divergência).
- Tratamento de concorrência (saldo mudou entre contagem e aprovação).
- Prevenção de saldo negativo ao aplicar ajuste de falta.

São regras de simulação que espelham o comportamento esperado do XanoScript;
a implementação autoritativa reside nos endpoints Xano.
"""

from datetime import datetime

import unittest


# --------------------------------------------------------------------------- #
# Regras simuladas (espelham o backend XanoScript)
# --------------------------------------------------------------------------- #

VALID_STATUSES = ["Aberto", "EmContagem", "AguardandoAprovacao", "Concluido"]

ALLOWED_TRANSITIONS = {
    "Aberto": ["EmContagem"],
    "EmContagem": ["Aberto", "AguardandoAprovacao"],
    "AguardandoAprovacao": ["EmContagem", "Concluido"],
    "Concluido": [],  # não permite alteração retroativa
}

DIVERGENCE_NONE = "none"
DIVERGENCE_SHORTAGE = "shortage"
DIVERGENCE_OVERAGE = "overage"


def classify_divergence(counted_quantity, reference_quantity):
    """Classifica a divergência entre quantidade contada e saldo de referência."""
    difference = counted_quantity - reference_quantity
    if difference == 0:
        return DIVERGENCE_NONE, difference, "Sem divergência"
    if difference < 0:
        return DIVERGENCE_SHORTAGE, difference, "Falta de estoque: físico menor que o registrado."
    return DIVERGENCE_OVERAGE, difference, "Sobra de estoque: físico maior que o registrado."


def allowed_transition(from_status, to_status):
    """Retorna True se a transição de estado é permitida."""
    if from_status not in VALID_STATUSES or to_status not in VALID_STATUSES:
        return False
    return to_status in ALLOWED_TRANSITIONS.get(from_status, [])


def can_decide(decider_id, latest_count, decider_is_manager):
    """Separação de funções + permissão de gestor.

    Retorna (permitido, motivo).
    """
    if not decider_is_manager:
        return False, "Apenas usuários com perfil de gestor podem decidir sobre divergências."
    if latest_count is not None and latest_count.get("counted_by") == decider_id:
        return False, "O responsável pela contagem não pode aprovar a própria divergência (separação de funções)."
    return True, ""


def apply_adjustment(product_current_stock, reference_quantity, counted_quantity, adjustment_applied):
    """Simula a aplicação de um ajuste de estoque.

    Regras:
    - Idempotência: se adjustment_applied for True, não aplica novamente.
    - Concorrência: compara saldo atual com referência.
      * Iguais -> aplica ajuste diretamente.
      * Diferentes -> recalcula; se a nova diferença for 0, nada a ajustar (movimentações posteriores zeraram a divergência);
        senão, solicita recontagem (não aplica com segurança).
    - Saldo negativo: para falta (shortage), não permite saldo negativo.

    Retorna dict com: applied, skipped, reason, new_stock (quando aplicável).
    """
    if adjustment_applied:
        return {"applied": False, "skipped": True, "reason": "Ajuste já foi aplicado anteriormente (idempotência)."}

    if product_current_stock == reference_quantity:
        difference = counted_quantity - reference_quantity
        new_stock = product_current_stock + difference
        if difference < 0 and product_current_stock < abs(difference):
            return {
                "applied": False, "skipped": True,
                "reason": "Saldo insuficiente para aplicar ajuste de falta (saldo negativo não permitido).",
                "new_stock": product_current_stock,
            }
        return {
            "applied": True, "skipped": False,
            "reason": "Ajuste aplicado.",
            "new_stock": new_stock,
            "difference": difference,
        }

    # Concorrência: saldo mudou entre contagem e aprovação
    difference_now = counted_quantity - product_current_stock
    if difference_now == 0:
        return {
            "applied": True, "skipped": False,
            "reason": "Divergência zerada por movimentações posteriores; nenhum ajuste necessário.",
            "new_stock": product_current_stock,
        }
    return {
        "applied": False, "skipped": True,
        "reason": "Saldo divergente da referência (movimentação concorrente). Solicitar recontagem.",
        "new_stock": product_current_stock,
        "difference_now": difference_now,
    }


# --------------------------------------------------------------------------- #
# Testes
# --------------------------------------------------------------------------- #

class TestClassificationRules(unittest.TestCase):

    def test_sem_divergencia(self):
        tipo, diff, impacto = classify_divergence(5, 5)
        self.assertEqual(tipo, "none")
        self.assertEqual(diff, 0)
        self.assertIn("Sem divergência", impacto)

    def test_falta_de_estoque(self):
        tipo, diff, impacto = classify_divergence(3, 5)
        self.assertEqual(tipo, "shortage")
        self.assertEqual(diff, -2)
        self.assertIn("Falta de estoque", impacto)

    def test_sobra_de_estoque(self):
        tipo, diff, impacto = classify_divergence(7, 5)
        self.assertEqual(tipo, "overage")
        self.assertEqual(diff, 2)
        self.assertIn("Sobra de estoque", impacto)


class TestTransitionRules(unittest.TestCase):

    def test_transicoes_permitidas(self):
        self.assertTrue(allowed_transition("Aberto", "EmContagem"))
        self.assertTrue(allowed_transition("EmContagem", "AguardandoAprovacao"))
        self.assertTrue(allowed_transition("AguardandoAprovacao", "Concluido"))
        self.assertTrue(allowed_transition("EmContagem", "Aberto"))
        self.assertTrue(allowed_transition("AguardandoAprovacao", "EmContagem"))

    def test_transicoes_invalidas(self):
        self.assertFalse(allowed_transition("Aberto", "AguardandoAprovacao"))  # pular contagem
        self.assertFalse(allowed_transition("Aberto", "Concluido"))  # pular etapas
        self.assertFalse(allowed_transition("Concluido", "EmContagem"))  # conclusão é imutável
        self.assertFalse(allowed_transition("Concluido", "Aberto"))

    def test_status_invalido(self):
        self.assertFalse(allowed_transition("Aberto", "QualquerCoisa"))
        self.assertFalse(allowed_transition("QualquerCoisa", "EmContagem"))


class TestAuthorizationRules(unittest.TestCase):

    def test_gestor_pode_decidir(self):
        permitido, motivo = can_decide(2, {"counted_by": 1}, decider_is_manager=True)
        self.assertTrue(permitido)

    def test_nao_gestor_nao_pode_decidir(self):
        permitido, motivo = can_decide(2, {"counted_by": 1}, decider_is_manager=False)
        self.assertFalse(permitido)
        self.assertIn("gestor", motivo)

    def test_contador_nao_aprovar_propria_divergencia(self):
        permitido, motivo = can_decide(1, {"counted_by": 1}, decider_is_manager=True)
        self.assertFalse(permitido)
        self.assertIn("separação de funções", motivo)

    def test_contador_de_outro_produto_pode_decidir(self):
        # Mesmo que seja o contador de uma contagem, se não contou este produto, pode decidir
        permitido, motivo = can_decide(1, {"counted_by": 9}, decider_is_manager=True)
        self.assertTrue(permitido)


class TestAdjustmentRules(unittest.TestCase):

    def test_idempotencia_nao_aplica_dois_vezes(self):
        resultado = apply_adjustment(5, 5, 7, adjustment_applied=True)
        self.assertFalse(resultado["applied"])
        self.assertTrue(resultado["skipped"])
        self.assertIn("idempotência", resultado["reason"])

    def test_aplicar_ajuste_sobra(self):
        resultado = apply_adjustment(5, 5, 7, adjustment_applied=False)
        self.assertTrue(resultado["applied"])
        self.assertEqual(resultado["new_stock"], 7)
        self.assertEqual(resultado["difference"], 2)

    def test_aplicar_ajuste_falta_respeita_saldo(self):
        resultado = apply_adjustment(2, 5, 3, adjustment_applied=False)
        # referencia 5, atual 2 -> concorrência! diferente -> recalcula
        self.assertFalse(resultado["applied"])
        self.assertTrue(resultado["skipped"])
        self.assertIn("concorrente", resultado["reason"])

    def test_falta_sem_concorrencia_saldo_suficiente(self):
        resultado = apply_adjustment(5, 5, 3, adjustment_applied=False)
        self.assertTrue(resultado["applied"])
        self.assertEqual(resultado["new_stock"], 3)

    def test_falta_sem_concorrencia_reduz_ate_zero(self):
        # saldo atual 1, referencia 1, contado 0 -> falta de 1, novo saldo 0 (nao negativo)
        resultado = apply_adjustment(1, 1, 0, adjustment_applied=False)
        self.assertTrue(resultado["applied"])
        self.assertEqual(resultado["new_stock"], 0)

    def test_concorrencia_saldo_igual_referencia_aplica(self):
        # Simulado na função: quando current_stock == reference, aplica diretamente
        resultado = apply_adjustment(8, 8, 10, adjustment_applied=False)
        self.assertTrue(resultado["applied"])
        self.assertEqual(resultado["new_stock"], 10)

    def test_concorrencia_divergencia_zerada_nao_ajusta(self):
        # referencia 5, atual 7, contado 7 -> diferenca agora 0 -> nenhum ajuste necessario
        resultado = apply_adjustment(7, 5, 7, adjustment_applied=False)
        self.assertTrue(resultado["applied"])
        self.assertEqual(resultado["new_stock"], 7)
        self.assertIn("nenhum ajuste necessário", resultado["reason"])

    def test_concorrencia_nao_seguro_solicita_recontagem(self):
        # referencia 5, atual 6, contado 8 -> diferenca agora 2, nao eh 0 e saldo mudou -> recontagem
        resultado = apply_adjustment(6, 5, 8, adjustment_applied=False)
        self.assertFalse(resultado["applied"])
        self.assertTrue(resultado["skipped"])
        self.assertIn("recontagem", resultado["reason"])


if __name__ == "__main__":
    unittest.main()
