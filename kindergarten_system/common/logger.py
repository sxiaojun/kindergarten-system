import logging


def get_logger(name):
    """
    获取配置好的日志记录器

    Args:
        name (str): 日志记录器名称，建议使用 __name__

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    return logger


# 创建默认的日志记录器
default_logger = get_logger(__name__)
