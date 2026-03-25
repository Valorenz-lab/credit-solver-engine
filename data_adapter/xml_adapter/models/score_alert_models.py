from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ScoreReason:
    """<Razon> node within <Score>."""
    code: str


@dataclass(frozen=True)
class ScoreRecord:
    """
    <Score> node in <Informe>.
    Only the most recent score per score type is included.
    See Table 19 for score types.
    """
    score_type: str          # tipo — Table 19
    score_value: float       # puntaje
    classification: Optional[str]   # clasificacion
    population_pct: Optional[int]   # poblacion — % of population above this score
    date: str                # fecha
    reasons: tuple[ScoreReason, ...]


@dataclass(frozen=True)
class AlertSource:
    """<Fuente> node within <Alerta>."""
    code: str
    name: Optional[str]


@dataclass(frozen=True)
class AlertRecord:
    """
    <Alerta> node in <Informe>.
    Fraud / identity alerts placed by the person or an entity.
    See Table 28 for alert codes.
    """
    placed_date: str         # colocacion
    expiry_date: str         # vencimiento
    cancelled_date: Optional[str]   # modificacion — set if manually cancelled
    code: str                # codigo — Table 28
    text: Optional[str]      # texto
    source: Optional[AlertSource]
