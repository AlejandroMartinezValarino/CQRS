"""Excepciones específicas de GraphQL."""
from common.exceptions import GraphQLError


class InvalidLimitError(GraphQLError):
    """Excepción cuando el límite es inválido."""
    pass
