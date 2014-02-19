class SelectionProviderNotFoundError(Exception):

    def __init__(self, provider_id):
        self.provider_id = provider_id

    def __str__(self):
        msg = "Selection provider '{id}' not found in selection service."
        return msg.format(id=self.provider_id)
