from typing import Annotated

from fastapi import Depends, Header, Path


def get_current_user_id(x_user_id: Annotated[int, Header()]) -> int:
    return x_user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]

EventId = Annotated[int, Path(gt=0)]
