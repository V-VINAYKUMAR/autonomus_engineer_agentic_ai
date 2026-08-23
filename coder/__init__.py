def __init__(self):

    self.state = load_state()
    self.coder = Coder()

    self.context_builder = ContextBuilder()