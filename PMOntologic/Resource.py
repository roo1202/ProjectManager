
# Class representing a Resource in the project
class Resource:
    def __init__(self, id: str, total: int):
        self.id = id
        self.total = total

    def __str__(self):
        return f"Resource(Id : {self.id} Total: {self.total})"
    



