from ..models  import *
from ..origin import *


class StandardReader:
    def __init__(self, *, student_id:Union[int, None]):
        if student_id:
            self.student_id = student_id
        else:
            self.student_id = None

    @property
    def get(self):
        if self.student_id:

