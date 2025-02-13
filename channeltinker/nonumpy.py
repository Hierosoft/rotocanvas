"""nonumpy is for when you don't have numpy, such as in GIMP"""
import math

class float64(float):
    pass

class array(list):
    def __init__(self, values, dtype=float64):
        list.__init__(self)
        self += values

    def __sub__(self, other):
        return array([self[i] - other[i] for i in range(len(other))])

    def __truediv__(self, scalar):
        """
        Divide vector by a scalar or element-wise by another vector.

        Args:
            scalar (float, int, or list/tuple/array): Scalar value or vector.

        Returns:
            array: Resulting vector after division.

        Raises:
            ValueError: If scalar is zero or vector lengths do not match.
        """
        if isinstance(scalar, (list, tuple, array)):
            if len(self) != len(scalar):
                raise ValueError("Vectors must be the same length for element-wise division.")
            return array([float(x) / float(y) for x, y in zip(self, scalar)])
        if scalar == 0:
            raise ValueError("Cannot divide by zero.")
        return array([float(x) / float(scalar) for x in self])

import math

class linalg:
    def __init__(self):
        raise RuntimeError("Cannot be instantiated. Use statically.")

    @classmethod
    def norm(cls, x, ord=None, axis=None, keepdims=False):
        """
        Compute the norm of a matrix or vector.

        Args:
            x (list or tuple): Input vector or matrix.
            ord (int, float, inf, -inf, str): Order of the norm. Options
                include:
                None (2-norm), 'fro' (Frobenius norm), 'nuc' (nuclear
                norm), inf (max sum of absolute values along axis), -inf
                (min sum), 1 (maximum sum along axis), etc.
            axis (int, tuple of ints, optional): Axis or axes along
                which to compute the norm.
            keepdims (bool): If True, the reduced axes are retained with
                size one.
                TODO: keepdims not implemented

        Returns:
            float or list: The norm of the matrix or vector.

        Raises:
            ValueError: If the input has an invalid shape or zero magnitude.
        """
        if isinstance(x, list) and all(isinstance(i, list) for i in x):
            # Handle the 2-D matrix norm
            return cls._norm_2d(x, ord=ord, axis=axis)
        elif isinstance(x, (list, tuple)):
            # Handle the 1-D vector norm
            return cls._norm_1d(x, ord=ord)
        else:
            raise ValueError("Input must be a 1-D or 2-D list or tuple.")

    @classmethod
    def _norm_1d(cls, vec, ord=None):
        """
        Compute the norm of a 1D vector.

        Args:
            vec (list or tuple): Input vector.
            ord (int, float, inf, -inf): Order of the norm.

        Returns:
            float: The computed norm of the vector.
        """
        if ord is None:
            # 2-norm (Euclidean norm)
            magnitude = math.sqrt(sum(x**2 for x in vec))
        elif ord == 1:
            # 1-norm (sum of absolute values)
            magnitude = sum(abs(x) for x in vec)
        elif ord == float('inf'):
            # Infinity norm (maximum absolute value)
            magnitude = max(abs(x) for x in vec)
        elif ord == -float('inf'):
            # Negative infinity norm (minimum absolute value)
            magnitude = min(abs(x) for x in vec)
        else:
            # General case for arbitrary ord
            magnitude = sum(abs(x)**ord for x in vec)**(1./ord)

        return magnitude

    @classmethod
    def _norm_2d(cls, matrix, ord=None, axis=None):
        """
        Compute the norm of a 2D matrix.

        Args:
            matrix (list of list): Input matrix.
            ord (int, float, str): Order of the norm.
            axis (int, tuple of ints): Axis along which to compute the norm.

        Returns:
            float or list: The computed norm of the matrix.
        """
        if ord == 'fro':
            # Frobenius norm (sqrt(sum of squared entries))
            return math.sqrt(sum(sum(x**2 for x in row) for row in matrix))
        elif ord == 'nuc':
            # Nuclear norm (sum of singular values) approximation
            raise NotImplementedError("Nuclear norm is not implemented.")
        elif axis is None:
            # Compute norm of the whole matrix
            return cls._norm_1d([item for row in matrix for item in row], ord=ord)
        else:
            # Compute norms along an axis
            if isinstance(axis, int):
                return [cls._norm_1d(row, ord=ord) for row in matrix]
            elif isinstance(axis, tuple):
                raise NotImplementedError("Multiple axis support is not implemented.")
            else:
                raise ValueError("Invalid axis value.")

def dot(a, b):
    """
    Compute the dot product of two vectors or matrices.

    Args:
        a (list or tuple): First vector or matrix.
        b (list or tuple): Second vector or matrix.

    Returns:
        float or list: The dot product result.

    Raises:
        ValueError: If the dimensions are not aligned for dot product.
    """
    # Case 1: If both are scalars
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a * b

    # Case 2: If both are 1-D arrays (vectors), compute the inner product
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            raise ValueError("Vectors must have the same length.")
        return sum(x * y for x, y in zip(a, b))

    # Case 3: If a is 2-D and b is 2-D, perform matrix multiplication
    if isinstance(a[0], (list, tuple)) and isinstance(b[0], (list, tuple)):
        if len(a[0]) != len(b):
            raise ValueError("Incompatible dimensions for matrix multiplication.")
        # Matrix multiplication: rows of a with columns of b
        return [
            [sum(x * y for x, y in zip(row_a, col_b)) for col_b in zip(*b)]
            for row_a in a
        ]

    # Case 4: If a is N-D and b is 1-D, sum product over the last axis of a and b
    if isinstance(a[0], (list, tuple)):
        # Handle higher dimensions and summing over last axis
        if len(a[0]) != len(b):
            raise ValueError("Incompatible dimensions for dot product.")
        return [
            [sum(x * y for x, y in zip(row_a, b)) for row_a in a]
        ]

    # Case 5: If a is N-D and b is M-D with M >= 2, sum product over last axis of a and second-to-last axis of b
    if isinstance(a[0], (list, tuple)) and isinstance(b[0][0], (list, tuple)):
        # Handle N-D with M >= 2
        if len(a[0]) != len(b):
            raise ValueError("Incompatible dimensions for dot product.")
        return [
            [sum(x * y for x, y in zip(row_a, col_b)) for col_b in zip(*b)]
            for row_a in a
        ]

    # If no condition matched, raise ValueError for incompatible types
    raise ValueError("Unsupported input types for dot product.")