from framework.logger import logger
import time
import functools


def disk_operation_with_retry(max_retries=3, delay=5):
    """Decorator for disk operations requiring retries"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context = next((arg for arg in args
                            if hasattr(arg, '_context')), None)

            # Check for negative test marker
            is_negative = (context and context._context.request.node
                           .get_closest_marker('nc') is not None)

            if is_negative:
                return func(*args, **kwargs)

            attempts = 0
            last_error = None

            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except ValueError as e:
                    last_error = e
                    attempts += 1
                    if attempts < max_retries:
                        logger.info(f"Attempt {attempts} failed: {str(e)}. "
                                    f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                        if context:
                            context._context.tools_manager.cluster.update_cluster_info()

            raise ValueError(f"Operation failed after {max_retries} attempts. "
                             f"Last error: {last_error}")

        return wrapper

    return decorator


