import socket


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


host = get_host_ip()


def make_link_html(text, link):
    return '<a href="http://' + host + ':8888/' + link + '">' + text + "</a>"
