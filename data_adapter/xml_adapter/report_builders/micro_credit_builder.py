"""Builder for InfoAgregadaMicrocredito node → MicroCreditAggregatedInfo."""

from typing import Optional
from xml.etree import ElementTree as ET

from data_adapter.xml_adapter.models.aggregated_info_models import (
    AccountBehaviorVector,
    BalanceDelinquencyVector,
    BehaviorMonthlyChar,
    CurrentDebtAccount,
    CurrentDebtBySector,
    CurrentDebtByType,
    CurrentDebtByUser,
    GeneralProfile,
    MicroCreditAggregatedInfo,
    MonthlyBalancesAndArrears,
    SectorBehaviorVector,
    SectorCreditCount,
    SectorSeniority,
    TrendDataPoint,
    TrendSeries,
)
from data_adapter.xml_adapter.report_builders.aggregated_info_builder import (
    parse_debt_evolution_analysis,
    parse_debt_evolution_quarters,
)
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class MicroCreditBuilder:
    """Parses <InfoAgregadaMicrocredito> within an <Informe> node."""

    def __init__(self, ex: XmlExtractor, report_node: ET.Element) -> None:
        self._ex = ex
        self._report_node = report_node

    def build(self) -> Optional[MicroCreditAggregatedInfo]:
        micro_node = self._ex.find_node(
            "InfoAgregadaMicrocredito", parent=self._report_node
        )
        if micro_node is None:
            return None

        resumen_node = self._ex.find_node("Resumen", parent=micro_node)
        analisis_node = self._ex.find_node("AnalisisVectores", parent=micro_node)
        evolution_node = self._ex.find_node("EvolucionDeuda", parent=micro_node)

        imagen_node: Optional[ET.Element] = None
        if resumen_node is not None:
            imagen_node = self._ex.find_node(
                "ImagenTendenciaEndeudamiento", parent=resumen_node
            )

        return MicroCreditAggregatedInfo(
            general_profile=self._parse_general_profile(resumen_node),
            balance_delinquency_vector=self._parse_balance_delinquency_vector(
                resumen_node
            ),
            current_debt_by_sector=self._parse_current_debt(resumen_node),
            sector_behavior_vectors=self._parse_behavior_vectors(analisis_node),
            trend_series=self._parse_trend_series(imagen_node),
            debt_evolution=parse_debt_evolution_quarters(self._ex, evolution_node),
            debt_evolution_analysis=parse_debt_evolution_analysis(
                self._ex, evolution_node
            ),
        )

    # ── PerfilGeneral ─────────────────────────────────────────────────────────

    def _parse_general_profile(
        self, resumen_node: Optional[ET.Element]
    ) -> Optional[GeneralProfile]:
        if resumen_node is None:
            return None
        node = self._ex.find_node("PerfilGeneral", parent=resumen_node)
        if node is None:
            return None

        antiguedad_node = self._ex.find_node("AntiguedadDesde", parent=node)
        oldest = SectorSeniority(
            financial=self._ex.get_attr(antiguedad_node, "sectorFinanciero"),
            cooperative=self._ex.get_attr(antiguedad_node, "sectorCooperativo"),
            real=self._ex.get_attr(antiguedad_node, "sectorReal"),
            telecom=self._ex.get_attr(antiguedad_node, "sectorTelcos"),
        )
        return GeneralProfile(
            active_credits=self._parse_sector_credit_count(node, "CreditosVigentes"),
            closed_credits=self._parse_sector_credit_count(node, "CreditosCerrados"),
            restructured_credits=self._parse_sector_credit_count(
                node, "CreditosReestructurados"
            ),
            refinanced_credits=self._parse_sector_credit_count(
                node, "CreditosRefinanciados"
            ),
            queries_last_6m=self._parse_sector_credit_count(node, "ConsultaUlt6Meses"),
            disputes=self._parse_sector_credit_count(node, "Desacuerdos"),
            oldest_account=oldest,
        )

    def _parse_sector_credit_count(
        self, parent: ET.Element, tag: str
    ) -> SectorCreditCount:
        child = self._ex.find_node(tag, parent=parent)
        return SectorCreditCount(
            financial=self._ex.get_int(child, "sectorFinanciero") or 0,
            cooperative=self._ex.get_int(child, "sectorCooperativo") or 0,
            real=self._ex.get_int(child, "sectorReal") or 0,
            telecom=self._ex.get_int(child, "sectorTelcos") or 0,
            total_as_principal=self._ex.get_int(child, "totalComoPrincipal") or 0,
            total_as_cosigner=self._ex.get_int(child, "totalComoCodeudorYOtros") or 0,
        )

    # ── VectorSaldosYMoras ────────────────────────────────────────────────────

    def _parse_balance_delinquency_vector(
        self, resumen_node: Optional[ET.Element]
    ) -> Optional[BalanceDelinquencyVector]:
        if resumen_node is None:
            return None
        node = self._ex.find_node("VectorSaldosYMoras", parent=resumen_node)
        if node is None:
            return None

        monthly = tuple(
            MonthlyBalancesAndArrears(
                date=self._ex.get_attr_required(sm, "fecha"),
                total_accounts_past_due=self._ex.get_int(sm, "totalCuentasMora") or 0,
                past_due_balance=self._ex.get_float(sm, "saldoDeudaTotalMora") or 0.0,
                total_balance=self._ex.get_float(sm, "saldoDeudaTotal") or 0.0,
                max_delinquency_financial=self._ex.get_attr(
                    sm, "morasMaxSectorFinanciero"
                ),
                max_delinquency_cooperative=self._ex.get_attr(
                    sm, "morasMaxSectorCooperativo"
                ),
                max_delinquency_real=self._ex.get_attr(sm, "morasMaxSectorReal"),
                max_delinquency_telecom=self._ex.get_attr(sm, "morasMaxSectorTelcos"),
                max_delinquency_overall=self._ex.get_attr(sm, "morasMaximas"),
                accounts_past_due_30=self._ex.get_int(sm, "numCreditos30"),
                accounts_past_due_60_plus=self._ex.get_int(
                    sm, "numCreditosMayorIgual60"
                ),
            )
            for sm in node.findall("SaldosYMoras")
        )
        return BalanceDelinquencyVector(
            has_financial=self._bool_attr(node, "poseeSectorFinanciero"),
            has_cooperative=self._bool_attr(node, "poseeSectorCooperativo"),
            has_real=self._bool_attr(node, "poseeSectorReal"),
            has_telecom=self._bool_attr(node, "poseeSectorTelcos"),
            monthly_data=monthly,
        )

    # ── EndeudamientoActual ───────────────────────────────────────────────────

    def _parse_current_debt(
        self, resumen_node: Optional[ET.Element]
    ) -> tuple[CurrentDebtBySector, ...]:
        if resumen_node is None:
            return ()
        actual_node = self._ex.find_node("EndeudamientoActual", parent=resumen_node)
        if actual_node is None:
            return ()
        return tuple(
            self._parse_current_debt_sector(s) for s in actual_node.findall("Sector")
        )

    def _parse_current_debt_sector(self, node: ET.Element) -> CurrentDebtBySector:
        by_type = tuple(
            self._parse_current_debt_type(t) for t in node.findall("TipoCuenta")
        )
        return CurrentDebtBySector(
            sector_code=self._ex.get_attr(node, "codSector") or "",
            by_type=by_type,
        )

    def _parse_current_debt_type(self, node: ET.Element) -> CurrentDebtByType:
        by_user = tuple(
            self._parse_current_debt_user(u) for u in node.findall("Usuario")
        )
        return CurrentDebtByType(
            account_type=self._ex.get_attr(node, "tipoCuenta") or "",
            by_user=by_user,
        )

    def _parse_current_debt_user(self, node: ET.Element) -> CurrentDebtByUser:
        accounts = tuple(
            CurrentDebtAccount(
                current_state=self._ex.get_attr(c, "estadoActual"),
                rating=self._ex.get_attr(c, "calificacion"),
                initial_value=self._ex.get_float(c, "valorInicial"),
                current_balance=self._ex.get_float(c, "saldoActual"),
                past_due_balance=self._ex.get_float(c, "saldoMora"),
                monthly_installment=self._ex.get_float(c, "cuotaMes"),
                has_negative_behavior=self._optional_bool(
                    self._ex.get_attr(c, "comportamientoNegativo")
                ),
                total_portfolio_debt=self._ex.get_float(c, "totalDeudaCarteras"),
            )
            for c in node.findall("Cuenta")
        )
        return CurrentDebtByUser(
            user_type=self._ex.get_attr(node, "tipoUsuario") or "",
            accounts=accounts,
        )

    # ── AnalisisVectores ──────────────────────────────────────────────────────

    def _parse_behavior_vectors(
        self, analisis_node: Optional[ET.Element]
    ) -> tuple[SectorBehaviorVector, ...]:
        if analisis_node is None:
            return ()
        return tuple(
            self._parse_sector_behavior(s) for s in analisis_node.findall("Sector")
        )

    def _parse_sector_behavior(self, node: ET.Element) -> SectorBehaviorVector:
        accounts = tuple(
            self._parse_account_behavior(c) for c in node.findall("Cuenta")
        )
        return SectorBehaviorVector(
            sector_name=self._ex.get_attr(node, "nombreSector") or "",
            accounts=accounts,
        )

    def _parse_account_behavior(self, node: ET.Element) -> AccountBehaviorVector:
        contains_raw = self._ex.get_attr(node, "contieneDatos")
        contains_data = contains_raw is not None and contains_raw.lower() == "true"

        monthly = tuple(
            BehaviorMonthlyChar(
                date=self._ex.get_attr_required(c, "fecha"),
                behavior=self._ex.get_attr(c, "saldoDeudaTotalMora"),
            )
            for c in node.findall("CaracterFecha")
        )
        moras_node = self._ex.find_node("MorasMaximas", parent=node)
        max_delinquency = tuple(
            BehaviorMonthlyChar(
                date=self._ex.get_attr_required(c, "fecha"),
                behavior=self._ex.get_attr(c, "saldoDeudaTotalMora"),
            )
            for c in (
                moras_node.findall("CaracterFecha") if moras_node is not None else []
            )
        )
        return AccountBehaviorVector(
            entity=self._ex.get_attr(node, "entidad") or "",
            account_number=self._ex.get_attr(node, "numeroCuenta") or "",
            account_type=self._ex.get_attr(node, "tipoCuenta") or "",
            state=self._ex.get_attr(node, "estado"),
            contains_data=contains_data,
            monthly_chars=monthly,
            max_delinquency_chars=max_delinquency,
        )

    # ── ImagenTendenciaEndeudamiento ──────────────────────────────────────────

    def _parse_trend_series(
        self, imagen_node: Optional[ET.Element]
    ) -> tuple[TrendSeries, ...]:
        if imagen_node is None:
            return ()
        result: list[TrendSeries] = []
        for series_node in imagen_node.findall("Series"):
            valores_node = self._ex.find_node("Valores", parent=series_node)
            data_points = tuple(
                TrendDataPoint(
                    value=self._ex.get_float(v, "valor") or 0.0,
                    date=self._ex.get_attr_required(v, "fecha"),
                )
                for v in (
                    valores_node.findall("Valor") if valores_node is not None else []
                )
            )
            result.append(
                TrendSeries(
                    series_name=self._ex.get_attr(series_node, "serie") or "",
                    data_points=data_points,
                )
            )
        return tuple(result)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _bool_attr(self, node: ET.Element, attr: str) -> bool:
        val = self._ex.get_attr(node, attr)
        return val is not None and val.lower() == "true"

    def _optional_bool(self, val: Optional[str]) -> Optional[bool]:
        if val is None:
            return None
        return val.lower() == "true"
