from typing import TypeVar

from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel
from pydantic import ValidationError

from config import get_llm

SchemaT = TypeVar("SchemaT", bound=BaseModel)
MAX_STRUCTURED_ATTEMPTS = 3


class StructuredOutputError(RuntimeError):
    pass


def invoke_structured(schema: type[SchemaT], prompt: str) -> SchemaT:
    """Invoke Gemini with schema validation and normalize dict responses."""
    structured_llm = get_llm().with_structured_output(schema)
    last_error = None
    for _ in range(MAX_STRUCTURED_ATTEMPTS):
        try:
            result = structured_llm.invoke(prompt)
            if isinstance(result, schema):
                return result
            return schema.model_validate(result)
        except (OutputParserException, ValidationError, TypeError, ValueError) as exc:
            last_error = exc

    raise StructuredOutputError(
        f"Model failed to return valid {schema.__name__} output after "
        f"{MAX_STRUCTURED_ATTEMPTS} attempts"
    ) from last_error
