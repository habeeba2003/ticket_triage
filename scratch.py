# # FUNCTIONS AND TYPE HINTS:

# def shout(text: str) -> str:
#     return text.upper() + "!"   #.upper() is a method make all text capital

# print(shout("payment failed"))


# # CLASSES:

# class Ticket:
#     def __init__(self, text: str, customer_id: int):
#         self.text = text
#         self.customer_id = customer_id

# t = Ticket("I was charged twice", 4821)
# print(t.text)

# # EXCEPTION HANDLING:  (use when LLM API can fail)

# try:
#     number = int("abc")
# except ValueError:
#     print("That was not a number")

# # JSON iN PYTHON:

# ticket = {"text": "I was charged twice", "customer_id": 4821}
# as_text = json.dumps(ticket)       # dictionary -> JSON string
# back = json.loads(as_text)         # JSON string -> dictionary
# print(as_text)
# print(back["text"])



# EXERCISE:

def count_words(text: str) -> int:
    
