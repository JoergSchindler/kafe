'''
.. module:: function_tools
   :platform: Unix
   :synopsis: This submodule contains several useful tools for getting
   information about a function, including the number, names and default
   values of its parameters and its derivatives with respect to the independent
   variable or the parameters.

.. moduleauthor:: Daniel Savoiu <danielsavoiu@gmail.com>

'''

import numpy as np

# get a numerical derivative calculating function from SciPy
from scipy.misc import derivative as scipy_der


def derivative(func, derive_by_index, variables_tuple, derivative_spacing):
    r'''
    Gives :math:`\frac{\partial f}{\partial x_k}` for :math:`f = f(x_0, x_1,
    \ldots)`. `func` is :math:`f`, `variables_tuple` is :math:`\{x_i\}` and
    `derive_by_index` is :math:`k`.
    '''

    # define a dummy function, so that the variable
    # by which f is to be derived is the only variable
    def tmp_func(derive_by_var):
        argument_list = []
        for arg_nr, arg_val in enumerate(variables_tuple):
            if arg_nr == derive_by_index:
                argument_list.append(derive_by_var)
            else:
                argument_list.append(arg_val)
        return func(*argument_list)

    # return the derivative of that function
    return scipy_der(tmp_func, variables_tuple[derive_by_index],
                     dx=derivative_spacing)


def get_function_property(func, prop):
    '''
    Returns a specific property of the function. This assumes that the function
    is defined as

        >>> def func(x, par1=1.0, par2=3.14, par3=2.71, ...): ...

    **func** : function
        A function object from which to extract the property.

    **prop** : string
        A string representing a property. Can be any of ``'name'``,
        ``'parameter names'``, ``'parameter defaults'`` and
        ``'number of parameters'``
    '''

    if prop == 'name':
        # get the function name from the Python function
        return func.__name__
    elif prop == 'number of parameters':
        # number of parameters is the argument number - 1
        return func.func_code.co_argcount-1
    elif prop == 'parameter names':
        # get list of parameter names
        return func.func_code.co_varnames[1:func.func_code.co_argcount]
    elif prop == 'parameter defaults':
        # get list of parameter defaults
        return func.func_defaults
    else:
        raise AttributeError("Error: Unknown function property `%s'."
                             % (prop,))


def derive_by_x(func, x_0, param_list, derivative_spacing):
    r'''
    If `x_0` is iterable, gives the array of derivatives of a function
    :math:`f(x, par_1, par_2, \ldots)` around :math:`x = x_i` at every
    math:`x_i` in :math:`\vec{x}`. If `x_0` is not iterable, gives the
    derivative of a function :math:`f(x, par_1, par_2, \ldots)` around
    :math:`x = \verb!x_0!`.
    '''
    try:
        iterator_over_x_0 = iter(x_0)  # try to get an iterator object
    except TypeError:
        # object is not iterable, return the derivative in x_0 (float)
        return scipy_der(func, x_0, args=param_list, dx=derivative_spacing)
    else:
        # object is iterable, go through it and derive at each x_0 in it
        output_list = []
        for x in iterator_over_x_0:
            # call recursively
            output_list.append(
                derive_by_x(func, x, param_list, derivative_spacing)
            )

        return np.asarray(output_list)


def derive_by_parameters(func, x_0, param_list, derivative_spacing):
    r'''
    Returns the gradient of `func` with respect to its parameters, i.e. with
    respect to every variable of `func` except the first one.
    '''
    output_list = []

    # compile all function arguments into a variables tuple
    variables_tuple = tuple([x_0] + list(param_list))

    # go through all arguments except the first ones
    # go through all arguments except the first one
    for derive_by_index in xrange(1, func.func_code.co_argcount):
        output_list.append(
            derivative(func, derive_by_index,
                       variables_tuple, derivative_spacing)
        )

    return np.asarray(output_list)


def outer_product(input_array):
    r'''
    Takes a `NumPy` array and returns the outer (dyadic, Kronecker) product
    with itself. If `input_array` is a vector :math:`\mathbf{x}`, this returns
    :math:`\mathbf{x}\mathbf{x}^T`.
    '''
    la = len(input_array)

    # return outer product as numpy array
    return np.kron(input_array, input_array).reshape(la, la)
