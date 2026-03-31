from typing import Optional
from xml.etree import ElementTree as ET

from data_adapter.transformers.credit_card_transformer import (
    transform_credit_card_class,
    transform_franchise,
    transform_plastic_status,
)
from data_adapter.transformers.global_report_transformer import transform_account_condition
from data_adapter.transformers.shared_transformers import (
    transform_credit_rating,
    transform_currency,
    transform_guarantee,
    transform_industry_sector,
    transform_origin_state,
    transform_ownership_situation,
    transform_payment_method,
    transform_payment_status,
)
from data_adapter.xml_adapter.models.credit_card_models import (
    CreditCard,
    CreditCardCharacteristics,
    CreditCardStates,
    CreditCardValues,
)
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class CreditCardReportBuilder:
    """Parses TarjetaCredito nodes into CreditCard dataclasses."""

    def parse_cards(self, ex: XmlExtractor, report_node: ET.Element) -> tuple[CreditCard, ...]:
        nodes = report_node.findall(".//TarjetaCredito")
        return tuple(self._parse_card(ex, node) for node in nodes)

    def _parse_card(self, ex: XmlExtractor, node: ET.Element) -> CreditCard:
        raw_hd = ex.get_attr(node, "calificacionHD")
        return CreditCard(
            lender=ex.get_attr_required(node, "entidad"),
            account_number=ex.get_attr_required(node, "numero"),
            opened_date=ex.get_attr(node, "fechaApertura"),
            maturity_date=ex.get_attr(node, "fechaVencimiento"),
            payment_history=ex.get_attr(node, "comportamiento"),
            payment_method=transform_payment_method(ex.get_attr(node, "formaPago")),
            default_probability=ex.get_float(node, "probabilidadIncumplimiento"),
            credit_rating=transform_credit_rating(ex.get_attr(node, "calificacion")),
            ownership_situation=transform_ownership_situation(ex.get_attr(node, "situacionTitular")),
            is_blocked=self._parse_blocked(ex, node),
            office=ex.get_attr(node, "oficina"),
            city=ex.get_attr(node, "ciudad"),
            dane_city_code=ex.get_attr(node, "codigoDaneCiudad"),
            sector=transform_industry_sector(ex.get_attr(node, "sector")),
            entity_id_type=ex.get_attr(node, "tipoIdentificacion"),
            entity_id=ex.get_attr(node, "identificacion"),
            hd_rating=raw_hd is not None and raw_hd.lower() in ("true", "1"),
            characteristics=self._parse_characteristics(ex, node),
            values=self._parse_values(ex, node),
            states=self._parse_states(ex, node),
        )

    def _parse_blocked(self, ex: XmlExtractor, node: ET.Element) -> bool:
        raw = ex.get_attr(node, "bloqueada")
        if raw is None:
            return False
        return raw.lower() in ("true", "1", "s", "si")

    def _parse_characteristics(self, ex: XmlExtractor, parent: ET.Element) -> CreditCardCharacteristics:
        node = ex.find_node("Caracteristicas", parent=parent)
        raw_covered = ex.get_attr(node, "amparada")
        is_covered = raw_covered is not None and raw_covered.lower() in ("true", "1", "s", "si")
        return CreditCardCharacteristics(
            franchise=transform_franchise(ex.get_attr(node, "franquicia")),
            card_class=transform_credit_card_class(ex.get_attr(node, "clase")),
            brand=ex.get_attr(node, "marca"),
            is_covered=is_covered,
            covered_code=ex.get_attr(node, "codigoAmparada"),
            guarantee=transform_guarantee(ex.get_attr(node, "garantia")),
        )

    def _parse_values(self, ex: XmlExtractor, parent: ET.Element) -> Optional[CreditCardValues]:
        values_node = ex.find_node("Valores", parent=parent)
        if values_node is None:
            return None
        valor_node = ex.find_node("Valor", parent=values_node)
        if valor_node is None:
            return None
        return CreditCardValues(
            currency_code=transform_currency(ex.get_attr(valor_node, "moneda")),
            date=ex.get_attr(valor_node, "fecha"),
            rating=transform_credit_rating(ex.get_attr(valor_node, "calificacion")),
            outstanding_balance=ex.get_float(valor_node, "saldoActual"),
            past_due_amount=ex.get_float(valor_node, "saldoMora"),
            available_limit=ex.get_float(valor_node, "disponible"),
            installment_value=ex.get_float(valor_node, "cuota"),
            missed_payments=ex.get_int(valor_node, "cuotasMora"),
            days_past_due=ex.get_int(valor_node, "diasMora"),
            last_payment_date=ex.get_attr(valor_node, "fechaPagoCuota"),
            due_date=ex.get_attr(valor_node, "fechaLimitePago"),
            total_credit_limit=ex.get_float(valor_node, "cupoTotal"),
        )

    def _parse_states(self, ex: XmlExtractor, parent: ET.Element) -> CreditCardStates:
        states_node = ex.find_node("Estados", parent=parent)
        if states_node is None:
            return CreditCardStates(
                plastic_state_code=None,
                plastic_state_date=None,
                account_state_code=None,
                account_state_date=None,
                origin_state_code=None,
                origin_state_date=None,
                payment_status_code=None,
                payment_status_months=None,
                payment_status_date=None,
            )

        ep = ex.find_node("EstadoPlastico", parent=states_node)
        ec = ex.find_node("EstadoCuenta", parent=states_node)
        eo = ex.find_node("EstadoOrigen", parent=states_node)
        epago = ex.find_node("EstadoPago", parent=states_node)

        return CreditCardStates(
            plastic_state_code=transform_plastic_status(ex.get_attr(ep, "codigo")),
            plastic_state_date=ex.get_attr(ep, "fecha"),
            account_state_code=transform_account_condition(ex.get_attr(ec, "codigo")),
            account_state_date=ex.get_attr(ec, "fecha"),
            origin_state_code=transform_origin_state(ex.get_attr(eo, "codigo")),
            origin_state_date=ex.get_attr(eo, "fecha"),
            payment_status_code=transform_payment_status(ex.get_attr(epago, "codigo")),
            payment_status_months=ex.get_attr(epago, "meses"),
            payment_status_date=ex.get_attr(epago, "fecha"),
        )
