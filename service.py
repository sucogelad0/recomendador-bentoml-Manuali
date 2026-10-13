"""Serviço de recomendação de produtos artesanais do Origem."""

from __future__ import annotations

import pickle
from pathlib import Path

import bentoml

modelo = bentoml.models.get("recomendador:latest")
ARTEFATO = "model.pkl"


@bentoml.service(resources={"cpu": "1"})
class Recomendador:

    def __init__(self) -> None:
        caminho = Path(modelo.path_of(ARTEFATO))
        self.artefato = pickle.loads(caminho.read_bytes())

    @bentoml.api
    def recomendar(
        self,
        produto_na_pagina: str,
        limite: int = 4,
        excluir: list[str] | None = None,
    ) -> dict:
        """Recomenda produtos relevantes e disponíveis no marketplace."""

        produtos = self.artefato["produtos"]
        pagina = produto_na_pagina

        # Valida a quantidade solicitada.
        if limite < 1 or limite > 12:
            return {
                "erro": "limite_invalido",
                "mensagem": "O limite deve estar entre 1 e 12.",
                "items": [],
            }

        # Verifica se o produto existe.
        if pagina not in produtos:
            return {
                "erro": "produto_inexistente",
                "produto_na_pagina": pagina,
                "items": [],
            }

        excluir_set = set(excluir or [])
        excluir_set.add(pagina)

        atual = produtos[pagina]
        tecnica = atual.get("tecnica", "")
        regiao = atual.get("regiao", "")

        pedidos_brutos = self.artefato.get("pedidos_brutos", {})
        cooc = self.artefato.get("cooc", {})
        cooc_pagina = cooc.get(pagina, {})

        def artesao_disponivel(produto: dict) -> bool:
            """Descarta artesãos suspensos ou banidos."""
            status = produto.get(
                "status_artesao",
                produto.get("situacao_artesao", "ativo"),
            )
            return str(status).strip().lower() not in {
                "suspenso",
                "suspensa",
                "banido",
                "banida",
            }

        def produto_disponivel(produto: dict) -> bool:
            """Só permite produtos com estoque positivo."""
            try:
                estoque = int(produto.get("estoque", 0))
            except (TypeError, ValueError):
                return False

            return estoque > 0 and artesao_disponivel(produto)

        # Exclui produtos indisponíveis e itens que o usuário já viu/comprou.
        candidatos = [
            pid
            for pid, produto in produtos.items()
            if pid not in excluir_set
            and produto_disponivel(produto)
        ]

        def pontuacao(pid: str) -> tuple:
            produto = produtos[pid]

            mesma_tecnica = produto.get("tecnica", "") == tecnica
            mesma_regiao = produto.get("regiao", "") == regiao
            coocorrencia = cooc_pagina.get(pid, 0.0)

            # A relevância considera técnica, região e produtos
            # frequentemente presentes na mesma cesta.
            score = (
                (0.50 if mesma_tecnica else 0.0)
                + (0.20 if mesma_regiao else 0.0)
                + (0.30 * float(coocorrencia))
            )

            return (
                score,
                mesma_tecnica,
                mesma_regiao,
                pid,
            )

        # Ordena por relevância, sem usar popularidade comercial
        # ou pedidos como fator de pontuação.
        candidatos.sort(key=pontuacao, reverse=True)

        escolhidos = candidatos[:limite]
        complemento_usado = any(
            produtos[pid].get("tecnica", "") != tecnica
            for pid in escolhidos
        )

        items = []

        for rank, pid in enumerate(escolhidos, start=1):
            produto = produtos[pid]

            mesma_tecnica = produto.get("tecnica", "") == tecnica
            mesma_regiao = produto.get("regiao", "") == regiao
            coocorrencia = cooc_pagina.get(pid, 0.0)

            score = (
                (0.50 if mesma_tecnica else 0.0)
                + (0.20 if mesma_regiao else 0.0)
                + (0.30 * float(coocorrencia))
            )

            if mesma_tecnica and mesma_regiao:
                motivo = "mesma_tecnica_e_regiao"
            elif mesma_tecnica:
                motivo = "mesma_tecnica"
            elif mesma_regiao:
                motivo = "mesma_regiao"
            elif coocorrencia > 0:
                motivo = "comprados_na_mesma_cesta"
            else:
                motivo = "recomendacao_complementar"

            items.append({
                "product_id": pid,
                "nome": produto.get("nome", ""),
                "tecnica": produto.get("tecnica", ""),
                "regiao": produto.get("regiao", ""),
                "estoque": int(produto["estoque"]),
                "id_artesao": produto.get("id_artesao"),
                "nome_artesao": produto.get("nome_artesao"),
                "score": round(score, 4),
                "reason": motivo,
                "rank": rank,
            })

        return {
            "items": items,
            "strategy": "relevancia_por_tecnica_regiao_e_cestas",
            "complemento_usado": complemento_usado,
            "produto_na_pagina": {
                "product_id": pagina,
                "nome": atual.get("nome", ""),
                "tecnica": tecnica,
                "regiao": regiao,
            },
            "modelo": str(modelo.tag),
        }