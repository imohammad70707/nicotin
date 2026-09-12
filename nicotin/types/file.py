from __future__ import annotations

from .object import Object


class File(Object):
    """
    Metadata about a photo/video/voice/document attached to a message,
    shaped like Pyrogram's media types (``Photo``, ``Document``, ...
    unified here into one class, since Rubika's API represents them
    uniformly as a ``file_inline`` object).

    :param id: the file's unique id on Rubika's storage (``file_id``).
    :param access_hash_rec: access hash needed to download the file.
    :param name: original file name, if any.
    :param size: size in bytes.
    :param mime_type: MIME type reported by the sender's client.
    :param duration: duration in seconds, for voice/video/music.
    :param width: width in pixels, for photo/video.
    :param height: height in pixels, for photo/video.
    """

    def __init__(
        self,
        *,
        client=None,
        id: str,
        access_hash_rec: str | None = None,
        name: str | None = None,
        size: int | None = None,
        mime_type: str | None = None,
        duration: int | None = None,
        width: int | None = None,
        height: int | None = None,
    ):
        self._client = client
        self.id = id
        self.access_hash_rec = access_hash_rec
        self.name = name
        self.size = size
        self.mime_type = mime_type
        self.duration = duration
        self.width = width
        self.height = height

    async def download(self, file_path: str | None = None) -> str:
        """Shortcut for ``client.download_media(file)``."""
        return await self._client.download_media(self, file_path=file_path)

    @classmethod
    def _parse(cls, client, data: dict) -> "File":
        return cls(
            client=client,
            id=data.get("file_id", ""),
            access_hash_rec=data.get("access_hash_rec"),
            name=data.get("file_name"),
            size=data.get("size"),
            mime_type=data.get("mime"),
            duration=data.get("time"),
            width=data.get("width"),
            height=data.get("height"),
        )
