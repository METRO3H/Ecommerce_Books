import time

def verbose_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours} horas, {minutes} minutos, {seconds} segundos"

