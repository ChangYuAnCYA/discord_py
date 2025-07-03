class _1A2B():
    def __init__(self, id:int):
        self.id = id
        self.string = None
        self.digit = None
        self.status = None
        self.guess = None
        self.total_count = None

    def update(self, string:str, num:int, total:int):
        self.string = string
        self.digit = num
        self.status = True
        self.total_count = total


    def call(self, guess_string:str):
        self.guess = guess_string
        result = None
        try:
            int(self.guess)
        except:
            return
        
        check = True
        for i in self.guess:
            num = self.guess.count(i)
            if num != 1:
                check = False
                result = f">>> 輸入數字有重複喔~"
                break
            
        if len(self.guess) != len(self.string):
            check = False
            result = f">>> 輸入數字位數與設置不同喔~"
        
        self.total_count += 1
        if check:
            checkA, checkB = 0, 0
            for i in self.guess:
                if i in self.string:
                    checkB += 1
            for i, j in enumerate(self.guess):
                if self.guess[i] == self.string[i]:
                    checkA += 1

            checkB = checkB - checkA
            result = f">>> {checkA}A{checkB}B\n目前回答次數: {self.total_count}"
            if checkA == len(self.guess):
                result = f">>> 恭喜回答正確！\n總回答次數: {self.total_count}\n可重新設置遊戲！"
                self.string = None
                self.digit = None
                self.status = None
                self.guess = None
                self.total_count = None
        
        return result