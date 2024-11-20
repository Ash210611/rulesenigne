from functools import wraps

import inspect


# ===============================================================================
def visualize_call_tree(some_function):
    '''
    To print a call tree, add this as a decorator before the function.

    For example, suppose you have a chain of functions like this:
        def a ():
                print ('a')
        def b ():
                a ()
        def c ():
                b ()

    When you call c(), it calls b(), which calls a(), which prints 'a'.

    If you add this decorator before defining a(), it will print the call
    tree.  In other words, if you edit your code to say:
        from visualize_call_tree		import visualize_call_tree
        ...
        @visualize_call_tree
        def a ():
                print ('a')

    Then it will print this before running the rest of a():
        Call tree: <module> -> c -> b -> a

    You can add that decorator before all your function calls, and turn them
    ALL off by changing the internal variable, should_print_call_tree = False
    '''

    @wraps(some_function)
    def visualize_wrapper(*args, **kwds):

        should_print_call_tree = False
        # Set False to turn this off

        if should_print_call_tree:
            frame = inspect.currentframe().f_back
            tree = ''
            while frame is not None:
                # (filename, line_num, func_name, lines, index) = inspect.getframeinfo(frame)
                (_, _, func_name, _, _) = inspect.getframeinfo(frame)

                if func_name != 'visualize_wrapper':
                    # print (f'  filename     : {filename}')
                    # print (f'  line_number  : {line_num}')
                    # print (f'  function_name: {func_name}')
                    # print (f'  line         : {lines}')
                    # print (f'  index        : {index}')
                    if tree == '':
                        tree = f'{func_name}'
                    else:
                        tree = f'{func_name} -> ' + tree

                frame = frame.f_back

            tree = f'{tree} -> ' + some_function.__name__
            print(f'Call tree: {tree}')

        return some_function(*args, **kwds)

    return visualize_wrapper
