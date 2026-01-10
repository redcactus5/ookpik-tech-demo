class RendererError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class RendererNotStartedError(RendererError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
