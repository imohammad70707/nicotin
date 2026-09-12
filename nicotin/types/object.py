"""Base class shared by every NICOTIN type, mirroring Pyrogram's ``Object``."""

import json


class Object:
    """
    Base class for all NICOTIN types.

    Gives every type (:class:`Message`, :class:`User`, :class:`Chat`, ...)
    a consistent, debuggable ``repr`` and a ``to_dict`` / JSON helper,
    exactly like Pyrogram's own base ``Object``.
    """

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, default=str, ensure_ascii=False)

    def __repr__(self) -> str:
        args = ", ".join(
            f"{k}={v!r}" for k, v in vars(self).items()
            if not k.startswith("_") and v is not None
        )
        return f"nicotin.types.{self.__class__.__name__}({args})"

    def to_dict(self) -> dict:
        return {
            k: v.to_dict() if isinstance(v, Object) else v
            for k, v in vars(self).items()
            if not k.startswith("_") and v is not None
        }
