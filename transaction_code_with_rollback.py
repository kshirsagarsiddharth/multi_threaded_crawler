import functools
class Account:
    def __init__(self,owner,amount = 0):
        self.owner = owner
        self.amount = amount
        self._transaction = []
    
    def __repr__(self):
        return f"Account({self.owner !r},{self.amount !r})"
    
    def __str__(self):
        return f"Account of {self.owner} with starting amount {self.amount}"
    
    def add_transaction(self,amount):
        if not isinstance(amount,int):
            raise ValueError("Please use int for amount")
        else:
            self._transaction.append(amount)
    
    @property
    def balance(self):
        return self.amount + sum(self._transaction)
    
    def __len__(self): 
        return len(self._transaction)
    
    def __getitem__(self,position):
        return self._transaction[position]
    
    def __reversed__(self):
        return self[::-1]
    
    @functools.total_ordering

    def __eq__(self,other):
        return self.balance == other.balance
    
    def  __lt__(self,other):
        return self.balance < other.balance
    
    def __gt__(self,other):
        return self.balance > other.balance
    
    def __add__(self,other):
        owner = f"{self.owner}&{other.owner}"
        start_amount = self.amount + other.amount
        acc = Account(owner,start_amount)
        for t in list(self) + list(other):
            acc.add_transaction(t)
        return acc
    
    def __call__(self):
        print(f"start amount {self.amount}")
        print("Transactions: ")
        for transaction in self:
            print(transaction)
        print(f"\n Balance {self.balance}")
    
    def __enter__(self):
        print("ENTER WITH: Making backup of transactions for rollback")
        self._copy_transaction = list(self._transaction)
        return self
    
    def __exit__(self,exc_type,exc_val,exc_tb):
        print("EXIT WITH:",end = " ")
        if exc_type:
            self._transaction = self._copy_transaction
            print("Rolling Back to previous transaction")
            print(f"Transaction resulted in {exc_type.__name__} ({eexc_val})")
        else:
            print("Transaction Ok")
    