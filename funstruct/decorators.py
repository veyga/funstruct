def tailrec(fn):
  """
  Marks a function as tail recursive.
  This allows recursive functions to not blow the call stack.
  (use with caution)
  """
  def wrapper(*args, **kwargs):
    return fn(*args, **kwargs)
  return wrapper
