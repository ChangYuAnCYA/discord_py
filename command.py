class Command:
    def __init__(self, id:int, message=[], font=None, delete=False, photoparameter=[]):
        self.id = id
        self.command = False
        self.idol = False
        self.channel = None
        self.task = None
        self.font = font
        self.photo = None
        self.welcome = None
        self.message = message
        self.btn_msg = None
        self.luck_cnt = {}
        self.reset = True
        self.delete = delete
        self.photoparameter = photoparameter