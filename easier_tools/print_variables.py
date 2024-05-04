import inspect
from easier_tools.Colorful_Console import ColoredText as CT

def print_variables_class(obj, specific_param=None):
    """
    输出对象的所有属性和属性值
    [使用方法]:
        from easier_tools.print_variables import print_variables_class as pvc
        pvc(你的对象, specific_param=["属性1",...])
    :param obj: 任意对象
    :param specific_param: 指定的属性名
    """
    print(CT("类" + str(obj.__class__) + "的参数如下：").pink())
    for attr in dir(obj):
        if not callable(getattr(obj, attr)) and not attr.startswith("__"):
            if specific_param is None or attr in specific_param:
                value = getattr(obj, attr)
                print(f"{CT(attr).pink()}: {value}")


def print_variables_function(func, *args, **kwargs):
    """
    输出函数的所有参数与其值
    [使用方法]:
        from easier_tools.print_variables import print_variables_function as pvf
        pvf(函数, 0~多个传入的参数)
    [注意事项]:
        传入的是函数名，因此函数不要带括号
    :param func: 传入的函数
    :param args: Positional arguments to pass to the function.
    :param kwargs: Keyword arguments to pass to the function.
    """
    # 获取函数的参数签名
    signature = inspect.signature(func)
    bound_args = signature.bind(*args, **kwargs)
    bound_args.apply_defaults()

    # 构建参数及其值的字典
    args_dict = dict(bound_args.arguments)
    # 输出字典的键值对
    print(CT("函数" + str(func.__name__) + "的参数如下：").pink())
    for key, value in args_dict.items():
        print(f"{CT(key).pink()}: {value}")

