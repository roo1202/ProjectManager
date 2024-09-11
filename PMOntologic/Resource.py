
# Class representing a Resource in the project
class Resource:
    def __init__(self, id: str, total: int, cost: float):
        self.id = id
        self.total = total
        self.cost = cost

    def __str__(self):
        return f"Resource(Id : {self.id} Total: {self.total})"
    



