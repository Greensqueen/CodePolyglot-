"""
示例代码 - 用于测试分析器
"""


def calculate_factorial(n: int) -> int:
    """计算一个整数的阶乘。

    Args:
        n: 非负整数

    Returns:
        n 的阶乘

    Raises:
        ValueError: 如果 n 为负数
    """
    if n < 0:
        raise ValueError(\"阶乘未定义负数\")
        if n == 0:
            return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


def fibonacci(n: int) -> int:
    """使用递归计算斐波那契数。

    TODO: 此函数效率较低，可考虑添加缓存优化。
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


class MathUtils:
    """数学工具类。

    这是一个示例类，包含一些基本的数学操作。
    """

    PI = 3.141592653589793

    @staticmethod
    def circle_area(radius: float) -> float:
        """计算圆的面积。"""
        return MathUtils.PI * radius * radius

    # FIXME: 此方法尚未实现异常处理
    @staticmethod
    def divide(a: float, b: float) -> float:
        """两个数相除。"""
        return a / b


def main() -> None:
    """主函数，演示功能。"""
    print(\"5的阶乘是:\", calculate_factorial(5))
    print(\"斐波那契第10项是:\", fibonacci(10))
    print(\"半径为3的圆面积是:\", MathUtils.circle_area(3.0))

    if __name__ == \"__main__\":
    main()