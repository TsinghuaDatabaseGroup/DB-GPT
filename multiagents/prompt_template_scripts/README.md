
## Initial Implementation
First, we generate the instruction from a small number of collected samples (splitting into training and evaluation sets), i.e., deriving several instructions using the LLM on training set and choosing the best instruction by evaluating on evaluation set. 

Second, based on the task requirements, we collect other input features such as demonstration examples (e.g., query rewriting pairs) and data statistics (e.g., distinct value ratios of the columns). 

Finally, we concatenate the instruction, collected features, and the input into a prompt sequence, and rely on the LLM to output desired results based on the prompt sequence.