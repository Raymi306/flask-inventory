from typing import Annotated

from pydantic import Field, TypeAdapter

from app.constants import MIN_PASSWORD_LENGTH

NewPassword = Annotated[str, Field(min_length=MIN_PASSWORD_LENGTH)]
validate_new_password = TypeAdapter(NewPassword).validate_python
